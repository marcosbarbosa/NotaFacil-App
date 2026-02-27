import streamlit as st
import database as db
import servicos_email as email_svc
import admin_auditoria as adm_aud
import admin_gestao as adm_gst

def exibir_sala_de_guerra():
    """Roteador Administrativo v11.5: Blindagem de Identidade e Minimalismo Executivo"""

    # 1. Recupera credenciais de segurança do banco de dados
    senha_master = db.obter_senha_admin()
    email_diretoria = db.obter_email_admin()

    # --- MENU LATERAL (Autenticação Discreta) ---
    st.sidebar.caption("Governança Corporativa")
    col_input, col_btn = st.sidebar.columns([4, 1])

    with col_input:
        senha_digitada = st.text_input(
            "Credencial", 
            type="password", 
            label_visibility="collapsed", 
            placeholder="Insira a credencial..."
        )

    # --- PROTOCOLO DE ACESSO ---
    if senha_digitada == senha_master:
        atl_data, vis_data, lan_data = db.carregar_dados_globais()

        # 🛡️ BLINDAGEM: Garante que exista um usuário logado para não travar a Auditoria
        if 'usuario_logado' not in st.session_state or st.session_state.usuario_logado is None:
            st.session_state.usuario_logado = {"tipo": "admin", "id": "MASTER", "nome": "Diretoria Executiva"}

        user_logado = st.session_state.usuario_logado
        admin_atual = user_logado.get('nome', 'Diretoria Executiva')

        # Abas limpas, sem emojis, focadas na seriedade do módulo
        tab_aud, tab_bi, tab_usr, tab_cfg = st.tabs([
            "Auditoria Operacional", 
            "Relatórios & BI", 
            "Gestão de Equipe", 
            "Configurações"
        ])

        with tab_aud:
            # Módulo de aprovação protegido contra erros de NoneType
            adm_aud.renderizar_aba_auditoria(atl_data, lan_data)

        with tab_bi:
            adm_aud.renderizar_aba_bi(atl_data, lan_data, admin_atual)

        with tab_usr:
            adm_gst.renderizar_aba_gestao(atl_data, vis_data)

        with tab_cfg:
            adm_gst.renderizar_aba_configuracoes()

    else: 
        # --- PROTOCOLO DE SEGURANÇA (Acesso Negado) ---
        with col_btn:
            st.button("➔", help="Validar")

        if senha_digitada: 
            st.sidebar.error("Credencial inválida.")

        st.sidebar.divider()

        if st.sidebar.button("Recuperar Acesso", use_container_width=True):
            with st.sidebar.spinner("Processando..."):
                ok, msg = email_svc.recover_senha_admin(senha_master, email_diretoria)

                if ok and "@" in email_diretoria:
                    partes = email_diretoria.split("@")
                    prefixo = partes[0][:4] if len(partes[0]) >= 4 else partes[0][:2]
                    email_oculto = f"{prefixo}***@{partes[1]}"
                    st.sidebar.success(f"Enviado para: {email_oculto}")
                else: 
                    st.sidebar.error(msg)

        # TELA DE BLOQUEIO MINIMALISTA (Área Principal)
        _renderizar_lock_screen()

def _renderizar_lock_screen():
    """Interface Visual de Bloqueio - Foco na Tipografia e Sobriedade"""
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])

    with c2:
        st.markdown("""
        <div style="text-align: center; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px;">
            <h2 style="color: #ffffff; font-weight: 300; letter-spacing: 4px; font-size: 22px; margin-bottom: 15px; text-transform: uppercase;">
                Acesso Restrito
            </h2>
            <div style="width: 30px; height: 2px; background-color: #ffc107; margin: 0 auto 25px auto;"></div>
            <p style="color: #888888; font-size: 14px; font-weight: 300; line-height: 1.6;">
                Módulo de Governança exclusivo para a Diretoria Executiva.<br>
                Por favor, autentique-se no painel lateral para prosseguir.
            </p>
        </div>
        """, unsafe_allow_html=True)

# [admin.py][Minimalismo & Blindagem v11.5][2026-02-27]