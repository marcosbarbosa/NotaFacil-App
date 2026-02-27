import pandas as pd
import io
import database as db
import calendar
from datetime import date

def _converter_mes_para_int(mes_input):
    """Converte o nome do mês para número para cálculos de reta final"""
    if isinstance(mes_input, int): return mes_input
    mapa = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}
    return mapa.get(mes_input, date.today().month)

def _get_rodape_seguro():
    """Fallback de segurança caso a tabela de configurações demore a responder"""
    try:
        return db.obter_config_rodape()
    except:
        return {'whatsapp': '(92) 99981-0256', 'instagram': '@driblecerto', 'copyright': 'NSG Basquete', 'versao': '1.0.0'}

def gerar_html_email_bi(df_f, mes, ano, st_f):
    """Gera o E-mail Executivo com Semântica de Cores Corrigida (Visão BI)"""
    resumo_atl = df_f.groupby('atleta_nome').agg({'Valor Bolsa': 'first', 'Saldo Atual': 'first', 'NFs Entregues Acumulado': 'first'}).reset_index()

    total_bolsa = resumo_atl['Valor Bolsa'].sum()
    saldo_receber = resumo_atl['Saldo Atual'].sum()
    enviado_periodo = df_f['valor'].sum()
    total_pendente = df_f[df_f['Status_UI'].astype(str).str.contains('Pendente', case=False, na=False)]['valor'].sum()

    # ⏱️ REGRA DA RETA FINAL (Faltam 7 dias ou menos pro fim do mês analisado)
    mes_idx, ano_int = _converter_mes_para_int(mes), int(ano)
    is_reta_final = ((calendar.monthrange(ano_int, mes_idx)[1] - date.today().day) <= 7 and date.today().month == mes_idx)

    # 🎨 SEMÂNTICA DE CORES DOS CARTÕES (KPIs)
    bg_enviado, txt_enviado = "#d4edda", "#155724"

    perc_restante_global = (saldo_receber / total_bolsa * 100) if total_bolsa > 0 else 0
    if is_reta_final and saldo_receber > 0:
        bg_saldo, txt_saldo = "#f8d7da", "#721c24" 
        titulo_dashboard = "🚨 ALERTA: RETA FINAL - SALDO CRÍTICO"
        cor_header = "#dc3545"
    else:
        bg_saldo, txt_saldo = "#cce5ff", "#004085" 
        titulo_dashboard = "📊 Dashboard Executivo de Auditoria"
        cor_header = "#1a252f"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <div style="background-color: {cor_header}; color: white; padding: 25px; text-align: center;">
            <h2 style="margin: 0; font-size: 22px; letter-spacing: 1px;">{titulo_dashboard}</h2>
            <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">Período: {mes}/{ano} | Risco Financeiro Restante: <strong>R$ {saldo_receber:,.2f}</strong></p>
        </div>
        <div style="background-color: #f8f9fa; padding: 20px; border-bottom: 2px solid #eee;">
            <table width="100%" cellspacing="8" cellpadding="12">
                <tr>
                    <td style="background: #fff; border: 1px solid #ddd; border-radius: 6px; text-align: center; width: 25%;">
                        <span style="font-size: 11px; color: #7f8c8d; font-weight: bold;">VALOR (BOLSA)</span><br>
                        <strong style="font-size: 16px; color: #2c3e50;">R$ {total_bolsa:,.2f}</strong>
                    </td>
                    <td style="background: {bg_enviado}; border: 1px solid #c3e6cb; border-radius: 6px; text-align: center; width: 25%;">
                        <span style="font-size: 11px; color: {txt_enviado}; font-weight: bold;">ENVIADOS NO MÊS</span><br>
                        <strong style="font-size: 16px; color: {txt_enviado};">R$ {enviado_periodo:,.2f}</strong>
                    </td>
                    <td style="background: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; text-align: center; width: 25%;">
                        <span style="font-size: 11px; color: #856404; font-weight: bold;">NFs PENDENTES</span><br>
                        <strong style="font-size: 16px; color: #856404;">R$ {total_pendente:,.2f}</strong>
                    </td>
                    <td style="background: {bg_saldo}; border: 1px solid {bg_saldo}; border-radius: 6px; text-align: center; width: 25%;">
                        <span style="font-size: 11px; color: {txt_saldo}; font-weight: bold;">SALDO A RECEBER</span><br>
                        <strong style="font-size: 16px; color: {txt_saldo};">R$ {saldo_receber:,.2f}</strong>
                    </td>
                </tr>
            </table>
        </div>
        <div style="padding: 25px;">
            <h3 style="color: #2c3e50; margin-top: 0; border-bottom: 2px solid #ffc107; padding-bottom: 10px; display: inline-block;">🚦 Status de Metas por Atleta</h3>
            <table width='100%' cellspacing='0' cellpadding='12' style="margin-top: 15px;">
    """
    for _, r in resumo_atl.iterrows():
        b, s, c = float(r['Valor Bolsa']), float(r['Saldo Atual']), float(r['NFs Entregues Acumulado'])
        p_c = (c / b * 100) if b > 0 else 0
        p_r = (s / b * 100) if b > 0 else 0

        if is_reta_final:
            cor_saldo = "#dc3545" if p_r > 1 else "#28a745"
        else:
            if p_r > 60: cor_saldo = "#dc3545" 
            elif p_r >= 30: cor_saldo = "#fd7e14" 
            else: cor_saldo = "#17a2b8" 

        bar_restante = f'<div style="width: {p_r}%; background: {cor_saldo}; color: white; font-size: 10px; line-height: 18px; text-align: center; font-weight: bold;">{p_r:.0f}%</div>' if p_r > 1 else ''

        nome_atleta = str(r['atleta_nome']).split('(')[0].strip()
        cor_texto_valor = cor_saldo if p_r > 1 else "#28a745"

        html += f"""
        <tr>
            <td width="30%" style="border-bottom: 1px solid #eee;">
                <strong style="color: #2c3e50; font-size: 14px;">{nome_atleta}</strong><br>
                <span style="font-size: 11px; color: #7f8c8d;">Bolsa: R$ {b:,.0f}</span>
            </td>
            <td width="45%" style="border-bottom: 1px solid #eee; vertical-align: middle;">
                <div style="display: flex; height: 18px; background: #ecf0f1; border-radius: 10px; overflow: hidden; border: 1px solid #ddd;">
                    <div style="width: {p_c}%; background: #28a745; color: white; font-size: 10px; line-height: 18px; text-align: center; font-weight: bold;">{p_c:.0f}%</div>
                    {bar_restante}
                </div>
            </td>
            <td width="25%" align="right" style="border-bottom: 1px solid #eee;">
                <strong style="color: {cor_texto_valor}; font-size: 14px;">R$ {s:,.2f}</strong>
            </td>
        </tr>"""

    rodape = _get_rodape_seguro()
    html += f"""
            </table>
        </div>
        <div style="background-color: #1a252f; padding: 20px; text-align: center; font-size: 11px; color: #bdc3c7;">
            <strong style="color: #f1c40f; font-size: 14px;">{rodape.get('copyright')}</strong><br><br>
            📱 Instagram: {rodape.get('instagram')} | 💬 WhatsApp: {rodape.get('whatsapp')}<br><br>
            <span style="opacity: 0.7;">Gerado automaticamente por NotaFácil Prime - {rodape.get('versao')}</span>
        </div>
    </div>"""
    return html

def gerar_excel_bi(df_f, mes, ano, st_f):
    """Gera o Excel Padrão Ouro com Auto-Fit Magnético nas Colunas"""
    df_export = df_f.copy()

    for col in df_export.columns:
        if pd.api.types.is_datetime64tz_dtype(df_export[col]):
            df_export[col] = df_export[col].dt.tz_localize(None)

    resumo_atl = df_export.groupby('atleta_nome').agg({'Valor Bolsa': 'first', 'Saldo Atual': 'first', 'NFs Entregues Acumulado': 'first'}).reset_index()
    total_bolsa = resumo_atl['Valor Bolsa'].sum()
    saldo_receber = resumo_atl['Saldo Atual'].sum()
    enviado_periodo = df_export['valor'].sum()
    total_pendente = df_export[df_export['Status_UI'].astype(str).str.contains('Pendente', case=False, na=False)]['valor'].sum()

    col_mapping = {
        'atleta_nome': 'Atleta', 'atleta_cpf': 'CPF do Atleta', 'Valor Bolsa': 'Bolsa Total',
        'NFs Entregues Acumulado': 'NFs Entregues', 'Saldo Atual': 'Saldo Restante',
        'created_at': 'Data/Hora Lançamento', 'data_nota': 'Data do Recibo', 
        'valor': 'Valor Desta NF', 'Status_UI': 'Status', 'lancado_por': 'Operador Logado'
    }
    df_export = df_export.rename(columns=col_mapping)
    df_base = df_export[[c for c in col_mapping.values() if c in df_export.columns]]

    mes_idx, ano_int = _converter_mes_para_int(mes), int(ano)
    is_reta_final = ((calendar.monthrange(ano_int, mes_idx)[1] - date.today().day) <= 7 and date.today().month == mes_idx)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_base.to_excel(writer, index=False, sheet_name='🗄️ Base de Dados')
        ws_base = writer.sheets['🗄️ Base de Dados']

        for i, col in enumerate(df_base.columns):
            tamanho_titulo = len(str(col))
            tamanho_dados = df_base[col].astype(str).map(len).max() if not df_base.empty else 0
            largura_ideal = max(tamanho_titulo, tamanho_dados) + 4
            ws_base.set_column(i, i, largura_ideal)

        wb = writer.book
        ws = wb.add_worksheet('📊 Dashboard Prime')

        # ESTILOS DE CÉLULAS (Paleta de Cores Sincronizada com HTML)
        f_title = wb.add_format({'bold': True, 'font_size': 14, 'bg_color': '#111111', 'font_color': '#ffc107', 'border': 1})
        f_head = wb.add_format({'bold': True, 'bg_color': '#e9ecef', 'border': 1, 'align': 'center'})
        f_money = wb.add_format({'num_format': 'R$ #,##0.00', 'align': 'center'})
        f_money_alert = wb.add_format({'num_format': 'R$ #,##0.00', 'font_color': '#dc3545', 'bold': True, 'align': 'center'})

        # 🟢 Destaque Verde (Enviados)
        f_money_green = wb.add_format({'num_format': 'R$ #,##0.00', 'font_color': '#155724', 'bg_color': '#d4edda', 'bold': True, 'align': 'center'})
        # 🟡 Destaque Amarelo (NFs Pendentes - NOVO)
        f_money_yellow = wb.add_format({'num_format': 'R$ #,##0.00', 'font_color': '#856404', 'bg_color': '#fff3cd', 'bold': True, 'align': 'center'})

        f_tbl_head = wb.add_format({'bold': True, 'bg_color': '#333333', 'font_color': 'white', 'align': 'center'})
        f_footer = wb.add_format({'font_size': 9, 'font_color': '#888888', 'italic': True})

        f_blue = wb.add_format({'num_format': 'R$ #,##0.00', 'bg_color': '#cce5ff', 'font_color': '#004085'})
        f_yellow = wb.add_format({'num_format': 'R$ #,##0.00', 'bg_color': '#fff3cd', 'font_color': '#856404'})
        f_red = wb.add_format({'num_format': 'R$ #,##0.00', 'bg_color': '#f8d7da', 'font_color': '#721c24'})
        f_empty = wb.add_format({'bg_color': '#f8f9fa'})

        ws.set_column('B:B', 28) 
        ws.set_column('C:F', 23) 

        ws.merge_range('B2:F2', f'DASHBOARD FINANCEIRO EXECUTIVO - {mes}/{ano}', f_title)

        ws.write('B4', 'VALOR TOTAL DE BOLSA', f_head)
        ws.write('C4', 'ENVIADOS NO PERÍODO', f_head)
        ws.write('D4', 'NFs PENDENTES', f_head)
        ws.write('E4', 'SALDO A RECEBER', f_head)

        ws.write('B5', total_bolsa, f_money)
        ws.write('C5', enviado_periodo, f_money_green) # Verde
        ws.write('D5', total_pendente, f_money_yellow) # 🚀 FIX: Amarelo Sincronizado

        if is_reta_final and saldo_receber > 0:
            ws.write('E5', saldo_receber, f_red)
        else:
            ws.write('E5', saldo_receber, f_blue)

        ws.write('B8', 'ATLETA', f_tbl_head)
        ws.write('C8', 'ENTREGUE E AUDITADO', f_tbl_head)
        ws.write('D8', 'DISPONÍVEL (SAUDÁVEL)', f_tbl_head)
        ws.write('E8', 'ALERTA (NO PRAZO)', f_tbl_head)
        ws.write('F8', 'CRÍTICO (RETA FINAL)', f_tbl_head)

        linha = 8
        for _, r in resumo_atl.iterrows():
            nome = str(r['atleta_nome']).split('(')[0].strip()
            entregue, saldo, bolsa = r['NFs Entregues Acumulado'], r['Saldo Atual'], r['Valor Bolsa']
            perc = (saldo / bolsa) if bolsa > 0 else 0

            ws.write(linha, 1, nome)
            ws.write(linha, 2, entregue, f_money)

            if is_reta_final or perc > 0.60:
                ws.write(linha, 3, "", f_empty); ws.write(linha, 4, "", f_empty); ws.write(linha, 5, saldo, f_red)
            elif perc >= 0.30:
                ws.write(linha, 3, "", f_empty); ws.write(linha, 4, saldo, f_yellow); ws.write(linha, 5, "", f_empty)
            else:
                ws.write(linha, 3, saldo, f_blue); ws.write(linha, 4, "", f_empty); ws.write(linha, 5, "", f_empty)
            linha += 1

        ws.conditional_format(f'C9:C{linha}', {'type': 'data_bar', 'bar_color': '#28a745'})

        rodape = _get_rodape_seguro()
        ws.write(linha + 2, 1, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", f_footer)
        ws.write(linha + 3, 1, f"© {rodape.get('copyright')} | {rodape.get('instagram')} | {rodape.get('whatsapp')}", f_footer)

    return buffer

# [admin_exportacao.py][Inteligência BI Semântica + Excel Sync v9.6][2026-02-27]
# Total de Linhas de Código: 186