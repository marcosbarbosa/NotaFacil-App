# ==============================================================================
# SISTEMA: NotaFácil Prime | ARQUIVO: admin.py
# DATA: 23/02/2026 | TÍTULO: Sala de Guerra v2.0
# FUNÇÃO: BI Real, Miniaturas de NF e Painel de Gestão Financeira
# VERSÃO: 2.0 | LINHAS: 110
# ==============================================================================
import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import database as db

def exibir_sala_de_guerra():
    if st.sidebar.text_input("Senha Admin", type="password") == "admin":
        atl_data, _, lan_data = db.carregar_dados_globais()

        if not lan_data:
            st.info("Nenhum lançamento encontrado ainda.")
            return

        df_lan = pd.DataFrame(lan_data)
        df_lan['dt'] = pd.to_datetime(df_lan['created_at'])

        st.subheader("🔍 Filtros de Período")
        c1, c2 = st.columns(2)
        mes_ref = c1.selectbox("Mês:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1)
        ano_ref = c2.selectbox("Ano:", [2024, 2025, 2026], index=2)
        m_num = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes_ref) + 1
        df_f = df_lan[(df_lan['dt'].dt.month == m_num) & (df_lan['dt'].dt.year == ano_ref)]

        if df_f.empty:
            st.warning("Nenhuma nota neste período.")
            return

        # --- BI REAL: PARA ONDE VAI O DINHEIRO ---
        st.divider()
        g1, g2 = st.columns(2)
        with g1:
            # Gráfico de Categoria (Tags)
            df_f['Categoria'] = df_f.apply(lambda r: db.calcular_tag_3x3(r['atletas']['sexo'], r['atletas']['data_nascimento']) if pd.notnull(r.get('atletas')) else "Visitante", axis=1)
            fig_cat = px.pie(df_f, values='valor', names='Categoria', title=f"Distribuição por Grupo ({mes_ref})", hole=.4, template="plotly_dark")
            st.plotly_chart(fig_cat, use_container_width=True)
        with g2:
            # Gráfico Top Consumidores
            df_f['Atleta'] = df_f.apply(lambda r: r['atletas']['nome'] if pd.notnull(r.get('atletas')) else "S/ Vínculo", axis=1)
            consumo = df_f.groupby('Atleta')['valor'].sum().reset_index().sort_values('valor', ascending=False).head(5)
            fig_bar = px.bar(consumo, x='valor', y='Atleta', orientation='h', title="Top 5 Reembolsos", template="plotly_dark", color_discrete_sequence=['#FFD700'])
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- AUDITORIA COM MINIATURA E SALDOS ---
        st.divider()
        st.subheader(f"📋 Auditoria Visual ({len(df_f)} registros)")

        # Preparando a tabela enriquecida
        df_view = df_f.copy()
        df_view['ID'] = df_view['id'].str[:6] # ID Curto para facilitar na tela
        df_view['Quem'] = df_view.apply(lambda r: r['atletas']['nome'] if pd.notnull(r.get('atletas')) else f"Vis: {r['visitantes']['nome']}", axis=1)
        # Pegando Bolsa (Limite) e Saldo Atual direto do objeto atletas que veio do banco
        df_view['Bolsa'] = df_view.apply(lambda r: r['atletas']['limite_mensal'] if pd.notnull(r.get('atletas')) else 0, axis=1)

        # O Streamlit renderiza a imagem se passarmos na configuração da coluna
        st.dataframe(
            df_view[['ID', 'Quem', 'Bolsa', 'valor', 'data_nota', 'foto_url']],
            column_config={
                "ID": "Cód.",
                "Quem": "Lançador/Atleta",
                "Bolsa": st.column_config.NumberColumn("Bolsa/Meta", format="R$ %.2f"),
                "valor": st.column_config.NumberColumn("Valor NF", format="R$ %.2f"),
                "data_nota": "Data NF",
                "foto_url": st.column_config.ImageColumn("NF (Miniatura)", help="Foto do Comprovante")
            },
            use_container_width=True, hide_index=True
        )

        # --- PAINEL DE GESTÃO (EDITAR/EXCLUIR) ---
        st.divider()
        with st.expander("⚙️ Gerenciar Notas (Editar ou Excluir)"):
            lista_notas = df_view.apply(lambda r: f"{r['ID']} | {r['Quem']} | R$ {r['valor']} | {r['data_nota']}", axis=1).tolist()
            nota_selecionada = st.selectbox("Selecione a Nota Fiscal:", ["Escolha uma nota..."] + lista_notas)

            if nota_selecionada != "Escolha uma nota...":
                id_curto = nota_selecionada.split(" | ")[0]
                nota_real = df_f[df_f['id'].str.startswith(id_curto)].iloc[0]

                c_edit, c_del = st.columns(2)
                with c_edit:
                    st.write("**Editar Valor**")
                    novo_valor = st.number_input("Corrigir Valor (R$):", value=float(nota_real['valor']), min_value=0.01)
                    if st.button("✏️ Salvar Correção"):
                        db.editar_valor_nota(nota_real['id'], nota_real['atleta_cpf'], nota_real['valor'], novo_valor)
                        st.success("Valor corrigido e saldo reprocessado!")
                        st.rerun()
                with c_del:
                    st.write("**Estornar (Excluir)**")
                    st.error("⚠️ Esta ação apagará a nota e devolverá o saldo ao atleta.")
                    if st.button("🗑️ Excluir Lançamento"):
                        db.excluir_nota_fiscal(nota_real['id'], nota_real['atleta_cpf'], nota_real['valor'])
                        st.success("Nota excluída e saldo devolvido com sucesso!")
                        st.rerun()
    else: 
        st.info("Acesso Administrativo Restrito.")