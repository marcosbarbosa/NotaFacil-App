import streamlit as st

def aplicar_tema_dinamico():
    """Injeta CSS baseado no estado do tema selecionado"""

    # Inicializa o estado do tema se não existir
    if 'tema_atual' not in st.session_state:
        st.session_state['tema_atual'] = 'light'

    tema = st.session_state['tema_atual']

    if tema == 'dark':
        css = """
        <style>
            .stApp {
                background-color: #0e1117;
                color: #ffffff;
            }
            [data-testid="stSidebar"] {
                background-color: #161b22;
            }
            .stMarkdown, p, h1, h2, h3, h4 {
                color: #ffffff !important;
            }
            .stButton>button {
                background-color: #21262d;
                color: white;
                border: 1px solid #30363d;
            }
        </style>
        """
    else:
        css = """
        <style>
            .stApp {
                background-color: #ffffff;
                color: #000000;
            }
            [data-testid="stSidebar"] {
                background-color: #f0f2f6;
            }
            .stMarkdown, p, h1, h2, h3, h4 {
                color: #000000 !important;
            }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)

def renderizar_botoes_tema():
    """Renderiza os botões de troca no rodapé do menu"""
    st.sidebar.markdown("---")
    st.sidebar.caption("🌓 Acessibilidade Visual")

    c1, c2 = st.sidebar.columns(2)

    if c1.button("☀️ Light", use_container_width=True):
        st.session_state['tema_atual'] = 'light'
        st.rerun()

    if c2.button("🌙 Dark", use_container_width=True):
        st.session_state['tema_atual'] = 'dark'
        st.rerun()