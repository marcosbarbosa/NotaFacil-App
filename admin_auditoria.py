import streamlit as st
from datetime import date, datetime
import time
import pandas as pd
import plotly.express as px
import database as db
import funcoes_admin as f_adm
import servicos_email as email_svc
import admin_exportacao as export_svc


def _enriquecer_dados(df_f, atl_data):
    """Enriquece a tabela com dados financeiros atuais e remove Timezone"""
    atl_map = {
        a['cpf']: {
            'saldo': a.get('saldo', 0),
            'bolsa': a.get('bolsa', 0)
        }
        for a in atl_data
    }

    def get_fin(cpf, campo):
        return atl_map.get(cpf, {}).get(campo, 0.0) if cpf else 0.0

    df_f['Saldo Atual'] = df_f['atleta_cpf'].apply(
        lambda x: get_fin(x, 'saldo'))
    df_f['Valor Bolsa'] = df_f['atleta_cpf'].apply(
        lambda x: get_fin(x, 'bolsa'))
    df_f['NFs Entregues Acumulado'] = df_f['Valor Bolsa'] - df_f['Saldo Atual']

    # Blindagem contra erro de Timezone para exportação Excel
    for col in df_f.columns:
        if pd.api.types.is_datetime64tz_dtype(df_f[col]):
            df_f[col] = df_f[col].dt.tz_localize(None)

    return df_f


