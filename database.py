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

def excluir_nota_fiscal(id_nota, cpf_atleta, valor, status_atual):
    """Deleta a nota permanentemente e estorna o saldo se ela estava aprovada"""
    try:
        # Se a nota estava aprovada, devolve o dinheiro para o saldo do atleta antes de apagar
        if "Aprovada" in status_atual or status_atual == "Aprovado":
            res_atl = supabase.table("atletas").select("saldo").eq("cpf", cpf_atleta).execute()
            if res_atl.data:
                novo_saldo = res_atl.data[0]['saldo'] + float(valor)
                supabase.table("atletas").update({"saldo": novo_saldo}).eq("cpf", cpf_atleta).execute()

        supabase.table("lancamentos").delete().eq("id", id_nota).execute()
        return True, "Nota excluída e sistema atualizado!"
    except Exception as e:
        return False, f"Erro ao excluir: {str(e)}"

# --- INTELIGÊNCIA BI (TAGS E HISTÓRICO) ---

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

def obter_ultimo_email_exportacao():
    """UX Prime: Busca o último e-mail utilizado nos disparos de relatórios para poupar digitação"""
    try:
        res = supabase.table('logs_exportacao').select('destinatario').order('created_at', desc=True).limit(1).execute()
        return res.data[0]['destinatario'] if res.data else ""
    except:
        return ""

# Observação: Funções de 'configuracoes' foram limpas daqui pois já estão blindadas no db_config.py 
# [database.py][Unificador Prime Limpo v7.5][2026-02-27]
# Total de Linhas de Código: 83