import streamlit as st
import database as db
import servicos_email as email_svc
import admin_auditoria as adm_aud
import admin_gestao as adm_gst

def exibir_sala_de_guerra():
    """Roteador Administrativo v10.5: Arquitetura de Abas Especializadas e Lock Screen Prime"""

    # 1. Recupera credenciais de segurança do banco de dados
    senha_master = db.obter_senha_admin()
    email_diretoria = db.obter_email_admin()

    # --- MENU LATERAL (Camada de Proteção) ---
    st.sidebar.caption("🔑 Acesso Restrito à Diretoria")
    col_input, col_btn = st.sidebar.columns([4, 1])

    with col_input:
        # Placeholder ajuda na orientação visual do diretor
        senha_digitada = st.text_input(
            "Senha Admin", 
            type="password", 
            label_visibility="collapsed", 
            placeholder="Chave Mestra..."
        )

    # --- PROTOCOLO DE ACESSO ---
    if senha_digitada == senha_master:
        # Sincronização de Dados Globais para Auditoria e BI
        atl_data, vis_data, lan_data = db.carregar_dados_globais()

        # Identificação do Operador para Logs de Governança
        user_logado = st.session_state.get('usuario_logado')
        admin_atual = user_logado.get('nome', 'Administrador Local') if isinstance(user_logado, dict) else 'Administrador Local'

        # Estrutura de Abas de Comando
        tab_aud, tab_bi, tab_usr, tab_cfg = st.tabs([
            "🔎 Auditoria Operacional", 
            "📊 Relatórios & BI", 
            "👥 Gestão de Equipe", 
            "⚙️ Configurações"
        ])

        with tab_aud:
            # Módulo de análise e aprovação de notas v13.0
            adm_aud.renderizar_aba_auditoria(atl_data, lan_data)

        with tab_bi:
            # Inteligência de negócio e gráficos de volume financeiro
            adm_aud.renderizar_aba_bi(atl_data, lan_data, admin_atual)

        with tab_usr:
            # Gestão de RH, Atletas e Visitantes v15.0
            adm_gst.renderizar_aba_gestao(atl_data, vis_data)

        with tab_cfg:
            # Regras de negócio e comunicação estratégica
            adm_gst.renderizar_aba_configuracoes()

    else: 
        # --- PROTOCOLO DE SEGURANÇA (Acesso Negado) ---
        with col_btn:
            st.button("➔", help="Validar Acesso")

        if senha_digitada: 
            st.sidebar.error("❌ Credencial Inválida.")

        st.sidebar.divider()

        # Fluxo de Recuperação com Ocultação Parcial de E-mail
        if st.sidebar.button("🆘 Resgatar Acesso", use_container_width=True):
            with st.sidebar.spinner("Solicitando resgate..."):
                ok, msg = email_svc.recuperar_senha_admin(senha_master, email_diretoria)

                if ok and "@" in email_diretoria:
                    partes = email_diretoria.split("@")
                    prefixo = partes[0][:4] if len(partes[0]) >= 4 else partes[0][:2]
                    email_oculto = f"{prefixo}***@{partes[1]}"
                    st.sidebar.success(f"Senha enviada para: {email_oculto}")
                else: 
                    st.sidebar.error(msg)

        # TELA DE BLOQUEIO PRIME (Área Principal)
        _renderizar_lock_screen()

def _renderizar_lock_screen():
    """Interface Visual de Bloqueio com Design Stealth"""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])

    with c2:
        st.markdown("""
        <div style="
            background-color: rgba(20, 22, 28, 0.95); 
            padding: 40px; 
            border-radius: 16px; 
            text-align: center; 
            border: 1px solid #333; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
            backdrop-filter: blur(10px);
        ">
            <h1 style="font-size: 65px; margin-bottom: 0;">🛡️</h1>
            <h2 style="color: #ffc107; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-top: 10px;">SALA DE GUERRA</h2>
            <hr style="border-color: #444; margin: 20px 0;">
            <p style="color: #ddd; font-size: 16px; margin-bottom: 25px; line-height: 1.5;">
                Acesso exclusivo para a <b>Diretoria Executiva</b>.<br>Utilize sua chave mestra no menu lateral para desbloquear a Central de Governança.
            </p>
            <div style="background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; padding: 15px; text-align: left; border-radius: 4px;">
                <span style="color: #ffc107; font-weight: bold;">🔑 Status do Sistema:</span><br>
                <span style="color: #ccc; font-size: 14px;">Módulo Financeiro e de RH protegidos por criptografia de ponta.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# [admin.py][Sincronização Sala de Guerra v10.5][2026-02-27]
# Total de Linhas de Código: 105