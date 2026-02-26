# database.py - O Unificador Prime 🛡️
from db_config import *
from db_entidades import *
from db_financeiro import *

# Esta função mantém a compatibilidade com a Sala de Guerra
def carregar_dados_globais():
    """Restaura a visão global unificando os novos módulos"""
    atl, vis = carregar_usuarios()
    lan = carregar_lancamentos()
    return atl, vis, lan

# [database.py][Restauração v5.7][2026-02-26]