import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sistema de Avisos", layout="centered")

# Dicionário de Usuários: 'login': ['senha', 'Nome Completo']
USUARIOS = {
    "admin": ["master123", "Washington Silva"],
    "joao_sup": ["master456", "João Souza"],
    "maria_adm": ["master789", "Maria Oliveira"],
    "visitante": ["ver123", "Visitante"]
}

SETORES = ["Suporte", "Financeiro", "Administração", "Operacional", "Vendas"]

# Inicializa variáveis de sessão de forma segura
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome_colaborador" not in st.session_state:
    st.session_state["nome_colaborador"] = ""
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None

# --- LÓGICA DE LOGIN ---
def login():
    st.title("🔐 Login do Sistema")
    usuario_input = st.text_input("Usuário").lower().strip()
    senha_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if usuario_input in USUARIOS and USUARIOS[usuario_input][0] == senha_input:
            st.session_state["logado"] = True
            st.session_state["perfil"] = usuario_input
            st.session_state["nome_colaborador"] = USUARIOS[usuario_input][1]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

# FORÇA O LOGIN: Se não estiver logado OU se o nome estiver vazio, para tudo e mostra login
if not st.session_state["logado"] or st.session_state["nome_colaborador"] == "":
    login()
    st.stop()

# --- FUNÇÕES DE DADOS ---
def load_data():
    if os.path.exists("avisos.csv"):
        try:
            df = pd.read_csv("avisos.csv")
            if "Setor" not in df.columns:
                df["Setor"] = "Geral"
            return df
        except:
            return pd.DataFrame(columns=["Data", "Autor", "Setor", "Aviso"])
    return pd.DataFrame(columns=["Data", "Autor", "Setor", "Aviso"])

def save_data(df):
    df.to_csv("avisos.csv", index=False)

# --- INTERFACE PRINCIPAL ---
with st.sidebar:
    st.write(f"👤 **{st.session_state['nome_colaborador']}**")
    if st.button("Sair"):
        st.session_state.clear() # Limpa tudo para forçar login na volta
        st.rerun()
    st.divider()

st.title("📢 Mural de Avisos Digital")

# --- ÁREA DE POSTAGEM (APENAS MASTER) ---
if st.session_state["perfil"] != "visitante":
    st.sidebar.header("📝 Novo Aviso")
    
    # Nome automático e travado
    st.sidebar.text_input("Colaborador", value=st.session_state['nome_colaborador'], disabled=True)
    setor_selecionado = st.sidebar.selectbox("Setor Responsável", SETORES)
    texto_aviso = st.sidebar.text_area("Mensagem do aviso")

    if st.sidebar.button("Publicar Aviso"):
        if texto_aviso:
            nova_linha = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Autor": st.session_state['nome_colaborador'],
                "Setor": setor_selecionado,
                "Aviso": texto_aviso
            }
            df = load_data()
            df = pd.concat([pd.DataFrame([nova_linha]), df], ignore_index=True)
            save_data(df)
            st.sidebar.success("Aviso publicado!")
            st.rerun()
        else:
            st.sidebar.error("Escreva a mensagem.")
else:
    st.sidebar.info("Modo Visualização")

# --- EXIBIÇÃO ---
st.subheader("Avisos Recentes")
df_display = load_data()

if not df
