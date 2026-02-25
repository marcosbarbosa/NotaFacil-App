import streamlit as st

# Mantenha a URL da sua logo
LOGO_URL = "https://sua-logo-aqui.com/logo.png" # Substitua pela sua URL real

def aplicar_design():
    # Aqui pode estar o seu CSS de imagem de fundo...

    # --- NOVO: PATCH DE CONTRASTE EXECUTIVO ---
    css_contraste = """
    <style>
    /* 1. Força texto branco e sombra na área principal para saltar do fundo escuro */
    [data-testid="stAppViewContainer"] h1, 
    [data-testid="stAppViewContainer"] h2, 
    [data-testid="stAppViewContainer"] h3, 
    [data-testid="stAppViewContainer"] p, 
    [data-testid="stAppViewContainer"] label, 
    [data-testid="stAppViewContainer"] span {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
    }

    /* 2. Mantém o texto PRETO dentro das caixas de digitação para não sumir o que o usuário digita */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        color: #000000 !important;
        text-shadow: none !important;
        background-color: #FFFFFF !important;
    }

    /* 3. Protege a Barra Lateral (Sidebar) mantendo a cor escura, pois o fundo dela é claro */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1 {
        color: #1E1E1E !important;
        text-shadow: none !important;
    }

    /* 4. Blinda as Métricas (Cards de Saldo) para ficarem brilhantes e visíveis */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
    }
    </style>
    """
    st.markdown(css_contraste, unsafe_allow_html=True)

# [styles.py][Patch de Alta Legibilidade e Text-Shadow][2026-02-25 05:40][v1.5]