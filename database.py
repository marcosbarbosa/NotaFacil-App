import os
import time
import pandas as pd
from datetime import date
from supabase import create_client, Client

def conectar():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

supabase = conectar()

def carregar_dados_globais():
    atl = supabase.table('atletas').select("*").execute()
    vis = supabase.table('visitantes').select("*").execute()
    lan = supabase.table('lancamentos').select("*, atletas(nome, email, cpf, saldo), visitantes(nome, email)").order('created_at', desc=True).execute()
    return atl.data, vis.data, lan.data

def salvar_nota_fiscal(valor, data, arquivo, cpf=None, v_id=None):
    if arquivo:
        ref = cpf if cpf else v_id
        path = f"{ref}_{int(time.time())}_{arquivo.name}"
        supabase.storage.from_("comprovantes").upload(path=path, file=arquivo.getvalue())
        url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/comprovantes/{path}"
        supabase.table('lancamentos').insert({"valor": valor, "data_nota": str(data), "status": "Pendente", "foto_url": url, "atleta_cpf": cpf, "visitante_id": v_id}).execute()
        if cpf:
            a = supabase.table('atletas').select('saldo').eq('cpf', cpf).execute()
            if a.data: supabase.table('atletas').update({'saldo': float(a.data[0]['saldo']) - float(valor)}).eq('cpf', cpf).execute()

def vincular_atleta_a_nota(id_nota, cpf_atleta, valor_nota):
    try:
        supabase.table('lancamentos').update({"atleta_cpf": cpf_atleta}).eq('id', id_nota).execute()
        a = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
        if a.data:
            novo_saldo = float(a.data[0]['saldo']) - float(valor_nota)
            supabase.table('atletas').update({'saldo': novo_saldo}).eq('cpf', cpf_atleta).execute()
        return True, "Beneficiário vinculado e saldo atualizado!"
    except Exception as e:
        return False, f"Erro no banco: {str(e)}"

def cadastrar_novo_atleta(nome, cpf, data_nasc, sexo, limite, email, senha):
    dados = {
        "nome": nome, "cpf": cpf, "data_nascimento": str(data_nasc), 
        "sexo": sexo, "bolsa": float(limite), "limite_mensal": float(limite), 
        "saldo": float(limite), "email": email, "senha": senha, "categoria": "Base"
    }
    try:
        supabase.table('atletas').insert(dados).execute()
        return True, "Sucesso"
    except Exception as e:
        msg = str(e)
        return (False, f"CPF {cpf} já cadastrado.") if "duplicate key" in msg else (False, msg)

def alterar_status_nota(id_nota, cpf_atleta, valor, status_curr, status_new):
    status_limpo = status_new.replace("⚠️ ", "").replace("✅ ", "").replace("❌ ", "")
    supabase.table('lancamentos').update({'status': status_limpo}).eq('id', id_nota).execute()
    if "Reprovada" in status_new and "Reprovada" not in status_curr and cpf_atleta:
        a = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
        if a.data:
            novo_saldo = float(a.data[0]['saldo']) + float(valor)
            supabase.table('atletas').update({'saldo': novo_saldo}).eq('cpf', cpf_atleta).execute()

def calcular_tag_3x3(sexo, data_nasc):
    if not data_nasc or not sexo: return "⚪ SEM_DADOS"
    h = date.today()
    n = pd.to_datetime(data_nasc).date()
    idade = h.year - n.year - ((h.month, h.day) < (n.month, n.day))
    return "🟪 3X3_FEM" if sexo == "F" else ("🟦 3X3_M_BASE" if idade <= 18 else "🟥 3X3_M_ELITE")

def formatar_saldo_mask(saldo, privilegiado=False):
    """RESTAURADA: Aplica máscara visual no saldo para a tela de sucesso"""
    TETO = 500.0
    return f"R$ {float(saldo):,.2f}" if privilegiado or float(saldo) <= TETO else f"R$ {TETO:,.0f}+"

# [database.py][Restauração da Função formatar_saldo_mask][2026-02-24 21:50][v2.28][80 linhas]