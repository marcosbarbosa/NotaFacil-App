import streamlit as st
import database as db
import servicos_email as email_svc
import admin_auditoria as adm_aud
import admin_gestao as adm_gst

def exibir_sala_de_guerra():
    """Roteador Administrativo: Importa os submódulos da Sala de Guerra"""
    senha_master = db.obter_senha_admin()
    senha_digitada = st.sidebar.text_input("🔑 Senha Admin", type="password")

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
        if senha_digitada: st.sidebar.error("❌ Senha incorreta.")

        st.info("🔒 Acesso restrito à Diretoria. Insira a Senha Admin no menu lateral.")

        st.divider()
        if st.sidebar.button("🆘 Esqueci a Senha"):
            with st.sidebar.spinner("Solicitando resgate..."):
                # Busca o e-mail cadastrado no banco para envio
                email_diretoria = db.obter_email_admin()
                ok, msg = email_svc.recuperar_senha_admin(senha_master, email_diretoria)

                if ok: st.sidebar.success(f"Senha enviada para a Diretoria ({email_diretoria})")
                else: st.sidebar.error(msg)

# [admin.py][Injeção Dinâmica de E-mail de Resgate][2026-02-26 09:30][v8.1][40 linhas]