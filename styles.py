# ==============================================================================
# SISTEMA: NotaFácil Prime | ARQUIVO: styles.py
# DATA: 19/02/2026 | HORA: 13:00 | TÍTULO: Design & Assets v1.2
# FUNÇÃO: Centralização de CSS e Estilos de Feedback
# VERSÃO: 1.2 | LINHAS: 28
# ==============================================================================
import streamlit as st

LOGO_URL = "https://qqvruwobaqfvnrbmnfnq.supabase.co/storage/v1/object/public/comprovantes/logo-notaFacil.png"
BG_MOBILE = "https://qqvruwobaqfvnrbmnfnq.supabase.co/storage/v1/object/public/comprovantes/background-nf-mob.png"
BG_DESKTOP = "https://qqvruwobaqfvnrbmnfnq.supabase.co/storage/v1/object/public/comprovantes/background-nf-desktop-pc.png"

def aplicar_design():
    st.markdown(f"""
        <style>
        .stApp {{ background-attachment: fixed; background-size: cover; background-position: center; }}
        @media (max-width: 768px) {{ .stApp {{ background-image: linear-gradient(rgba(14, 17, 23, 0.9), rgba(14, 17, 23, 0.9)), url("{BG_MOBILE}"); }} }}
        @media (min-width: 769px) {{ .stApp {{ background-image: linear-gradient(rgba(14, 17, 23, 0.8), rgba(14, 17, 23, 0.8)), url("{BG_DESKTOP}"); }} }}
        div[data-testid="stMetricValue"] {{ color: #FFD700 !important; font-weight: bold; }}
        .success-box {{ background: rgba(0, 255, 0, 0.05); padding: 25px; border-radius: 15px; border: 2px solid #2ecc71; text-align: center; }}
        </style>
        """, unsafe_allow_html=True)
# Quantidade total de linhas: 28