import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def _conectar_smtp(usr, pwd, destinatario, msg):
    """Função interna para evitar repetição de código SMTP"""
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(usr, pwd)
        s.sendmail(usr, destinatario, msg.as_string())
        s.quit()
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        return False, f"Erro SMTP: {str(e)}"

def enviar_relatorio(destinatario, assunto, html_body):
    """Dispara relatórios da Sala de Guerra"""
    usr = os.environ.get("EMAIL_USER")
    pwd = os.environ.get("EMAIL_PASS")
    if not usr or not pwd: return False, "Credenciais de e-mail não configuradas."

    msg = MIMEMultipart()
    msg['From'] = usr
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(html_body, 'html'))
    return _conectar_smtp(usr, pwd, destinatario, msg)

def recuperar_senha_usuario(email_user, nome_user, senha_real):
    """Dispara a senha atual para o e-mail do atleta/visitante"""
    usr = os.environ.get("EMAIL_USER")
    pwd = os.environ.get("EMAIL_PASS")
    if not usr or not pwd: return False, "Credenciais de e-mail não configuradas."

    assunto = "Recuperação de Acesso - NotaFácil Prime"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2>Recuperação de Acesso</h2>
        <p>Olá, <strong>{nome_user}</strong>.</p>
        <p>Sua senha atual para acessar o sistema é: <strong style="color: #0056b3; font-size: 18px;">{senha_real}</strong></p>
        <p>Guarde-a com segurança!</p>
        <br><p>Equipe NotaFácil Prime</p>
    </div>
    """
    msg = MIMEMultipart()
    msg['From'] = usr
    msg['To'] = email_user
    msg['Subject'] = assunto
    msg.attach(MIMEText(html_body, 'html'))
    return _conectar_smtp(usr, pwd, email_user, msg)

def recuperar_senha_admin(senha_master, email_destino):
    """Dispara a senha Master para o e-mail da Diretoria (Dinâmico)"""
    usr = os.environ.get("EMAIL_USER")
    pwd = os.environ.get("EMAIL_PASS")
    if not usr or not pwd: return False, "SMTP não configurado."

    html = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2>Acesso Administrativo</h2>
        <p>A senha Master atual da Central de Governança é:</p>
        <p><strong style="color: #d9534f; font-size: 24px;">{senha_master}</strong></p>
        <p><i>Esta é uma mensagem automática do sistema de segurança.</i></p>
    </div>
    """
    msg = MIMEMultipart()
    msg['From'] = usr
    msg['To'] = email_destino
    msg['Subject'] = "🔐 Recuperação: Senha Master - NotaFácil Prime"
    msg.attach(MIMEText(html, 'html'))
    return _conectar_smtp(usr, pwd, email_destino, msg)

# [servicos_email.py][Remoção do e-mail hardcoded][2026-02-26 09:30][v1.1][68 linhas]