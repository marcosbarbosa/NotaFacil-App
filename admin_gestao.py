import streamlit as st
import database as db
import pandas as pd
import time
from datetime import date

def renderizar_aba_gestao(atl_data, vis_data):
    """Módulo de RH v17.0: Gestão de Equipe com Sanitização Máxima"""
    st.markdown("### 👥 Gestão Integrada de Equipe")

    # SUB-MENU DE NAVEGAÇÃO INTERNA
    modo = st.radio(
        "Modo de Operação:", 
        ["📊 Visão Geral", "➕ Novo Cadastro", "✏️ Editar Membro"], 
        horizontal=True, 
        label_visibility="collapsed"
    )
    st.divider()

    # ==========================================
    # 📊 MODO 1: VISÃO GERAL (Tabelas)
    # ==========================================
    if modo == "📊 Visão Geral":
        col_atl, col_vis = st.columns(2)
        with col_atl:
            st.markdown("#### 🏃‍♂️ Base de Atletas")
            if atl_data:
                df_atl = pd.DataFrame(atl_data)
                if 'data_nascimento' in df_atl.columns:
                    df_atl['data_nascimento'] = pd.to_datetime(df_atl['data_nascimento']).dt.strftime('%d/%m/%Y')

                st.dataframe(
                    df_atl[['nome', 'cpf', 'bolsa', 'saldo']], 
                    use_container_width=True, hide_index=True,
                    column_config={
                        "bolsa": st.column_config.NumberColumn("Bolsa (R$)", format="%.2f"),
                        "saldo": st.column_config.NumberColumn("Saldo (R$)", format="%.2f")
                    }
                )
            else: st.info("Nenhum atleta cadastrado.")

        with col_vis:
            st.markdown("#### 👔 Base da Diretoria / Visitantes")
            if vis_data:
                df_vis = pd.DataFrame(vis_data)
                if 'role' not in df_vis.columns: df_vis['role'] = 'viewer'
                st.dataframe(df_vis[['nome', 'email', 'role']], use_container_width=True, hide_index=True)
            else: st.info("Nenhum visitante configurado.")

    # ==========================================
    # ➕ MODO 2: NOVO CADASTRO
    # ==========================================
    elif modo == "➕ Novo Cadastro":
        col1, col2 = st.columns(2)

        # FORMULÁRIO: NOVO ATLETA
        with col1:
            st.markdown("#### 🏃‍♂️ Cadastrar Atleta")
            with st.form("form_novo_atleta", clear_on_submit=True):
                n_nome = st.text_input("Nome Completo*")
                n_cpf = st.text_input("CPF* (Apenas números)", max_chars=14)
                n_bolsa = st.number_input("Valor da Bolsa Mensal (R$)*", min_value=0.0, step=50.0)
                n_nasc = st.date_input("Data de Nascimento", format="DD/MM/YYYY", min_value=date(1950, 1, 1), max_value=date.today())
                n_sexo = st.selectbox("Sexo", ["M", "F"])
                n_email = st.text_input("E-mail do Atleta")
                n_senha = st.text_input("Senha de Acesso", value="atleta123", type="password")

                if st.form_submit_button("🚀 Salvar Novo Atleta", use_container_width=True, type="primary"):
                    cpf_limpo = n_cpf.replace(".", "").replace("-", "").strip()
                    if n_nome.strip() and cpf_limpo.isdigit() and len(cpf_limpo) == 11:
                        dados_atl = {
                            "nome": n_nome.strip(), "cpf": cpf_limpo, "bolsa": n_bolsa, 
                            "data_nascimento": n_nasc.strftime('%Y-%m-%d'), 
                            "sexo": n_sexo, "email": n_email.strip(), "senha": n_senha.strip(), "saldo": n_bolsa
                        }
                        ok, msg = db.upsert_atleta(dados_atl)
                        if ok: st.success(f"Atleta {n_nome.strip()} cadastrado!"); time.sleep(1.5); st.rerun()
                        else: st.error(f"Erro: {msg}")
                    else: st.warning("⚠️ Preencha o Nome e insira um CPF válido (11 números)!")

        # FORMULÁRIO: NOVO VISITANTE/DIRETOR
        with col2:
            st.markdown("#### 👔 Cadastrar Diretoria / Visitante")
            with st.form("form_novo_visitante", clear_on_submit=True):
                v_nome = st.text_input("Nome Completo*")
                v_email = st.text_input("E-mail* (Usado para login)")
                v_whats = st.text_input("WhatsApp (DDD + Número)*", placeholder="(11) 99999-9999", help="Insira o DDD entre parênteses seguido do número.")
                v_role = st.selectbox("Nível de Acesso", ["viewer", "auditor", "admin"])
                v_senha = st.text_input("Senha de Acesso*", value="diretoria123", type="password")

                if st.form_submit_button("🚀 Salvar Novo Visitante", use_container_width=True, type="primary"):
                    if v_nome.strip() and "@" in v_email and v_senha.strip():
                        dados_vis = {"nome": v_nome.strip(), "email": v_email.strip(), "whatsapp": v_whats.strip(), "role": v_role, "senha": v_senha.strip()}
                        ok, msg = db.upsert_visitante(dados_vis)
                        if ok: st.success(f"Membro {v_nome.strip()} cadastrado!"); time.sleep(1.5); st.rerun()
                        else: st.error(msg)
                    else: st.warning("⚠️ Nome, Senha e um E-mail válido (com @) são obrigatórios!")

    # ==========================================
    # ✏️ MODO 3: EDITAR MEMBRO EXISTENTE
    # ==========================================
    elif modo == "✏️ Editar Membro":
        tipo_edit = st.selectbox("Quem você deseja editar?", ["🏃‍♂️ Atleta", "👔 Diretoria / Visitante"])

        if "Atleta" in tipo_edit:
            if atl_data:
                atl_map = {f"{a['nome']} (CPF: {a['cpf']})": a for a in atl_data}
                escolha = st.selectbox("Selecione o Atleta:", ["Selecione..."] + list(atl_map.keys()))
                if escolha != "Selecione...":
                    atleta = atl_map[escolha]
                    with st.form("form_edit_atleta"):
                        e_nome = st.text_input("Nome", value=atleta.get('nome', ''))
                        e_bolsa = st.number_input("Valor da Bolsa (R$)", value=float(atleta.get('bolsa', 0.0)))
                        e_saldo = st.number_input("Ajuste Manual de Saldo (R$)", value=float(atleta.get('saldo', 0.0)))
                        data_v = pd.to_datetime(atleta.get('data_nascimento', date.today())).date()
                        e_nasc = st.date_input("Data de Nascimento", value=data_v, format="DD/MM/YYYY")
                        e_email = st.text_input("E-mail", value=atleta.get('email', ''))
                        e_senha = st.text_input("Redefinir Senha", value=atleta.get('senha', ''), type="password")

                        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary"):
                            dados_atl = atleta.copy(); dados_atl.update({
                                "nome": e_nome.strip(), "bolsa": e_bolsa, "saldo": e_saldo, 
                                "data_nascimento": e_nasc.strftime('%Y-%m-%d'), "email": e_email.strip(), "senha": e_senha.strip()
                            })
                            ok, msg = db.upsert_atleta(dados_atl)
                            if ok: st.success("Perfil atualizado!"); time.sleep(1); st.rerun()
                            else: st.error(msg)
            else: st.info("Nenhum atleta para editar.")
        else:
            if vis_data:
                vis_map = {f"{v['nome']} ({v.get('email', 'S/ Email')})": v for v in vis_data}
                escolha = st.selectbox("Selecione o Membro:", ["Selecione..."] + list(vis_map.keys()))
                if escolha != "Selecione...":
                    visitante = vis_map[escolha]
                    with st.form("form_edit_visitante"):
                        e_nome = st.text_input("Nome", value=visitante.get('nome', ''))
                        e_email = st.text_input("E-mail", value=visitante.get('email', ''))
                        e_whats = st.text_input("WhatsApp", value=visitante.get('whatsapp', ''), placeholder="(11) 99999-9999")
                        papel_atual = visitante.get('role', 'viewer')
                        idx_role = ["viewer", "auditor", "admin"].index(papel_atual) if papel_atual in ["viewer", "auditor", "admin"] else 0
                        e_role = st.selectbox("Nível de Acesso", ["viewer", "auditor", "admin"], index=idx_role)
                        e_senha = st.text_input("Redefinir Senha", value=visitante.get('senha', ''), type="password")

                        if st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary"):
                            dados_vis = visitante.copy(); dados_vis.update({"nome": e_nome.strip(), "email": e_email.strip(), "whatsapp": e_whats.strip(), "role": e_role, "senha": e_senha.strip()})
                            ok, msg = db.upsert_visitante(dados_vis)
                            if ok: st.success("Perfil atualizado!"); time.sleep(1); st.rerun()
                            else: st.error(msg)
            else: st.info("Nenhum membro para editar.")

