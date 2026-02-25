import streamlit as st
import pandas as pd
from datetime import date
import database as db
import funcoes_admin as f_adm
import time

def exibir_sala_de_guerra():
    if st.sidebar.text_input("Senha Admin", type="password") == "admin":
        atl_data, vis_data, lan_data = db.carregar_dados_globais()
        tab_fin, tab_usr = st.tabs(["📊 Auditoria Financeira", "👥 Gestão de Usuários"])

        # --- ABA 1: AUDITORIA ---
        with tab_fin:
            c1, c2, c3 = st.columns(3)
            mes = c1.selectbox("Mês:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"], index=date.today().month-1)
            ano = c2.selectbox("Ano:", [2024, 2025, 2026], index=2)
            st_f = c3.selectbox("Status:", ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"])

            m_idx = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes) + 1
            df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

            if df_f.empty: st.warning("Nada para auditar.")
            else:
                id_sel = None
                ev = st.dataframe(df_f[['Status_UI', 'Atleta (Bolsa)', 'Lançado por', 'valor', 'data_nota', 'foto_url']], 
                                  column_config={"foto_url": st.column_config.ImageColumn("NF"), "valor": st.column_config.NumberColumn("R$", format="%.2f")},
                                  use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
                if ev.selection.rows: id_sel = df_f.iloc[ev.selection.rows[0]]['id']

                st.divider()
                with st.expander("🔍 Auditoria Detalhada", expanded=(id_sel is not None)):
                    if id_sel:
                        nota = df_f[df_f['id'] == id_sel].iloc[0]
                        f_adm.exibir_origem_com_saldo(nota['Atleta (Bolsa)'], nota['Lançado por'], nota['Saldo_Atleta'])

                        if nota['orfao']:
                            st.warning("🚨 REGISTRO SEM BENEFICIÁRIO: Selecione um atleta para vincular:")
                            atl_opcoes = {f"{a['nome']} (Saldo: R$ {a['saldo']:.2f})": a['cpf'] for a in atl_data}
                            escolha = st.selectbox("Vincular a:", ["Selecione..."] + list(atl_opcoes.keys()))
                            if st.button("🔗 Confirmar Vínculo e Abater Saldo", use_container_width=True):
                                if escolha != "Selecione...":
                                    ok, msg = db.vincular_atleta_a_nota(nota['id'], atl_opcoes[escolha], nota['valor'])
                                    if ok: st.success(msg); time.sleep(1.2); st.rerun()
                                    else: st.error(msg)

                        c_img, c_btn = st.columns([1, 1])
                        c_img.image(nota['foto_url'], use_container_width=True)
                        with c_btn:
                            st.write(f"**Valor NF:** R$ {nota['valor']:.2f}")
                            if st.button("✅ Aprovar", use_container_width=True):
                                db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'], "✅ Aprovada"); st.rerun()
                            if st.button("❌ Reprovar", use_container_width=True, type="primary"):
                                db.alterar_status_nota(nota['id'], nota['atleta_cpf'], nota['valor'], nota['Status_UI'], "❌ Reprovada"); st.rerun()

        # --- ABA 2: GESTÃO & BI ---
        with tab_usr:
            # Gráfico de BI
            grafico = f_adm.gerar_grafico_consumo(atl_data)
            if grafico: st.plotly_chart(grafico, use_container_width=True)
            st.divider()

            if "lote_key" not in st.session_state: st.session_state.lote_key = 0
            st.subheader("👥 Lista de Acessos")
            u_l = [{"Nome": a['nome'], "Tipo": "🏃 Atleta", "Saldo": a['saldo'], "Email": a.get('email', '-')} for a in atl_data] + [{"Nome": v['nome'], "Tipo": "👤 Visitante", "Saldo": "-", "Email": v.get('email', '-')} for v in vis_data]
            st.dataframe(pd.DataFrame(u_l).sort_values("Nome"), use_container_width=True, hide_index=True)

            st.divider()
            with st.expander("⚡ Cadastro Rápido de Atletas", expanded=False):
                # O calendário nativo agora força o formato e blinda datas vazias
                df_mod = pd.DataFrame(columns=["Nome","CPF","Nascimento","Sexo","Bolsa","Email","Senha"])
                df_ed = st.data_editor(df_mod, num_rows="dynamic", use_container_width=True, key=f"ed_{st.session_state.lote_key}",
                                      column_config={
                                          "Sexo": st.column_config.SelectboxColumn("Sexo", options=["M", "F"], required=True),
                                          "Nascimento": st.column_config.DateColumn("Nascimento", format="DD/MM/YYYY"),
                                          "Senha": st.column_config.TextColumn("Senha Inicial")
                                      })
                if st.button("🚀 Salvar Novos Registros", type="primary"):
                    if not df_ed.empty:
                        sucessos, erros = 0, []
                        for _, r in df_ed.iterrows():
                            nm, cp = r.get('Nome'), r.get('CPF')
                            if pd.notnull(nm) and pd.notnull(cp) and str(nm).strip() != '':
                                cpf_str = ''.join(filter(str.isdigit, str(cp)))

                                # Tratamento blindado para calendário vazio
                                nasc = r.get('Nascimento')
                                if pd.isnull(nasc): nasc_str = str(date.today())
                                else: nasc_str = nasc.strftime('%Y-%m-%d') if hasattr(nasc, 'strftime') else str(nasc)[:10]

                                b_val = float(r.get('Bolsa')) if pd.notnull(r.get('Bolsa')) else 0.0
                                e_val = str(r.get('Email')) if pd.notnull(r.get('Email')) else f"{cpf_str}@notafacil.com"
                                s_val = str(r.get('Senha')) if pd.notnull(r.get('Senha')) else "mudar123"
                                sex_val = str(r.get('Sexo')) if pd.notnull(r.get('Sexo')) else "M"

                                ok, msg = db.cadastrar_novo_atleta(nm, cpf_str, nasc_str, sex_val, b_val, e_val, s_val)
                                if ok: sucessos += 1
                                else: erros.append(f"{nm}: {msg}")

                        if sucessos > 0:
                            st.success(f"✅ {sucessos} atleta(s) cadastrados com sucesso!")
                            st.session_state.lote_key += 1
                            time.sleep(1.2); st.rerun()
                        for err in erros: st.error(err)
    else: st.info("Restrito.")

# [admin.py][Gráfico BI, Máscara de Calendário e Blindagem de Insert][2026-02-24 21:35][v6.4][135 linhas]