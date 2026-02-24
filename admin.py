# ==============================================================================
# SISTEMA: NotaFácil Prime | ARQUIVO: admin.py
# DATA: 19/02/2026 | HORA: 14:10 | TÍTULO: Sala de Guerra v1.1
# FUNÇÃO: Dashboard BI e Disparo Real de Relatórios
# VERSÃO: 1.1 | LINHAS: 75
# ==============================================================================
import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import database as db

def exibir_sala_de_guerra():
    if st.sidebar.text_input("Senha Admin", type="password") == "admin":
        atl_data, _, lan_data = db.carregar_dados_globais()
        df_lan = pd.DataFrame(lan_data)
        df_lan['dt'] = pd.to_datetime(df_lan['created_at'])

        st.subheader("🔍 Filtros de Período")
        c1, c2 = st.columns(2)
        mes_ref = c1.selectbox("Mês:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1)
        ano_ref = c2.selectbox("Ano:", [2024, 2025, 2026], index=2)
        m_num = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes_ref) + 1
        df_f = df_lan[(df_lan['dt'].dt.month == m_num) & (df_lan['dt'].dt.year == ano_ref)]

        st.plotly_chart(px.pie(df_f, values='valor', names='status', title=f"Consolidado {mes_ref}", hole=.4, template="plotly_dark"), use_container_width=True)

        st.subheader(f"📋 Auditoria ({len(df_f)} registros)")
        pag = st.number_input("Página:", 1, (len(df_f)//5)+1, 1)
        df_f['Quem'] = df_f.apply(lambda r: r['atletas']['nome'] if r['atletas'] else f"Vis: {r['visitantes']['nome']}", axis=1)
        st.dataframe(df_f.iloc[(pag-1)*5 : pag*5][['Quem', 'valor', 'data_nota', 'foto_url']], use_container_width=True, hide_index=True)

        st.divider()
        st.write("📧 **Enviar Relatório Consolidado**")
        email_dest = st.text_input("E-mail do Destinatário:", value="marcosbarbosa.am@gmail.com")
        if st.button("🚀 Gerar e Enviar E-mail"):
            # Montagem do Relatório em HTML
            total = df_f['valor'].sum()
            html = f"<h2>Relatório NotaFácil Prime - {mes_ref}/{ano_ref}</h2>"
            html += f"<p><b>Total Processado:</b> R$ {total:,.2f}</p>"
            html += f"<p><b>Quantidade de Notas:</b> {len(df_f)}</p>"
            html += "<hr><p><i>Este é um log automático do sistema.</i></p>"

            if db.enviar_email_relatorio(email_dest, f"Relatório Financeiro {mes_ref}/{ano_ref}", html):
                db.log_exportacao("dcatletas@gmail.com", email_dest, f"{mes_ref}/{ano_ref}")
                st.success(f"Relatório enviado com sucesso para {email_dest}! ✅")
            else:
                st.error("Falha no envio. Verifique as credenciais SMTP.")
    else: st.info("Acesso Administrativo Restrito.")
# Quantidade total de linhas: 75