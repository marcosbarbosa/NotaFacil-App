import streamlit as st
import pandas as pd
from datetime import date
import time
import database as db
import funcoes_admin as f_adm
import servicos_email as email_svc

def renderizar_aba_auditoria(atl_data, lan_data, admin_atual):
    """Módulo MVC isolado para a Auditoria Financeira"""
    c1, c2, c3 = st.columns(3)
    mes = c1.selectbox("Mês:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1)
    ano = c2.selectbox("Ano:", [2024, 2025, 2026], index=2)
    st_f = c3.selectbox("Status:", ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"], index=1)

    m_idx = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes) + 1
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty: st.warning("Nada para auditar.")
    else:
        id_sel = None
        ev = st.dataframe(df_f[['Status_UI', 'Atleta (Bolsa)', 'Lançado por', 'valor', 'data_nota', 'foto_url']], 
                          column_config={"foto_url": st.column_config.ImageColumn("NF"), "valor": st.column_config.NumberColumn("R$", format="%.2f")},
                          use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        if ev.selection.rows: id_sel = df_f.iloc[ev.selection.rows[0]]['id']

        with st.expander("📤 Exportar / Enviar Relatório por E-mail", expanded=False):
            st.info(f"O relatório conterá as **{len(df_f)} notas** listadas na tabela acima, totalizando **R$ {df_f['valor'].sum():,.2f}**.")
            dest = st.text_input("E-mail do Destinatário (ex: diretoria@nsg.com):")
            if st.button("📧 Gerar e Enviar Relatório", type="primary"):
                if "@" in dest:
                    with st.spinner("Compilando dados e disparando e-mail..."):
                        html_body = f_adm.montar_html_relatorio(df_f, mes, ano, st_f)
                        assunto = f"Relatório de Auditoria ({mes}/{ano}) - Status: {st_f}"
                        str_filtros = f"Mês: {mes}, Ano: {ano}, Status: {st_f}"

                        ok, msg = email_svc.enviar_relatorio(dest, assunto, html_body)
                        if ok: 
                            db.registrar_log_exportacao(admin_atual, dest, str_filtros, len(df_f))
                            st.success(msg)
                        else: st.error(msg)
                else: st.warning("Por favor, insira um e-mail válido.")

        st.divider()
        with st.expander("🔍 Auditoria Detalhada", expanded=(id_sel is not None)):
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

# [admin_auditoria.py][Isolamento do Core Financeiro][2026-02-25 16:15][v1.0][67 linhas]