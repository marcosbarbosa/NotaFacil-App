import streamlit as st
import base64
import os

def get_base64_of_bin_file(bin_file):
    """Lê a imagem local de fundo e converte para o CSS em Base64"""
    try:
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        return ""
    except Exception:
        return ""

def aplicar_design(tema="branco"):
    """Motor Dinâmico de Temas com Acessibilidade Visual Garantida"""

    # 1. DEFINIÇÃO DE FUNDO E FONTES COM BASE NO TEMA
    if tema == "imagem":
        img_base64 = get_base64_of_bin_file("background-nf-prime-mob.png")
        if img_base64:
            fundo_css = f"""
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/png;base64,{img_base64}");
                background-size: cover; 
                background-position: center;
                background-attachment: fixed;
            }}
            [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 {{ 
                color: #FFFFFF !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.9) !important; 
            }}
            """
        else:
            fundo_css = """[data-testid="stAppViewContainer"] { background-color: #0E1117; }"""

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
        [data-testid="stAppViewContainer"] { background-color: #F4F6F8; }

        [data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] span, [data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3 { 
            color: #1A1A1A !important; text-shadow: none !important; 
        }
        """

    # 2. INJEÇÃO DO CSS BASE (Agressivo para Botões e Inputs)
    css_base = f"""
    <style>
    {fundo_css}

    /* Proteção da Barra Lateral (Sempre Escura) */
    [data-testid="stSidebar"] {{ background-color: #1A1A1D !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1 {{ 
        color: #FFFFFF !important; text-shadow: none !important; 
    }}

    /* Proteção dos Campos de Formulário (Brancos com Letra Preta) */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {{ 
        color: #000000 !important; 
        background-color: #FFFFFF !important; 
        border: 1px solid #CCCCCC !important;
        text-shadow: none !important; 
    }}

    /* CSS BRUTAL DE BOTÕES: Força a cor de fundo */
    .stButton > button, 
    div[data-testid="stFormSubmitButton"] button {{
        background-color: #0056B3 !important;
        border: 1px solid #004494 !important;
    }}

    /* CORREÇÃO DE ACESSIBILIDADE: Força o texto BRANCO dentro de qualquer elemento do botão */
    .stButton > button, 
    .stButton > button *,
    div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stFormSubmitButton"] button * {{
        color: #FFFFFF !important;
        font-weight: bold !important;
        text-shadow: none !important;
    }}

    /* Efeito Hover (Interação do Mouse) */
    .stButton > button:hover, 
    div[data-testid="stFormSubmitButton"] button:hover {{
        background-color: #004494 !important;
        border: 1px solid #002a5c !important;
    }}
    </style>
    """
    st.markdown(css_base, unsafe_allow_html=True)

# [styles.py][Correção de Acessibilidade e Contraste de Botões][2026-02-25 10:52