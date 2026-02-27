# database.py - O Unificador Prime v8.0 🛡️
from db_config import *
from db_entidades import *
from db_financeiro import *

# --- NÚCLEO DE DADOS E SINCRONIZAÇÃO ---

def carregar_dados_globais():
    """Restaura a visão global unificando os novos módulos"""
    atl, vis = carregar_usuarios()
    lan = carregar_lancamentos()
    return atl, vis, lan

# --- MOTOR DE AUDITORIA E EDIÇÃO ---

def atualizar_lancamento(lan_id, novo_valor, novo_atleta_cpf, novo_operador, valor_antigo, cpf_antigo, status_atual):
    """
    UPGRADE v8.0: Permite editar beneficiário, valor e operador com reajuste de saldo.
    Resolve o problema de registros 'None' e erros de lançamento.
    """
    try:
        # 1. Se a nota estava aprovada, precisamos sincronizar os saldos
        if "Aprovada" in status_atual or status_atual == "Aprovado":
            # Estorna o valor antigo do atleta antigo
            res_antigo = supabase.table("atletas").select("saldo").eq("cpf", cpf_antigo).execute()
            if res_antigo.data:
                saldo_revertido = res_antigo.data['saldo'] + float(valor_antigo)
                supabase.table("atletas").update({"saldo": saldo_revertido}).eq("cpf", cpf_antigo).execute()

            # Debita o novo valor do novo atleta (ou do mesmo, se apenas o valor mudou)
            res_novo = supabase.table("atletas").select("saldo").eq("cpf", novo_atleta_cpf).execute()
            if res_novo.data:
                saldo_debitado = res_novo.data['saldo'] - float(novo_valor)
                supabase.table("atletas").update({"saldo": saldo_debitado}).eq("cpf", novo_atleta_cpf).execute()

        # 2. Atualiza os dados no registro do lançamento
        supabase.table("lancamentos").update({
            "valor": float(novo_valor),
            "atleta_cpf": novo_atleta_cpf,
            "lancado_por": novo_operador
        }).eq("id", lan_id).execute()

        return True, "Lançamento e saldos atualizados com sucesso!"
    except Exception as e:
        return False, f"Erro na atualização: {str(e)}"

def alterar_status_nota(id_nota, cpf_atleta, valor, novo_status, id_admin=None):
    """Aprova/Reprova notas e recalcula o saldo do atleta."""
    try:
        supabase.table("lancamentos").update({"status": novo_status}).eq("id", id_nota).execute()

        if novo_status in ["Aprovado", "✅ Aprovada"]:
            res_atl = supabase.table("atletas").select("saldo").eq("cpf", cpf_atleta).execute()
            if res_atl.data:
                novo_saldo = res_atl.data['saldo'] - float(valor)
                supabase.table("atletas").update({"saldo": novo_saldo}).eq("cpf", cpf_atleta).execute()

        return True, f"Nota {novo_status} com sucesso!"
    except Exception as e:
        return False, str(e)

def excluir_nota_fiscal(id_nota, cpf_atleta, valor, status_atual):
    """Deleta a nota e estorna o saldo se ela estava aprovada"""
    try:
        if "Aprovada" in status_atual or status_atual == "Aprovado":
            res_atl = supabase.table("atletas").select("saldo").eq("cpf", cpf_atleta).execute()
            if res_atl.data:
                novo_saldo = res_atl.data['saldo'] + float(valor)
                supabase.table("atletas").update({"saldo": novo_saldo}).eq("cpf", cpf_atleta).execute()

        supabase.table("lancamentos").delete().eq("id", id_nota).execute()
        return True, "Nota excluída e sistema atualizado!"
    except Exception as e:
        return False, f"Erro ao excluir: {str(e)}"

# --- INTELIGÊNCIA BI ---

def calcular_tag_3x3(saldo, bolsa):
    """Define a categoria de risco (Verde, Amarelo, Vermelho)."""
    if bolsa <= 0: return "SALDO (AZUL)"
    percentual = (saldo / bolsa)
    if percentual > 0.60: return "SALDO (VERMELHO)"
    elif percentual >= 0.40: return "SALDO (AMARELO)"
    else: return "SALDO (AZUL)"

def obter_ultimo_email_exportacao():
    """UX Prime: Recupera o último destinatário do BI."""
    try:
        res = supabase.table('logs_exportacao').select('destinatario').order('created_at', desc=True).limit(1).execute()
        return res.data['destinatario'] if res.data else ""
    except: return ""

# [database.py][v8.0 - Governança & Edição][2026-02-27]