def renderizar_aba_configuracoes():
    """Painel de Governança Operacional: Regras e Radares"""
    st.markdown("### ⚙️ Painel de Governança Operacional")

    # --- LINHA 1: SEGURANÇA E COMUNICAÇÃO ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚨 Risco Financeiro (BI)")
        limite_atual = db.obter_limite_alerta()
        novo_limite = st.number_input("Gatilho de Saldo Crítico (R$):", value=limite_atual)
        if st.button("💾 Salvar Regra de Segurança", use_container_width=True, key="btn_limite"):
            ok, msg = db.salvar_limite_alerta(novo_limite)
            if ok: st.success(f"✅ Regra atualizada: R$ {novo_limite:,.2f}")
            else: st.error(msg)

    with col2:
        st.subheader("📧 Comunicação Oficial")
        email_atual = db.obter_email_admin()
        novo_email = st.text_input("E-mail Padrão da Diretoria:", value=email_atual)
        if st.button("💾 Salvar Destinatário", use_container_width=True, key="btn_email"):
            if "@" in novo_email:
                ok, msg = db.salvar_email_admin(novo_email.strip())
                if ok: st.success("✅ E-mail oficial atualizado!")
                else: st.error(msg)
            else: st.warning("⚠️ Insira um e-mail válido com '@'.")

    st.divider()

    # --- LINHA 2: O RADAR PRIME 5AM ---
    st.markdown("#### ⏰ Radar de Cobrança Automático (BI Prime)")
    st.caption("Configuração do robô que envia a lista de atletas com pendências financeiras para a Diretoria às 05:00 AM.")

    try:
        cfg_atual = db.obter_config_alerta()
    except:
        cfg_atual = {"ativo": False, "frequencia_dias": 3}

    with st.container(border=True):
        c_rad1, c_rad2 = st.columns()
        with c_rad1:
            st.markdown("<br>", unsafe_allow_html=True)
            alerta_ativo = st.toggle("Habilitar Radar Matinal", value=cfg_atual.get('ativo', False))
        with c_rad2:
            freq = st.number_input(
                "Frequência do Alerta (Dias):", 
                min_value=1, max_value=30, 
                value=int(cfg_atual.get('frequencia_dias', 3)),
                help="1 = Todos os dias | 3 = A cada 3 dias | 7 = Semanalmente",
                disabled=not alerta_ativo
            )

        if st.button("💾 Atualizar Motor do Radar", use_container_width=True, type="primary"):
            with st.spinner("Sincronizando gatilhos com o servidor..."):
                ok, msg = db.salvar_config_alerta(alerta_ativo, freq)
                if ok: st.success("✅ Radar configurado com sucesso!")
                else: st.error(msg)

# [admin_gestao.py][v17.0 - Radar e Sanitização Total][2026-02-27]