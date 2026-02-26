import streamlit as st
import db_config as db 

def aplicar_estilos_globais(tema="🌑 Escuro"):
    """
    Motor Visual v10.5: Root Control Refinado.
    Garante a mudança de fundo na raiz do sistema, mas preserva a elegância 
    nativa das tabelas, sombras e componentes de alerta do Streamlit.
    """

    # 1. CSS BASE: Oculta headers nativos e configura os botões
    css_base = """
    <style>
    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden !important; background: transparent !important; }
    .block-container { padding-top: 1.5rem !important; }

    .stMarkdown div pre { display: none !important; }
    .stMarkdown code { display: none !important; }

    /* 🎛️ SUPER BOTÕES PRIME (Efeito 3D Preservado) */
    .stButton > button { 
        border-radius: 8px !important; 
        transition: all 0.3s ease !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important; 
        filter: brightness(1.1);
    }
    .stButton > button:active { transform: translateY(0px); }
    </style>
    """

    css_tema = ""

    if tema == "🌑 Escuro":
        css_tema = """
        <style>
        /* Injeta a cor no HTML e BODY para anular o navegador */
        html, body, .stApp, [data-testid="stAppViewContainer"] { background-color: #0e1117 !important; color: #fafafa !important; }
        h1, h2, h3, .stMarkdown { color: #fafafa !important; }
        section[data-testid="stSidebar"], [data-testid="stSidebarContent"] { background-color: #1a1c24 !important; }

        button[kind="secondary"] { background-color: #2b2b36 !important; color: #ffffff !important; border: 1px solid #444 !important; }
        button[kind="primary"] { background-color: #ffc107 !important; color: #000000 !important; border: 1px solid #d39e00 !important; }
        </style>
        """

    elif tema == "☀️ Claro":
        css_tema = """
        <style>
        html, body, .stApp, [data-testid="stAppViewContainer"] { background-color: #ffffff !important; color: #000000 !important; }
        h1, h2, h3, .stMarkdown { color: #000000 !important; font-weight: 600 !important; }
        section[data-testid="stSidebar"], [data-testid="stSidebarContent"] { background-color: #f8f9fa !important; }

        button[kind="secondary"] { background-color: #f1f3f5 !important; color: #333 !important; border: 1px solid #ccc !important; }
        button[kind="primary"] { background-color: #0056b3 !important; color: #ffffff !important; border: 1px solid #004085 !important; }
        </style>
        """

    elif tema == "🏢 Cinza (Prime)":
        css_tema = """
        <style>
        html, body, .stApp, [data-testid="stAppViewContainer"] { background-color: #262730 !important; color: #ffffff !important; } 
        h1, h2, h3, .stMarkdown { color: #ffffff !important; }
        section[data-testid="stSidebar"], [data-testid="stSidebarContent"] { background-color: #111111 !important; }

        button[kind="secondary"] { background-color: #3e404f !important; color: white !important; border: 1px solid #555 !important; }
        button[kind="primary"] { background-color: #ffc107 !important; color: #000 !important; border: 1px solid #d39e00 !important; }
        </style>
        """

    elif tema == "🏀 Fundo Imagem":
        b64_img = db.obter_imagem_fundo_db()
        if b64_img:
            css_tema = f"""
            <style>
            html, body, .stApp, [data-testid="stAppViewContainer"] {{
                background-color: transparent !important;
                background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), 
                url("data:image/png;base64,{b64_img}") !important;
                background-size: cover !important; 
                background-attachment: fixed !important;
            }}
            .stApp {{ color: #000000 !important; }}
            h1, h2, h3, .stMarkdown {{ color: #000000 !important; font-weight: 800 !important; }}

            button[kind="secondary"] {{ background-color: #ffffff !important; color: #333 !important; border: 2px solid #333 !important; }}
            button[kind="primary"] {{ background-color: #ffc107 !important; color: #000 !important; border: 2px solid #d39e00 !important; }}
            </style>
            """
        else:
            css_tema = "<style>html, body, .stApp, [data-testid=\"stAppViewContainer\"] { background-color: #f0f2f6 !important; }</style>"

    # O Mestre da Injeção
    st.markdown(css_base + css_tema, unsafe_allow_html=True)

# [styles.py][Root Control + Elegância Nativa v10.5][2026-02-26]