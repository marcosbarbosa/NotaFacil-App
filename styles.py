import streamlit as st
import db_config as db 

def aplicar_estilos_globais(tema="🌑 Escuro"):
    """
    Motor Visual v8.5: Botões Inteligentes (UX) + Força Bruta de Contraste (UI).
    Separa ações positivas de negativas e blinda os textos para nunca sumirem.
    """

    # 1. CSS BASE: Animações 3D suaves, formato de botões e bloqueio de vazamentos
    css_base = """
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }

    /* BLOQUEIO DE VAZAMENTO */
    .stMarkdown div pre { display: none !important; }
    .stMarkdown code { display: none !important; }

    /* 🎛️ SUPER BOTÕES PRIME (Efeito 3D e Sombra) */
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
    .stButton > button:active {
        transform: translateY(0px);
    }
    </style>
    """

    css_tema = ""

    if tema == "🌑 Escuro":
        # REPARO MARVEL v8: Adicionado !important em fundos e textos para blindagem total
        css_tema = """
        <style>
        .stApp { background-color: #0e1117 !important; }
        h1, h2, h3, h4, label, p, span, div, .stMarkdown { color: #fafafa !important; }
        section[data-testid="stSidebar"] { background-color: #1a1c24 !important; }

        /* Botão Padrão/Reprovar (Escuro/Discreto) */
        button[kind="secondary"] { background-color: #2b2b36 !important; color: #ffffff !important; border: 1px solid #444 !important; }
        /* Botão Destaque/Aprovar (Amarelo Prime) */
        button[kind="primary"] { background-color: #ffc107 !important; color: #000000 !important; border: 1px solid #d39e00 !important; }
        </style>
        """

    elif tema == "☀️ Claro":
        css_tema = """
        <style>
        .stApp { background-color: #ffffff !important; }
        h1, h2, h3, h4, label, p, span, div, .stMarkdown { color: #000000 !important; font-weight: 600 !important; }
        section[data-testid="stSidebar"] { background-color: #f8f9fa !important; }

        /* Botão Padrão/Reprovar (Cinza Claro) */
        button[kind="secondary"] { background-color: #f1f3f5 !important; color: #333 !important; border: 1px solid #ccc !important; }
        /* Botão Destaque/Aprovar (Azul Escuro) */
        button[kind="primary"] { background-color: #0056b3 !important; color: #ffffff !important; border: 1px solid #004085 !important; }
        </style>
        """

    elif tema == "🏢 Cinza (Prime)":
        css_tema = """
        <style>
        .stApp { background-color: #262730 !important; } 
        h1, h2, h3, h4, label, p, span, div, .stMarkdown { color: #ffffff !important; }
        section[data-testid="stSidebar"] { background-color: #111111 !important; }

        /* Botão Padrão/Reprovar */
        button[kind="secondary"] { background-color: #3e404f !important; color: white !important; border: 1px solid #555 !important; }
        /* Botão Destaque/Aprovar */
        button[kind="primary"] { background-color: #ffc107 !important; color: #000 !important; border: 1px solid #d39e00 !important; }
        </style>
        """

    elif tema == "🏀 Fundo Imagem":
        b64_img = db.obter_imagem_fundo_db()
        if b64_img:
            css_tema = f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), 
                url("data:image/png;base64,{b64_img}");
                background-size: cover; background-attachment: fixed;
            }}
            h1, h2, h3, h4, label, p, span, div, .stMarkdown {{ color: #000000 !important; font-weight: 800 !important; }}

            /* Botão Padrão/Reprovar (Branco com borda forte) */
            button[kind="secondary"] {{ background-color: #ffffff !important; color: #333 !important; border: 2px solid #333 !important; }}
            /* Botão Destaque/Aprovar (Amarelo Prime Vivo) */
            button[kind="primary"] {{ background-color: #ffc107 !important; color: #000 !important; border: 2px solid #d39e00 !important; }}
            </style>
            """
        else:
            css_tema = "<style>.stApp { background-color: #f0f2f6; }</style>"

    # O Mestre da Injeção
    st.markdown(css_base + css_tema, unsafe_allow_html=True)

# [styles.py][Fusão Botões 3D + Força Bruta de Contraste v8.5][2026-02-26]