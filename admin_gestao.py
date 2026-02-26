import streamlit as st
import pandas as pd
from datetime import date
import time
import database as db
import funcoes_admin as f_adm

def renderizar_aba_gestao(atl_data, vis_data):
    # ... (MANTENHA O CÓDIGO DA GESTÃO DE USUÁRIOS IGUAL AO ANTERIOR, ou copie este bloco abaixo que é idêntico) ...
    grafico = f_adm.gerar_grafico_consumo(atl_data)
    if grafico: st.plotly_chart(grafico, use_container_width=True)
    st.divider()

    if "lote_key" not in st.session_state: st.session_state.lote_key = 0
    st.subheader("👥 Lista de Acessos")

    u_l = []
    for a in atl_data:
        b_val = float(a.get('bolsa') or a.get('limite_mensal') or 0.0)
        s_val = float(a.get('saldo') or 0.0)
        u_l.append({"Nome": a['nome'], "Tipo": "🏃 Atleta", "Bolsa Total": f"R$ {b_val:,.2f}", "NFs Entregues": f"R$ {(b_val - s_val):,.2f}", "Saldo Restante": f"R$ {s_val:,.2f}", "Email": a.get('email', '-')})
    for v in vis_data:
        u_l.append({"Nome": v['nome'], "Tipo": "👤 Visitante", "Bolsa Total": "-", "NFs Entregues": "-", "Saldo Restante": "-", "Email": v.get('email', '-')})

    st.dataframe(pd.DataFrame(u_l).sort_values("Nome"), use_container_width=True, hide_index=True)

    st.divider()
    with st.expander("⚡ Cadastro Rápido de Atletas", expanded=False):
        df_mod = pd.DataFrame(columns=["Nome","CPF","Nascimento","Sexo","Bolsa","Email","Senha"])
        df_ed = st.data_editor(df_mod, num_rows="dynamic", use_container_width=True, key=f"ed_{st.session_state.lote_key}",
                              column_config={"Sexo": st.column_config.SelectboxColumn("Sexo", options=["M", "F"], required=True), "Nascimento": st.column_config.DateColumn("Nascimento", format="DD/MM/YYYY"), "Senha": st.column_config.TextColumn("Senha Inicial")})
        if st.button("🚀 Salvar Novos Registros", type="primary"):
            if not df_ed.empty:
                sucessos, erros = 0, []
                for _, r in df_ed.iterrows():
                    nm, cp = r.get('Nome'), r.get('CPF')
                    if pd.notnull(nm) and pd.notnull(cp) and str(nm).strip() != '':
                        cpf_str = ''.join(filter(str.isdigit, str(cp)))
                        nasc = r.get('Nascimento')
                        if pd.isnull(nasc): nasc_str = str(date.today())
                        else: nasc_str = nasc.strftime('%Y-%m-%d') if hasattr(nasc, 'strftime') else str(nasc)[:10]
                        ok, msg = db.cadastrar_novo_atleta(nm, cpf_str, nasc_str, str(r.get('Sexo','M')), float(r.get('Bolsa',0) if pd.notnull(r.get('Bolsa')) else 0), str(r.get('Email')) if pd.notnull(r.get('Email')) else f"{cpf_str}@notafacil.com", str(r.get('Senha')) if pd.notnull(r.get('Senha')) else "mudar123")
                        if ok: sucessos += 1
                        else: erros.append(f"{nm}: {msg}")
                if sucessos > 0:
                    st.success(f"✅ {sucessos} cadastrados!"); st.session_state.lote_key += 1; time.sleep(1.2); st.rerun()
                for err in erros: st.error(err)

    st.divider()
    with st.expander("🛠️ Manutenção (Editar / Excluir)", expanded=False):
        tipo_edit = st.radio("Selecione a conta:", ["🏃 Atleta", "👤 Visitante"], horizontal=True)
        if tipo_edit == "🏃 Atleta":
            atl_dict = {f"{a['nome']} (CPF: {a['cpf']})": a for a in atl_data}
            user_sel = st.selectbox("Selecione o Atleta:", ["Selecione..."] + list(atl_dict.keys()))
            if user_sel != "Selecione...":
                dados = atl_dict[user_sel]
                with st.form("form_edit_atl"):
                    e_nm = st.text_input("Nome", dados['nome'])
                    e_em = st.text_input("E-mail", dados.get('email', ''))
                    e_sn = st.text_input("Senha", dados.get('senha', ''))
                    bolsa_atual = float(dados.get('bolsa') or dados.get('limite_mensal') or 0.0)
                    e_bl = st.number_input("Valor da Bolsa (R$)", value=bolsa_atual)
                    c_sv, c_del = st.columns(2)
                    if c_sv.form_submit_button("💾 Salvar", type="primary"):
                        ok, msg = db.atualizar_dados_atleta(dados['cpf'], e_nm, e_em, e_sn, e_bl)
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)
                    if c_del.form_submit_button("🗑️ Excluir"):
                        ok, msg = db.excluir_usuario('atleta', dados['cpf'])
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)
        else:
            vis_dict = {f"{v['nome']} (Email: {v.get('email', 'Sem Email')})": v for v in vis_data}
            user_sel = st.selectbox("Selecione o Visitante:", ["Selecione..."] + list(vis_dict.keys()))
            if user_sel != "Selecione...":
                dados = vis_dict[user_sel]
                with st.form("form_edit_vis"):
                    e_nm = st.text_input("Nome", dados['nome'])
                    e_em = st.text_input("E-mail", dados.get('email', ''))
                    e_sn = st.text_input("Senha", dados.get('senha', ''))
                    c_sv, c_del = st.columns(2)
                    if c_sv.form_submit_button("💾 Salvar", type="primary"):
                        ok, msg = db.atualizar_dados_visitante(dados['id'], e_nm, e_em, e_sn)
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)
                    if c_del.form_submit_button("🗑️ Excluir"):
                        ok, msg = db.excluir_usuario('visitante', dados['id'])
                        if ok: st.success(msg); time.sleep(1); st.rerun()
                        else: st.error(msg)

