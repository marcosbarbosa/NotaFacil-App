import streamlit as st

# Mantenha a URL da sua logo
LOGO_URL = "https://raw.githubusercontent.com/marcosbarbosaam/Streamlit-Core/main/logo.png" # Ajuste para a sua URL real da logo

def aplicar_design(tema="preto"):
    """Motor de temas dinâmico para garantir contraste Prime em qualquer ambiente."""

    if tema == "imagem":
        # ATENÇÃO: Coloque a URL da sua imagem de fundo com as linhas douradas aqui dentro dos parênteses da url()
        fundo_css = """
        [data-testid="stAppViewContainer"] {
            background-image: url("COLOQUE_AQUI_A_URL_DA_SUA_IMAGEM_DE_FUNDO"); 
            background-size: cover; background-position: center;
        }
        [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 { 
            color: #FFFFFF !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.9) !important; 
        }
        """
    elif tema == "preto":
        fundo_css = """
        [data-testid="stAppViewContainer"] { background-color: #0E1117; }
        [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 { 
            color: #FFFFFF !important; text-shadow: none !important; 
        }
        """
    elif tema == "cinza":
        fundo_css = """
        [data-testid="stAppViewContainer"] { background-color: #262730; }
        [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 { 
            color: #FAFAFA !important; text-shadow: none !important; 
        }
        """
    elif tema == "branco":
        fundo_css = """
        [data-testid="stAppViewContainer"] { background-color: #F8F9FA; }
        [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 { 
            color: #1E1E1E !important; text-shadow: none !important; 
        }
        """

    css_base = f"""
    <style>
    {fundo_css}

    /* Proteção Blindada: Sidebar (Menu Lateral) sempre escura e legível */
    [data-testid="stSidebar"] {{ background-color: #1A1A1D !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1 {{ 
        color: #FFFFFF !important; text-shadow: none !important; 
    }}

    /* Proteção Blindada: Campos de digitação sempre brancos com letra preta */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {{ 
        color: #000000 !important; background-color: #FFFFFF !important; text-shadow: none !important; 
    }}
    </style>
    """
    st.markdown(css_base, unsafe_allow_html=True)

# [styles.py][Motor Dinâmico de Temas][2026-02-25 06:10][v2.0][44 linhas]