def renderizar_aba_auditoria(atl_data, lan_data, vis_data):
    """Módulo de Auditoria: Rastreabilidade, Aprovação e Log de Edição"""
    st.markdown("### Auditoria Operacional")

    # --- FILTROS DE NAVEGAÇÃO ---
    c1, c2, c3 = st.columns(3)
    meses_lista = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
        "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    mes = c1.selectbox("Mês:",
                       meses_lista,
                       index=date.today().month - 1,
                       key="aud_mes")
    # 🛠️ CORREÇÃO 1: Lista de anos inserida corretamente (Evita SyntaxError)
    ano = c2.selectbox("Ano:", index=2, key="aud_ano")
    st_f = c3.selectbox("Status:",
                        ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"],
                        index=1,
                        key="aud_st")

    m_idx = meses_lista.index(mes) + 1
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty:
        st.warning("Sem registros para auditoria no período selecionado.")
        return

    df_f = _enriquecer_dados(df_f, atl_data)
    id_sel = None

    # --- TABELA DE SELEÇÃO PRIME ---
    ev = st.dataframe(df_f[[
        'Status_UI', 'atleta_nome', 'Valor Bolsa', 'valor', 'Saldo Atual',
        'data_nota', 'foto_url', 'lancado_por'
    ]],
                      column_config={
                          "Status_UI":
                          "Status",
                          "atleta_nome":
                          "Atleta",
                          "foto_url":
                          st.column_config.ImageColumn("NF"),
                          "Valor Bolsa":
                          st.column_config.NumberColumn("Bolsa Total",
                                                        format="R$ %.2f"),
                          "valor":
                          st.column_config.NumberColumn("Valor NF",
                                                        format="R$ %.2f"),
                          "Saldo Atual":
                          st.column_config.NumberColumn("Saldo Restante",
                                                        format="R$ %.2f"),
                          "lancado_por":
                          "Operador"
                      },
                      use_container_width=True,
                      hide_index=True,
                      on_select="rerun",
                      selection_mode="single-row")

    if ev.selection.rows:
        # 🛠️ CORREÇÃO 2: Adicionado para pegar o índice correto da linha selecionada
        id_sel = df_f.iloc[ev.selection.rows]['id']

    if id_sel:
        st.divider()
        # 🛠️ CORREÇÃO 3: Adicionado para evitar erro de série do Pandas
        nota = df_f[df_f['id'] == id_sel].iloc
        f_adm.exibir_origem_com_saldo(nota['atleta_nome'],
                                      nota.get('lancado_por', 'N/A'),
                                      nota['Saldo Atual'])

        c_img, c_btn = st.columns([1.2, 1])
        with c_img:
            st.image(nota['foto_url'],
                     caption="Documento Comprobatório",
                     use_container_width=True)

        with c_btn:
            st.markdown(
                f"#### Valor do Documento: **R$ {nota['valor']:,.2f}**")

            user_logado = st.session_state.get('usuario_logado')
            admin_nome = user_logado.get(
                'nome', 'ADMIN_MASTER') if user_logado else 'ADMIN_MASTER'

            # 1. BOTÕES DE AÇÃO RÁPIDA
            col_ap, col_re = st.columns(2)
            with col_ap:
                if st.button("✅ Aprovar",
                             use_container_width=True,
                             type="primary"):
                    ok, msg = db.alterar_status_nota(nota['id'],
                                                     nota['atleta_cpf'],
                                                     nota['valor'], "Aprovado",
                                                     admin_nome)
                    if ok:
                        st.success("Aprovação registrada!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
            with col_re:
                if st.button("❌ Reprovar", use_container_width=True):
                    ok, msg = db.alterar_status_nota(nota['id'],
                                                     nota['atleta_cpf'],
                                                     nota['valor'],
                                                     "Reprovado", admin_nome)
                    if ok:
                        st.warning("Reprovação registrada!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)

            # 2. MÓDULO DE EDIÇÃO MINIMALISTA (EXCLUSIVO ADMIN)
            st.divider()
            with st.expander("📝 Editar NF"):
                # Lista de Atletas para Beneficiário
                lista_atl_nomes = [a['nome'] for a in atl_data]
                lista_atl_cpfs = [a['cpf'] for a in atl_data]
                idx_atl = lista_atl_cpfs.index(
                    nota['atleta_cpf']
                ) if nota['atleta_cpf'] in lista_atl_cpfs else 0

                novo_nome_beneficiario = st.selectbox("Corrigir Beneficiário:",
                                                      lista_atl_nomes,
                                                      index=idx_atl)
                novo_cpf = lista_atl_cpfs[lista_atl_nomes.index(
                    novo_nome_beneficiario)]

                # Correção de Valor
                novo_v = st.number_input("Corrigir Valor NF:",
                                         value=float(nota['valor']),
                                         step=1.0)

                # Lista unificada de Operadores (Atletas + Visitantes/Admin)
                lista_ops = sorted(
                    list(
                        set([a['nome'] for a in atl_data] +
                            [v['nome'] for v in vis_data])))
                op_original = nota.get('lancado_por', 'Diretoria')

                # Garante que o operador original esteja na lista para evitar erros de index
                if op_original not in lista_ops: lista_ops.append(op_original)

                novo_op = st.selectbox("Operador Responsável:",
                                       lista_ops,
                                       index=lista_ops.index(op_original))

                if st.button("💾 Salvar e Notificar Diretoria",
                             use_container_width=True):
                    with st.spinner(
                            "Atualizando registros e sincronizando saldos..."):
                        ok, msg = db.atualizar_lancamento(
                            nota['id'], novo_v, novo_cpf, novo_op,
                            nota['valor'], nota['atleta_cpf'],
                            nota['Status_UI'])
                        if ok:
                            # DISPARO DE LOG POR E-MAIL (GOVERNANÇA ATIVA)
                            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                            html_log = f"""
                            <h3>⚠️ Alerta de Auditoria: Edição Administrativa</h3>
                            <p>O administrador <b>{admin_nome}</b> realizou uma alteração manual no sistema.</p>
                            <table border='1' style='border-collapse: collapse; width: 100%;'>
                                <tr style='background-color: #f2f2f2;'><td><b>Campo</b></td><td><b>Valor Anterior</b></td><td><b>Valor Novo</b></td></tr>
                                <tr><td>Valor NF</td><td>R$ {nota['valor']:.2f}</td><td>R$ {novo_v:.2f}</td></tr>
                                <tr><td>Beneficiário</td><td>{nota['atleta_nome']}</td><td>{novo_nome_beneficiario}</td></tr>
                                <tr><td>Operador Responsável</td><td>{op_original}</td><td>{novo_op}</td></tr>
                            </table>
                            <p><i>Data/Hora da Operação: {agora} | Status Original: {nota['Status_UI']}</i></p>
                            """
                            email_svc.enviar_relatorio(
                                "diretoria@nsg.com",
                                "⚠️ LOG: Alteração Administrativa NF",
                                html_log)

                            st.success(
                                "Alteração salva e Diretoria notificada!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)

            if st.button("🗑️ Excluir Registro Permanente",
                         use_container_width=True):
                ok, msg = db.excluir_nota_fiscal(nota['id'],
                                                 nota['atleta_cpf'],
                                                 nota['valor'],
                                                 nota['Status_UI'])
                if ok:
                    st.success("Registro removido com sucesso!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)


def renderizar_aba_bi(atl_data, lan_data, admin_atual):
    """Módulo de BI: Visão Executiva"""
    st.markdown("### Inteligência Financeira")

    c1, c2, c3 = st.columns(3)
    meses_lista = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
        "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    mes = c1.selectbox("Mês Análise:",
                       meses_lista,
                       index=date.today().month - 1,
                       key="bi_mes")
    # 🛠️ CORREÇÃO 4: Lista de anos inserida corretamente (Evita SyntaxError)
    ano = c2.selectbox("Ano Análise:", index=2, key="bi_ano")
    st_f = c3.selectbox("Filtro de Status:",
                        ["Todas", "⚠️ Pendente", "✅ Aprovada", "❌ Reprovada"],
                        index=0,
                        key="bi_st")

    m_idx = meses_lista.index(mes) + 1
    df_f = f_adm.preparar_auditoria(lan_data, m_idx, ano, st_f)

    if df_f.empty:
        st.warning("Nenhum dado financeiro para análise neste filtro.")
        return

    df_f = _enriquecer_dados(df_f, atl_data)

    st.markdown("#### Distribuição de Volume por Atleta")
    df_agrupado = df_f.groupby(
        'atleta_nome')['valor'].sum().reset_index().sort_values(
            by='valor', ascending=False)
    fig = px.bar(df_agrupado,
                 x='atleta_nome',
                 y='valor',
                 text_auto='.2f',
                 color='valor',
                 color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown("#### Exportação e Governança Executiva")
    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.info("💾 **Relatório em Excel**")
        excel_buffer = export_svc.gerar_excel_bi(df_f, mes, ano, st_f)
        st.download_button(label="📥 Download Planilha Auditada",
                           data=excel_buffer,
                           file_name=f"Relatorio_BI_{mes}_{ano}.xlsx",
                           use_container_width=True)

    with col_exp2:
        st.info("📧 **Disparo para Diretoria**")
        ultimo_email = db.obter_ultimo_email_exportacao()
        dest = st.text_input("E-mail do Destinatário:",
                             value=ultimo_email,
                             placeholder="ex: diretor@nsg.com",
                             key="email_dest")

        if st.button("🚀 Enviar Dashboard",
                     use_container_width=True,
                     type="primary"):
            if "@" in dest:
                with st.spinner("Gerando e enviando relatório..."):
                    html_body = export_svc.gerar_html_email_bi(
                        df_f, mes, ano, st_f)
                    ok, msg = email_svc.enviar_relatorio(
                        dest.strip(),
                        f"Relatório Financeiro NSG ({mes}/{ano})", html_body)

                    if ok:
                        db.registrar_log_exportacao(admin_atual, dest.strip(),
                                                    f"{mes}/{ano}", len(df_f))
                        st.success(
                            "Relatório enviado com sucesso para a diretoria.")
                    else:
                        st.error(f"Erro no envio: {msg}")
            else:
                st.warning("⚠️ Forneça um e-mail institucional válido.")


# [admin_auditoria.py][v15.6 - Governança Prime Híbrida][2026-02-27]
