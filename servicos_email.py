import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import database as db

# --- MOTOR VISUAL DE E-MAIL ---
def _montar_rodape():
    """Gera o HTML do rodapé oficial com base nos dados do banco"""
    cfg = db.obter_config_rodape()

    html = f"""
    <br><br>
    <div style="background-color: #f4f4f4; padding: 20px; border-top: 3px solid #0056b3; font-family: Arial, sans-serif; font-size: 12px; color: #555;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td style="padding-bottom: 10px;">
                    <strong style="font-size: 14px; color: #333;">🏢 NotaFácil Prime</strong><br>
                    <span style="color: #777;">Sistema de Governança Financeira</span>
                </td>
            </tr>
            <tr>
                <td style="padding-bottom: 10px;">
                    <p style="margin: 5px 0;">📍 <strong>Suporte:</strong> {cfg['whatsapp']} | 📧 <strong>Contato:</strong> contato@driblecerto.com</p>
                    <p style="margin: 5px 0;">📸 <strong>Instagram:</strong> <a href="https://instagram.com/{cfg['instagram'].replace('@','')}" style="color: #0056b3; text-decoration: none;">{cfg['instagram']}</a></p>
                </td>
            </tr>
            <tr>
                <td style="border-top: 1px solid #ddd; padding-top: 10px; font-size: 11px; color: #999;">
                    © 2026 {cfg['copyright']}. Todos os direitos reservados.<br>
                    Versão do Sistema: <strong>{cfg['versao']}</strong> | 🔒 Ambiente Seguro SSL
                </td>
            </tr>
        </table>
    </div>
    """
    return html

def _conectar_smtp(usr, pwd, destinatario, msg):
    """Função interna para envio SMTP"""
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(usr, pwd)
        s.sendmail(usr, destinatario, msg.as_string())
        s.quit()
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        return False, f"Erro SMTP: {str(e)}"

# --- FUNÇÕES PÚBLICAS DE ENVIO ---
def enviar_relatorio(destinatario, assunto, html_body):
    usr = os.environ.get("EMAIL_USER")
    pwd = os.environ.get("EMAIL_PASS")
    if not usr or not pwd: return False, "Credenciais de e-mail não configuradas."

    # Injeta o rodapé no corpo do e-mail
    corpo_completo = html_body + _montar_rodape()

    msg = MIMEMultipart()
    msg['From'] = usr
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo_completo, 'html'))
    return _conectar_smtp(usr, pwd, destinatario, msg)

def recuperar_senha_usuario(email_user, nome_user, senha_real):
    usr = os.environ.get("EMAIL_USER")
    pwd = os.environ.get("EMAIL_PASS")
    if not usr or not pwd: return False, "Credenciais de e-mail não configuradas."

    assunto = "Recuperação de Acesso - NotaFácil Prime"
    # Conteúdo específico + Rodapé automático
    html_core = f"""
    <div style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
        <h2 style="color: #0056b3;">🔐 Recuperação de Acesso</h2>
        <p>Olá, <strong>{nome_user}</strong>.</p>
        <p>Recebemos uma solicitação para recuperar sua senha de acesso.</p>
        <div style="background-color: #eef; padding: 15px; border-radius: 5px; margin: 20px 0; display: inline-block;">
            Senha Atual: <strong style="color: #0056b3; font-size: 20px; letter-spacing: 2px;">{senha_real}</strong>
        </div>
        <p>Recomendamos que você apague este e-mail após memorizar a senha.</p>
    </div>
    """

    msg = MIMEMultipart()
    msg['From'] = usr
    msg['To'] = email_user
    msg['Subject'] = assunto
    msg.attach(MIMEText(html_core + _montar_rodape(), 'html'))
    return _conectar_smtp(usr, pwd, email_user, msg)

def recuperar_senha_admin(senha_master, email_destino):
    usr = os.environ.get("EMAIL_USER")
    pwd = os.environ.get("EMAIL_PASS")
    if not usr or not pwd: return False, "SMTP não configurado."

    html_core = f"""
    <div style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
        <h2 style="color: #d9534f;">🚨 Acesso Administrativo Master</h2>
        <p>Esta é uma notificação de segurança da Central de Governança.</p>
        <p>A senha Master atual é:</p>
        <p><strong style="font-size: 24px; background-color: #fee; padding: 5px 10px;">{senha_master}</strong></p>
    </div>
    """

    msg = MIMEMultipart()
    msg['From'] = usr
    msg['To'] = email_destino
    msg['Subject'] = "🔐 Recuperação: Senha Master - NotaFácil Prime"
    msg.attach(MIMEText(html_core + _montar_rodape(), 'html'))
    return _conectar_smtp(usr, pwd, email_destino, msg)

# [servicos_email.py][Rodapé HTML Oficial Prime Integrado][2026-02-26 10:15][v1.2][112 linhas]