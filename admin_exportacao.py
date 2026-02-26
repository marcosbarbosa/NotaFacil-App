import pandas as pd
import io
import database as db
import calendar
from datetime import date

# ==========================================
# 1. MOTOR DE TEMPO E TRADUÇÃO
# ==========================================
def _converter_mes_para_int(mes_input):
    """Tradutor Universal: Converte nome do mês para número (1-12)"""
    if isinstance(mes_input, int): return mes_input
    mapa = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    return mapa.get(mes_input, date.today().month)

def _obter_status_meta(saldo, bolsa, is_reta_final):
    """Lógica de Semaforização de Metas"""
    perc_saldo = (saldo / bolsa) if bolsa > 0 else 0

    if is_reta_final: return "#dc3545", "⚠️ RETA FINAL", "#ffffff"
    if perc_saldo > 0.60: return "#dc3545", "Crítico (>60%)", "#ffffff"
    if perc_saldo >= 0.50: return "#ffc107", "Atenção (50-60%)", "#000000"
    return "#0056b3", "Em dia", "#ffffff"

# ==========================================
# 2. GERADOR DE E-MAIL (BI HTML)
# ==========================================
def gerar_html_email_bi(df_f, mes, ano, st_f):
    """Gera Dashboard Financeiro Auditado para Diretoria"""

    # Cálculos de BI
    resumo_atl = df_f.groupby('Atleta (Bolsa)').agg({
        'Valor Bolsa': 'first', 'Saldo Atual': 'first', 'NFs Entregues Acumulado': 'first'
    }).reset_index()

    macro_total_saldo = resumo_atl['Saldo Atual'].sum()
    limite_seguranca = db.obter_limite_alerta()

    # Lógica de Alerta
    is_critico = macro_total_saldo < limite_seguranca
    cor_alerta = "#dc3545" if is_critico else "#0056b3"
    titulo = "🚨 ALERTA: SALDO CRÍTICO" if is_critico else "📊 Dashboard Financeiro"

    # Variáveis de Tempo
    mes_idx = _converter_mes_para_int(mes)
    ultimo_dia = calendar.monthrange(int(ano), mes_idx)[1]
    hoje = date.today()
    is_reta_final = ((ultimo_dia - hoje.day) <= 7 and hoje.month == mes_idx)

    # Início do HTML (CSS embutido para compatibilidade de e-mail)
    html = f"""
    <div style="font-family: Arial; max-width: 800px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
        <div style="background: {cor_alerta}; color: white; padding: 20px;">
            <h2 style="margin:0;">{titulo}</h2>
            <p style="margin:5px 0 0 0;">Período: {mes}/{ano} | Saldo Global: R$ {macro_total_saldo:,.2f}</p>
        </div>
        <div style="padding: 20px;">
            <h3 style="color: #333;">🚦 Status de Metas por Atleta</h3>
            <table width='100%' cellspacing='0' cellpadding='10' style='border: 1px solid #eee;'>
    """

    for _, r in resumo_atl.iterrows():
        b, s, c = float(r['Valor Bolsa']), float(r['Saldo Atual']), float(r['NFs Entregues Acumulado'])
        cor_s, txt_s, cor_t = _obter_status_meta(s, b, is_reta_final)
        p_c = (c / b * 100) if b > 0 else 0
        p_r = (s / b * 100) if b > 0 else 0

        html += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td width="30%"><strong>{str(r['Atleta (Bolsa)']).split('(')[0]}</strong><br><small>Bolsa: R$ {b:,.0f}</small></td>
            <td width="50%">
                <div style="display: flex; height: 20px; background: #eee; border-radius: 10px; overflow: hidden;">
                    <div style="width: {p_c}%; background: #28a745; color: white; font-size: 10px; text-align: center;">{p_c:.0f}%</div>
                    <div style="width: {p_r}%; background: {cor_s}; color: {cor_t}; font-size: 10px; text-align: center;">{p_r:.0f}%</div>
                </div>
            </td>
            <td width="20%" align="right"><span style="color:{cor_s}; font-weight:bold;">R$ {s:,.2f}</span></td>
        </tr>"""

    html += "</table></div></div>"
    return html

# ==========================================
# 3. EXPORTADOR EXECUTIVO (EXCEL PRIME)
# ==========================================
def gerar_excel_bi(df_f, mes, ano, st_f):
    """Gera Planilha Auditada com Dash Automático"""
    df_export = df_f.copy()

    # PROTOCOLO ANTICRASH: Limpeza de Timezone
    for col in df_export.columns:
        if pd.api.types.is_datetime64tz_dtype(df_export[col]):
            df_export[col] = df_export[col].dt.tz_localize(None)

    # Renomeação Executiva
    df_export = df_export.rename(columns={
        'data_nota': 'Data do Recibo', 'Status_UI': 'Status da NF', 
        'Atleta (Bolsa)': 'Atleta', 'valor': 'Valor Desta NF', 'Saldo Atual': 'Saldo Restante'
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Aba 1: Dados
        df_export.to_excel(writer, index=False, sheet_name='🗄️ Base de Dados')

        # Aba 2: Dashboard
        wb = writer.book
        ws = wb.add_worksheet('📊 Dashboard Prime')
        f_head = wb.add_format({'bold': True, 'bg_color': '#1A1A1D', 'font_color': 'white'})

        ws.write('B5', 'RESUMO EXECUTIVO', f_head)
        ws.write('B6', f'Volume: {len(df_export)} NFs')
        ws.write('B7', f'Total: R$ {df_export["Valor Desta NF"].sum():,.2f}')

        # Gráfico Automático
        chart = wb.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Valor por Nota',
            'values': ['🗄️ Base de Dados', 1, 7, len(df_export), 7],
        })
        ws.insert_chart('D5', chart)

    return buffer

# [admin_exportacao.py][Arquitetura Modular v5.0][2026-02-26 17:15]