import os
import base64
from supabase import create_client, Client

def conectar():
    """Inicializa a conexão segura com o Supabase"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

supabase = conectar()

def obter_imagem_fundo_db():
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'background_b64').execute()
        return res.data[0]['valor'] if res.data else None
    except: return None

def salvar_imagem_fundo_db(binario_imagem):
    try:
        b64_string = base64.b64encode(binario_imagem).decode()
        supabase.table('configuracoes').upsert({'chave': 'background_b64', 'valor': b64_string}).execute()
        return True, "✅ Identidade visual atualizada!"
    except Exception as e: return False, str(e)

def obter_limite_alerta():
    """Recupera o gatilho de saldo crítico"""
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'limite_alerta').execute()
        return float(res.data[0]['valor']) if res.data else 5000.0
    except: return 5000.0

def salvar_limite_alerta(novo_limite):
    """Salva o novo limite de alerta no banco de dados"""
    try:
        supabase.table('configuracoes').upsert({'chave': 'limite_alerta', 'valor': str(novo_limite)}).execute()
        return True, "✅ Limite de alerta atualizado!"
    except Exception as e: return False, str(e)

def obter_senha_admin():
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'senha_admin').execute()
        return res.data[0]['valor'] if res.data else "admin"
    except: return "admin"

def obter_email_admin():
    """Busca o e-mail do administrador com fallback inteligente"""
    try:
        res = supabase.table('configuracoes').select('valor').eq('chave', 'email_admin').execute()
        valor = res.data[0]['valor'] if res.data else ""
        return valor if valor else "diretoria@nsg.com"
    except: return "diretoria@nsg.com"

# --- A FUNÇÃO QUE FALTAVA ---
def salvar_email_admin(novo_email):
    """Permite que o administrador altere o e-mail de destino do BI"""
    try:
        supabase.table('configuracoes').upsert({'chave': 'email_admin', 'valor': novo_email}).execute()
        return True, "✅ E-mail padrão da diretoria atualizado!"
    except Exception as e: return False, str(e)

def obter_config_rodape():
    padrao = {"instagram": "@driblecerto", "whatsapp": "(11) 99999-9999", "versao": "v1.0.0", "copyright": "NSG Basquete"}
    try:
        res = supabase.table('configuracoes').select('*').in_('chave', list(padrao.keys())).execute()
        if res.data:
            for item in res.data: padrao[item['chave']] = item['valor']
    except: pass
    return padrao

# [db_config.py][Lógica de Negócio Prime Restaurada][2026-02-26]