import time
import os
from db_config import supabase

def carregar_lancamentos():
    """Busca registros financeiros com auditoria detalhada e todos os campos"""
    # O select("*") garante que o campo lancado_por seja puxado para o Dashboard
    return supabase.table('lancamentos').select("*, atletas(nome, cpf, saldo, bolsa), visitantes(nome, email)").order('created_at', desc=True).execute().data

def salvar_nota_fiscal(valor, data, arquivo, cpf=None, v_id=None, operador_nome="Sistema"):
    """Processa upload da NF e salva no banco vinculando o operador real (Sem Duplo Desconto)"""
    try:
        if arquivo:
            # Limpa espaços no nome do arquivo para evitar quebra de URL
            nome_seguro = arquivo.name.replace(" ", "_")
            path = f"{cpf if cpf else v_id}_{int(time.time())}_{nome_seguro}"

            # Faz o upload do comprovante para o Storage
            supabase.storage.from_("comprovantes").upload(path=path, file=arquivo.getvalue())
            url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/comprovantes/{path}"

            # Salva os dados no banco, incluindo quem fez o lançamento
            supabase.table('lancamentos').insert({
                "valor": valor, 
                "data_nota": str(data), 
                "status": "Pendente", 
                "foto_url": url, 
                "atleta_cpf": cpf, 
                "visitante_id": v_id,
                "lancado_por": operador_nome # 🚀 FIM DO BUG DO ESPELHO: Registra o Operador!
            }).execute()

            # 🛑 ALERTA DE GOVERNANÇA: O desconto imediato de saldo foi REMOVIDO daqui.
            # Motivo: O saldo agora é descontado EXCLUSIVAMENTE pelo módulo de Auditoria 
            # (database.py -> alterar_status_nota) quando a diretoria clica em "Aprovar Nota".
            # Isso impede o risco do Atleta ser cobrado duas vezes.

            return True, "Nota fiscal registrada e aguardando auditoria!"

        return False, "Nenhum arquivo anexado."
    except Exception as e:
        return False, f"Erro ao processar transação: {str(e)}"

def registrar_log_exportacao(admin_nome, destinatario, filtros, qtd):
    """Registra histórico de auditoria para cada exportação realizada (Rastreabilidade)"""
    try:
        supabase.table('logs_exportacao').insert({
            "admin_nome": admin_nome, 
            "destinatario": destinatario, 
            "filtros": filtros, 
            "quantidade_registros": int(qtd)
        }).execute()
    except: 
        pass

# [db_financeiro.py][Motor Transacional Blindado v10.0][2026-02-27]
# Total de Linhas de Código: 48