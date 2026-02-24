    # ==============================================================================
    # SISTEMA: NotaFácil Prime | ARQUIVO: database.py
    # DATA: 23/02/2026 | TÍTULO: Motor de Dados e Inteligência Financeira
    # FUNÇÃO: Exclusão e Edição com Recálculo Automático de Saldo
    # VERSÃO: 2.4 | LINHAS: 80
    # ==============================================================================
    import os, time, pandas as pd, smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
    from supabase import create_client, Client

    def conectar():
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        return create_client(url, key)

    supabase = conectar()

    def carregar_dados_globais():
        atl = supabase.table('atletas').select("*").execute()
        vis = supabase.table('visitantes').select("*").execute()
        lan = supabase.table('lancamentos').select("*, atletas(nome, data_nascimento, sexo, limite_mensal, categoria), visitantes(nome)").order('created_at', desc=True).execute()
        return atl.data, vis.data, lan.data

    # --- NOVAS FUNÇÕES DE GESTÃO FINANCEIRA ---
    def excluir_nota_fiscal(id_nota, cpf_atleta, valor_nota):
        """Exclui a nota e devolve o valor para o saldo do atleta (Estorno)."""
        if cpf_atleta:
            atl = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
            if atl.data:
                novo_saldo = float(atl.data[0]['saldo']) + float(valor_nota)
                supabase.table('atletas').update({'saldo': novo_saldo}).eq('cpf', cpf_atleta).execute()
        supabase.table('lancamentos').delete().eq('id', id_nota).execute()

    def editar_valor_nota(id_nota, cpf_atleta, valor_antigo, valor_novo):
        """Edita a nota e calcula a diferença no saldo do atleta."""
        diferenca = float(valor_novo) - float(valor_antigo)
        if cpf_atleta:
            atl = supabase.table('atletas').select('saldo').eq('cpf', cpf_atleta).execute()
            if atl.data:
                novo_saldo = float(atl.data[0]['saldo']) - diferenca
                supabase.table('atletas').update({'saldo': novo_saldo}).eq('cpf', cpf_atleta).execute()
        supabase.table('lancamentos').update({'valor': valor_novo}).eq('id', id_nota).execute()

    # --- FUNÇÕES EXISTENTES ---
    def log_exportacao(admin, destino, filtro):
        supabase.table('logs_exportacao').insert({"admin_email": admin, "destinatario_email": destino, "filtro_periodo": filtro}).execute()

    def enviar_email_relatorio(destinatario, assunto, conteudo_html):
        remetente = os.environ.get("EMAIL_USER")
        senha = os.environ.get("EMAIL_PASS")
        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(conteudo_html, 'html'))
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
            server.quit()
            return True
        except:
            return False

    def salvar_nota_fiscal(valor, data_nota, arquivo, cpf=None, v_id=None):
        if arquivo:
            ref = cpf if cpf else v_id
            nome_f = f"{ref}_{int(time.time())}_{arquivo.name}"
            supabase.storage.from_("comprovantes").upload(path=nome_f, file=arquivo.getvalue())
            foto_url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/comprovantes/{nome_f}"
            supabase.table('lancamentos').insert({"valor": valor, "data_nota": str(data_nota), "status": "Pendente", "foto_url": foto_url, "atleta_cpf": cpf, "visitante_id": v_id}).execute()
            if cpf:
                atl = supabase.table('atletas').select('saldo').eq('cpf', cpf).execute()
                if atl.data:
                    supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) - valor}).eq('cpf', cpf).execute()

    def formatar_saldo_mask(saldo, eh_privilegiado=False):
        TETO = 500.0
        if eh_privilegiado or saldo <= TETO:
            return f"R$ {saldo:,.2f}"
        return f"R$ {TETO:,.0f}+"

    def calcular_tag_3x3(sexo, data_nasc):
        if not data_nasc or not sexo: return "⚪ SEM_DADOS"
        hoje = date.today()
        nasc = pd.to_datetime(data_nasc).date()
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        if sexo == "F": return "🟪 3X3_FEM"
        return "🟦 3X3_M_BASE" if idade <= 18 else "🟥 3X3_M_ELITE"

    def upsert_visitante(dados):
        res = supabase.table('visitantes').upsert(dados, on_conflict='email').execute()
        return res.data[0]['id']