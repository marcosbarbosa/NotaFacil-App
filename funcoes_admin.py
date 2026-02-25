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
    """Gera o mapa de calor financeiro com nomenclatura clara para o BI"""
    if not atl_data: return None
    df = pd.DataFrame(atl_data)
    col_bolsa = 'bolsa' if 'bolsa' in df.columns else 'limite_mensal'
    if col_bolsa in df.columns and 'saldo' in df.columns:
        # A matemática clara: Bolsa - Saldo = O que já foi entregue em NFs
        df['NFs Entregues (R$)'] = df[col_bolsa].astype(float) - df['saldo'].astype(float)
        df_plot = df[df['NFs Entregues (R$)'] > 0].sort_values('NFs Entregues (R$)', ascending=False)
        if df_plot.empty: return None
        fig = px.bar(df_plot, x='nome', y='NFs Entregues (R$)', text_auto='.2f', 
                     title="📊 Volume de NFs Entregues por Atleta", 
                     color='NFs Entregues (R$)', color_continuous_scale='Reds')
        return fig
    return None

# [funcoes_admin.py][Inteligência Gráfica BI Descomplicada][2026-02-24 22:45][v1.13][40 linhas]