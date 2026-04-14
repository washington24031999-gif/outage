import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO E LOGIN ---
st.set_page_config(page_title="Sistema de Avisos", layout="centered")

# Definição simples de usuários e senhas
# Em um sistema real, use segredos do Streamlit para não deixar senhas no código
USUARIOS = {
    "admin": "master123",
    "visitante": "ver123"
}

def login():
    st.title("🔐 Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state["logado"] = True
            st.session_state["perfil"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

if "logado" not in st.session_state:
    login()
    st.stop() # Para a execução aqui se não estiver logado

# --- LÓGICA DO SISTEMA (Pós-Login) ---

def load_data():
    if os.path.exists("avisos.csv"):
        return pd.read_csv("avisos.csv")
    else:
        return pd.DataFrame(columns=["Data", "Autor", "Aviso"])

def save_data(df):
    df.to_csv("avisos.csv", index=False)

# Botão de Logout na barra lateral
if st.sidebar.button("Sair"):
    del st.session_state["logado"]
    st.rerun()

st.title("📢 Mural de Avisos Digital")
st.write(f"Conectado como: **{st.session_state['perfil'].capitalize()}**")

# --- ÁREA DO MASTER (ADMIN) ---
if st.session_state["perfil"] == "admin":
    st.sidebar.header("Painel Administrativo")
    autor = st.sidebar.text_input("Seu nome/setor")
    texto_aviso = st.sidebar.text_area("Mensagem do aviso")

    if st.sidebar.button("Publicar Aviso"):
        if autor and texto_aviso:
            nova_linha = {"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Autor": autor, "Aviso": texto_aviso}
            df = load_data()
            df = pd.concat([pd.DataFrame([nova_linha]), df], ignore_index=True)
            save_data(df)
            st.sidebar.success("Aviso publicado!")
            st.rerun()
else:
    st.sidebar.info("Você está no modo de apenas visualização.")

# --- EXIBIÇÃO DOS AVISOS (PARA AMBOS) ---
st.subheader("Avisos Recentes")
df_display = load_data()

if not df_display.empty:
    for i, row in df_display.iterrows():
        with st.container():
            # Se for admin, mostra botão de excluir. Se não, mostra apenas o texto.
            if st.session_state["perfil"] == "admin":
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.markdown(f"### {row['Autor']}")
                    st.caption(f"Postado em: {row['Data']}")
                    st.info(row['Aviso'])
                with col2:
                    st.write("") 
                    if st.button("🗑️", key=f"del_{i}"):
                        df_novo = df_display.drop(i)
                        save_data(df_novo)
                        st.rerun()
            else:
                st.markdown(f"### {row['Autor']}")
                st.caption(f"Postado em: {row['Data']}")
                st.info(row['Aviso'])
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
