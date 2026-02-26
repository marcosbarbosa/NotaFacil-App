import streamlit as st

def aplicar_estilos_globais():
    """
    Motor Visual v14.0: O Farol de Resgate Total.
    Libera o botão do menu lateral e o torna gigante.
    """

    css_resgate_total = """
    <style>
    /* 1. LIMPEZA DO TOPO (SEM ESCONDER O BOTÃO DO MENU) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        color: transparent !important;
    }
    #MainMenu, footer { visibility: hidden !important; }
    .block-container { padding-top: 1.5rem !important; }

    /* 2. O BOTÃO DE RESGATE: Força a visibilidade e dá destaque */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        background-color: #ffc107 !important; /* Amarelo Prime */
        border-radius: 0 15px 15px 0 !important;
        width: 120px !important;
        height: 50px !important;
        position: fixed !important;
        top: 20px !important;
        left: 0px !important;
        z-index: 999999 !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3) !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Adiciona a palavra MENU ao botão */
    [data-testid="stSidebarCollapsedControl"]::after {
        content: "MENU";
        color: black !important;
        font-weight: 900 !important;
        font-size: 14px !important;
        margin-left: 5px;
    }

    /* 3. BOTÕES 3D PADRÃO */
    .stButton > button { border-radius: 8px !important; font-weight: 700 !important; }
    </style>
    """

    st.markdown(css_resgate_total, unsafe_allow_html=True)