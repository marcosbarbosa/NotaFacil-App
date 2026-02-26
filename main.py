import streamlit as st

# 1. CONFIGURAÇÃO DA PÁGINA (A PROTEÇÃO DO MENU LATERAL)
# Esta deve ser sempre a PRIMEIRA linha de código do Streamlit no arquivo.
st.set_page_config(
    page_title="NotaFácil Prime | NSG",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded" # 🔓 ISSO GARANTE QUE O MENU SEMPRE APAREÇA!
)

# 2. Importação dos Módulos Internos
import styles
import portal_lancamento as portal
import admin

def main():
    # 3. Inicialização de Variáveis de Sessão (State)
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    if 'tela' not in st.session_state:
        st.session_state.tela = "lancamento"
    if 'res_data' not in st.session_state:
        st.session_state.res_data = {}
    if 'mostra_cadastro' not in st.session_state:
        st.session_state.mostra_cadastro = False

    # 4. Aplicação do Visual (Modo Operacional Stealth)
    styles.aplicar_estilos_globais()

    # 5. CONSTRUÇÃO DO MENU LATERAL (Sidebar)
    st.sidebar.markdown("<h2 style='text-align: center;'>🏀 NotaFácil Prime</h2>", unsafe_allow_html=True)

    # Este é o seletor que controla o que aparece na tela direita
    destino = st.sidebar.radio(
        "Navegação Estratégica:",
        ["🏃 Lançamento de NF", "🏛️ Central de Governança"],
        label_visibility="visible"
    )

    st.sidebar.divider()

    # 6. ROTEADOR DE TELAS
    if destino == "🏃 Lançamento de NF":
        # Tela para Atletas e Visitantes
        portal.renderizar_portal()
    else:
        # Tela da Diretoria (Com o campo de senha que configuramos)
        admin.exibir_sala_de_guerra()

if __name__ == "__main__":
    main()

# [main.py][Sidebar Persistente v6.5][2026-02-26]