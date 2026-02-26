import pandas as pd
import io
import database as db
import calendar
from datetime import date

def _converter_mes_para_int(mes_input):
    if isinstance(mes_input, int): return mes_input
    mapa = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}
    return mapa.get(mes_input, date.today().month)

def gerar_html_email_bi(df_f, mes, ano, st_f):
    """Gera o E-mail Executivo (4 Indicadores + Barras de Progresso)"""
    resumo_atl = df_f.groupby('Atleta (Bolsa)').agg({'Valor Bolsa': 'first', 'Saldo Atual': 'first', 'NFs Entregues Acumulado': 'first'}).reset_index()

    total_bolsa = resumo_atl['Valor Bolsa'].sum()
    saldo_receber = resumo_atl['Saldo Atual'].sum()
    enviado_periodo = df_f['valor'].sum()
    total_pendente = df_f[df_f['Status_UI'].astype(str).str.contains('Pendente', case=False, na=False)]['valor'].sum()

    limite_seguranca = db.obter_limite_alerta()
    is_critico = saldo_receber < limite_seguranca
    cor_alerta = "#dc3545" if is_critico else "#0056b3"
    titulo_dashboard = "🚨 ALERTA: SALDO CRÍTICO GLOBAL" if is_critico else "📊 Dashboard Executivo de Auditoria"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
        <div style="background-color: {cor_alerta}; color: white; padding: 20px;">
            <h2 style="margin: 0;">{titulo_dashboard}</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Período: {mes}/{ano} | Saldo Global: R$ {saldo_receber:,.2f}</p>
        </div>
        <div style="background-color: #f8f9fa; padding: 15px; border-bottom: 2px solid #ddd;">
            <table width="100%" cellspacing="5" cellpadding="10">
                <tr>
                    <td style="background: #e9ecef; border-radius: 5px; text-align: center;"><span style="font-size: 10px; color: #666;">VALOR TOTAL (BOLSA)</span><br><strong style="font-size: 14px;">R$ {total_bolsa:,.2f}</strong></td>
                    <td style="background: #e9ecef; border-radius: 5px; text-align: center;"><span style="font-size: 10px; color: #666;">ENVIADOS NO PERÍODO</span><br><strong style="font-size: 14px; color: #0056b3;">R$ {enviado_periodo:,.2f}</strong></td>
                    <td style="background: #fff3cd; border-radius: 5px; text-align: center;"><span style="font-size: 10px; color: #856404;">NFs PENDENTES</span><br><strong style="font-size: 14px; color: #856404;">R$ {total_pendente:,.2f}</strong></td>
                    <td style="background: {'#f8d7da' if is_critico else '#d4edda'}; border-radius: 5px; text-align: center;"><span style="font-size: 10px; color: {'#721c24' if is_critico else '#155724'};">SALDO A RECEBER</span><br><strong style="font-size: 14px; color: {'#721c24' if is_critico else '#155724'};">R$ {saldo_receber:,.2f}</strong></td>
                </tr>
            </table>
        </div>
        <div style="padding: 20px;">
            <h3 style="color: #333; margin-top: 0;">🚦 Status de Metas por Atleta</h3>
            <table width='100%' cellspacing='0' cellpadding='10'>
    """
    for _, r in resumo_atl.iterrows():
        b, s, c = float(r['Valor Bolsa']), float(r['Saldo Atual']), float(r['NFs Entregues Acumulado'])
        p_c = (c / b * 100) if b > 0 else 0
        p_r = (s / b * 100) if b > 0 else 0
        cor_saldo = "#dc3545" if p_r < 40 else "#0056b3"
        html += f"""
        <tr>
            <td width="30%"><strong>{str(r['Atleta (Bolsa)']).split('(')[0]}</strong><br><span style="font-size: 11px;">Bolsa: R$ {b:,.0f}</span></td>
            <td width="50%">
                <div style="display: flex; height: 18px; background: #eee; border-radius: 4px; overflow: hidden;">
                    <div style="width: {p_c}%; background: #28a745; color: white; font-size: 9px; text-align: center;">{p_c:.0f}%</div>
                    <div style="width: {p_r}%; background: {cor_saldo}; color: white; font-size: 9px; text-align: center;">{p_r:.0f}%</div>
                </div>
            </td>
            <td width="20%" align="right"><strong>R$ {s:,.2f}</strong></td>
        </tr>"""

    rodape = db.obter_config_rodape()
    html += f"""
            </table>
        </div>
        <div style="background-color: #111; padding: 15px; text-align: center; font-size: 10px; color: #aaa;">
            <strong style="color: #fff;">{rodape.get('copyright', 'NSG Basquete')}</strong><br>
            Insta: {rodape.get('instagram', '@driblecerto')} | Whats: {rodape.get('whatsapp', '(11) 99999-9999')}<br>
            Gerado por NotaFácil Prime - {rodape.get('versao', 'v1.0.0')}
        </div>
    </div>"""
    return html

def gerar_excel_bi(df_f, mes, ano, st_f):
    """Gera o Excel Padrão Ouro com Auto-Fit Magnético nas Colunas"""
    df_export = df_f.copy()

    for col in df_export.columns:
        if pd.api.types.is_datetime64tz_dtype(df_export[col]):
            df_export[col] = df_export[col].dt.tz_localize(None)

    # 1. CÁLCULO DOS 4 INDICADORES GLOBAIS
    resumo_atl = df_export.groupby('Atleta (Bolsa)').agg({'Valor Bolsa': 'first', 'Saldo Atual': 'first', 'NFs Entregues Acumulado': 'first'}).reset_index()
    total_bolsa = resumo_atl['Valor Bolsa'].sum()
    saldo_receber = resumo_atl['Saldo Atual'].sum()
    enviado_periodo = df_export['valor'].sum()
    total_pendente = df_export[df_export['Status_UI'].astype(str).str.contains('Pendente', case=False, na=False)]['valor'].sum()

    # Base de Dados (Aba 1)
    col_mapping = {
        'Atleta (Bolsa)': 'Atleta', 'atleta_cpf': 'CPF do Atleta', 'Valor Bolsa': 'Bolsa Total',
        'NFs Entregues Acumulado': 'NFs Entregues', 'Saldo Atual': 'Saldo Restante',
        'created_at': 'Data/Hora Lançamento', 'data_nota': 'Data do Recibo', 
        'valor': 'Valor Desta NF', 'Status_UI': 'Status', 'Lançado por': 'Lançado por'
    }
    df_export = df_export.rename(columns=col_mapping)
    df_base = df_export[[c for c in col_mapping.values() if c in df_export.columns]]

    mes_idx, ano_int = _converter_mes_para_int(mes), int(ano)
    is_reta_final = ((calendar.monthrange(ano_int, mes_idx)[1] - date.today().day) <= 7 and date.today().month == mes_idx)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # --- ABA 1: BASE DE DADOS ---
        df_base.to_excel(writer, index=False, sheet_name='🗄️ Base de Dados')
        ws_base = writer.sheets['🗄️ Base de Dados']

        # MÁGICA MARVEL: Algoritmo de Auto-Ajuste de Colunas (Auto-Fit)
        for i, col in enumerate(df_base.columns):
            # Encontra o maior tamanho entre o título da coluna e os dados dentro dela
            tamanho_titulo = len(str(col))
            tamanho_dados = df_base[col].astype(str).map(len).max() if not df_base.empty else 0
            largura_ideal = max(tamanho_titulo, tamanho_dados) + 4 # +4 de "respiro" visual

            # Aplica a largura exata na coluna
            ws_base.set_column(i, i, largura_ideal)

        # --- ABA 2: DASHBOARD PRIME ---
        wb = writer.book
        ws = wb.add_worksheet('📊 Dashboard Prime')

        f_title = wb.add_format({'bold': True, 'font_size': 14, 'bg_color': '#111111', 'font_color': '#ffc107', 'border': 1})
        f_head = wb.add_format({'bold': True, 'bg_color': '#e9ecef', 'border': 1, 'align': 'center'})
        f_money = wb.add_format({'num_format': 'R$ #,##0.00', 'align': 'center'})
        f_money_alert = wb.add_format({'num_format': 'R$ #,##0.00', 'font_color': '#dc3545', 'bold': True, 'align': 'center'})
        f_tbl_head = wb.add_format({'bold': True, 'bg_color': '#333333', 'font_color': 'white', 'align': 'center'})
        f_footer = wb.add_format({'font_size': 9, 'font_color': '#888888', 'italic': True})

        f_blue = wb.add_format({'num_format': 'R$ #,##0.00', 'bg_color': '#cce5ff', 'font_color': '#004085'})
        f_yellow = wb.add_format({'num_format': 'R$ #,##0.00', 'bg_color': '#fff3cd', 'font_color': '#856404'})
        f_red = wb.add_format({'num_format': 'R$ #,##0.00', 'bg_color': '#f8d7da', 'font_color': '#721c24'})
        f_empty = wb.add_format({'bg_color': '#f8f9fa'})

        # Larguras calculadas para o Dashboard (Mais espaço para o nome do Atleta)
        ws.set_column('B:B', 28) # Coluna de Nomes
        ws.set_column('C:F', 23) # Colunas de Indicadores e Cores

        ws.merge_range('B2:F2', f'DASHBOARD FINANCEIRO EXECUTIVO - {mes}/{ano}', f_title)

        # OS 4 INDICADORES (Linhas 4 e 5)
        ws.write('B4', 'VALOR TOTAL DE BOLSA', f_head)
        ws.write('C4', 'ENVIADOS NO PERÍODO', f_head)
        ws.write('D4', 'NFs PENDENTES', f_head)
        ws.write('E4', 'SALDO A RECEBER', f_head)

        ws.write('B5', total_bolsa, f_money)
        ws.write('C5', enviado_periodo, f_money)
        ws.write('D5', total_pendente, f_money)
        ws.write('E5', saldo_receber, f_money_alert if saldo_receber < db.obter_limite_alerta() else f_money)

        # TABELA SEMAFÓRICA (A partir da Linha 8)
        ws.write('B8', 'ATLETA', f_tbl_head)
        ws.write('C8', 'ENTREGUE E AUDITADO', f_tbl_head)
        ws.write('D8', 'DISPONÍVEL (SAUDÁVEL)', f_tbl_head)
        ws.write('E8', 'ALERTA (NO PRAZO)', f_tbl_head)
        ws.write('F8', 'CRÍTICO (RETA FINAL)', f_tbl_head)

        linha = 8
        for _, r in resumo_atl.iterrows():
            nome = str(r['Atleta (Bolsa)']).split('(')[0].strip()
            entregue, saldo, bolsa = r['NFs Entregues Acumulado'], r['Saldo Atual'], r['Valor Bolsa']
            perc = (saldo / bolsa) if bolsa > 0 else 0

            ws.write(linha, 1, nome)
            ws.write(linha, 2, entregue, f_money)

            # Lógica de Distribuição das Cores do Saldo
            if is_reta_final or perc > 0.60:
                ws.write(linha, 3, "", f_empty); ws.write(linha, 4, "", f_empty); ws.write(linha, 5, saldo, f_red)
            elif perc >= 0.50:
                ws.write(linha, 3, "", f_empty); ws.write(linha, 4, saldo, f_yellow); ws.write(linha, 5, "", f_empty)
            else:
                ws.write(linha, 3, saldo, f_blue); ws.write(linha, 4, "", f_empty); ws.write(linha, 5, "", f_empty)
            linha += 1

        # Barras de Progresso Verdes na coluna C (Entregue)
        ws.conditional_format(f'C9:C{linha}', {'type': 'data_bar', 'bar_color': '#28a745'})

        # RODAPÉ INSTITUCIONAL NO EXCEL
        rodape = db.obter_config_rodape()
        ws.write(linha + 2, 1, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", f_footer)
        ws.write(linha + 3, 1, f"© {rodape.get('copyright', 'NSG Basquete')} | {rodape.get('instagram', '')} | {rodape.get('whatsapp', '')}", f_footer)

    return buffer

# [admin_exportacao.py][Excel BI c/ Auto-Fit e Largura Perfeita v8.6][2026-02-26]