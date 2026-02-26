import streamlit as st
from datetime import date
import time
import pandas as pd
import plotly.express as px
import database as db  # Ponto de unificação modular que conecta db_config e db_financeiro
import funcoes_admin as f_adm
import servicos_email as email_svc
import admin_exportacao as export_svc

def _enriquecer_dados(df_f, atl_data):
    """Enriquece a tabela com dados financeiros atuais e remove Timezone"""
    atl_map = {a['cpf']: {'saldo': a.get('saldo', 0), 'bolsa': a.get('bolsa', 0)} for a in atl_data}

    def get_fin(cpf, campo): 
        return atl_map.get(cpf, {}).get(campo, 0.0) if cpf else 0.0

    df_f['Saldo Atual'] = df_f['atleta_cpf'].apply(lambda x: get_fin(x, 'saldo'))
    df_f['Valor Bolsa'] = df_f['atleta_cpf'].apply(lambda x: get_fin(x, 'bolsa'))
    df_f['NFs Entregues Acumulado'] = df_f['Valor Bolsa'] - df_f['Saldo Atual']

    # REPARO MARVEL: Blindagem contra erro de Timezone para visualização e Excel
    for col in df_f.columns:
        if pd.api.types.is_datetime64tz_dtype(df_f[col]):
            df_f[col] = df_f[col].dt.tz_localize(None)

    return df_f

