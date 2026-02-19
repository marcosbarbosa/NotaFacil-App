import streamlit as st
import pandas as pd
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="NotaFácil Prime", page_icon="💰", layout="wide")

# --- DADOS DE MENTIRINHA (Para testar agora) ---
if 'db_atletas' not in st.session_state:
    st.session_state['db_atletas'] = pd.DataFrame([
        {'cpf': '111', 'nome': 'Marcos Barbosa', 'bolsa': 1000.0, 'saldo': 1013.13},
        {'cpf': '222', 'nome': 'Atleta Exemplo', 'bolsa': 800.0, 'saldo': 100.00},
        {'cpf': '333', 'nome': 'João Crítico', 'bolsa': 1000.0, 'saldo': 950.00},
    ])

if 'db_notas' not in st.session_state:
    st.session_state['db_notas'] = []

# --- ESTILO (Visual Dourado e Preto) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    div[data-testid="stMetricValue"] { color: #FFD700; }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.title("🏆 NotaFácil Prime")
menu = st.sidebar.radio("Ir para:", ["Área do Atleta", "Sala de Guerra (Admin)"])

# --- TELA 1: ATLETA ---
if menu == "Área do Atleta":
    st.title("🏃 Área do Atleta")
    st.info("Oculte o menu lateral para mais privacidade.")

    # Login Falso
    nomes = st.session_state['db_atletas']['nome'].tolist()
    quem_sou = st.selectbox("Selecione seu nome:", nomes)

    st.divider()

    with st.form("envio_nota"):
        st.write(f"Olá, **{quem_sou}**! Envie seu comprovante.")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        data = st.date_input("Data do Comprovante", date.today())
        arquivo = st.file_uploader("Foto da Nota", type=['png', 'jpg', 'pdf'])

        botao = st.form_submit_button("🚀 ENVIAR AGORA")

        if botao:
            st.success(f"Sucesso! Nota de R$ {valor} enviada para auditoria.")
            # Salva na memória temporária
            st.session_state['db_notas'].append({
                "Nome": quem_sou, "Valor": valor, "Data": data
            })

# --- TELA 2: ADMIN ---
elif menu == "Sala de Guerra (Admin)":
    st.title("🛡️ Sala de Guerra")
    senha = st.sidebar.text_input("Senha Admin", type="password")

    if senha == "admin": # Senha simples
        # Pega os dados
        df = st.session_state['db_atletas'].copy()

        # A MÁGICA DOS 80% (Cálculo)
        df['Limite_Alerta'] = df['bolsa'] * 0.80
        df['Status'] = df.apply(lambda x: '🚨 CRÍTICO' if x['saldo'] >= x['Limite_Alerta'] else '✅ Em Dia', axis=1)

        # Painel de Números
        col1, col2 = st.columns(2)
        total_devendo = df['saldo'].sum()
        criticos = df[df['Status'] == '🚨 CRÍTICO'].shape[0]

        col1.metric("💰 Total a Receber", f"R$ {total_devendo:,.2f}")
        col2.metric("🔥 Atletas Críticos", f"{criticos} atletas")

        st.divider()
        st.subheader("📋 Quem está devendo?")

        # Tabela Colorida
        st.dataframe(
            df[['nome', 'saldo', 'Status']].sort_values('saldo', ascending=False),
            use_container_width=True
        )

    else:
        st.warning("🔒 Digite a senha 'admin' na barra lateral.")