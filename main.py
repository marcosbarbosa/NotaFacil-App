import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client
import os
import time

# --- 1. CONEXÃO COM O SUPABASE ---
try:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("❌ Chaves não encontradas nos Secrets!")
        st.stop()
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"❌ Erro de Conexão: {e}")
    st.stop()

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="NotaFácil Prime", page_icon="🏆", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    div[data-testid="stMetricValue"] { color: #FFD700; } /* Dourado */
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def carregar_atletas():
    # Pega todos os atletas
    response = supabase.table('atletas').select("*").execute()
    return pd.DataFrame(response.data)

def enviar_nota_com_foto(cpf, valor, data_nota, arquivo_foto):
    foto_url = None

    # 1. Upload da Foto
    if arquivo_foto:
        try:
            # Nome único para não substituir arquivos iguais
            timestamp = int(time.time())
            nome_arquivo = f"{cpf}_{timestamp}_{arquivo_foto.name}"

            arquivo_bytes = arquivo_foto.getvalue()

            supabase.storage.from_("comprovantes").upload(
                path=nome_arquivo,
                file=arquivo_bytes,
                file_options={"content-type": arquivo_foto.type}
            )

            # Monta o Link Público
            foto_url = f"{url}/storage/v1/object/public/comprovantes/{nome_arquivo}"

        except Exception as e:
            st.error(f"Erro no upload da foto: {e}")
            return # Para se der erro

    # 2. Salva no Banco
    dados = {
        "atleta_cpf": cpf,
        "valor": valor,
        "data_nota": str(data_nota),
        "status": "Pendente",
        "foto_url": foto_url
    }
    supabase.table('lancamentos').insert(dados).execute()

    # 3. Abate a dívida
    atleta = supabase.table('atletas').select('saldo').eq('cpf', cpf).execute()
    if atleta.data:
        saldo_atual = float(atleta.data[0]['saldo'])
        novo_saldo = saldo_atual - valor
        supabase.table('atletas').update({'saldo': novo_saldo}).eq('cpf', cpf).execute()

# --- INTERFACE ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2845/2845667.png", width=80)
st.sidebar.title("NotaFácil Prime")
menu = st.sidebar.radio("Menu", ["Área do Atleta", "Sala de Guerra (Admin)"])

# === TELA DO ATLETA ===
if menu == "Área do Atleta":
    st.title("🏃 Área do Atleta")
    st.info("💡 Dica: Oculte o menu lateral para ter mais privacidade.")

    try:
        df_atletas = carregar_atletas()
        if not df_atletas.empty:
            nomes = df_atletas['nome'].tolist()
            nome = st.selectbox("Identifique-se:", nomes)
            # Pega o CPF do nome escolhido
            cpf = df_atletas[df_atletas['nome'] == nome]['cpf'].values[0]

            st.divider()

            with st.form("form_nota"):
                st.write(f"Olá, **{nome}**! Qual o valor do reembolso?")
                col1, col2 = st.columns(2)
                with col1:
                    valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01)
                with col2:
                    data = st.date_input("Data do Comprovante", date.today())

                arquivo = st.file_uploader("📸 Foto do Comprovante (Obrigatório)", type=['jpg', 'png', 'pdf', 'jpeg'])

                botao = st.form_submit_button("🚀 ENVIAR COMPROVANTE")

                if botao:
                    if not arquivo:
                        st.warning("⚠️ É obrigatório anexar a foto!")
                    else:
                        with st.spinner("Enviando e atualizando saldo..."):
                            enviar_nota_com_foto(cpf, valor, data, arquivo)
                            st.success("✅ Recebido! Seu saldo foi atualizado.")
                            time.sleep(2)
                            st.rerun()
    except Exception as e:
        st.error(f"Erro ao carregar sistema: {e}")

# === TELA DO ADMIN ===
elif menu == "Sala de Guerra (Admin)":
    st.title("🛡️ Sala de Guerra")
    senha = st.sidebar.text_input("Senha Admin", type="password")

    if senha == "admin":
        if st.button("🔄 Atualizar Dados"): st.rerun()

        df_atletas = carregar_atletas()

        if not df_atletas.empty:
            # Lógica dos 80%
            df_atletas['Limite'] = df_atletas['bolsa'] * 0.80
            df_atletas['Status'] = df_atletas.apply(lambda x: '🚨 CRÍTICO' if x['saldo'] >= x['Limite'] else '✅ Em Dia', axis=1)

            # KPIs
            total = df_atletas['saldo'].sum()
            criticos = df_atletas[df_atletas['Status'] == '🚨 CRÍTICO'].shape[0]

            c1, c2, c3 = st.columns(3)
            c1.metric("Total a Receber", f"R$ {total:,.2f}")
            c2.metric("Atletas Críticos", f"{criticos}")
            c3.metric("Total Cadastrados", f"{len(df_atletas)}")

            st.divider()
            st.subheader("📋 Situação Financeira")

            # Tabela de Devedores
            st.dataframe(
                df_atletas[['nome', 'saldo', 'Status']].sort_values('saldo', ascending=False),
                column_config={
                    "nome": "Atleta",
                    "saldo": st.column_config.NumberColumn("Saldo Devedor", format="R$ %.2f")
                },
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.subheader("📥 Últimos Lançamentos (Auditoria)")

            # Busca lançamentos
            lancamentos = supabase.table('lancamentos').select("*").order('created_at', desc=True).limit(10).execute()

            if lancamentos.data:
                df_lanc = pd.DataFrame(lancamentos.data)

                # --- A MÁGICA: TROCAR CPF POR NOME ---
                # 1. Pega só CPF e Nome da tabela de atletas
                df_nomes = df_atletas[['cpf', 'nome']]

                # 2. Cruza as tabelas (Join)
                df_final = pd.merge(df_lanc, df_nomes, left_on='atleta_cpf', right_on='cpf', how='left')

                # 3. Exibe bonito
                st.dataframe(
                    df_final[['nome', 'valor', 'data_nota', 'foto_url']],
                    column_config={
                        "nome": "Atleta",
                        "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                        "data_nota": st.column_config.DateColumn("Data"),
                        "foto_url": st.column_config.LinkColumn("Comprovante")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhum lançamento encontrado.")
    else:
        st.warning("🔒 Área restrita.")