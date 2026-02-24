import os
import time
import smtplib
import pandas as pd
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
    lan = supabase.table('lancamentos').select("*, atletas(nome, email, data_nascimento, sexo, limite_mensal, categoria), visitantes(nome, email)").order('created_at', desc=True).execute()
    return atl.data, vis.data, lan.data

def cadastrar_novo_atleta(nome, cpf, data_nascimento, sexo, limite_mensal, email, senha):
    dados = {"nome": nome, "cpf": cpf, "data_nascimento": str(data_nascimento), "sexo": sexo, "limite_mensal": float(limite_mensal), "saldo": float(limite_mensal), "email": email, "senha": senha}
    try:
        supabase.table('atletas').insert(dados).execute()
        return True
    except:
        return False

def atualizar_usuario(tipo, identificador, novo_email, nova_senha=None):
    tabela = 'atletas' if tipo == 'atleta' else 'visitantes'
    coluna_id = 'cpf' if tipo == 'atleta' else 'id'
    dados_update = {"email": novo_email}
    if nova_senha: dados_update["senha"] = nova_senha
    supabase.table(tabela).update(dados_update).eq(coluna_id, identificador).execute()
    return True

def notificar_status_nf(email, nome_atleta, status, valor, data_nota, lancador, foto_url):
    assunto = f"Auditoria NotaFácil: Status Atualizado - {status}"

    # Adiciona instrução extra se for reprovada
    msg_extra = "<p style='color: #d9534f;'><b>Atenção:</b> Seu lançamento foi reprovado (motivos comuns: fora da política, valor incorreto ou <b>foto ilegível</b>). O saldo foi estornado para sua bolsa. Por favor, faça um <b>novo lançamento</b> com os dados/foto corretos.</p>" if "❌" in status else ""

    html = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
        <h2 style="color: #0056b3;">Atualização de Lançamento</h2>
        <p>Olá, <b>{nome_atleta}</b>!</p>
        <p>A nota fiscal lançada em seu nome passou por auditoria e teve o status atualizado:</p>
        <ul>
            <li><b>Lançador:</b> {lancador}</li>
            <li><b>Data da NF:</b> {data_nota}</li>
            <li><b>Valor:</b> R$ {float(valor):,.2f}</li>
            <li><b style="font-size: 16px;">Novo Status: {status}</b></li>
        </ul>
        {msg_extra}
        <p>Para conferir o comprovante anexado, <a href="{foto_url}" target="_blank">clique aqui</a>.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #777;">Equipe Administrativa - NotaFácil Prime</p>
    </div>
    """
    return enviar_email_relatorio(email, assunto, html)

def alterar_status_nota(id_nota, cpf_atleta, valor, status_atual, novo_status, email_dest, nome_atleta, data_nota, lancador, foto_url):
    if "❌ Reprovada" in novo_status and "❌ Reprovada" not in status_atual:
        if cpf_atleta:
            atl = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
            if atl.data:
                supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) + float(valor)}).eq('cpf', cpf_atleta).execute()

    elif "❌ Reprovada" in status_atual and "❌ Reprovada" not in novo_status:
        if cpf_atleta:
            atl = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
            if atl.data:
                supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) - float(valor)}).eq('cpf', cpf_atleta).execute()

    supabase.table('lancamentos').update({'status': novo_status}).eq('id', id_nota).execute()

    if email_dest:
        notificar_status_nf(email_dest, nome_atleta, novo_status, valor, data_nota, lancador, foto_url)

def excluir_nota_fiscal(id_nota, cpf_atleta, valor_nota):
    if cpf_atleta:
        atl = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
        if atl.data:
            supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) + float(valor_nota)}).eq('cpf', cpf_atleta).execute()
    supabase.table('lancamentos').delete().eq('id', id_nota).execute()

def editar_valor_nota(id_nota, cpf_atleta, valor_antigo, valor_novo):
    diferenca = float(valor_novo) - float(valor_antigo)
    if cpf_atleta:
        atl = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
        if atl.data:
            supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) - diferenca}).eq('cpf', cpf_atleta).execute()
    supabase.table('lancamentos').update({'valor': valor_novo}).eq('id', id_nota).execute()

def salvar_nota_fiscal(valor, data_nota, arquivo, cpf=None, v_id=None):
    if arquivo:
        ref = cpf if cpf else v_id
        nome_f = f"{ref}_{int(time.time())}_{arquivo.name}"
        supabase.storage.from_("comprovantes").upload(path=nome_f, file=arquivo.getvalue())
        foto_url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/comprovantes/{nome_f}"
        supabase.table('lancamentos').insert({"valor": valor, "data_nota": str(data_nota), "status": "❓ Pendente", "foto_url": foto_url, "atleta_cpf": cpf, "visitante_id": v_id}).execute()
        if cpf:
            atl = supabase.table('atletas').select('saldo').eq('cpf', cpf).execute()
            if atl.data:
                supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) - valor}).eq('cpf', cpf).execute()

def upsert_visitante(dados):
    res = supabase.table('visitantes').upsert(dados, on_conflict='email').execute()
    return res.data[0]['id']

def log_exportacao(admin, destino, filtro):
    supabase.table('logs_exportacao').insert({"admin_email": admin, "destinatario_email": destino, "filtro_periodo": filtro}).execute()

def enviar_email_relatorio(destinatario, assunto, conteudo_html):
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
    except:
        return False

def recuperar_senha(email, nome, senha_atual):
    assunto = "Recuperação de Senha - NotaFácil Prime"
    html = f"<h3>Olá, {nome}!</h3><p>Sua senha: <b>{senha_atual}</b></p>"
    return enviar_email_relatorio(email, assunto, html)

def formatar_saldo_mask(saldo, eh_privilegiado=False):
    TETO = 500.0
    return f"R$ {saldo:,.2f}" if eh_privilegiado or saldo <= TETO else f"R$ {TETO:,.0f}+"

def calcular_tag_3x3(sexo, data_nasc):
    if not data_nasc or not sexo: return "⚪ SEM_DADOS"
    hoje = date.today()
    nasc = pd.to_datetime(data_nasc).date()
    idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    if sexo == "F": return "🟪 3X3_FEM"
    return "🟦 3X3_M_BASE" if idade <= 18 else "🟥 3X3_M_ELITE"

# [database.py][Motor de Dados, E-mail Unificado para Reprovação][2026-02-24 19:20][v2.10][132 linhas]