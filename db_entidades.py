from db_config import supabase
from datetime import date

def carregar_usuarios():
    """Recupera dados de Atletas e Diretoria"""
    atl = supabase.table('atletas').select("*").execute()
    vis = supabase.table('visitantes').select("*").execute()
    return atl.data, vis.data

def adicionar_atleta(nome, cpf, bolsa):
    """Cadastra novo atleta com saldo inicial automatizado"""
    dados = {
        "nome": nome, "cpf": cpf, "bolsa": float(bolsa), "saldo": float(bolsa),
        "limite_mensal": float(bolsa), "email": f"{cpf}@atleta.nsg", "senha": "123",
        "sexo": "M", "categoria": "Base", "data_nascimento": str(date.today()) 
    }
    return supabase.table('atletas').insert(dados).execute()

def atualizar_usuario(email_antigo, novo_nome, novo_email, nova_role):
    """Atualiza permissões respeitando a coluna 'role' do Supabase"""
    dados = {"nome": novo_nome, "email": novo_email, "role": nova_role}
    return supabase.table('visitantes').update(dados).eq('email', email_antigo).execute()

def excluir_usuario(email_alvo):
    """Revoga acesso de um membro da diretoria"""
    return supabase.table('visitantes').delete().eq('email', email_alvo).execute()

# [db_entidades.py][Gestão de Atletas e Diretoria][2026-02-26 16:51]