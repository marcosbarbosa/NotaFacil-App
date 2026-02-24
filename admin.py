import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import database as db
import time

def exibir_sala_de_guerra():
    if st.sidebar.text_input("Senha Admin", type="password") == "admin":
        # 1. Carregamento de dados (Forçamos a atualização se houver mudança)
        atl_data, vis_data, lan_data = db.carregar_dados_globais()

        tab_fin, tab_usr = st.tabs(["📊 Auditoria Financeira", "👥 Gestão de Usuários"])

        # ==========================================================
        # ABA 1: AUDITORIA COM SELEÇÃO POR CLIQUE
        # ==========================================================
        with tab_fin:
            if not lan_data:
                st.info("Nenhum lançamento encontrado no sistema.")
            else:
                df_lan = pd.DataFrame(lan_data)
                df_lan['dt'] = pd.to_datetime(df_lan['created_at'])
                df_lan['status'] = df_lan['status'].replace({"⏳ Pendente": "❓ Pendente", "📸 Reenviar Foto": "❌ Reprovada"}).fillna("❓ Pendente")

                st.subheader("🔍 Filtros e Visão Geral")
                c1, c2, c3 = st.columns(3)
                mes_ref = c1.selectbox("Mês:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1)
                ano_ref = c2.selectbox("Ano:", [2024, 2025, 2026], index=2)
                status_f = c3.selectbox("Status Geral:", ["Todas as Notas", "❓ Pendente", "✅ Aprovada", "❌ Reprovada"])

                m_num = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes_ref) + 1
                df_f = df_lan[(df_lan['dt'].dt.month == m_num) & (df_lan['dt'].dt.year == ano_ref)]
                if status_f != "Todas as Notas": df_f = df_f[df_f['status'] == status_f]

                if df_f.empty:
                    st.warning("Nenhuma nota encontrada.")
                else:
                    st.divider()
                    st.subheader("📋 Tabela de Auditoria")
                    st.caption("💡 **Dica Prime:** Clique em uma linha para abrir a auditoria detalhada abaixo.")

                    df_view = df_f.copy()
                    df_view['ID'] = df_view['id'].astype(str).str[:6]
                    df_view['Quem'] = df_view.apply(lambda r: r.get('atletas', {}).get('nome', 'Sem Nome') if pd.notnull(r.get('atletas')) else f"Vis: {r.get('visitantes', {}).get('nome', 'Sem Nome')}", axis=1)

                    # --- SELEÇÃO INTERATIVA NA AUDITORIA ---
                    id_selecionado_clique = None
                    try:
                        ev_aud = st.dataframe(
                            df_view[['ID', 'status', 'Quem', 'valor', 'data_nota', 'foto_url']],
                            use_container_width=True, hide_index=True,
                            on_select="rerun", selection_mode="single-row",
                            column_config={"foto_url": st.column_config.ImageColumn("NF (Zoom)")}
                        )
                        if ev_aud.selection.rows:
                            id_selecionado_clique = df_view.iloc[ev_aud.selection.rows[0]]['ID']
                    except:
                        st.dataframe(df_view[['ID', 'status', 'Quem', 'valor', 'data_nota', 'foto_url']], use_container_width=True, hide_index=True)

                    st.divider()
                    # --- MESA DE OPERAÇÃO AUTOMATIZADA ---
                    with st.expander("🔍 Mesa de Operação: Validar Nota", expanded=(id_selecionado_clique is not None)):
                        lista_opcoes = ["Selecione..."] + df_view.apply(lambda r: f"{r['ID']} | {r['status']} | {r['Quem']} | R$ {r['valor']}", axis=1).tolist()

                        # Se clicou na tabela, já pré-seleciona no combo
                        idx_combo = 0
                        if id_selecionado_clique:
                            for i, opt in enumerate(lista_opcoes):
                                if opt.startswith(id_selecionado_clique):
                                    idx_combo = i; break

                        nota_sel = st.selectbox("Nota em Auditoria:", lista_opcoes, index=idx_combo)

                        if nota_sel != "Selecione...":
                            id_final = nota_sel.split(" | ")[0]
                            nota_c = df_f[df_f['id'].astype(str).str.startswith(id_final)].iloc[0]

                            d_atl = nota_c.get('atletas'); d_vis = nota_c.get('visitantes')
                            n_atl = d_atl.get('nome') if pd.notnull(d_atl) else d_vis.get('nome', 'Desconhecido')
                            e_atl = d_atl.get('email') if pd.notnull(d_atl) else d_vis.get('email', '')

                            c_img, c_btns = st.columns([1, 1])
                            with c_img: st.image(nota_c['foto_url'], use_container_width=True)
                            with c_btns:
                                st.write(f"**Status:** {nota_c['status']}")
                                if st.button("✅ Aprovar Nota", use_container_width=True):
                                    db.alterar_status_nota(nota_c['id'], nota_c['atleta_cpf'], nota_c['valor'], nota_c['status'], "✅ Aprovada", e_atl, n_atl, nota_c['data_nota'], n_atl, nota_c['foto_url'])
                                    st.success("Aprovado!"); time.sleep(1); st.rerun()
                                if st.button("❌ Reprovar", use_container_width=True, type="primary"):
                                    db.alterar_status_nota(nota_c['id'], nota_c['atleta_cpf'], nota_c['valor'], nota_c['status'], "❌ Reprovada", e_atl, n_atl, nota_c['data_nota'], n_atl, nota_c['foto_url'])
                                    st.error("Reprovado!"); time.sleep(1); st.rerun()

        # ==========================================================
        # ABA 2: GESTÃO E CADASTRO (FIX CACHE)
        # ==========================================================
        with tab_usr:
            if "lote_key" not in st.session_state: st.session_state.lote_key = 0

            with st.expander("⚡ Cadastro Rápido (Lote)", expanded=False):
                df_mod = pd.DataFrame(columns=["Nome", "CPF", "Nascimento", "Sexo", "Bolsa", "Email", "Senha"])
                df_ed = st.data_editor(df_mod, num_rows="dynamic", use_container_width=True, hide_index=True, key=f"ed_{st.session_state.lote_key}",
                    column_config={"Sexo": st.column_config.SelectboxColumn("Sexo", options=["M", "F"], required=True), "Bolsa": st.column_config.NumberColumn("Bolsa (R$)", min_value=0.0)})

                if st.button("🚀 Salvar Lote", type="primary"):
                    if not df_ed.empty:
                        for i, r in df_ed.iterrows():
                            nm = str(r.get('Nome','')).strip()
                            cp = str(r.get('CPF','')).strip()
                            if nm and cp and nm.lower() != 'nan':
                                cp_l = ''.join(filter(str.isdigit, cp))
                                db.cadastrar_novo_atleta(nm, cp_l, r.get('Nascimento') or date.today(), r.get('Sexo') or 'M', float(r.get('Bolsa') or 0.0), str(r.get('Email') or f"{cp_l}@notafacil.com"), str(r.get('Senha') or "mudar123"))

                        st.success("Salvo! Atualizando...")
                        st.session_state.lote_key += 1
                        time.sleep(1); st.rerun()

            st.divider()
            st.subheader("👥 Lista de Acessos")
            u_l = [{"Nome": a['nome'], "Tipo": "Atleta", "E-mail": a.get('email', '-'), "Ref": a} for a in atl_data] + [{"Nome": v['nome'], "Tipo": "Visitante", "E-mail": v.get('email', '-'), "Ref": v} for v in vis_data]
            df_u = pd.DataFrame(u_l).sort_values("Nome").reset_index(drop=True)

            n_sel_t = "Selecione..."
            try:
                ev_u = st.dataframe(df_u[['Nome', 'Tipo', 'E-mail']], use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
                if ev_u.selection.rows: n_sel_t = df_u.iloc[ev_u.selection.rows[0]]['Nome']
            except: st.dataframe(df_u[['Nome', 'Tipo', 'E-mail']], use_container_width=True, hide_index=True)

            with st.expander("🛠️ Editar Acesso", expanded=(n_sel_t != "Selecione...")):
                ops = ["Selecione..."] + df_u['Nome'].tolist()
                u_s = st.selectbox("Usuário:", ops, index=ops.index(n_sel_t) if n_sel_t in ops else 0)
                if u_s != "Selecione...":
                    obj = next(u for u in u_l if u['Nome'] == u_s)
                    t_r = "atleta" if obj['Tipo'] == "Atleta" else "visitante"
                    c_id = obj['Ref'].get('cpf') if t_r == "atleta" else obj['Ref'].get('id')
                    n_em = st.text_input("E-mail:", value=obj['Ref'].get('email', ''))
                    n_se = st.text_input("Nova Senha:", placeholder="Opcional")
                    if st.button("💾 Salvar Alterações", type="primary"):
                        db.atualizar_usuario(t_r, c_id, n_em, n_se if n_se else None)
                        st.success("OK!"); time.sleep(1); st.rerun()

    else: st.info("Acesso Administrativo Restrito.")

# [admin.py][Auditoria e Gestão Sincronizadas por Clique][2026-02-24 19:40][v4.2][135 linhas]