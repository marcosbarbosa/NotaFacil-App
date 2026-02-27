import streamlit as st

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="NotaFácil | DC",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Importação dos Módulos Internos
import styles
import portal_lancamento as portal
import admin

def main():
    # 3. Inicialização de Variáveis de Sessão
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    if 'tela' not in st.session_state:
        st.session_state.tela = "lancamento"
    if 'mostra_cadastro' not in st.session_state:
        st.session_state.mostra_cadastro = False

    # 4. Aplicação do Motor Visual Dinâmico
    styles.aplicar_estilos_globais()

    # 5. CONSTRUÇÃO DO MENU LATERAL (Sidebar)
    # 📸 EXIBIÇÃO DA LOGO CORRETA
    try:
        st.sidebar.image("logo-notaFacil.png", use_container_width=True)
    except:
        st.sidebar.markdown("<h1 style='text-align: center;'>🏀</h1>", unsafe_allow_html=True)

    st.sidebar.markdown("<h2 style='text-align: center; margin-top: -10px;'>NotaFácil | DC</h2>", unsafe_allow_html=True)

    st.sidebar.caption("Navegação Estratégica")
    destino = st.sidebar.radio(
        "Ir para:",
        ["🏃 Lançamento", "🏛️ Central de Governança"],
        label_visibility="collapsed"
    )

    st.sidebar.divider()

    # 6. ROTEADOR DE TELAS PRINCIPAL
    if destino == "🏃 Lançamento":
        portal.renderizar_portal()
    else:
        admin.exibir_sala_de_guerra()

    # 7. ACESSIBILIDADE E ASSINATURA EXECUTIVA
    styles.renderizar_botoes_tema()

    st.sidebar.divider()

    # ASSINATURA DE ELITE
    st.sidebar.markdown("""
        <div style='color: #6b7280; font-size: 13px; line-height: 1.6; padding-left: 5px;'>
            <strong>IFC DC</strong> | v1.5.0<br>
            Governança Prime&reg;
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# [main.py][v8.6 - Logo NotaFacil Fix][2026-02-27]