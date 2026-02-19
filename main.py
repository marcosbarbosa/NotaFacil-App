import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client
import os
import time
import plotly.express as px

# --- 1. CONFIGURAÇÕES VISUAIS ---
LOGO_URL = "https://qqvruwobaqfvnrbmnfnq.supabase.co/storage/v1/object/public/comprovantes/logo-notaFacil.png"
BG_MOBILE = "https://qqvruwobaqfvnrbmnfnq.supabase.co/storage/v1/object/public/comprovantes/background-nf-mob.png"
BG_DESKTOP = "https://qqvruwobaqfvnrbmnfnq.supabase.co/storage/v1/object/public/comprovantes/background-nf-desktop-pc.png"

try:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
except:
    st.error("Erro de conexão com o Banco de Dados.")
    st.stop()

# --- 2. CSS RESPONSIVO ---
st.set_page_config(page_title="NotaFácil Prime", page_icon="📊", layout="wide")
st.markdown(f"""
    <style>
    .stApp {{ background-attachment: fixed; background-size: cover; background-position: center; }}
    @media (max-width: 768px) {{ .stApp {{ background-image: linear-gradient(rgba(14, 17, 23, 0.85), rgba(14, 17, 23, 0.85)), url("{BG_MOBILE}"); }} }}
    @media (min-width: 769px) {{ .stApp {{ background-image: linear-gradient(rgba(14, 17, 23, 0.8), rgba(14, 17, 23, 0.8)), url("{BG_DESKTOP}"); }} }}
    div[data-testid="stMetricValue"] {{ color: #FFD700 !important; font-weight: bold; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; white-space: pre-wrap; background-color: rgba(255, 255, 255, 0.05); border-radius: 10px 10px 0 0; padding: 10px 20px; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES ---
def carregar_tudo():
    atl = supabase.table('atletas').select("*").execute()
    vis = supabase.table('visitantes').select("*").execute()
    lan = supabase.table('lancamentos').select("*, atletas(nome), visitantes(nome)").execute()
    return pd.DataFrame(atl.data), pd.DataFrame(vis.data), pd.DataFrame(lan.data)

def salvar_nota(valor, data_nota, arquivo, cpf=None, v_id=None):
    if arquivo:
        ref = cpf if cpf else v_id
        nome_f = f"{ref}_{int(time.time())}_{arquivo.name}"
        supabase.storage.from_("comprovantes").upload(path=nome_f, file=arquivo.getvalue())
        foto_url = f"{url}/storage/v1/object/public/comprovantes/{nome_f}"

        dados = {"valor": valor, "data_nota": str(data_nota), "status": "Pendente", "foto_url": foto_url, "atleta_cpf": cpf, "visitante_id": v_id}
        supabase.table('lancamentos').insert(dados).execute()

        if cpf:
            atl = supabase.table('atletas').select('saldo').eq('cpf', cpf).execute()
            if atl.data:
                supabase.table('atletas').update({'saldo': float(atl.data[0]['saldo']) - valor}).eq('cpf', cpf).execute()

# --- 4. INTERFACE ---
st.sidebar.image(LOGO_URL, use_container_width=True)
menu = st.sidebar.radio("Navegação", ["🏃 Lançamento", "🛡️ Sala de Guerra"])

if menu == "🏃 Lançamento":
    st.title("Lançamento de Nota")
    df_atl, _, _ = carregar_tudo()
    opcoes = ["Selecione..."] + df_atl['nome'].tolist() + ["Sou Visitante"]
    escolha = st.selectbox("Quem está lançando?", opcoes)

    if escolha != "Selecione...":
        with st.form("form_v6", clear_on_submit=True):
            v_id, cpf_atl = None, None
            if escolha == "Sou Visitante":
                email = st.text_input("Seu E-mail")
                vis_res = supabase.table('visitantes').select("*").eq('email', email).execute()
                vis = vis_res.data[0] if vis_res.data else None
                nome_v = st.text_input("Nome", value=vis['nome'] if vis else "")
                whats = st.text_input("WhatsApp", value=vis['whatsapp'] if vis else "")
                canal = st.radio("Notificar por:", ["E-mail", "WhatsApp"], index=0 if not vis or vis['canal_preferido'] == 'E-mail' else 1, horizontal=True)
            else:
                cpf_atl = df_atl[df_atl['nome'] == escolha]['cpf'].values[0]

            valor = st.number_input("Valor (R$)", min_value=0.01)
            data = st.date_input("Data", date.today())
            foto = st.file_uploader("📸 Comprovante", type=['jpg', 'png', 'pdf', 'jpeg'])

            if st.form_submit_button("🚀 ENVIAR NOTA"):
                if not foto: st.warning("Anexe a foto!")
                else:
                    if escolha == "Sou Visitante":
                        v_res = supabase.table('visitantes').upsert({"nome": nome_v, "email": email, "whatsapp": whats, "canal_preferido": canal}, on_conflict='email').execute()
                        v_id = v_res.data[0]['id']
                    salvar_nota(valor, data, foto, cpf=cpf_atl, v_id=v_id)
                    st.success("✅ Enviado com sucesso!")
                    time.sleep(2)
                    st.rerun()

elif menu == "🛡️ Sala de Guerra":
    st.title("🛡️ Painel Estratégico")
    if st.sidebar.text_input("Senha Admin", type="password") == "admin":
        df_atl, df_vis, df_lan = carregar_tudo()

        aba1, aba2 = st.tabs(["📊 Dashboard BI", "📋 Auditoria de Notas"])

        with aba1:
            st.subheader("Inteligência Financeira")

            # KPIs de Topo
            c1, c2, c3 = st.columns(3)
            total_reembolsado = df_lan['valor'].sum()
            c1.metric("Total Reembolsado", f"R$ {total_reembolsado:,.2f}")
            c2.metric("Pendência Atletas", f"R$ {df_atl['saldo'].sum():,.2f}")
            c3.metric("Lançamentos", len(df_lan))

            st.divider()

            col_esq, col_dir = st.columns(2)

            with col_esq:
                # 1. Gráfico de Evolução Mensal
                df_lan['mes_ano'] = pd.to_datetime(df_lan['data_nota']).dt.strftime('%m/%Y')
                gastos_mes = df_lan.groupby('mes_ano')['valor'].sum().reset_index()
                fig_bar = px.bar(gastos_mes, x='mes_ano', y='valor', title="Evolução Mensal (R$)",
                                 color_discrete_sequence=['#FFD700'], template="plotly_dark")
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_dir:
                # 2. Distribuição Atleta vs Visitante
                df_lan['Tipo'] = df_lan['atleta_cpf'].apply(lambda x: 'Atleta' if pd.notnull(x) else 'Visitante')
                dist_tipo = df_lan.groupby('Tipo')['valor'].sum().reset_index()
                fig_pie = px.pie(dist_tipo, values='valor', names='Tipo', title="Origem dos Gastos",
                                 color_discrete_sequence=['#FFD700', '#C0C0C0'], hole=.4, template="plotly_dark")
                st.plotly_chart(fig_pie, use_container_width=True)

            # 3. Termômetro de Orçamento (Exemplo: Meta de R$ 5.000,00 por mês)
            st.divider()
            limite_mensal = 5000.00
            gasto_atual = df_lan[pd.to_datetime(df_lan['data_nota']).dt.month == date.today().month]['valor'].sum()
            progresso = min(gasto_atual / limite_mensal, 1.0)

            st.write(f"**Uso do Orçamento Mensal (Meta: R$ {limite_mensal:,.2f})**")
            st.progress(progresso)
            st.write(f"Já utilizamos **{progresso*100:.1f}%** do planejado para este mês.")

        with aba2:
            st.subheader("Auditoria de Lançamentos")
            if not df_lan.empty:
                df_lan['Quem'] = df_lan.apply(lambda r: r['atletas']['nome'] if r['atletas'] else f"Vis: {r['visitantes']['nome']}", axis=1)
                st.dataframe(df_lan[['Quem', 'valor', 'data_nota', 'status', 'foto_url']], 
                             column_config={"foto_url": st.column_config.LinkColumn("Ver Foto"), 
                                            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")},
                             use_container_width=True, hide_index=True)
    else:
        st.warning("Aguardando senha do Administrador...")