import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import database as db

# --- CONFIGURAÇÕES DE SERVIDOR ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # Protocolo SSL Seguro

# Segurança Máxima: Puxa do cadeado do Replit de forma invisível
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

# --- MOTOR VISUAL DE E-MAIL ---
def _montar_rodape() -> str:
    """Gera o HTML do rodapé oficial com blindagem contra falhas de banco"""
    try:
        cfg = db.obter_config_rodape()
    except:
        # Fallback de segurança caso o banco demore a responder
        cfg = {
            'whatsapp': '(92) 99981-0256', 
            'instagram': '@driblecerto', 
            'copyright': 'Drible Certo', 
            'versao': '1.0.0'
        }

    html = f"""
    <br><br>
    <div style="background-color: #f4f4f4; padding: 20px; border-top: 3px solid #ffc107; font-family: Arial, sans-serif; font-size: 12px; color: #555;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td style="padding-bottom: 10px;">
                    <strong style="font-size: 14px; color: #333;">🏢 NotaFácil Prime | NSG</strong><br>
                    <span style="color: #777;">Sistema de Governança Financeira de Elite</span>
                </td>
            </tr>
            <tr>
                <td style="padding-bottom: 10px;">
                    <p style="margin: 5px 0;">📍 <strong>Suporte:</strong> {cfg['whatsapp']} | 📧 <strong>Contato:</strong> marcosbarbosa.am@gmail.com</p>
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

def _enviar_base(destinatario: str, assunto: str, html_corpo: str) -> tuple[bool, str]:
    """Motor de envio SSL com diagnóstico de erros aprimorado"""
    if not EMAIL_USER or not EMAIL_PASS:
        return False, "⚠️ Credenciais de e-mail não encontradas na aba Secrets!"

    try:
        msg = MIMEMultipart()
        msg['From'] = f"NotaFácil Prime <{EMAIL_USER}>"
        msg['To'] = destinatario
        msg['Subject'] = assunto

        # Injeta o rodapé oficial automaticamente
        corpo_final = html_corpo + _montar_rodape()
        msg.attach(MIMEText(corpo_final, 'html'))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return True, "✅ E-mail enviado com sucesso!"

    except smtplib.SMTPAuthenticationError:
        return False, "❌ Falha de Autenticação: A Senha de App do Google inserida nos Secrets está incorreta ou foi revogada."
    except Exception as e:
        return False, f"❌ Erro de Conexão SMTP: {str(e)}"

# --- FUNÇÕES PÚBLICAS DE INTERFACE ---

def enviar_relatorio(destinatario: str, assunto: str, html_body: str) -> tuple[bool, str]:
    """Dispara relatórios de BI com o template executivo"""
    return _enviar_base(destinatario, assunto, html_body)

def recuperar_senha_usuario(email_user: str, nome_user: str, senha_real: str) -> tuple[bool, str]:
    """Envia chave de acesso para Atletas e Visitantes"""
    assunto = "🔐 Recuperação de Acesso - NotaFácil Prime"
    html_core = f"""
    <div style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
        <h2 style="color: #ffc107;">🔐 Recuperação de Acesso</h2>
        <p>Olá, <strong>{nome_user}</strong>.</p>
        <p>Recebemos uma solicitação para recuperar sua senha de acesso ao portal.</p>
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 5px solid #ffc107; margin: 20px 0;">
            Sua Senha Atual: <strong style="font-size: 20px; letter-spacing: 2px;">{senha_real}</strong>
        </div>
        <p><b>Dica de Segurança:</b> Memorize sua senha e apague este e-mail.</p>
    </div>
    """
    return _enviar_base(email_user, assunto, html_core)

def recuperar_senha_admin(senha_master: str, email_destino: str) -> tuple[bool, str]:
    """Alerta de segurança para envio da Senha Mestra"""
    assunto = "🛡️ ALERTA: Recuperação de Senha Master"
    html_core = f"""
    <div style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
        <h2 style="color: #d9534f;">🚨 Acesso Administrativo Master</h2>
        <p>Este é um alerta de segurança da <b>Sala de Guerra</b>.</p>
        <p>Abaixo está a chave mestra solicitada para acesso à Central de Governança:</p>
        <div style="background-color: #fee; color: #d9534f; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
            <strong style="font-size: 26px; letter-spacing: 4px;">{senha_master}</strong>
        </div>
        <p style="font-size: 12px; color: #999;">Aviso: O acesso via senha master é monitorado e registrado.</p>
    </div>
    """
    return _enviar_base(email_destino, assunto, html_core)

# [servicos_email.py][v9.0 - Blindagem SSL & Diagnóstico SMTP][2026-02-27]
# Total de Linhas de Código: 111