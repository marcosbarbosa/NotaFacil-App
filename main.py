import os
import streamlit as st
from PIL import Image

# Importação dos nossos módulos
import styles as ui
import database as db
import admin as adm
import portal_lancamento as portal

# -------------------------------------------------------------
# 1. CONTROLE DE MEMÓRIA E SESSÃO (STATE MANAGEMENT)
# -------------------------------------------------------------
if "tela" not in st.session_state: st.session_state.tela = "lancamento"
if "res_data" not in st.session_state: st.session_state.res_data = {}
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "mostra_cadastro" not in st.session_state: st.session_state.mostra_cadastro = False
if "tema_escolhido" not in st.session_state: st.session_state.tema_escolhido = "branco"

# Aplica o design dinâmico assim que a página carrega
ui.aplicar_design(st.session_state.tema_escolhido)

# -------------------------------------------------------------
# 2. CONSTRUÇÃO DA BARRA LATERAL E LOGOMARCA ANTI-CRASH
# -------------------------------------------------------------
try:
    # ATUALIZAÇÃO: Rede de captura robusta para todas as extensões!
    if os.path.exists("logo-notaFacil.png"):
        logo_img = Image.open("logo-notaFacil.png")
        st.sidebar.image(logo_img, use_container_width=True)
    elif os.path.exists("logo-notaFacil.jpg"):
        logo_img = Image.open("logo-notaFacil.jpg")
        st.sidebar.image(logo_img, use_container_width=True)
    elif os.path.exists("logo.png"):
        logo_img = Image.open("logo.png")
        st.sidebar.image(logo_img, use_container_width=True)
    elif os.path.exists("Logo.png"):
        logo_img = Image.open("Logo.png")
        st.sidebar.image(logo_img, use_container_width=True)
    else:
        st.sidebar.markdown("### 🏀 NotaFácil Prime")
except Exception:
    st.sidebar.markdown("### 🏀 NotaFácil Prime")

# Menu Principal desobstruído no topo
menu = st.sidebar.radio("Navegação", ["🏃 Lançamento", "🏛️ Central de Governança"])

st.sidebar.divider()

# --- ATUALIZAÇÃO UX: Ocultado em um Expander na base da barra lateral ---
with st.sidebar.expander("🎨 Personalização Visual", expanded=False):
    temas_opcoes = {
        "⚪ Fundo Branco": "branco", 
        "🌌 Fundo Imagem": "imagem", 
        "🌑 Fundo Preto": "preto", 
        "📓 Fundo Cinza": "cinza"
    }
    idx_atual = list(temas_opcoes.values()).index(st.session_state.tema_escolhido)

    tema_sel = st.selectbox("Tema da Interface:", list(temas_opcoes.keys()), index=idx_atual)
    if temas_opcoes[tema_sel] != st.session_state.tema_escolhido:
        st.session_state.tema_escolhido = temas_opcoes[tema_sel]
        st.rerun()

# -------------------------------------------------------------
# 3. ROTEADOR DE MÓDULOS (MVC Pattern)
# -------------------------------------------------------------
if menu == "🏃 Lançamento":
    portal.renderizar_portal()

elif menu == "🏛️ Central de Governança":
    st.title("🏛️ Central de Governança")
    adm.exibir_sala_de_guerra()

# [main.py][Injeção da Logomarca PNG com Múltiplas Capturas][2026-02-25 18:45][v27.3][76 linhas]