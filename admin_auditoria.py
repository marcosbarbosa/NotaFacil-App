import streamlit as st
from datetime import date
import time
import pandas as pd
import plotly.express as px
import database as db  
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

    # REPARO MARVEL: Blindagem contra erro de Timezone para Excel
    for col in df_f.columns:
        if pd.api.types.is_datetime64tz_dtype(df_f[col]):
            df_f[col] = df_f[col].dt.tz_localize(None)

    return df_f

def renderizar_aba_auditoria(atl_data, lan_data):
    """ABA 1: Operação de Auditoria - Aprovação e Vínculo"""
    st.markdown("### 🔍 Auditoria Operacional")

    c1, c2, c3 = st.columns(3)
    meses_lista = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    mes = c1.selectbox("Mês:", meses_lista, index=date.today().month-1, key="aud_mes")
    ano = c2.selectbox("Ano:", [2024, 2025, 2026], index=2, key="aud_ano")
    st_f = c3.selectbox("Status:", ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"], index=1, key="aud_st")

    m_idx = meses_lista.index(mes) + 1
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty: 
        st.warning("Nada para auditar neste período.")
        return

    df_f = _enriquecer_dados(df_f, atl_data)
    id_sel = None

    # Tabela Prime com visualização de NF
    ev = st.dataframe(
        df_f[['Status_UI', 'atleta_nome', 'Valor Bolsa', 'valor', 'Saldo Atual', 'data_nota', 'foto_url', 'lancado_por']], 
        column_config={
            "foto_url": st.column_config.ImageColumn("NF"), 
            "Valor Bolsa": st.column_config.NumberColumn("Bolsa Total", format="R$ %.2f"),
            "valor": st.column_config.NumberColumn("Valor NF", format="R$ %.2f"),
            "Saldo Atual": st.column_config.NumberColumn("Saldo Restante", format="R$ %.2f"),
            "lancado_por": "Operador"
        },
        use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row"
    )

    if ev.selection.rows: 
        id_sel = df_f.iloc[ev.selection.rows[0]]['id']

    if id_sel:
        st.divider()
        nota = df_f[df_f['id'] == id_sel].iloc[0]

        # FIX OPERADOR: Exibe quem lançou vs quem recebe
        f_adm.exibir_origem_com_saldo(nota['atleta_nome'], nota.get('lancado_por', 'N/A'), nota['Saldo Atual'])

        c_img, c_btn = st.columns([1.2, 1])
        with c_img:
            st.image(nota['foto_url'], caption="Comprovante Selecionado", use_container_width=True)

        with c_btn:
            st.markdown(f"### Valor NF: **R$ {nota['valor']:,.2f}**")

            # FIX APROVAÇÃO: Envia os 5 argumentos corretos para o database.py
            admin_id = st.session_state.usuario_logado['id']

            if st.button("✅ Aprovar Nota", use_container_width=True, type="primary"):
                ok, msg = db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], "Aprovado", admin_id)
                if ok: st.success("Nota Aprovada!"); time.sleep(1); st.rerun()
                else: st.error(msg)

            if st.button("❌ Reprovar e Estornar", use_container_width=True):
                ok, msg = db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], "Reprovado", admin_id)
                if ok: st.warning("Nota Reprovada!"); time.sleep(1); st.rerun()
                else: st.error(msg)

            st.divider()
            if st.button("🗑️ Excluir Permanentemente", use_container_width=True):
                ok, msg = db.excluir_nota_fiscal(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'])
                if ok: st.success(msg); time.sleep(1); st.rerun()
                else: st.error(msg)

def renderizar_aba_bi(atl_data, lan_data, admin_atual):
    """ABA 2: Inteligência de Negócio e Governança"""
    st.markdown("### 📊 Inteligência Financeira (BI)")

    c1, c2, c3 = st.columns(3)
    meses_lista = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    mes = c1.selectbox("Mês Análise:", meses_lista, index=date.today().month-1, key="bi_mes")
    ano = c2.selectbox("Ano Análise:", [2024, 2025, 2026], index=2, key="bi_ano")
    st_f = c3.selectbox("Status Filtro:", ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"], index=0, key="bi_st")

    m_idx = meses_lista.index(mes) + 1
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty: 
        st.warning("Nenhum dado disponível para este filtro.")
        return

    df_f = _enriquecer_dados(df_f, atl_data)

    # GRÁFICO DE VOLUME
    st.markdown("#### 📈 Volume Financeiro por Atleta")
    df_agrupado = df_f.groupby('atleta_nome')['valor'].sum().reset_index().sort_values(by='valor', ascending=False)
    fig = px.bar(df_agrupado, x='atleta_nome', y='valor', text_auto='.2f', color='valor', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # EXPORTAÇÃO EXECUTIVA
    st.markdown("#### 📤 Exportação e Governança")
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.info("💾 **Planilha Detalhada (.xlsx)**")
        excel_buffer = export_svc.gerar_excel_bi(df_f, mes, ano, st_f)
        st.download_button(label="📥 Baixar Excel Auditado", data=excel_buffer, file_name=f"Auditoria_BI_{mes}_{ano}.xlsx", use_container_width=True)

    with col_exp2:
        st.info("📧 **Relatório para Diretoria**")
        dest = st.text_input("E-mail de destino:", value=db.obter_email_admin(), key="email_dest")
        if st.button("🚀 Disparar Dashboard", use_container_width=True, type="primary"):
            if "@" in dest:
                with st.spinner("Enviando relatório..."):
                    html_body = export_svc.gerar_html_email_bi(df_f, mes, ano, st_f)
                    ok, msg = email_svc.enviar_relatorio(dest, f"📊 Relatório Financeiro ({mes}/{ano})", html_body)
                    if ok: 
                        db.registrar_log_exportacao(admin_atual, dest, f"{mes}/{ano}", len(df_f))
                        st.success(msg)
                    else: st.error(msg)
            else: st.warning("Insira um e-mail válido.")

# [admin_auditoria.py][v13.0 - Blindagem Marvel][2026-02-27]
# Total de Linhas de Código: 142