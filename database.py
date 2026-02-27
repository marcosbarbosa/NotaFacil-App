# database.py - O Unificador Prime 🛡️
from db_config import *
from db_entidades import *
from db_financeiro import *

# --- NÚCLEO DE DADOS E SINCRONIZAÇÃO ---

def carregar_dados_globais():
    """Restaura a visão global unificando os novos módulos"""
    atl, vis = carregar_usuarios()
    lan = carregar_lancamentos()
    return atl, vis, lan

def upsert_atleta(dados):
    """Salva ou atualiza um atleta no banco de dados"""
    try:
        # Usa o CPF como chave única para evitar duplicidade
        res = supabase.table("atletas").upsert(dados, on_conflict="cpf").execute()
        return True, "Atleta salvo com sucesso!"
    except Exception as e:
        return False, str(e)

def upsert_visitante(dados):
    """Salva ou atualiza um membro da diretoria/visitante"""
    try:
        # Resolve o erro de 'attribute not found'
        res = supabase.table("visitantes").upsert(dados, on_conflict="email").execute()
        return True, "Membro salvo com sucesso!"
    except Exception as e:
        # INDENTAÇÃO CORRIGIDA: O return agora está dentro do bloco except
        return False, str(e)

# --- MOTOR DE AUDITORIA E GOVERNANÇA ---

def alterar_status_nota(id_nota, cpf_atleta, valor, novo_status, id_admin=None):
    """
    Função de Auditoria: Aprova/Reprova notas e recalcula o saldo do atleta.
    Aceita 5 argumentos para resolver o TypeError do sistema.
    """
    try:
        # 1. Atualiza o status da nota na tabela de lançamentos
        supabase.table("lancamentos").update({"status": novo_status}).eq("id", id_nota).execute()

        # 2. Se a nota for APROVADA, deduz o valor do saldo do atleta
        if novo_status == "Aprovado" or novo_status == "✅ Aprovada":
            res_atl = supabase.table("atletas").select("saldo").eq("cpf", cpf_atleta).execute()
            if res_atl.data:
                saldo_atual = res_atl.data[0]['saldo']
                novo_saldo = saldo_atual - valor
                supabase.table("atletas").update({"saldo": novo_saldo}).eq("cpf", cpf_atleta).execute()

        return True, f"Nota {novo_status} com sucesso!"
    except Exception as e:
        return False, str(e)

# --- INTELIGÊNCIA BI (TAGS 3X3) ---

def calcular_tag_3x3(saldo, bolsa):
    """
    Inteligência BI: Define a categoria de risco do atleta.
    Define se o saldo está Azul, Amarelo ou Vermelho.
    """
    if bolsa <= 0: 
        return "SALDO (AZUL)"

    percentual = (saldo / bolsa)

    # Lógica baseada no Dashboard Prime
    if percentual > 0.60:
        return "SALDO (VERMELHO)" # Risco crítico
    elif percentual >= 0.40:
        return "SALDO (AMARELO)" # Alerta
    else:
        return "SALDO (AZUL)"    # Saudável

# --- CONFIGURAÇÕES DE GOVERNANÇA ---

def obter_limite_alerta():
    """Busca o gatilho de BI nas configurações"""
    try:
        res = supabase.table("configuracoes").select("valor").eq("chave", "limite_alerta").execute()
        return float(res.data[0]['valor']) if res.data else 500.0
    except: return 500.0

def obter_email_admin():
    """Busca o e-mail oficial da diretoria para exportação"""
    try:
        res = supabase.table("configuracoes").select("valor").eq("chave", "email_diretoria").execute()
        return res.data[0]['valor'] if res.data else "admin@nsg.com"
    except: return "admin@nsg.com"

# [database.py][Unificador Prime v6.5][2026-02-27]
# Total de Linhas de Código: 84