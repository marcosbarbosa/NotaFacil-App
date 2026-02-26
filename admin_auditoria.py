import streamlit as st
from datetime import date
import time
import database as db
import funcoes_admin as f_adm
import servicos_email as email_svc
import admin_exportacao as export_svc  # NOVO: Importando o Motor de Exportação

def _enriquecer_dados(df_f, atl_data):
    """Função interna para enriquecer a tabela com dados financeiros atuais"""
    atl_map = {a['cpf']: {'saldo': a.get('saldo', 0), 'bolsa': a.get('bolsa', 0)} for a in atl_data}
    def get_fin(cpf, campo): return atl_map.get(cpf, {}).get(campo, 0.0) if cpf else 0.0

    df_f['Saldo Atual'] = df_f['atleta_cpf'].apply(lambda x: get_fin(x, 'saldo'))
    df_f['Valor Bolsa'] = df_f['atleta_cpf'].apply(lambda x: get_fin(x, 'bolsa'))
    df_f['NFs Entregues Acumulado'] = df_f['Valor Bolsa'] - df_f['Saldo Atual']
    return df_f

def renderizar_aba_auditoria(atl_data, lan_data, admin_atual):
    """Controlador de Interface MVC (Limpo e Modular)"""

    # 1. ÁREA DE FILTROS
    c1, c2, c3 = st.columns(3)
    mes = c1.selectbox("Mês:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1)
    ano = c2.selectbox("Ano:", [2024, 2025, 2026], index=2)
    st_f = c3.selectbox("Status:", ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"], index=1)

    m_idx = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes) + 1

    # 2. PREPARAÇÃO DOS DADOS
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty: 
        st.warning("Nada para auditar neste período.")
        return

    df_f = _enriquecer_dados(df_f, atl_data)
    id_sel = None

    # 3. RENDERIZAÇÃO DA TABELA PRINCIPAL
    ev = st.dataframe(df_f[['Status_UI', 'Atleta (Bolsa)', 'Valor Bolsa', 'NFs Entregues Acumulado', 'valor', 'Saldo Atual', 'data_nota', 'foto_url']], 
                      column_config={
                          "foto_url": st.column_config.ImageColumn("NF"), 
                          "Valor Bolsa": st.column_config.NumberColumn("Bolsa Total", format="%.2f"),
                          "NFs Entregues Acumulado": st.column_config.NumberColumn("NFs Entregues", format="%.2f"),
                          "valor": st.column_config.NumberColumn("Valor desta NF", format="%.2f"),
                          "Saldo Atual": st.column_config.NumberColumn("Saldo Restante", format="%.2f")
                      },
                      use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    if ev.selection.rows: id_sel = df_f.iloc[ev.selection.rows[0]]['id']

    # 4. FERRAMENTAS DE EXPORTAÇÃO (Delegadas para o Motor)
    with st.expander("📤 Ferramentas de Exportação Executiva (Excel BI / E-mail)", expanded=False):
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            st.markdown("##### 💾 Baixar Planilha BI")
            # CHAMADA LIMPA: O motor gera o buffer do Excel em uma única linha
            excel_buffer = export_svc.gerar_excel_bi(df_f, mes, ano, st_f)

            st.download_button(
                label="📥 Download Excel (.xlsx)",
                data=excel_buffer,
                file_name=f"Auditoria_BI_{mes}_{ano}.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )

        with col_exp2:
            st.markdown("##### 📧 Enviar Relatório BI")
            dest = st.text_input("E-mail do Destinatário:", placeholder="diretoria@nsg.com")
            if st.button("Enviar E-mail", use_container_width=True):
                if "@" in dest:
                    with st.spinner("Gerando gráficos e enviando..."):
                        # CHAMADA LIMPA: O motor gera o HTML do BI
                        html_body = export_svc.gerar_html_email_bi(df_f, mes, ano, st_f)
                        assunto = f"📊 Dashboard de Auditoria ({mes}/{ano}) - Status: {st_f}"
                        str_filtros = f"Mês: {mes}, Ano: {ano}, Status: {st_f}"

                        ok, msg = email_svc.enviar_relatorio(dest, assunto, html_body)
                        if ok: 
                            db.registrar_log_exportacao(admin_atual, dest, str_filtros, len(df_f))
                            st.success(msg)
                        else: st.error(msg)
                else: st.warning("E-mail inválido.")

    st.divider()

    # 5. AUDITORIA DETALHADA E AÇÕES DO BANCO
    with st.expander("🔍 Auditoria Detalhada da Nota Selecionada", expanded=(id_sel is not None)):
        if id_sel:
            nota = df_f[df_f['id'] == id_sel].iloc[0]
            f_adm.exibir_origem_com_saldo(nota['Atleta (Bolsa)'], nota['Lançado por'], nota['Saldo_Atleta'])

            if nota['orfao']:
                st.warning("🚨 REGISTRO SEM BENEFICIÁRIO: Selecione um atleta para vincular:")
                atl_opcoes = {f"{a['nome']} (Saldo: R$ {a['saldo']:.2f})": a['cpf'] for a in atl_data}
                escolha = st.selectbox("Vincular a:", ["Selecione..."] + list(atl_opcoes.keys()))
                if st.button("🔗 Confirmar Vínculo e Abater Saldo", use_container_width=True):
                    if escolha != "Selecione...":
                        ok, msg = db.vincular_atleta_a_nota(nota['id'], atl_opcoes[escolha], nota['valor'])
                        if ok: st.success(msg); time.sleep(1.2); st.rerun()
                        else: st.error(msg)

            c_img, c_btn = st.columns([1, 1])
            c_img.image(nota['foto_url'], use_container_width=True)
            with c_btn:
                st.write(f"**Valor NF:** R$ {nota['valor']:.2f}")
                if st.button("✅ Aprovar", use_container_width=True):
                    db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'], "✅ Aprovada"); st.rerun()
                if st.button("❌ Reprovar", use_container_width=True):
                    db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'], "❌ Reprovada"); st.rerun()
                st.divider()
                if st.button("🗑️ Apagar Nota do Banco", use_container_width=True, type="primary"):
                    ok, msg = db.excluir_nota_fiscal(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'])
                    if ok: st.success(msg); time.sleep(1); st.rerun()
                    else: st.error(msg)