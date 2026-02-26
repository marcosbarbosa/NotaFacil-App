import streamlit as st
import database as db  # Conector unificado
import pandas as pd
import time

def renderizar_aba_gestao(atl_data, vis_data):
    """
    Módulo de Controle de Acessos e Membros da Equipe.
    Garante que a diretoria tenha as permissões (roles) corretas.
    """
    st.markdown("### 👥 Gestão de Atletas e Diretoria")

    col_atl, col_vis = st.columns(2)

    with col_atl:
        st.markdown("#### 🏃‍♂️ Base de Atletas")
        if atl_data:
            df_atl = pd.DataFrame(atl_data)
            # Exibição executiva focada em saldo e bolsa
            st.dataframe(
                df_atl[['nome', 'cpf', 'bolsa', 'saldo']], 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "bolsa": st.column_config.NumberColumn("Bolsa (R$)", format="%.2f"),
                    "saldo": st.column_config.NumberColumn("Saldo (R$)", format="%.2f")
                }
            )
        else:
            st.info("Nenhum atleta cadastrado.")

    with col_vis:
        st.markdown("#### 👔 Acessos da Diretoria")
        if vis_data:
            df_vis = pd.DataFrame(vis_data)

            # REPARO MARVEL: Blindagem contra erro de coluna 'role' inexistente
            if 'role' not in df_vis.columns:
                df_vis['role'] = 'admin'  # Define um padrão seguro para evitar crash

            st.dataframe(
                df_vis[['nome', 'email', 'role']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Nenhum acesso de diretoria configurado.")

    st.divider()

    # --- ÁREA DE EDIÇÃO DE PERMISSÕES ---
    st.markdown("#### 🛠️ Atualizar Permissões de Acesso")
    if vis_data:
        usuarios_lista = [f"{u['nome']} ({u['email']})" for u in vis_data]
        escolha = st.selectbox("Selecione o membro para editar:", ["Selecione..."] + usuarios_lista)

        if escolha != "Selecione...":
            email_alvo = escolha.split('(')[1].replace(')', '')
            usuario_atual = next(u for u in vis_data if u['email'] == email_alvo)

            with st.form("form_edit_permissao"):
                novo_nome = st.text_input("Nome:", value=usuario_atual['nome'])
                novo_email = st.text_input("E-mail:", value=usuario_atual['email'])
                nova_role = st.selectbox("Role (Nível de Acesso):", ["admin", "viewer", "auditor"], 
                                         index=["admin", "viewer", "auditor"].index(usuario_atual.get('role', 'admin')))

                if st.form_submit_button("💾 Salvar Alterações"):
                    ok, msg = db.atualizar_usuario(email_alvo, novo_nome, novo_email, nova_role)
                    if ok:
                        st.success("✅ Acesso atualizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Erro ao atualizar: {msg}")

def renderizar_aba_configuracoes():
    """
    Centro de Comando Prime: Identidade Visual, Risco Financeiro e Comunicação.
    """
    st.markdown("### ⚙️ Painel de Governança Integrada")

    col1, col2 = st.columns(2)

    # 1. GESTÃO DE RISCO FINANCEIRO (Lado Esquerdo)
    with col1:
        st.subheader("🚨 Risco Financeiro (BI)")
        limite_atual = db.obter_limite_alerta()

        novo_limite = st.number_input(
            "Gatilho para Alerta de Saldo Crítico (R$):", 
            value=limite_atual, 
            help="O sistema destacará em vermelho se o saldo global ficar abaixo deste valor."
        )

        if st.button("💾 Salvar Regra de Segurança", use_container_width=True):
            ok, msg = db.salvar_limite_alerta(novo_limite)
            if ok:
                st.success(f"✅ Regra atualizada: Alerta em R$ {novo_limite:,.2f}")
            else:
                st.error(msg)

    # 2. GESTÃO DE COMUNICAÇÃO (Lado Direito)
    with col2:
        st.subheader("📧 Comunicação Oficial")
        email_atual = db.obter_email_admin()

        novo_email = st.text_input(
            "E-mail Padrão da Diretoria:", 
            value=email_atual,
            help="Este e-mail será o destinatário padrão na hora de exportar os dashboards de BI."
        )

        if st.button("💾 Salvar Destinatário", use_container_width=True):
            ok, msg = db.salvar_email_admin(novo_email)
            if ok:
                st.success("✅ E-mail oficial atualizado!")
            else:
                st.error(msg)

    st.divider()

    # 3. GESTÃO DE IDENTIDADE VISUAL
    st.subheader("🖼️ Identidade Visual (Fundo do Sistema)")
    st.info("Suba aqui o arquivo da quadra para que o sistema carregue-o automaticamente nos temas visuais.")

    arquivo_bg = st.file_uploader("Upload do arquivo .png ou .jpg:", type=['png', 'jpg', 'jpeg'])

    if st.button("💾 Gravar Identidade no Banco de Dados", use_container_width=True):
        if arquivo_bg:
            with st.spinner("Sincronizando com o Supabase..."):
                ok, msg = db.salvar_imagem_fundo_db(arquivo_bg.getvalue())
                if ok:
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.warning("Selecione um arquivo de imagem primeiro.")

# [admin_gestao.py][Edição Marvel Prime c/ Comunicação Oficial v6.0][2026-02-26]