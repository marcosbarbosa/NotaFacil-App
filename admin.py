import streamlit as st
import database as db
import servicos_email as email_svc
import admin_auditoria as adm_aud
import admin_gestao as adm_gst

def exibir_sala_de_guerra():
    """Roteador Administrativo: Importa os submódulos da Sala de Guerra"""
    senha_master = db.obter_senha_admin()

    st.sidebar.caption("🔑 Acesso Restrito")

    # DIVISÃO INLINE: 80% do espaço para a senha, 20% para o botão minimalista
    col_input, col_btn = st.sidebar.columns([4, 1])

    with col_input:
        # label_visibility="collapsed" remove o texto de cima para alinhar com o botão
        senha_digitada = st.text_input("Senha Admin", type="password", label_visibility="collapsed", placeholder="Sua senha...")

    if senha_digitada == senha_master:
        atl_data, vis_data, lan_data = db.carregar_dados_globais()

        tab_fin, tab_usr, tab_cfg = st.tabs(["📊 Auditoria Financeira", "👥 Gestão de Usuários", "⚙️ Configurações Master"])

        user_logado = st.session_state.get('usuario_logado')
        admin_atual = user_logado.get('nome', 'Administrador Local') if isinstance(user_logado, dict) else 'Administrador Local'

        with tab_fin:
            adm_aud.renderizar_aba_auditoria(atl_data, lan_data, admin_atual)

        with tab_usr:
            adm_gst.renderizar_aba_gestao(atl_data, vis_data)

        with tab_cfg:
            adm_gst.renderizar_aba_configuracoes()

    else: 
        with col_btn:
            # UX Prime: Seta vetorial limpa (sem o bloco azul do Windows) herdando nosso CSS Oficial
            btn_entrar = st.button("➔", use_container_width=True, help="Entrar no Sistema")

        if senha_digitada: st.sidebar.error("❌ Senha incorreta.")

        st.sidebar.divider()
        if st.sidebar.button("🆘 Esqueci a Senha", use_container_width=True):
            with st.sidebar.spinner("Solicitando resgate..."):
                email_diretoria = db.obter_email_admin()
                ok, msg = email_svc.recuperar_senha_admin(senha_master, email_diretoria)

                if ok: 
                    # BLINDAGEM DE SEGURANÇA: Ofuscação de PII
                    if "@" in email_diretoria:
                        partes = email_diretoria.split("@")
                        prefixo = partes[0][:4] if len(partes[0]) >= 4 else partes[0][:2]
                        email_oculto = f"{prefixo}***@{partes[1]}"
                    else:
                        email_oculto = "***"

                    st.sidebar.success(f"Senha enviada: {email_oculto}")
                else: 
                    st.sidebar.error(msg)

# [admin.py][Botão Inline Vetorial Limpo][2026-02-26 10:55][v8.5][55 linhas]