def renderizar_aba_configuracoes():
    """Módulo MVC isolado para a configuração de Segurança e Rodapé"""
    st.subheader("🔐 Segurança e Identidade")

    tab_seg, tab_vis = st.tabs(["🔑 Credenciais Master", "🎨 Rodapé dos E-mails"])

    with tab_seg:
        st.info("Aqui você gerencia as credenciais Master da Diretoria.")
        email_atual = db.obter_email_admin()

        with st.form("form_cfg_master"):
            n_email = st.text_input("E-mail Oficial da Diretoria (Para resgate de senha):", value=email_atual)
            n_senha = st.text_input("Nova Senha Admin (Deixe em branco para não alterar):", type="password")

            if st.form_submit_button("💾 Salvar Credenciais", type="primary"):
                if "@" in n_email: db.atualizar_email_admin(n_email)
                if n_senha and len(n_senha) >= 4: db.atualizar_senha_admin(n_senha)
                st.success("Credenciais salvas!")
                time.sleep(1.5); st.rerun()

    with tab_vis:
        st.info("Configure as informações que aparecem no rodapé de todos os e-mails enviados.")
        cfg = db.obter_config_rodape()

        with st.form("form_cfg_rodape"):
            c1, c2 = st.columns(2)
            inst = c1.text_input("📸 Instagram (ex: @driblecerto)", value=cfg.get('instagram',''))
            whats = c2.text_input("💬 WhatsApp (ex: (11) 99999-9999)", value=cfg.get('whatsapp',''))

            c3, c4 = st.columns(2)
            vers = c3.text_input("🔢 Versão do Sistema", value=cfg.get('versao','v1.0.0'))
            copy = c4.text_input("© Copyright", value=cfg.get('copyright','NSG Basquete'))

            if st.form_submit_button("💾 Atualizar Rodapé Oficial", type="primary"):
                novos_dados = {"instagram": inst, "whatsapp": whats, "versao": vers, "copyright": copy}
                ok, msg = db.atualizar_config_rodape(novos_dados)
                if ok: st.success(msg); time.sleep(1.5); st.rerun()
                else: st.error(msg)

# [admin_gestao.py][Configuração de Rodapé e Credenciais][2026-02-26 10:15][v1.2][138 linhas]