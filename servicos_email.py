import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import database as db

# --- CONFIGURAÇÕES DE SERVIDOR ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # Protocolo SSL Seguro

# Segurança Máxima: Puxa do ambiente de forma invisível no Render
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
            'versao': '1.5.0'
        }

    html = f"""
    <br><br>
    <div style="background-color: #f4f4f4; padding: 20px; border-top: 3px solid #ffc107; font-family: Arial, sans-serif; font-size: 12px; color: #555;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td style="padding-bottom: 10px;">
                    <strong style="font-size: 14px; color: #333;">🏢 NotaFácil | DC</strong><br>
                    <span style="color: #777;">Sistema de Governança Financeira</span>
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
                    Versão do Sistema: <strong>{cfg['versao']}</strong> | 🔒 Governança Prime 
                </td>
            </tr>
        </table>
    </div>
    """
    return html

def _enviar_base(destinatario: str, assunto: str, html_corpo: str) -> tuple[bool, str]:
    """Motor de envio SSL com diagnóstico de erros aprimorado"""
    if not EMAIL_USER or not EMAIL_PASS:
        return False, "⚠️ Credenciais de e-mail não encontradas nas Variáveis de Ambiente!"

    try:
        msg = MIMEMultipart()
        msg['From'] = f"NotaFácil | DC <{EMAIL_USER}>"
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
        return False, "❌ Falha de Autenticação: A Senha de App do Google está incorreta ou foi revogada."
    except Exception as e:
        return False, f"❌ Erro de Conexão SMTP: {str(e)}"

# --- FUNÇÕES PÚBLICAS DE INTERFACE ---

def enviar_relatorio(destinatario: str, assunto: str, html_body: str) -> tuple[bool, str]:
    """Dispara relatórios de BI e LOGS com o template executivo"""
    return _enviar_base(destinatario, assunto, html_body)

def recuperar_senha_usuario(email_user: str, nome_user: str, senha_real: str) -> tuple[bool, str]:
    """Envia chave de acesso para Atletas e Visitantes"""
    assunto = "🔐 Recuperação de Acesso - NotaFácil | DC"
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

def disparar_radar_matinal(email_destino: str, atletas_pendentes: list) -> tuple[bool, str]:
    """Motor BI Prime: Dispara o relatório das 05:00 AM com saldos devedores"""
    assunto = "📊 RADAR DE GOVERNANÇA: Saldos a Repor (Atenção Diretoria)"

    # Constrói a tabela dinamicamente com os atletas que devem notas
    linhas_tabela = ""
    total_devedor = 0.0

    for atl in atletas_pendentes:
        saldo_repor = float(atl['bolsa']) - float(atl['saldo'])
        if saldo_repor > 0:  # Só mostra quem realmente deve reposição
            linhas_tabela += f"""
            <tr>
                <td style='padding: 8px; border-bottom: 1px solid #ddd;'><b>{atl['nome']}</b></td>
                <td style='padding: 8px; border-bottom: 1px solid #ddd; color: #555;'>{atl['cpf']}</td>
                <td style='padding: 8px; border-bottom: 1px solid #ddd; color: #d9534f; font-weight: bold;'>R$ {saldo_repor:.2f}</td>
            </tr>
            """
            total_devedor += saldo_repor

    if not linhas_tabela:
        linhas_tabela = "<tr><td colspan='3' style='text-align: center; padding: 15px;'>Nenhuma pendência. Todos os saldos estão zerados! 🎉</td></tr>"

    html_core = f"""
    <div style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
        <h2 style="color: #212529; border-bottom: 2px solid #ffc107; padding-bottom: 10px;">⏰ Radar Matinal de Pendências</h2>
        <p>Bom dia, Diretoria.</p>
        <p>Segue o extrato atualizado dos atletas que possuem <b>saldo pendente de comprovação (Notas Fiscais)</b>.</p>

        <table style='width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;'>
            <tr style='background-color: #f8f9fa; text-align: left;'>
                <th style='padding: 10px; border-bottom: 2px solid #dee2e6;'>Atleta</th>
                <th style='padding: 10px; border-bottom: 2px solid #dee2e6;'>CPF</th>
                <th style='padding: 10px; border-bottom: 2px solid #dee2e6;'>A Repor em NFs</th>
            </tr>
            {linhas_tabela}
        </table>

        <div style="background-color: #fff3cd; color: #856404; padding: 15px; border-left: 5px solid #ffeeba; margin-top: 20px;">
            <b>Montante Total Pendente na Base:</b> <span style="font-size: 18px;">R$ {total_devedor:.2f}</span>
        </div>
        <p style="font-size: 11px; color: #999; margin-top: 20px;">Este é um alerta automático. Para alterar a frequência, acesse Configurações no sistema.</p>
    </div>
    """
    return _enviar_base(email_destino, assunto, html_core)

# [servicos_email.py][v9.2 - Rebranding Minimalista][2026-02-27]