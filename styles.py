import streamlit as st
import db_config as db 

def aplicar_estilos_globais(tema="🌑 Escuro"):
    """
    Motor Visual v5.6: Blindagem Final Marvel Prime.
    Resolve vazamento de CSS e garante contraste absoluto em BI.
    """

    # 1. CSS BASE: Blindagem contra elementos nativos e vazamentos
    css_base = """
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; }

    /* BLOQUEIO DE VAZAMENTO: Garante que o CSS não seja interpretado como texto Markdown */
    .stMarkdown div pre { background-color: transparent !important; border: none !important; display: none !important; }
    .stMarkdown code { display: none !important; }

    /* Suavização de interface */
    .stButton > button { border-radius: 8px !important; transition: 0.3s; }
    .stButton > button:hover { transform: scale(1.02); }
    </style>
    """

    css_tema = ""

    if tema == "🌑 Escuro":
        css_tema = """
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        section[data-testid="stSidebar"] { background-color: #1a1c24; }
        .stButton > button { background-color: #0056b3 !important; color: white !important; font-weight: bold; border: none; }
        </style>
        """

    elif tema == "☀️ Claro":
        css_tema = """
        <style>
        .stApp { background-color: #ffffff !important; }
        /* Força o preto em TUDO no modo claro */
        h1, h2, h3, h4, label, p, span, .stMarkdown { color: #000000 !important; }
        </style>
        """
    
    elif tema == "🏢 Cinza (Prime)":
        css_tema = """
        <style>
        .stApp { background-color: #262730; color: #ffffff; }
        section[data-testid="stSidebar"] { background-color: #111111; }
        h1, h2, h3, h4, label, div, span, .stMarkdown { color: #ffffff !important; }
        .stButton > button { background-color: #444444 !important; color: white !important; border: 1px solid #555; }
        </style>
        """

    elif tema == "🏀 Fundo Imagem":
        # Busca a imagem em Base64 do banco para evitar links quebrados
        b64_img = db.obter_imagem_fundo_db()
        if b64_img:
            css_tema = f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), 
                url("data:image/png;base64,{b64_img}");
                background-size: cover; 
                background-position: center; 
                background-attachment: fixed; 
                color: #000;
            }}
            /* Contraste absoluto para Dashboard de BI */
            h1, h2, h3, h4, label, p, span, .stMarkdown {{ color: #000 !important; font-weight: 700 !important; }}
            .stButton > button {{ 
                background-color: #ffc107 !important; 
                color: #000 !important; 
                font-weight: bold; 
                border: 1px solid #d39e00; 
            }}
            </style>"""
        else:
            css_tema = "<style>.stApp { background-color: #f0f2f6; }</style>"

    # 3. INJEÇÃO MESTRE: O parâmetro unsafe_allow_html=True é o que "mata" o texto na tela
    st.markdown(css_base + css_tema, unsafe_allow_html=True)

# [styles.py][Edição Marvel Prime v5.6 Final][2026-02-26 17:15]