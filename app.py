import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Outage St1", layout="wide")

URL_LOGO = "https://lp.st1.net.br/_assets/v11/5ed2c17da035a77db190d04005e3598e98c2cb7a.png"
st.logo(URL_LOGO)

st.markdown("""
    <style>
    * { border-radius: 0px !important; }
    .stButton>button { border: 1px solid #333; background: #f0f0f0; color: black; font-family: monospace; width: 100%; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { border: 1px solid #333 !important; font-family: monospace; }
    .aviso-box { border: 1px solid #000; padding: 10px; margin-bottom: 5px; background-color: #fff; color: #000; font-family: monospace; }
    .aviso-header { border-bottom: 1px solid #000; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    .status-pendente { color: #d00; }
    .btn-perigo>div>button { background-color: #ffcccc !important; border: 1px solid #d00 !important; font-weight: bold; color: #b00 !important; }
    </style>
""", unsafe_allow_html=True)

# --- USUÁRIOS ---
USUARIOS = {
    "admin": ["notgnihsaw", "Washington Muniz", "Operação de campo"],
    "victor melo": ["12345678", "Victor Melo", "Suporte"],
    "victor": ["123456", "Victor", "Operação de campo"],
    "lucas": ["123456", "Lucas", "Operação de campo"],
    "levi": ["123456", "Levi", "Operação de campo"],
    "alexandro": ["123456", "Alexandro", "Coordenação"],
    "visitante": ["ver123", "Visitante", "Operacional"],
    "visualizar": ["viewst1", "Visualizador Outage", "Visualização"]
}

# --- PERSISTÊNCIA DE LOGIN (RECUPERAÇÃO PÓS-REFRESH) ---
if "logado" not in st.session_state:
    # Se existir o parâmetro 'u' na URL, reconecta o usuário automaticamente
    if "u" in st.query_params:
        user_url = st.query_params["u"]
        if user_url in USUARIOS:
            st.session_state["logado"] = True
            st.session_state["user_id"] = user_url
            st.session_state["nome_colaborador"] = USUARIOS[user_url][1]
            st.session_state["setor_colaborador"] = USUARIOS[user_url][2]
    
    # Caso não tenha o parâmetro ou o usuário seja inválido, define como deslogado
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

if "user_id" not in st.session_state: st.session_state["user_id"] = ""
if "nome_colaborador" not in st.session_state: st.session_state["nome_colaborador"] = ""
if "setor_colaborador" not in st.session_state: st.session_state["setor_colaborador"] = ""
if "mostrar_historico" not in st.session_state: st.session_state["mostrar_historico"] = True
if "edit_index" not in st.session_state: st.session_state["edit_index"] = None
if "edit_text" not in st.session_state: st.session_state["edit_text"] = ""

def get_brasilia_time():
    return datetime.utcnow() - timedelta(hours=3)

# --- LOGIN ---
if not st.session_state["logado"]:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c: st.image(URL_LOGO, use_container_width=True)
    st.write("### LOGIN TERMINAL OUTAGE")
    u = st.text_input("ID USUARIO:").lower().strip()
    p = st.text_input("SENHA:", type="password")
    if st.button("EXECUTAR AUTENTICACAO"):
        if u in USUARIOS and USUARIOS[u][0] == p:
            st.session_state["logado"], st.session_state["user_id"] = True, u
            st.session_state["nome_colaborador"], st.session_state["setor_colaborador"] = USUARIOS[u][1], USUARIOS[u][2]
            st.query_params["u"] = u  # Injeta o ID na URL para aguentar o F5
            st.rerun()
        else: st.error("ACESSO NEGADO")
    st
    
