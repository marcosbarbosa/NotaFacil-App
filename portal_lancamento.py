import streamlit as st
from datetime import date
import time
import database as db
import servicos_email as email_svc

# --- HELPERS (Regras de Negócio) ---
def _gerar_senha_padrao(email, nome):
    """Gera a senha padrão com blindagem absoluta de tipos (String Fix)"""
    if email and "@" in str(email):
        prefixo = str(email).strip().split("@")
    else:
        prefixo = str(nome).strip().split(" ")

    prefixo_str = str(prefixo)
    base = prefixo_str[-3:] if len(prefixo_str) >= 3 else prefixo_str.ljust(3, 'x')
    return base.capitalize() + "123"

# --- MÓDULOS DE TELA (Views) ---
def _exibir_tela_login(atl_raw, vis_raw):
    """Renderiza a tela de autenticação e registro blindada"""
    st.title("🔐 Acesso ao Sistema")

    if st.session_state.get('mostra_cadastro', False):
        st.info("Preencha os dados abaixo para criar seu acesso.")
        with st.form("form_cadastro"):
            nm = st.text_input("Seu Nome Completo*")
            em = st.text_input("Seu E-mail*")
            wh = st.text_input("Seu WhatsApp (DDD + Número)*", placeholder="(11) 99999-9999")
            submit = st.form_submit_button("Criar Acesso e Entrar", use_container_width=True)

            if submit:
                if nm.strip() and "@" in em:
                    senha_nova = _gerar_senha_padrao(em, nm)
                    v_id = db.upsert_visitante({"nome": nm.strip(), "email": em.strip(), "whatsapp": wh.strip(), "senha": senha_nova, "role": "viewer"})
                    st.session_state.usuario_logado = {"tipo": "visitante", "id": v_id, "nome": nm.strip()}
                    st.success(f"Cadastro realizado! Sua senha automática é: {senha_nova}")
                    st.session_state.mostra_cadastro = False
                    time.sleep(4)
                    st.rerun()
                else:
                    st.error("⚠️ Nome e um E-mail válido (com @) são obrigatórios!")

        if st.button("⬅️ Voltar para o Login", use_container_width=True):
            st.session_state.mostra_cadastro = False
            st.rerun()

    else:
        # 🛡️ MOTOR DE MAPEAMENTO PRIME
        mapa_usuarios = {}
        for a in atl_raw:
            label = f"🏃 {a['nome'].strip()}"
            mapa_usuarios[label] = {"obj": a, "tipo": "atleta"}

        for v in vis_raw:
            label = f"👤 {v['nome'].strip()} (Visitante)"
            mapa_usuarios[label] = {"obj": v, "tipo": "visitante"}

        labels_ordenados = sorted(list(mapa_usuarios.keys()))
        lista = [""] + labels_ordenados
        escolha = st.selectbox("Busque e selecione seu nome para entrar:", lista, index=0)

        if escolha != "":
            user_info = mapa_usuarios.get(escolha)
            if user_info:
                user_obj = user_info["obj"]
                eh_atl = user_info["tipo"] == "atleta"

                senha_digitada = st.text_input("Digite sua Senha:", type="password")

                # 🛠️ CORREÇÃO DEFINITIVA (Linha 72): Adicionado spec
                c1, c2 = st.columns() 

                with c1:
                    if st.button("🚀 Entrar", use_container_width=True):
                        email_user = user_obj.get('email', '')
                        senha_db = user_obj.get('senha')
                        senha_dinamica = _gerar_senha_padrao(email_user, user_obj['nome'])
                        senha_real = senha_dinamica if (not senha_db or senha_db == 'mudar123') else senha_db

                        if str(senha_digitada).strip() == str(senha_real).strip():
                            tipo = "atleta" if eh_atl else "visitante"
                            chave_id = user_obj.get('cpf') if eh_atl else user_obj.get('id')
                            st.session_state.usuario_logado = {"tipo": tipo, "id": chave_id, "nome": user_obj['nome']}
                            st.rerun()
                        else:
                            st.error("❌ Senha incorreta!")
                with c2:
                    if st.button("🔑 Esqueci a Senha", use_container_width=True):
                        email_user = user_obj.get('email', '')
                        if email_user and "@" in email_user:
                            senha_db = user_obj.get('senha')
                            senha_real = _gerar_senha_padrao(email_user, user_obj['nome']) if (not senha_db or senha_db == 'mudar123') else senha_db
                            with st.spinner("Conectando ao servidor..."):
                                sucesso, msg = email_svc.recuperar_senha_usuario(email_user, user_obj['nome'], senha_real)
                            if sucesso: st.success(f"Senha enviada para: {email_user}")
                            else: st.error(f"Falha ao enviar: {msg}")
                        else: st.warning("⚠️ Usuário sem e-mail cadastrado ou inválido.")

        st.divider()
        if st.button("➕ Novo Visitante? Cadastre-se aqui"):
            st.session_state.mostra_cadastro = True
            st.rerun()

