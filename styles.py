import streamlit as st

def aplicar_estilos_globais():
    """Injeta CSS Dinâmico com foco em UI Executiva e Contraste Inteligente"""

    if 'tema_atual' not in st.session_state:
        st.session_state.tema_atual = 'light'

    tema = st.session_state.tema_atual

    if tema == 'dark':
        css = """
        <style>
            .stApp { background-color: #0e1117; color: #ffffff; }
            [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

            /* Títulos e Textos Padrão */
            h1, h2, h3, h4, p, span, label { color: #ffffff !important; }

            /* Restaura o Menu de Navegação (Radio Buttons) */
            div[role="radiogroup"] * { color: #ffffff !important; }

            /* Subtítulos discretos (Captions) */
            [data-testid="stCaptionContainer"] * { color: #9ca3af !important; }

            /* TODOS OS BOTÕES PADRÃO E SIDEBAR */
            div.stButton > button {
                background-color: #21262d !important;
                border: 1px solid #30363d !important;
                border-radius: 8px !important;
            }
            div.stButton > button * { color: #ffffff !important; }

            div.stButton > button:hover { border-color: #ffc107 !important; }
            div.stButton > button:hover * { color: #ffc107 !important; }

            /* BOTÕES PRIMÁRIOS (Ações de destaque) */
            div.stButton > button[kind="primary"] { background-color: #ffc107 !important; border-color: #ffc107 !important; }
            div.stButton > button[kind="primary"] * { color: #000000 !important; font-weight: bold !important; }
        </style>
        """
    else:
        css = """
        <style>
            .stApp { background-color: #f8f9fa; color: #1f2937; }
            [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }

            /* Títulos e Textos Padrão */
            h1, h2, h3, h4, p, span, label { color: #111827 !important; }

            /* Restaura o Menu de Navegação (Radio Buttons) para cor escura */
            div[role="radiogroup"] * { color: #1f2937 !important; }

            /* Subtítulos discretos (Captions) - Mantém o tom cinza elegante */
            [data-testid="stCaptionContainer"] * { color: #6b7280 !important; }

            /* TODOS OS BOTÕES PADRÃO (Estilo "Novo Visitante") */
            div.stButton > button {
                background-color: #ffffff !important;
                border: 1px solid #d1d5db !important;
                border-radius: 8px !important;
                transition: all 0.2s ease !important;
            }
            div.stButton > button * { color: #1f2937 !important; }

            div.stButton > button:hover {
                border-color: #ffc107 !important;
                background-color: #fffbeb !important;
            }
            div.stButton > button:hover * { color: #d97706 !important; }

            /* BOTÕES PRIMÁRIOS (Ex: Salvar - Ficam pretos no modo claro) */
            div.stButton > button[kind="primary"] { background-color: #111827 !important; border: 1px solid #111827 !important; }
            div.stButton > button[kind="primary"] * { color: #ffffff !important; }
            div.stButton > button[kind="primary"]:hover { background-color: #374151 !important; border-color: #374151 !important; }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)

def renderizar_botoes_tema():
    """Adiciona os botões de acessibilidade ao rodapé do menu"""
    st.sidebar.markdown("---")
    st.sidebar.caption("🌓 Acessibilidade Visual")

    c1, c2 = st.sidebar.columns(2)

    if  c1.button("☀️ Light", use_container_width=True, help=""):
        # Ideal para ambientes claros
        st.session_state.tema_atual = 'light'
        st.rerun()

    if c2.button("🌙 Dark", use_container_width=True, help=""):
        # Ideal para apresentações em projetores
        st.session_state.tema_atual = 'dark'
        st.rerun()

# [styles.py][v3.6 - Blindagem Antifantasma][2026-02-27]