import streamlit as st
from datetime import date
import time
import database as db
import servicos_email as email_svc

# --- HELPERS (Regras de Negócio) ---
def _gerar_senha_padrao(email, nome):
    """Gera a senha padrão do usuário baseada no e-mail ou nome"""
    if email and "@" in email:
        prefixo = email.split("@")[0]
    else:
        prefixo = nome.split(" ")[0]

    # Preenche com 'x' se o prefixo for menor que 3 letras
    base = prefixo[-3:] if len(prefixo) >= 3 else prefixo.ljust(3, 'x')
    return base.capitalize() + "123"

# --- MÓDULOS DE TELA (Views) ---
def _exibir_tela_login(atl_raw, vis_raw):
    """Renderiza a tela de autenticação e registro"""
    st.title("🔐 Acesso ao Sistema")

    # 1. Fluxo de Cadastro de Visitante
    if st.session_state.get('mostra_cadastro', False):
        st.info("Preencha os dados abaixo para criar seu acesso.")
        with st.form("form_cadastro"):
            nm = st.text_input("Seu Nome Completo")
            em = st.text_input("Seu E-mail")
            wh = st.text_input("Seu WhatsApp")

            submit = st.form_submit_button("Criar Acesso e Entrar", use_container_width=True)

            if submit:
                if nm and em:
                    senha_nova = _gerar_senha_padrao(em, nm)
                    v_id = db.upsert_visitante({"nome": nm, "email": em, "whatsapp": wh, "senha": senha_nova})
                    st.session_state.usuario_logado = {"tipo": "visitante", "id": v_id, "nome": nm}
                    st.success(f"Cadastro realizado! Sua senha automática é: {senha_nova}")
                    st.session_state.mostra_cadastro = False
                    time.sleep(4)
                    st.rerun()
                else:
                    st.error("Nome e E-mail são obrigatórios!")

        if st.button("⬅️ Voltar para o Login", use_container_width=True):
            st.session_state.mostra_cadastro = False
            st.rerun()

    # 2. Fluxo de Login Tradicional
    else:
        nomes_combinados = [f"🏃 {a['nome']}" for a in atl_raw] + [f"👤 {v['nome']} (Visitante)" for v in vis_raw]
        nomes_combinados.sort(key=lambda x: x.replace("🏃 ", "").replace("👤 ", "").lower())

        lista = [""] + nomes_combinados
        escolha = st.selectbox("Busque e selecione seu nome para entrar:", lista, index=0)

        if escolha != "":
            eh_atl = "🏃" in escolha
            n_limpo = escolha.replace("🏃 ", "").replace("👤 ", "").split(" (")[0]

            # Localiza o usuário selecionado nas listas em memória
            user_obj = next((a for a in atl_raw if a['nome'] == n_limpo), None) if eh_atl else next((v for v in vis_raw if v['nome'] == n_limpo), None)

            if user_obj:
                senha_digitada = st.text_input("Digite sua Senha:", type="password")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🚀 Entrar", use_container_width=True):
                        email_user = user_obj.get('email', '')
                        senha_db = user_obj.get('senha')
                        senha_dinamica = _gerar_senha_padrao(email_user, user_obj['nome'])
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
                            senha_dinamica = _gerar_senha_padrao(email_user, user_obj['nome'])
                            senha_real = senha_dinamica if (not senha_db or senha_db == 'mudar123') else senha_db

                            with st.spinner("Conectando ao servidor de e-mail..."):
                                sucesso, msg_retorno = email_svc.recuperar_senha_usuario(email_user, user_obj['nome'], senha_real)

                            if sucesso:
                                st.success(f"Sua senha foi enviada para: {email_user}")
                            else:
                                st.error(f"Falha ao enviar: {msg_retorno}")
                        else:
                            st.warning("Este usuário não possui e-mail cadastrado.")

        st.divider()
        st.caption("Ainda não tem acesso ao sistema?")
        if st.button("➕ Novo Visitante? Cadastre-se aqui"):
            st.session_state.mostra_cadastro = True
            st.rerun()