def _exibir_tela_sucesso():
    """Renderiza o comprovante de sucesso com spec fix"""
    res = st.session_state.res_data
    st.success("### ✅ Lançamento Registrado no Banco!")
    with st.container(border=True):
        st.write(f"**Atleta Beneficiado:** 🏃 {res['atleta_nome']}")
        st.write(f"**Status de BI:** {res['atleta_tag']}")

        # 🛠️ BLINDAGEM: Adicionado
        c1, c2 = st.columns() 
        c1.metric("Valor desta NF", f"R$ {res['valor']:,.2f}")
        c2.metric("Saldo Atualizado", f"R$ {res['saldo']:,.2f}")

    if st.button("🔄 FAZER OUTRO LANÇAMENTO", use_container_width=True, type="primary"): 
        st.session_state.tela = "lancamento"
        st.rerun()

def _exibir_tela_formulario(atl_raw):
    """Formulário de lançamento com spec fix"""
    # 🛠️ BLINDAGEM: Adicionado para o header
    c_titulo, c_logout = st.columns()
    with c_titulo:
        st.title(f"Olá, {st.session_state.usuario_logado['nome']}! 👋")
    with c_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sair (Logout)", type="secondary", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()

    st.divider()
    with st.form("form_portal_prime", clear_on_submit=True):
        st.markdown("#### Detalhes do Lançamento")
        lista_nomes = sorted([a['nome'] for a in atl_raw], key=str.lower)
        usuario_atual = st.session_state.usuario_logado['nome']
        idx_padrao = lista_nomes.index(usuario_atual) if st.session_state.usuario_logado['tipo'] == 'atleta' and usuario_atual in lista_nomes else 0
        dest = st.selectbox("Para qual Atleta você está lançando?", lista_nomes, index=idx_padrao)
        dt_recibo = st.date_input("Data do Recibo/Nota:", format="DD/MM/YYYY")
        val = st.number_input("Valor da Nota (R$)", min_value=0.00, step=10.0, format="%.2f")
        ft = st.file_uploader("📸 Anexar Comprovante", type=['jpg', 'png', 'pdf', 'jpeg'])
        submit_nf = st.form_submit_button("🚀 ENVIAR PARA AUDITORIA", use_container_width=True)

        if submit_nf:
            if not ft: st.warning("⚠️ Você precisa anexar o comprovante!")
            elif val <= 0: st.warning("⚠️ O valor da nota deve ser maior que zero!")
            else:
                with st.spinner("Gravando no Banco de Dados..."):
                    atl_obj = next(a for a in atl_raw if a['nome'] == dest)
                    v_id = st.session_state.usuario_logado['id'] if st.session_state.usuario_logado['tipo'] == 'visitante' else None
                    operador_nome = st.session_state.usuario_logado['nome']
                    ok, msg = db.salvar_nota_fiscal(valor=val, data=dt_recibo, arquivo=ft, cpf=atl_obj['cpf'], v_id=v_id, operador_nome=operador_nome)
                    if ok:
                        dados_up, _, _ = db.carregar_dados_globais()
                        atl_up = next((a for a in dados_up if a['cpf'] == atl_obj['cpf']), None)
                        if atl_up:
                            tag = db.calcular_tag_3x3(atl_up['saldo'], atl_up['bolsa'])
                            st.session_state.res_data = {"valor": val, "saldo": atl_up['saldo'], "atleta_nome": atl_up['nome'], "atleta_tag": tag}
                            st.session_state.tela = "resumo"
                            st.rerun()
                    else: st.error(f"🚨 Fato impeditivo no Banco de Dados: {msg}")

def renderizar_portal():
    if st.session_state.get('usuario_logado') is None:
        atl_raw, vis_raw, _ = db.carregar_dados_globais()
        _exibir_tela_login(atl_raw, vis_raw)
    elif st.session_state.get('tela') == "resumo":
        _exibir_tela_sucesso()
    else:
        atl_raw, _, _ = db.carregar_dados_globais()
        _exibir_tela_formulario(atl_raw)

# [portal_lancamento.py][v18.8 - Fix absoluto de spec][2026-02-27]