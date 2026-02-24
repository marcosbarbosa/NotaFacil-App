# ==============================================================================
# SISTEMA: NotaFácil Prime | ARQUIVO: main.py
# DATA: 19/02/2026 | HORA: 14:15 | TÍTULO: Interface Prime v17.0
# FUNÇÃO: Lançamentos e Navegação para Sala de Guerra
# VERSÃO: 17.0 | LINHAS: 130
# ==============================================================================
import streamlit as st
from datetime import date
import time
import database as db, styles as ui, admin as adm

ui.aplicar_design()
if "tela" not in st.session_state: st.session_state.tela = "lancamento"
if "res_data" not in st.session_state: st.session_state.res_data = {}

st.sidebar.image(ui.LOGO_URL, use_container_width=True)
menu = st.sidebar.radio("Navegação", ["🏃 Lançamento", "🛡️ Sala de Guerra"])

if menu == "🏃 Lançamento":
    if st.session_state.tela == "resumo":
        res = st.session_state.res_data
        st.markdown("<div class='success-box'>", unsafe_allow_html=True)
        st.subheader("✅ Lançamento Realizado!")
        st.write(f"**Atleta:** 🏃 {res['atleta_nome']} | **Categoria:** {res['atleta_tag']}")
        c1, c2 = st.columns(2)
        c1.metric("Valor NF", f"R$ {res['valor']:,.2f}")
        c2.metric("Saldo Meta Atual", db.formatar_saldo_mask(res['saldo'], True))
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🔄 NOVO LANÇAMENTO", use_container_width=True): st.session_state.tela = "lancamento"; st.rerun()
    else:
        st.title("Lançamento de Nota Fiscal")
        atl_raw, vis_raw, _ = db.carregar_dados_globais()
        lista = ["Selecione..."] + [f"🏃 {a['nome']}" for a in atl_raw] + [f"👤 {v['nome']} (Visitante)" for v in vis_raw] + ["➕ Novo Visitante"]
        escolha = st.selectbox("Quem está lançando?", lista)
        if escolha != "Selecione...":
            with st.form("form_v17", clear_on_submit=True):
                eh_atl = "🏃" in escolha
                n_limpo = escolha.replace("🏃 ", "").replace("👤 ", "").split(" (")[0]
                atl_obj = next((a for a in atl_raw if a['nome'] == n_limpo), None)
                v_id, cpf_b = None, None
                if not eh_atl or "Novo" in escolha:
                    if "Novo" in escolha: em = st.text_input("E-mail"); nm = st.text_input("Nome"); wh = st.text_input("WhatsApp")
                    else: v_id = next(v['id'] for v in vis_raw if v['nome'] == n_limpo)
                    dest = st.selectbox("Para qual Atleta?", [a['nome'] for a in atl_raw])
                    atl_obj = next(a for a in atl_raw if a['nome'] == dest); cpf_b = atl_obj['cpf']
                else: cpf_b = atl_obj['cpf']
                st.info(f"Saldo Meta: {db.formatar_saldo_mask(float(atl_obj['saldo']), eh_atl)}")
                val = st.number_input("Valor da Nota (R$)", min_value=0.01)
                ft = st.file_uploader("📸 Comprovante", type=['jpg', 'png', 'pdf', 'jpeg'])
                if st.form_submit_button("🚀 FINALIZAR"):
                    if not ft: st.warning("Anexe a foto!")
                    else:
                        if "Novo" in escolha: v_id = db.upsert_visitante({"nome": nm, "email": em, "whatsapp": wh})
                        db.salvar_nota_fiscal(val, date.today(), ft, cpf=cpf_b, v_id=v_id)
                        atl_res = next(a for a in db.carregar_dados_globais()[0] if a['cpf'] == cpf_b)
                        tag = db.calcular_tag_3x3(atl_res['sexo'], atl_res['data_nascimento'])
                        st.session_state.res_data = {"valor": val, "saldo": atl_res['saldo'], "atleta_nome": atl_res['nome'], "atleta_tag": tag}
                        st.session_state.tela = "resumo"; st.rerun()

elif menu == "🛡️ Sala de Guerra":
    st.title("🛡️ Sala de Guerra")
    adm.exibir_sala_de_guerra()

# Quantidade total de linhas: 130