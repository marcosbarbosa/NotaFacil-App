import streamlit as st
import database as db # Mantemos o alias para compatibilidade com outros arquivos
import styles
import portal_lancamento as portal
import admin

# ==========================================
# 1. SETUP INICIAL DE PLATAFORMA
# ==========================================
st.set_page_config(
    page_title="NotaFácil Prime", 
    page_icon="🏀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INICIALIZAÇÃO DE SESSÕES (CACHE BI)
# ==========================================
# Garante que as variáveis de controle existam na memória do navegador
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None

if 'mostra_cadastro' not in st.session_state:
    st.session_state['mostra_cadastro'] = False

# Recupera o tema visual preferido (Inicia no Escuro por padrão)
if 'tema_visual' not in st.session_state:
    st.session_state['tema_visual'] = "🌑 Escuro"

# ==========================================
# 3. APLICAÇÃO DO MOTOR VISUAL BLINDADO
# ==========================================
# Chama o styles.py que agora processa o fundo vindo do banco de dados
styles.aplicar_estilos_globais(st.session_state['tema_visual'])

# ==========================================
# 4. MENU LATERAL DE GOVERNANÇA
# ==========================================
with st.sidebar:
    st.image("logo-notaFacil.png", use_container_width=True)
    st.divider()

    st.caption("Navegação Estratégica")
    navegacao = st.radio(
        "Selecione o Módulo", 
        ["🏃 Lançamento", "🏛️ Central de Governança"],
        label_visibility="collapsed"
    )

    st.divider()

    # Seletor de Temas (Integrado com db_config para ler o fundo da quadra)
    st.caption("🎨 Personalização Visual")
    opcoes_temas = ["🌑 Escuro", "☀️ Claro", "🏢 Cinza (Prime)", "🏀 Fundo Imagem"]

    try: 
        idx_atual = opcoes_temas.index(st.session_state['tema_visual'])
    except: 
        idx_atual = 0

    tema_selecionado = st.selectbox(
        "Escolha o Tema", 
        opcoes_temas,
        index=idx_atual,
        label_visibility="collapsed"
    )

    # Lógica de atualização imediata de UI
    if tema_selecionado != st.session_state['tema_visual']:
        st.session_state['tema_visual'] = tema_selecionado
        st.rerun()

# ==========================================
# 5. ROTEADOR DE MÓDULOS (CORE)
# ==========================================
if navegacao == "🏃 Lançamento":
    # Módulo de entrada de dados para atletas e visitantes
    portal.renderizar_portal()

elif navegacao == "🏛️ Central de Governança":
    # Módulo de Auditoria, BI e Gestão de Equipe
    admin.exibir_sala_de_guerra()

# ==========================================
# 6. RODAPÉ DE VERSÃO (BI AUDIT)
# ==========================================
# Recupera as informações de copyright do banco modularizado
cfg_rodape = db.obter_config_rodape()
st.sidebar.markdown(f"""
---
<div style='text-align: center; color: #777; font-size: 10px;'>
    {cfg_rodape['copyright']} | {cfg_rodape['versao']}<br>
    Governança Inteligente
</div>
""", unsafe_allow_html=True)

# [main.py][Unificador de Módulos Database][2026-02-26 16:45][v1.5]