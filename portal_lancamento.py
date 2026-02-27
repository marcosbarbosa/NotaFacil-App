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
    base = prefixo[-3:] if len(prefixo) >= 3 else prefixo.ljust(3, 'x')
    return base.capitalize() + "123"

# --- MÓDULOS DE TELA (Views) ---
def _exibir_tela_login(atl_raw, vis_raw):
    """Renderiza a tela de autenticação e registro"""
    st.title("🔐 Acesso ao Sistema")

    if st.session_state.get('mostra_cadastro', False):
        st.info("Preencha os dados abaixo para criar seu acesso.")
        with st.form("form_cadastro"):
            nm = st.text_input("Seu Nome Completo*")
            em = st.text_input("Seu E-mail*")

            # 📞 MÁSCARA ORIENTADA: Placeholder para o WhatsApp
            wh = st.text_input(
                "Seu WhatsApp (DDD + Número)*", 
                placeholder="(11) 99999-9999", 
                help="Insira o DDD entre parênteses seguido do número."
            )

            submit = st.form_submit_button("Criar Acesso e Entrar", use_container_width=True)

            if submit:
                if nm and em:
                    senha_nova = _gerar_senha_padrao(em, nm)
                    # Resolve o erro de upsert_visitante
                    v_id = db.upsert_visitante({"nome": nm, "email": em, "whatsapp": wh, "senha": senha_nova, "role": "viewer"})
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

    else:
        nomes_combinados = [f"🏃 {a['nome']}" for a in atl_raw] + [f"👤 {v['nome']} (Visitante)" for v in vis_raw]
        nomes_combinados.sort(key=lambda x: x.replace("🏃 ", "").replace("👤 ", "").lower())

        lista = [""] + nomes_combinados
        escolha = st.selectbox("Busque e selecione seu nome para entrar:", lista, index=0)

        if escolha != "":
            eh_atl = "🏃" in escolha
            n_limpo = escolha.replace("🏃 ", "").replace("👤 ", "").split(" (")[0]
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
                            with st.spinner("Conectando ao servidor..."):
                                sucesso, msg = email_svc.recuperar_senha_usuario(email_user, user_obj['nome'], senha_real)
                            if sucesso: st.success(f"Senha enviada para: {email_user}")
                            else: st.error(f"Falha ao enviar: {msg}")
                        else: st.warning("Usuário sem e-mail cadastrado.")

        st.divider()
        if st.button("➕ Novo Visitante? Cadastre-se aqui"):
            st.session_state.mostra_cadastro = True
            st.rerun()

def _exibir_tela_sucesso():
    """Renderiza o comprovante com a Tag de BI correta"""
    res = st.session_state.res_data
    st.success("### ✅ Lançamento Realizado!")

    with st.container(border=True):
        st.write(f"**Atleta Beneficiado:** 🏃 {res['atleta_nome']}")
        st.write(f"**Status de BI:** {res['atleta_tag']}")

        c1, c2 = st.columns(2)
        c1.metric("Valor desta NF", f"R$ {res['valor']:,.2f}")
        c2.metric("Saldo Atualizado", f"R$ {res['saldo']:,.2f}")

    if st.button("🔄 FAZER OUTRO LANÇAMENTO", use_container_width=True, type="primary"): 
        st.session_state.tela = "lancamento"
        st.rerun()

def _exibir_tela_formulario(atl_raw):
    """Formulário de lançamento registrando o Operador real"""
    st.title(f"Olá, {st.session_state.usuario_logado['nome']}! 👋")
    if st.button("Sair (Logout)", type="secondary"):
        st.session_state.usuario_logado = None
        st.rerun()

    st.divider()

    with st.form("form_portal_prime", clear_on_submit=True):
        st.markdown("#### Detalhes do Lançamento")
        lista_nomes = sorted([a['nome'] for a in atl_raw], key=str.lower)

        usuario_atual = st.session_state.usuario_logado['nome']
        idx_padrao = lista_nomes.index(usuario_atual) if st.session_state.usuario_logado['tipo'] == 'atleta' and usuario_atual in lista_nomes else 0

        dest = st.selectbox("Para qual Atleta você está lançando?", lista_nomes, index=idx_padrao)

        # CORREÇÃO DE DATA: YYYY de 4 dígitos para evitar erro
        dt_recibo = st.date_input("Data do Recibo/Nota:", format="DD/MM/YYYY")

        val = st.number_input("Valor da Nota (R$)", min_value=0.01, step=10.0, format="%.2f")
        ft = st.file_uploader("📸 Anexar Comprovante", type=['jpg', 'png', 'pdf', 'jpeg'])

        submit_nf = st.form_submit_button("🚀 ENVIAR PARA AUDITORIA", use_container_width=True)

        if submit_nf:
            if not ft: 
                st.warning("Anexe o comprovante!")
            else:
                with st.spinner("Registrando lançamento..."):
                    atl_obj = next(a for a in atl_raw if a['nome'] == dest)
                    v_id = st.session_state.usuario_logado['id'] if st.session_state.usuario_logado['tipo'] == 'visitante' else None

                    # 🚀 FIX DO OPERADOR: Envia o nome de quem está logado (ex: Fernando)
                    operador_nome = st.session_state.usuario_logado['nome']

                    db.salvar_nota_fiscal(
                        valor=val, 
                        data=dt_recibo, 
                        arquivo=ft, 
                        cpf=atl_obj['cpf'], 
                        v_id=v_id, 
                        operador_nome=operador_nome # <--- Nome real do operador
                    )

                    # Recalcula BI para o recibo
                    dados_up, _, _ = db.carregar_dados_globais()
                    atl_up = next((a for a in dados_up if a['cpf'] == atl_obj['cpf']), None)

                    if atl_up:
                        tag = db.calcular_tag_3x3(atl_up['saldo'], atl_up['bolsa'])
                        st.session_state.res_data = {"valor": val, "saldo": atl_up['saldo'], "atleta_nome": atl_up['nome'], "atleta_tag": tag}
                        st.session_state.tela = "resumo"
                        st.rerun()

def renderizar_portal():
    """Roteador do Portal"""
    if st.session_state.get('usuario_logado') is None:
        atl_raw, vis_raw, _ = db.carregar_dados_globais()
        _exibir_tela_login(atl_raw, vis_raw)
    elif st.session_state.get('tela') == "resumo":
        _exibir_tela_sucesso()
    else:
        atl_raw, _, _ = db.carregar_dados_globais()
        _exibir_tela_formulario(atl_raw)

# [portal_lancamento.py][Edição Stealth v16.0 - Operator & Date Fix][2026-02-27]