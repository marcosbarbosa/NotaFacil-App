import os
import base64
from supabase import create_client, Client

def conectar() -> Client:
    """Inicializa a conexão segura com o Supabase validando os Secrets do Replit"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("⚠️ ERRO CRÍTICO: SUPABASE_URL ou SUPABASE_KEY ausentes nos Secrets!")

    return create_client(url, key)

# Inicialização global da conexão
try:
    supabase = conectar()
except Exception as e:
    print(f"Falha ao conectar com o banco de dados: {e}")
    supabase = None

# --- MÓDULO VISUAL (Adormecido para otimização de performance) ---
def obter_imagem_fundo_db() -> str | None:
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'background_b64').execute()
        return res.data[0]['valor'] if res.data else None
    except: return None

def salvar_imagem_fundo_db(binario_imagem) -> tuple[bool, str]:
    try:
        b64_string = base64.b64encode(binario_imagem).decode()
        supabase.table('configuracoes').upsert({'chave': 'background_b64', 'valor': b64_string}).execute()
        return True, "✅ Identidade visual atualizada!"
    except Exception as e: return False, str(e)

# --- MÓDULO DE GOVERNANÇA FINANCEIRA (BI) ---
def obter_limite_alerta() -> float:
    """Recupera o gatilho de saldo crítico para o Dashboard"""
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'limite_alerta').execute()
        return float(res.data[0]['valor']) if res.data else 5000.0
    except: return 5000.0

def salvar_limite_alerta(novo_limite: float) -> tuple[bool, str]:
    """Salva o novo limite de alerta de risco no banco de dados"""
    try:
        supabase.table('configuracoes').upsert({'chave': 'limite_alerta', 'valor': str(novo_limite)}).execute()
        return True, "✅ Limite de alerta de risco atualizado!"
    except Exception as e: return False, str(e)

# --- MÓDULO DE SEGURANÇA E COMUNICAÇÃO ---
def obter_senha_admin() -> str:
    """Recupera a chave mestra da Sala de Guerra"""
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'senha_admin').execute()
        return res.data[0]['valor'] if res.data else "admin"
    except: return "admin"

def obter_email_admin() -> str:
    """Busca o e-mail do administrador com fallback para o oficial"""
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'email_admin').execute()
        valor = res.data[0]['valor'] if res.data else ""
        return valor if valor else "marcosbarbosa.am@gmail.com"
    except: return "marcosbarbosa.am@gmail.com"

def salvar_email_admin(novo_email: str) -> tuple[bool, str]:
    """Permite alterar o e-mail de destino dos relatórios executivos"""
    try:
        supabase.table('configuracoes').upsert({'chave': 'email_admin', 'valor': novo_email}).execute()
        return True, "✅ E-mail padrão da diretoria atualizado!"
    except Exception as e: return False, str(e)

def obter_config_rodape() -> dict:
    """Gera as informações institucionais para o rodapé dos e-mails e relatórios"""
    padrao = {"instagram": "@driblecerto", "whatsapp": "(92) 99981-0256", "versao": "v1.0.0", "copyright": "NSG Basquete"}
    try:
        res = supabase.table('configuracoes').select('*').in_('chave', list(padrao.keys())).execute()
        if res.data:
            for item in res.data: padrao[item['chave']] = item['valor']
    except: pass
    return padrao

# [db_config.py][Alicerce Blindado v12.0][2026-02-27]
# Total de Linhas de Código: 77