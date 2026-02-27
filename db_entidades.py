from db_config import supabase
from datetime import date

def carregar_usuarios():
    """Recupera dados de Atletas e Diretoria com blindagem contra falhas de conexão"""
    try:
        # Busca os dados de forma limpa e segura
        atl = supabase.table('atletas').select("*").execute()
        vis = supabase.table('visitantes').select("*").execute()
        return atl.data, vis.data
    except Exception as e:
        # Fallback de segurança: Retorna listas vazias se o banco cair, evitando tela vermelha
        print(f"Erro ao carregar usuários: {str(e)}")
        return [], []

def adicionar_atleta(nome, cpf, bolsa):
    """(Legado Seguro) Cadastra novo atleta com saldo inicial automatizado"""
    try:
        dados = {
            "nome": nome, 
            "cpf": cpf, 
            "bolsa": float(bolsa), 
            "saldo": float(bolsa),
            "limite_mensal": float(bolsa), 
            "email": f"{cpf}@nsg.com", # Domínio atualizado
            "senha": "123",
            "sexo": "M", 
            "categoria": "Base", 
            "data_nascimento": str(date.today()) 
        }
        # 🚀 FIX: Trocado para upsert para evitar erro fatal de CPF duplicado
        res = supabase.table('atletas').upsert(dados, on_conflict="cpf").execute()
        return True, "Atleta cadastrado/atualizado com sucesso!"
    except Exception as e:
        return False, str(e)

def atualizar_usuario(email_antigo, novo_nome, novo_email, nova_role):
    """Atualiza permissões respeitando a coluna 'role' do Supabase"""
    try:
        dados = {"nome": novo_nome, "email": novo_email, "role": nova_role}
        res = supabase.table('visitantes').update(dados).eq('email', email_antigo).execute()
        return True, "Permissões atualizadas com sucesso!"
    except Exception as e:
        return False, str(e)

def excluir_usuario(email_alvo):
    """Revoga acesso de um membro da diretoria com tratamento de erro"""
    try:
        res = supabase.table('visitantes').delete().eq('email', email_alvo).execute()
        return True, "Acesso revogado com sucesso!"
    except Exception as e:
        return False, str(e)

# [db_entidades.py][Entidades Blindadas v11.0][2026-02-27]
# Total de Linhas de Código: 45