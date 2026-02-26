import time
import os
from db_config import supabase

def carregar_lancamentos():
    """Busca registros financeiros com auditoria detalhada"""
    return supabase.table('lancamentos').select("*, atletas(nome, cpf, saldo, bolsa), visitantes(nome, email)").order('created_at', desc=True).execute().data

def salvar_nota_fiscal(valor, data, arquivo, cpf=None, v_id=None):
    """Processa upload e realiza abatimento imediato de saldo"""
    if arquivo:
        path = f"{cpf if cpf else v_id}_{int(time.time())}_{arquivo.name}"
        supabase.storage.from_("comprovantes").upload(path=path, file=arquivo.getvalue())
        url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/comprovantes/{path}"

        supabase.table('lancamentos').insert({
            "valor": valor, "data_nota": str(data), "status": "Pendente", 
            "foto_url": url, "atleta_cpf": cpf, "visitante_id": v_id
        }).execute()

        if cpf:
            a = supabase.table('atletas').select('saldo').eq('cpf', cpf).execute()
            if a.data: 
                supabase.table('atletas').update({'saldo': float(a.data[0]['saldo']) - float(valor)}).eq('cpf', cpf).execute()

def registrar_log_exportacao(admin_nome, destinatario, filtros, qtd):
    """Registra histórico de auditoria para cada exportação realizada"""
    try:
        supabase.table('logs_exportacao').insert({
            "admin_nome": admin_nome, "destinatario": destinatario, 
            "filtros": filtros, "quantidade_registros": int(qtd)
        }).execute()
    except: pass

# [db_financeiro.py][Motor Financeiro e Auditoria][2026-02-26 16:52]