def _exibir_tela_sucesso():
    """Renderiza o comprovante de sucesso após o envio da nota"""
    res = st.session_state.res_data
    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
    st.subheader("✅ Lançamento Realizado!")
    st.write(f"**Atleta Beneficiado:** 🏃 {res['atleta_nome']} | **Categoria:** {res['atleta_tag']}")
    c1, c2 = st.columns(2)
    c1.metric("Valor NF", f"R$ {res['valor']:,.2f}")
    c2.metric("Novo Saldo Meta", db.formatar_saldo_mask(res['saldo'], True))
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 FAZER OUTRO LANÇAMENTO", use_container_width=True): 
        st.session_state.tela = "lancamento"
        st.rerun()

def _exibir_tela_formulario(atl_raw):
    """Renderiza o formulário principal de envio de NFs para usuários logados"""
    st.title(f"Olá, {st.session_state.usuario_logado['nome']}! 👋")
    if st.button("Sair (Logout)"):
        st.session_state.usuario_logado = None
        st.rerun()

    st.divider()

    with st.form("form_v24", clear_on_submit=True):
        st.write("**Para qual Atleta você está lançando esta nota?**")
        lista_nomes = [a['nome'] for a in atl_raw]
        lista_nomes.sort(key=lambda x: x.lower())

        # Define quem aparece pré-selecionado no combobox
        usuario_atual = st.session_state.usuario_logado['nome']
        idx_padrao = lista_nomes.index(usuario_atual) if st.session_state.usuario_logado['tipo'] == 'atleta' and usuario_atual in lista_nomes else 0

        dest = st.selectbox("Selecione o beneficiário:", lista_nomes, index=idx_padrao)
        atl_obj = next(a for a in atl_raw if a['nome'] == dest)
        cpf_b = atl_obj['cpf']

        val = st.number_input("Valor da Nota (R$)", min_value=0.01)
        ft = st.file_uploader("📸 Comprovante", type=['jpg', 'png', 'pdf', 'jpeg'])

        submit_nf = st.form_submit_button("🚀 ENVIAR NOTA FISCAL", use_container_width=True)

        if submit_nf:
            if not ft: 
                st.warning("Anexe a foto do comprovante!")
            else:
                v_id = st.session_state.usuario_logado['id'] if st.session_state.usuario_logado['tipo'] == 'visitante' else None
                # Salva a nota no Supabase
                db.salvar_nota_fiscal(val, date.today(), ft, cpf=cpf_b, v_id=v_id)

                # Busca o novo saldo do atleta para mostrar no recibo
                dados_atualizados, _, _ = db.carregar_dados_globais()
                atl_res_novo = next((a for a in dados_atualizados if a['cpf'] == cpf_b), None)

                if atl_res_novo:
                    tag = db.calcular_tag_3x3(atl_res_novo['sexo'], atl_res_novo['data_nascimento'])
                    st.session_state.res_data = {"valor": val, "saldo": atl_res_novo['saldo'], "atleta_nome": atl_res_novo['nome'], "atleta_tag": tag}
                    st.session_state.tela = "resumo"
                    st.rerun()

# --- CONTROLADOR PRINCIPAL DO MÓDULO ---
def renderizar_portal():
    """Roteador interno: Decide qual tela do portal mostrar baseado no State"""
    if st.session_state.get('usuario_logado') is None:
        atl_raw, vis_raw, _ = db.carregar_dados_globais()
        _exibir_tela_login(atl_raw, vis_raw)
    elif st.session_state.get('tela') == "resumo":
        _exibir_tela_sucesso()
    else:
        atl_raw, _, _ = db.carregar_dados_globais()
        _exibir_tela_formulario(atl_raw)

# [portal_lancamento.py][Edição Marvel Prime c/ Recálculo de Saldo][2026-02-26]