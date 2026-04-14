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

# Inicializa as variáveis de sessão para evitar o KeyError
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None
if "nome_colaborador" not in st.session_state:
    st.session_state["nome_colaborador"] = ""

# --- LÓGICA DE LOGIN ---
def login():
    st.title("🔐 Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario][0] == senha:
            st.session_state["logado"] = True
            st.session_state["perfil"] = usuario
            st.session_state["nome_colaborador"] = USUARIOS[usuario][1]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

if not st.session_state["logado"]:
    login()
    st.stop()

# --- FUNÇÕES DE DADOS ---
def load_data():
    if os.path.exists("avisos.csv"):
        try:
            df = pd.read_csv("avisos.csv")
            # Verifica se a coluna Setor existe (caso o arquivo seja antigo)
            if "Setor" not in df.columns:
                df["Setor"] = "Geral"
            return df
        except:
            return pd.DataFrame(columns=["Data", "Autor", "Setor", "Aviso"])
    else:
        return pd.DataFrame(columns=["Data", "Autor", "Setor", "Aviso"])

def save_data(df):
    df.to_csv("avisos.csv", index=False)

# --- INTERFACE ---
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.session_state["perfil"] = None
    st.rerun()

st.title("📢 Mural de Avisos Digital")
st.write(f"Bem-vindo, **{st.session_state['nome_colaborador']}**")

# --- ÁREA DO MASTER ---
if st.session_state["perfil"] != "visitante":
    st.sidebar.header("📝 Novo Aviso")
    
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

# --- EXIBIÇÃO ---
st.subheader("Avisos Recentes")
df_display = load_data()

if not df_display.empty:
    for i, row in df_display.iterrows():
        with st.container():
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.markdown(f"### {row['Autor']} | {row['Setor']}")
                st.caption(f"Postado em: {row['Data']}")
                st.info(row['Aviso'])
            with col2:
                if st.session_state["perfil"] != "visitante":
                    st.write("")
                    if st.button("🗑️", key=f"del_{i}"):
                        df_novo = df_display.drop(i)
                        save_data(df_novo)
                        st.rerun()
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