def renderizar_aba_auditoria(atl_data, lan_data):
    """ABA 1: Módulo de Operação (Visualização de Notas e Ações de Status)"""
    st.markdown("### 🔍 Auditoria Operacional")

    c1, c2, c3 = st.columns(3)
    mes = c1.selectbox("Mês:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1, key="aud_mes")
    ano = c2.selectbox("Ano:", [2024, 2025, 2026], index=2, key="aud_ano")
    st_f = c3.selectbox("Status:", ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"], index=1, key="aud_st")

    m_idx = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes) + 1

    # Filtra os lançamentos através do motor de funções admin
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty: 
        st.warning("Nada para auditar neste período.")
        return

    df_f = _enriquecer_dados(df_f, atl_data)
    id_sel = None

    # Visualização de Tabela Prime com configuração de moeda
    ev = st.dataframe(
        df_f[['Status_UI', 'Atleta (Bolsa)', 'Valor Bolsa', 'NFs Entregues Acumulado', 'valor', 'Saldo Atual', 'data_nota', 'foto_url']], 
        column_config={
            "foto_url": st.column_config.ImageColumn("NF"), 
            "Valor Bolsa": st.column_config.NumberColumn("Bolsa Total", format="R$ %.2f"),
            "NFs Entregues Acumulado": st.column_config.NumberColumn("Já Recebido", format="R$ %.2f"),
            "valor": st.column_config.NumberColumn("Valor NF", format="R$ %.2f"),
            "Saldo Atual": st.column_config.NumberColumn("Saldo Restante", format="R$ %.2f")
        },
        use_container_width=True, 
        hide_index=True, 
        on_select="rerun", 
        selection_mode="single-row"
    )

    if ev.selection.rows: 
        id_sel = df_f.iloc[ev.selection.rows[0]]['id']

    # --- AÇÃO DA NOTA SELECIONADA ---
    if id_sel:
        st.divider()
        nota = df_f[df_f['id'] == id_sel].iloc[0]

        # Mostra detalhes financeiros do beneficiário
        f_adm.exibir_origem_com_saldo(nota['Atleta (Bolsa)'], nota['Lançado por'], nota['Saldo Atual'])

        if nota.get('orfao', False):
            st.warning("🚨 REGISTRO SEM BENEFICIÁRIO: Vincule a um atleta:")
            atl_opcoes = {f"{a['nome']} (Saldo: R$ {a['saldo']:.2f})": a['cpf'] for a in atl_data}
            escolha = st.selectbox("Vincular a:", ["Selecione..."] + list(atl_opcoes.keys()))
            if st.button("🔗 Confirmar Vínculo e Abater Saldo", use_container_width=True):
                if escolha != "Selecione...":
                    ok, msg = db.vincular_atleta_a_nota(nota['id'], atl_opcoes[escolha], nota['valor'])
                    if ok: st.success(msg); time.sleep(1.2); st.rerun()
                    else: st.error(msg)

        c_img, c_btn = st.columns([1.2, 1])
        with c_img:
            st.image(nota['foto_url'], caption="Comprovante Selecionado", use_container_width=True)

        with c_btn:
            st.markdown(f"### Valor: **R$ {nota['valor']:,.2f}**")
            # Ações de Status via db_financeiro (integrado em database.py)
            if st.button("✅ Aprovar Nota", use_container_width=True, type="secondary"):
                db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'], "✅ Aprovada")
                st.rerun()
            if st.button("❌ Reprovar e Estornar", use_container_width=True):
                db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'], "❌ Reprovada")
                st.rerun()
            st.divider()
            if st.button("🗑️ Excluir permanentemente", use_container_width=True, type="primary"):
                ok, msg = db.excluir_nota_fiscal(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'])
                if ok: st.success(msg); time.sleep(1); st.rerun()
                else: st.error(msg)

def renderizar_aba_bi(atl_data, lan_data, admin_atual):
    """ABA 2: Centro de Comando (Gráficos e Chamada p/ Módulo de Exportação)"""
    st.markdown("### 📊 Inteligência Financeira (BI)")

    c1, c2, c3 = st.columns(3)
    mes = c1.selectbox("Mês Análise:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1, key="bi_mes")
    ano = c2.selectbox("Ano Análise:", [2024, 2025, 2026], index=2, key="bi_ano")
    st_f = c3.selectbox("Status Filtro:", ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"], index=0, key="bi_st")

    m_idx = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes) + 1
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty: 
        st.warning("Nenhum dado financeiro disponível para este filtro.")
        return

    df_f = _enriquecer_dados(df_f, atl_data)

    st.divider()

    # --- MOTOR DE GRÁFICOS PI ---
    st.markdown("#### 📈 Volume Financeiro por Atleta")
    df_chart = df_f.copy()
    df_chart['Atleta_Nome'] = df_chart['Atleta (Bolsa)'].apply(lambda x: str(x).split('(')[0].strip())
    df_agrupado = df_chart.groupby('Atleta_Nome')['valor'].sum().reset_index().sort_values(by='valor', ascending=False)

    fig = px.bar(df_agrupado, x='Atleta_Nome', y='valor', text_auto='.2f', 
                 labels={'Atleta_Nome': 'Atleta', 'valor': 'Total (R$)'},
                 color='valor', color_continuous_scale='Reds')

    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- EXPORTAÇÃO EXECUTIVA ---
    st.markdown("#### 📤 Exportação e Governança")
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.info("💾 **Planilha Detalhada (.xlsx)**")
        # O export_svc já cuida da remoção de timezone internamente para o Excel
        excel_buffer = export_svc.gerar_excel_bi(df_f, mes, ano, st_f)
        st.download_button(
            label="📥 Baixar Excel Auditado",
            data=excel_buffer,
            file_name=f"Auditoria_BI_{mes}_{ano}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )

    with col_exp2:
        st.info("📧 **Relatório para Diretoria**")
        # Recupera e-mail padrão do db_config através de database.py
        dest = st.text_input("E-mail de destino:", value=db.obter_email_admin(), key="email_dest")
        if st.button("🚀 Disparar Dashboard", use_container_width=True, type="primary"):
            if "@" in dest:
                with st.spinner("Compilando dados e enviando..."):
                    html_body = export_svc.gerar_html_email_bi(df_f, mes, ano, st_f)
                    assunto = f"📊 Relatório Financeiro ({mes}/{ano}) - {st_f}"
                    ok, msg = email_svc.enviar_relatorio(dest, assunto, html_body)
                    if ok: 
                        db.registrar_log_exportacao(admin_atual, dest, f"Filtros: {mes}/{ano}-{st_f}", len(df_f))
                        st.success(msg)
                    else: st.error(msg)
            else: st.warning("Insira um e-mail válido.")

# [admin_auditoria.py][Blindagem Marvel v5.2][2026-02-26 17:15]