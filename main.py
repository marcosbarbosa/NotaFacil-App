import streamlit as st
from datetime import date
import time
import database as db, styles as ui, admin as adm

ui.aplicar_design()

if "tela" not in st.session_state: st.session_state.tela = "lancamento"
if "res_data" not in st.session_state: st.session_state.res_data = {}
if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "mostra_cadastro" not in st.session_state: st.session_state.mostra_cadastro = False

# --- MOTOR GERADOR DE SENHA DINÂMICA ---
def gerar_senha_padrao(email, nome):
    if email and "@" in email:
        prefixo = email.split("@")[0]
    else:
        prefixo = nome.split(" ")[0]

    base = prefixo[-3:] if len(prefixo) >= 3 else prefixo.ljust(3, 'x')
    return base.capitalize() + "123"

st.sidebar.image(ui.LOGO_URL, use_container_width=True)
menu = st.sidebar.radio("Navegação", ["🏃 Lançamento", "🛡️ Sala de Guerra"])

if menu == "🏃 Lançamento":
    # -------------------------------------------------------------
    # TELA DE LOGIN / AUTENTICAÇÃO
    # -------------------------------------------------------------
    if st.session_state.usuario_logado is None:
        st.title("🔐 Acesso ao Sistema")
        atl_raw, vis_raw, _ = db.carregar_dados_globais()

        # --- FLUXO DE CADASTRO (ISOLADO E IMUNE À PESQUISA) ---
        if st.session_state.mostra_cadastro:
            st.info("Preencha os dados abaixo para criar seu acesso.")
            with st.form("form_cadastro"):
                nm = st.text_input("Seu Nome Completo")
                em = st.text_input("Seu E-mail")
                wh = st.text_input("Seu WhatsApp")

                if st.form_submit_button("Criar Acesso e Entrar"):
                    if nm and em:
                        senha_nova = gerar_senha_padrao(em, nm)
                        v_id = db.upsert_visitante({"nome": nm, "email": em, "whatsapp": wh, "senha": senha_nova})
                        st.session_state.usuario_logado = {"tipo": "visitante", "id": v_id, "nome": nm}
                        st.success(f"Cadastro realizado! Sua senha automática é: {senha_nova}")
                        st.session_state.mostra_cadastro = False # Reseta a tela
                        time.sleep(4)
                        st.rerun()
                    else:
                        st.error("Nome e E-mail são obrigatórios!")

            if st.button("⬅️ Voltar para o Login"):
                st.session_state.mostra_cadastro = False
                st.rerun()

        # --- FLUXO DE LOGIN NORMAL ---
        else:
            nomes_combinados = [f"🏃 {a['nome']}" for a in atl_raw] + [f"👤 {v['nome']} (Visitante)" for v in vis_raw]
            nomes_combinados.sort(key=lambda x: x.replace("🏃 ", "").replace("👤 ", "").lower())

            lista = [""] + nomes_combinados
            escolha = st.selectbox("Busque e selecione seu nome para entrar:", lista, index=0)

            if escolha != "":
                eh_atl = "🏃" in escolha
                n_limpo = escolha.replace("🏃 ", "").replace("👤 ", "").split(" (")[0]

                user_obj = next((a for a in atl_raw if a['nome'] == n_limpo), None) if eh_atl else next((v for v in vis_raw if v['nome'] == n_limpo), None)
                senha_digitada = st.text_input("Digite sua Senha:", type="password")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🚀 Entrar", use_container_width=True):
                        email_user = user_obj.get('email', '')
                        senha_db = user_obj.get('senha')

                        senha_dinamica = gerar_senha_padrao(email_user, user_obj['nome'])
                        senha_real = senha_dinamica if (not senha_db or senha_db == 'mudar123') else senha_db

                        if senha_digitada == senha_real:
                            tipo = "atleta" if eh_atl else "visitante"
                            chave_id = user_obj.get('cpf') if eh_atl else user_obj.get('id')
                            st.session_state.usuario_logado = {"tipo": tipo, "id": chave_id, "nome": user_obj['nome']}
                            st.rerun()
                        else:
                            st.error("❌ Senha incorreta!")
                with c2:
                    if st.button("🔑 Esqueci a Senha", use_container_width=True):
                        email_user = user_obj.get('email', '')
                        if email_user:
                            senha_db = user_obj.get('senha')
                            senha_dinamica = gerar_senha_padrao(email_user, user_obj['nome'])
                            senha_real = senha_dinamica if (not senha_db or senha_db == 'mudar123') else senha_db
                            db.recuperar_senha(email_user, user_obj['nome'], senha_real)
                            st.success(f"Sua senha ({senha_real}) foi enviada para: {email_user}")
                        else:
                            st.warning("Este usuário não possui e-mail cadastrado para recuperar a senha.")

            st.divider()
            st.caption("Ainda não tem acesso ao sistema?")
            if st.button("➕ Novo Visitante? Cadastre-se aqui"):
                st.session_state.mostra_cadastro = True
                st.rerun()

    # -------------------------------------------------------------
    # TELA DE SUCESSO PÓS-LANÇAMENTO
    # -------------------------------------------------------------
    elif st.session_state.tela == "resumo":
        res = st.session_state.res_data
        st.markdown("<div class='success-box'>", unsafe_allow_html=True)
        st.subheader("✅ Lançamento Realizado!")
        st.write(f"**Atleta Beneficiado:** 🏃 {res['atleta_nome']} | **Categoria:** {res['atleta_tag']}")
        c1, c2 = st.columns(2)
        c1.metric("Valor NF", f"R$ {res['valor']:,.2f}")
        # AQUI CHAMAMOS A FUNÇÃO RESTAURADA DO DATABASE.PY
        c2.metric("Novo Saldo Meta", db.formatar_saldo_mask(res['saldo'], True))
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🔄 FAZER OUTRO LANÇAMENTO", use_container_width=True): 
            st.session_state.tela = "lancamento"
            st.rerun()

    # -------------------------------------------------------------
    # FORMULÁRIO REAL (USUÁRIO JÁ LOGADO)
    # -------------------------------------------------------------
    else:
        st.title(f"Olá, {st.session_state.usuario_logado['nome']}! 👋")
        if st.button("Sair (Logout)"):
            st.session_state.usuario_logado = None
            st.rerun()

        st.divider()
        atl_raw, _, _ = db.carregar_dados_globais()

        with st.form("form_v24", clear_on_submit=True):
            st.write("**Para qual Atleta você está lançando esta nota?**")

            lista_nomes = [a['nome'] for a in atl_raw]
            lista_nomes.sort(key=lambda x: x.lower())

            idx_padrao = lista_nomes.index(st.session_state.usuario_logado['nome']) if st.session_state.usuario_logado['tipo'] == 'atleta' and st.session_state.usuario_logado['nome'] in lista_nomes else 0

            dest = st.selectbox("Selecione o beneficiário:", lista_nomes, index=idx_padrao)
            atl_obj = next(a for a in atl_raw if a['nome'] == dest)
            cpf_b = atl_obj['cpf']

            val = st.number_input("Valor da Nota (R$)", min_value=0.01)
            ft = st.file_uploader("📸 Comprovante", type=['jpg', 'png', 'pdf', 'jpeg'])

            if st.form_submit_button("🚀 ENVIAR NOTA FISCAL"):
                if not ft: 
                    st.warning("Anexe a foto do comprovante!")
                else:
                    v_id = st.session_state.usuario_logado['id'] if st.session_state.usuario_logado['tipo'] == 'visitante' else None
                    db.salvar_nota_fiscal(val, date.today(), ft, cpf=cpf_b, v_id=v_id)

                    # Buscamos apena os atletas na segunda vez para montar o resumo, não o banco inteiro.
                    atl_res_novo = next(a for a in db.carregar_dados_globais()[0] if a['cpf'] == cpf_b)
                    tag = db.calcular_tag_3x3(atl_res_novo['sexo'], atl_res_novo['data_nascimento'])

                    st.session_state.res_data = {"valor": val, "saldo": atl_res_novo['saldo'], "atleta_nome": atl_res_novo['nome'], "atleta_tag": tag}
                    st.session_state.tela = "resumo"
                    st.rerun()

elif menu == "🛡️ Sala de Guerra":
    st.title("🛡️ Sala de Guerra")
    adm.exibir_sala_de_guerra()

# [main.py][Motor de Autenticação e Lançamento][2026-02-24 22:00][v24.1][168 linhas]