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
    except Exception as e: return False, f"Erro no banco: {str(e)}"

def cadastrar_novo_atleta(nome, cpf, data_nasc, sexo, limite, email, senha):
    dados = {"nome": nome, "cpf": cpf, "data_nascimento": str(data_nasc), "sexo": sexo, "bolsa": float(limite), "limite_mensal": float(limite), "saldo": float(limite), "email": email, "senha": senha, "categoria": "Base"}
    try:
        supabase.table('atletas').insert(dados).execute()
        return True, "Sucesso"
    except Exception as e:
        return (False, f"CPF {cpf} já cadastrado.") if "duplicate key" in str(e) else (False, str(e))

def alterar_status_nota(id_nota, cpf_atleta, valor, status_curr, status_new):
    status_limpo = status_new.replace("⚠️ ", "").replace("✅ ", "").replace("❌ ", "")
    supabase.table('lancamentos').update({'status': status_limpo}).eq('id', id_nota).execute()
    if "Reprovada" in status_new and "Reprovada" not in status_curr and cpf_atleta:
        a = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
        if a.data:
            novo_saldo = float(a.data[0]['saldo']) + float(valor)
            supabase.table('atletas').update({'saldo': novo_saldo}).eq('cpf', cpf_atleta).execute()

# --- NOVO: HARD DELETE DE NOTA FISCAL ---
def excluir_nota_fiscal(id_nota, cpf_atleta, valor, status_curr):
    """Exclui a nota do banco e devolve o saldo ao atleta se necessário."""
    try:
        # Se a nota NÃO estava reprovada, o dinheiro dela estava descontado do saldo. Precisamos devolver.
        if "Reprovada" not in status_curr and cpf_atleta:
            a = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
            if a.data:
                novo_saldo = float(a.data[0]['saldo']) + float(valor)
                supabase.table('atletas').update({'saldo': novo_saldo}).eq('cpf', cpf_atleta).execute()

        # Deleta fisicamente o registro
        supabase.table('lancamentos').delete().eq('id', id_nota).execute()
        return True, "Nota excluída!"
    except Exception as e:
        return False, str(e)

def atualizar_dados_atleta(cpf, nome, email, senha, bolsa_nova):
    dados = {"nome": nome, "email": email, "senha": senha, "bolsa": float(bolsa_nova), "limite_mensal": float(bolsa_nova)}
    try:
        supabase.table('atletas').update(dados).eq('cpf', cpf).execute()
        return True, "Atleta atualizado!"
    except Exception as e: return False, f"Erro: {str(e)}"

def atualizar_dados_visitante(v_id, nome, email, senha):
    dados = {"nome": nome, "email": email, "senha": senha}
    try:
        supabase.table('visitantes').update(dados).eq('id', v_id).execute()
        return True, "Visitante atualizado!"
    except Exception as e: return False, f"Erro: {str(e)}"

def excluir_usuario(tipo, identificador):
    tabela = 'atletas' if tipo == 'atleta' else 'visitantes'
    coluna = 'cpf' if tipo == 'atleta' else 'id'
    try:
        supabase.table(tabela).delete().eq(coluna, identificador).execute()
        return True, "Usuário excluído!"
    except Exception as e:
        return False, f"O usuário possui notas vinculadas. Exclua as notas dele primeiro!"

def calcular_tag_3x3(sexo, data_nasc):
    if not data_nasc or not sexo: return "⚪ SEM_DADOS"
    h = date.today()
    n = pd.to_datetime(data_nasc).date()
    idade = h.year - n.year - ((h.month, h.day) < (n.month, n.day))
    return "🟪 3X3_FEM" if sexo == "F" else ("🟦 3X3_M_BASE" if idade <= 18 else "🟥 3X3_M_ELITE")

def formatar_saldo_mask(saldo, privilegiado=False):
    TETO = 500.0
    return f"R$ {float(saldo):,.2f}" if privilegiado or float(saldo) <= TETO else f"R$ {TETO:,.0f}+"

# [database.py][Inclusão do Hard Delete de NFs com Estorno Automático][2026-02-24 22:30][v2.30][100 linhas]