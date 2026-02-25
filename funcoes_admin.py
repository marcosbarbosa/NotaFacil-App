import streamlit as st
import pandas as pd
import plotly.express as px

def preparar_auditoria(lan_data, mes_n, ano_r, status_f):
    if not lan_data: return pd.DataFrame()
    df = pd.DataFrame(lan_data)
    df['dt'] = pd.to_datetime(df['created_at'])
    mapa = {"Pendente": "⚠️ Pendente", "Aprovada": "✅ Aprovada", "Reprovada": "❌ Reprovada"}
    df['Status_UI'] = df['status'].map(mapa).fillna("⚠️ Pendente")

    df['Atleta (Bolsa)'] = df.apply(lambda r: r.get('atletas', {}).get('nome', '🚨 SEM VÍNCULO') if isinstance(r.get('atletas'), dict) else '🚨 SEM VÍNCULO', axis=1)
    df['Lançado por'] = df.apply(lambda r: r.get('visitantes', {}).get('nome') if isinstance(r.get('visitantes'), dict) else (r.get('atletas', {}).get('nome', 'Sistema') if isinstance(r.get('atletas'), dict) else 'Sistema'), axis=1)

    df['Saldo_Atleta'] = df.apply(lambda r: r.get('atletas', {}).get('saldo') if isinstance(r.get('atletas'), dict) else None, axis=1)
    df['orfao'] = df['atleta_cpf'].isna()

    df_f = df[(df['dt'].dt.month == mes_n) & (df['dt'].dt.year == ano_r)]
    if status_f != "Todas": df_f = df_f[df_f['Status_UI'] == status_f]
    return df_f

def exibir_origem_com_saldo(atleta, operador, saldo):
    st.markdown("#### 🔍 Detalhes da Origem e Saldo")
    c1, c2, c3 = st.columns(3)
    if "🚨" in atleta: c1.error(f"**Beneficiário:** {atleta}")
    else: c1.success(f"**Beneficiário:** {atleta}")
    c2.info(f"**Operador:** {operador}")
    if saldo is not None:
        cor = "normal" if saldo > 0 else "inverse"
        c3.metric("Saldo Disponível", f"R$ {float(saldo):,.2f}", delta_color=cor)
    else: c3.metric("Saldo Disponível", "N/A")

def gerar_grafico_consumo(atl_data):
    if not atl_data: return None
    df = pd.DataFrame(atl_data)
    col_bolsa = 'bolsa' if 'bolsa' in df.columns else 'limite_mensal'
    if col_bolsa in df.columns and 'saldo' in df.columns:
        df['NFs Entregues (R$)'] = df[col_bolsa].astype(float) - df['saldo'].astype(float)
        df_plot = df[df['NFs Entregues (R$)'] > 0].sort_values('NFs Entregues (R$)', ascending=False)
        if df_plot.empty: return None
        fig = px.bar(df_plot, x='nome', y='NFs Entregues (R$)', text_auto='.2f', title="📊 Volume de NFs Entregues por Atleta", color='NFs Entregues (R$)', color_continuous_scale='Reds')
        return fig
    return None

def montar_html_relatorio(df_f, mes, ano, status):
    """Transforma os dados filtrados em um e-mail HTML com layout corporativo."""
    if df_f.empty: return "<p>Nenhum dado encontrado para os filtros selecionados.</p>"

    df_export = df_f[['Status_UI', 'Atleta (Bolsa)', 'Lançado por', 'valor', 'data_nota']].copy()
    df_export.columns = ['Status', 'Beneficiário', 'Operador', 'Valor (R$)', 'Data NF']

    # Renderiza a tabela em HTML limpo
    html_table = df_export.to_html(index=False, border=1, justify='center')

    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #0056b3;">Relatório de Auditoria - NotaFácil Prime</h2>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <p><strong>Filtros aplicados:</strong> Mês: {mes} | Ano: {ano} | Status: {status}</p>
            <p><strong>Total de NFs Processadas:</strong> {len(df_export)}</p>
            <p><strong>Volume Financeiro Total:</strong> R$ {df_export['Valor (R$)'].sum():,.2f}</p>
        </div>
        {html_table}
        <br>
        <p style="font-size: 12px; color: #777;"><em>Relatório gerado automaticamente através da Sala de Guerra (Módulo Admin).</em></p>
    </div>
    """
    return html_body

# [funcoes_admin.py][Formatador de Relatório HTML e BI][2026-02-24 22:50][v1.14][60 linhas]