import pandas as pd
import io
import database as db
import calendar
from datetime import date

def _converter_mes_para_int(mes_input):
    """Tradutor Universal: Converte nome do mês para número (1-12)"""
    if isinstance(mes_input, int): return mes_input

    mapa = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    return mapa.get(mes_input, date.today().month)

def gerar_html_email_bi(df_f, mes, ano, st_f):
    """Gera HTML com Painel Financeiro Macro (Bolsas + Saldos + Processado)"""

    # 1. Cálculos Micro (Sobre as Notas filtradas)
    total_valor_notas = df_f['valor'].sum()
    qtd_notas = len(df_f)

    # 2. Cálculos Macro (Sobre os Atletas envolvidos - Sem duplicidade)
    resumo_atl = df_f.groupby('Atleta (Bolsa)').agg({
        'Valor Bolsa': 'first', 'Saldo Atual': 'first', 'NFs Entregues Acumulado': 'first'
    }).reset_index()

    macro_total_bolsas = resumo_atl['Valor Bolsa'].sum()
    macro_total_saldo = resumo_atl['Saldo Atual'].sum()

    # 3. Preparação das Variáveis de Tempo
    mes_idx = _converter_mes_para_int(mes)
    ano_int = int(ano)
    ultimo_dia = calendar.monthrange(ano_int, mes_idx)[1]
    hoje = date.today()
    dias_restantes = ultimo_dia - hoje.day

    is_reta_final = (dias_restantes <= 7 and dias_restantes >= 0 and hoje.month == mes_idx and hoje.year == ano_int)

    # 4. UX PRIME: Etiquetas Dinâmicas
    if "Pendente" in st_f:
        label_total = "Total Pendente (NFs):"
    elif "Aprovada" in st_f:
        label_total = "Total Já Aprovado:"
    elif "Reprovada" in st_f:
        label_total = "Total Reprovado:"
    else:
        label_total = "Total Processado (NFs):"

    # 5. Construção do Corpo do E-mail (Novo Painel Quádruplo)
    html = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto;">
        <div style="background-color: #0056b3; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">📊 Dashboard Financeiro - Reta Final</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Período: {mes}/{ano} | Status: {st_f}</p>
        </div>

        <div style="background-color: #f8f9fa; padding: 15px; border-bottom: 2px solid #ddd; margin-bottom: 20px;">
            <table width="100%" cellspacing="5">
                <tr>
                    <td style="background: #e9ecef; padding: 10px; border-radius: 5px;">
                        <span style="font-size: 11px; color: #666; text-transform: uppercase;">Volume Auditado</span><br>
                        <strong>{qtd_notas} NFs</strong>
                    </td>
                    <td style="background: #e9ecef; padding: 10px; border-radius: 5px;" align="right">
                        <span style="font-size: 11px; color: #666; text-transform: uppercase;">{label_total}</span><br>
                        <strong style="color: #0056b3;">R$ {total_valor_notas:,.2f}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="background: #fff3cd; padding: 10px; border-radius: 5px; border: 1px solid #ffeeba;">
                        <span style="font-size: 11px; color: #856404; text-transform: uppercase;">Total de Bolsas (Equipe)</span><br>
                        <strong style="color: #856404;">R$ {macro_total_bolsas:,.2f}</strong>
                    </td>
                    <td style="background: #d4edda; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb;" align="right">
                        <span style="font-size: 11px; color: #155724; text-transform: uppercase;">Saldo Restante Global</span><br>
                        <strong style="color: #155724;">R$ {macro_total_saldo:,.2f}</strong>
                    </td>
                </tr>
            </table>
        </div>

        <h3 style="color: #333;">🚦 Status de Metas por Atleta</h3>
    """

    html += "<table width='100%' cellspacing='0' cellpadding='8' style='border: 1px solid #eee;'>"

    for _, r in resumo_atl.iterrows():
        bolsa = float(r['Valor Bolsa'])
        saldo = float(r['Saldo Atual'])
        consumido = float(r['NFs Entregues Acumulado'])
        nome = str(r['Atleta (Bolsa)']).split('(')[0].strip()

        perc_saldo = (saldo / bolsa) if bolsa > 0 else 0

        if is_reta_final:
            cor_saldo = "#dc3545" 
            txt_saldo = "⚠️ RETA FINAL"
        elif perc_saldo > 0.60:
            cor_saldo = "#dc3545" 
            txt_saldo = "Crítico (>60%)"
        elif perc_saldo >= 0.50:
            cor_saldo = "#ffc107" 
            txt_saldo = "Atenção (50-60%)"
        else:
            cor_saldo = "#0056b3" 
            txt_saldo = "Em dia"

        cor_txt_saldo = '#000000' if cor_saldo == '#ffc107' else '#ffffff'
        perc_cons = (consumido / bolsa * 100) if bolsa > 0 else 0
        perc_rest = (saldo / bolsa * 100) if bolsa > 0 else 0

        html += f"""
        <tr>
            <td width="25%" style="border-bottom: 1px solid #eee;">
                <strong>{nome}</strong><br>
                <span style="font-size: 11px; color: #666;">Meta: R$ {bolsa:,.0f}</span>
            </td>
            <td width="55%" style="border-bottom: 1px solid #eee; vertical-align: middle;">
                <div style="display: flex; height: 20px; width: 100%; background-color: #eee; border-radius: 4px; overflow: hidden;">
                    <div style="width: {perc_cons}%; background-color: #28a745; color: white; font-size: 10px; text-align: center; line-height: 20px;" title="Entregue">
                        {f'{perc_cons:.0f}%' if perc_cons > 10 else ''}
                    </div>
                    <div style="width: {perc_rest}%; background-color: {cor_saldo}; color: {cor_txt_saldo}; font-size: 10px; text-align: center; line-height: 20px;" title="Restante">
                        {f'{perc_rest:.0f}%' if perc_rest > 10 else ''}
                    </div>
                </div>
            </td>
            <td width="20%" align="right" style="border-bottom: 1px solid #eee;">
                <span style="display: block; font-size: 10px; color: {cor_saldo}; font-weight: bold;">{txt_saldo}</span>
                <strong>R$ {saldo:,.2f}</strong>
            </td>
        </tr>
        """
    html += "</table><br>"

    html += "<h3 style='color: #333;'>📑 Detalhamento (Base de Dados)</h3>"
    html += "<table width='100%' cellspacing='0' cellpadding='5' style='font-size: 11px; border-collapse: collapse;'>"
    html += "<tr style='background: #333; color: white;'><th align='left'>Data</th><th align='left'>Atleta</th><th align='right'>Valor</th><th align='right'>Saldo Restante</th></tr>"

    for _, r in df_f.head(20).iterrows():
        html += f"<tr style='border-bottom: 1px solid #ddd;'><td>{r['data_nota']}</td><td>{str(r['Atleta (Bolsa)']).split('(')[0]}</td><td align='right'>R$ {r['valor']:,.2f}</td><td align='right'>R$ {r['Saldo Atual']:,.2f}</td></tr>"

    html += "</table></div>"
    return html

def gerar_excel_bi(df_f, mes, ano, st_f):
    """Gera Excel com Painel Macro e Ordenação Prime"""
    df_export = df_f.copy()

    try: df_export['Data/Hora Lançamento'] = pd.to_datetime(df_export['created_at']).dt.strftime('%d/%m/%Y %H:%M')
    except: df_export['Data/Hora Lançamento'] = df_export['data_nota']

    df_export = df_export.rename(columns={
        'data_nota': 'Data do Recibo', 'Status_UI': 'Status', 'Atleta (Bolsa)': 'Atleta',
        'atleta_cpf': 'CPF do Atleta', 'Valor Bolsa': 'Bolsa Total', 
        'NFs Entregues Acumulado': 'NFs Entregues', 'valor': 'Valor Desta NF', 
        'Saldo Atual': 'Saldo Restante', 'Lançado por': 'Lançado por'
    })

    df_export['Atleta'] = df_export['Atleta'].apply(lambda x: str(x).split('(')[0].strip() if pd.notnull(x) else x)

    df_export = df_export.sort_values(by=['Atleta', 'Data/Hora Lançamento'], ascending=[True, False])

    ordem = ['Atleta', 'CPF do Atleta', 'Bolsa Total', 'NFs Entregues', 'Saldo Restante', 'Data/Hora Lançamento', 'Data do Recibo', 'Valor Desta NF', 'Status', 'Lançado por']
    df_export = df_export[[c for c in ordem if c in df_export.columns]]

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False, sheet_name='🗄️ Base de Dados')

        wb = writer.book
        ws_dash = wb.add_worksheet('📊 Dashboard Prime')

        f_head = wb.add_format({'bold': True, 'bg_color': '#1A1A1D', 'font_color': 'white', 'border': 1})
        f_money = wb.add_format({'num_format': 'R$ #,##0.00', 'border': 1})
        f_txt = wb.add_format({'border': 1})

        ws_base = writer.sheets['🗄️ Base de Dados']
        for i, col in enumerate(df_export.columns):
            w = 18 if 'R$' not in col else 15
            ws_base.set_column(i, i, w, f_money if any(x in col for x in ['Valor', 'Saldo', 'Bolsa', 'Entregues']) else None)

        # CÁLCULOS MACRO PARA O EXCEL
        resumo = df_export.groupby('Atleta').agg({
            'Bolsa Total': 'first', 'NFs Entregues': 'first', 'Saldo Restante': 'first'
        }).reset_index()

        # Inserção do Resumo Macro no Excel
        f_macro_label = wb.add_format({'bold': True, 'font_color': '#555'})
        f_macro_val = wb.add_format({'bold': True, 'num_format': 'R$ #,##0.00', 'font_size': 12})

        ws_dash.write('B6', 'Total de Bolsas (Global):', f_macro_label)
        ws_dash.write('C6', resumo['Bolsa Total'].sum(), f_macro_val)

        ws_dash.write('E6', 'Saldo Restante (Global):', f_macro_label)
        ws_dash.write('F6', resumo['Saldo Restante'].sum(), f_macro_val)

        # Lógica de Semaforização e Gráfico
        mes_idx = _converter_mes_para_int(mes)
        ano_int = int(ano)
        ultimo_dia = calendar.monthrange(ano_int, mes_idx)[1]
        hoje = date.today()
        dias_restantes = ultimo_dia - hoje.day
        is_reta_final = (dias_restantes <= 7 and dias_restantes >= 0 and hoje.month == mes_idx and hoje.year == ano_int)

        resumo['Saldo_Amarelo'] = 0
        resumo['Saldo_Vermelho'] = 0
        resumo['Saldo_Azul'] = 0

        for idx, r in resumo.iterrows():
            bolsa = float(r['Bolsa Total'])
            saldo = float(r['Saldo Restante'])
            perc = saldo / bolsa if bolsa > 0 else 0

            if is_reta_final: resumo.at[idx, 'Saldo_Vermelho'] = saldo
            elif perc > 0.60: resumo.at[idx, 'Saldo_Vermelho'] = saldo
            elif perc >= 0.50: resumo.at[idx, 'Saldo_Amarelo'] = saldo
            else: resumo.at[idx, 'Saldo_Azul'] = saldo

        # Tabela Detalhada (movida para linha 9 por causa do resumo macro)
        start_row = 9
        ws_dash.write(f'B{start_row}', 'ATLETA', f_head)
        ws_dash.write(f'C{start_row}', 'ENTREGUE (VERDE)', f_head)
        ws_dash.write(f'D{start_row}', 'SALDO (AZUL)', f_head)
        ws_dash.write(f'E{start_row}', 'SALDO (AMARELO)', f_head)
        ws_dash.write(f'F{start_row}', 'SALDO (VERMELHO)', f_head)

        row = start_row
        for _, r in resumo.iterrows():
            ws_dash.write(row, 1, r['Atleta'], f_txt)
            ws_dash.write(row, 2, r['NFs Entregues'], f_money)
            ws_dash.write(row, 3, r['Saldo_Azul'], f_money)
            ws_dash.write(row, 4, r['Saldo_Amarelo'], f_money)
            ws_dash.write(row, 5, r['Saldo_Vermelho'], f_money)
            row += 1

        chart = wb.add_chart({'type': 'bar', 'subtype': 'stacked'})

        # Atualizando referências do gráfico para a nova posição (linha 9)
        chart.add_series({
            'name': 'Já Recebido',
            'categories': ['📊 Dashboard Prime', start_row, 1, row-1, 1],
            'values':     ['📊 Dashboard Prime', start_row, 2, row-1, 2],
            'fill':       {'color': '#28a745'},
            'data_labels': {'value': True, 'font_color': 'white', 'num_format': 'R$ #,##0;;'}
        })

        chart.add_series({
            'name': 'Saldo (Em dia)',
            'values':     ['📊 Dashboard Prime', start_row, 3, row-1, 3],
            'fill':       {'color': '#0056b3'},
            'data_labels': {'value': True, 'font_color': 'white', 'num_format': 'R$ #,##0;;'}
        })

        chart.add_series({
            'name': 'Saldo (Atenção 50-60%)',
            'values':     ['📊 Dashboard Prime', start_row, 4, row-1, 4],
            'fill':       {'color': '#ffc107'},
            'data_labels': {'value': True, 'font_color': 'black', 'num_format': 'R$ #,##0;;'}
        })

        chart.add_series({
            'name': 'Saldo (Crítico/Reta Final)',
            'values':     ['📊 Dashboard Prime', start_row, 5, row-1, 5],
            'fill':       {'color': '#dc3545'},
            'data_labels': {'value': True, 'font_color': 'white', 'num_format': 'R$ #,##0;;'}
        })

        chart.set_title({'name': 'Status Financeiro da Equipe (Semaforização)'})
        chart.set_size({'width': 700, 'height': 450})
        chart.set_legend({'position': 'bottom'})

        ws_dash.insert_chart(f'H{start_row}', chart)

        cfg = db.obter_config_rodape()
        ws_dash.write(row+2, 1, f"Relatório gerado em: {date.today().strftime('%d/%m/%Y')}", wb.add_format({'italic': True}))
        ws_dash.write(row+3, 1, f"© {cfg.get('copyright','NSG')} - {cfg.get('versao','v1.0')}", wb.add_format({'italic': True, 'font_color': '#777'}))

    return buffer

# [admin_exportacao.py][Painel Macro Bolsas/Saldos + Gráfico Ajustado][2026-02-26 15:30][v3.4][245 linhas]