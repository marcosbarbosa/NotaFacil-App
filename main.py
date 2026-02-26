import streamlit as st

# 1. CONFIGURAÇÃO DA PÁGINA (A PROTEÇÃO DO MENU LATERAL)
# Deve ser obrigatoriamente a primeira linha de código Streamlit.
st.set_page_config(
    page_title="NotaFácil Prime | NSG",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded" # 🔓 GARANTE QUE O MENU SEMPRE APAREÇA AO INICIAR
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
    if 'mostra_cadastro' not in st.session_state:
        st.session_state.mostra_cadastro = False

    # 4. Aplicação do Motor Visual (Contém o "Botão de Resgate" do Menu)
    styles.aplicar_estilos_globais()

    # 5. CONSTRUÇÃO DO MENU LATERAL (Sidebar)
    st.sidebar.markdown("<h2 style='text-align: center;'>🏀 NotaFácil Prime</h2>", unsafe_allow_html=True)

    st.sidebar.caption("Navegação Estratégica")
    destino = st.sidebar.radio(
        "Ir para:",
        ["🏃 Lançamento", "🏛️ Central de Governança"],
        label_visibility="collapsed"
    )

    st.sidebar.divider()

    # Rodapé do Menu Lateral
    st.sidebar.info("IFC DC | v1.0.0\nGovernança Inteligente")

    # 6. ROTEADOR DE TELAS PRINCIPAL
    if destino == "🏃 Lançamento":
        # Tela para Atletas e Visitantes lançarem NFs
        portal.renderizar_portal()
    else:
        # Tela da Diretoria com bloqueio de senha
        admin.exibir_sala_de_guerra()

if __name__ == "__main__":
    main()

# [main.py][Sidebar Persistente v7.0][2026-02-26]