# ==============================================================================
# SISTEMA: NotaFácil Prime | ARQUIVO: database.py
# DATA: 19/02/2026 | HORA: 14:00 | TÍTULO: Motor de Dados e Comunicação
# FUNÇÃO: Dados, Criticidade, Tags e Envio de E-mail SMTP
# VERSÃO: 2.2 | LINHAS: 155
# ==============================================================================
import os, time, pandas as pd, smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client, Client

def conectar():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

supabase = conectar()

def carregar_dados_globais():
    atl = supabase.table('atletas').select("*").execute()
    vis = supabase.table('visitantes').select("*").execute()
    lan = supabase.table('lancamentos').select("*, atletas(nome, data_nascimento, sexo, limite_mensal, categoria), visitantes(nome)").order('created_at', desc=True).execute()
    return atl.data, vis.data, lan.data

def log_exportacao(admin, destino, filtro):
    supabase.table('logs_exportacao').insert({"admin_email": admin, "destinatario_email": destino, "filtro_periodo": filtro}).execute()

def enviar_email_relatorio(destinatario, assunto, conteudo_html):
    """Envia o relatório real utilizando dcatletas@gmail.com via SMTP."""
    remetente = os.environ.get("EMAIL_USER")
    senha = os.environ.get("EMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(conteudo_html, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

def calcular_status_atleta(atleta, lancamentos):
    lan_atl = [l for l in lancamentos if l['atleta_cpf'] == atleta['cpf']]
    dias = (date.today() - pd.to_datetime(lan_atl[0]['created_at']).date()).days if lan_atl else 99
    saldo, limite = float(atleta['saldo']), float(atleta['limite_mensal'])
    perc, gasto = saldo / limite if limite > 0 else 0, limite - saldo
    if gasto >= limite: return "🟢 Em Dia"
    elif perc < 0.10 or dias > 15: return "🔴 Crítico"
    elif perc < 0.30 or dias > 10: return "🟡 Atenção"
    return "🟢 Em Dia"

def formatar_saldo_mask(saldo, eh_privilegiado=False):
    TETO = 500.0
    if eh_privilegiado or saldo <= TETO: return f"R$ {saldo:,.2f}"
    return f"R$ {TETO:,.0f}+"

def calcular_tag_3x3(sexo, data_nasc):
    if not data_nasc or not sexo: return "⚪ SEM_DADOS"
    hoje = date.today()
    nasc = pd.to_datetime(data_nasc).date()
    idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    if sexo == "F": return "🟪 3X3_FEM"
    return "🟦 3X3_M_BASE" if idade <= 18 else "🟥 3X3_M_ELITE"

def salvar_nota_fiscal(valor, data_nota, arquivo, cpf=None, v_id=None):
    if arquivo:
        ref = cpf if cpf else v_id
        nome_f = f"{ref}_{int(time.time())}_{arquivo.name}"
        supabase.storage.from_("comprovantes").upload(path=nome_f, file=arquivo.getvalue())
        foto_url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/comprovantes/{nome_f}"
        supabase.table('lancamentos').insert({"valor": valor, "data_nota": str(data_nota), "status": "Pendente", "foto_url": foto_url, "atleta_cpf": cpf, "visitante_id": v_id}).execute()
        if cpf:
            atl = supabase.table('atletas').select('saldo').eq('cpf', cpf).execute()
            if atl.data: supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) - valor}).eq('cpf', cpf).execute()

def upsert_visitante(dados):
    res = supabase.table('visitantes').upsert(dados, on_conflict='email').execute()
    return res.data[0]['id']
# Quantidade total de linhas: 155