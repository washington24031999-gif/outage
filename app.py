import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Avisos", layout="centered")

# Dicionário de Usuários: 'login': ['senha', 'Nome Completo']
USUARIOS = {
    "admin": ["master123", "Washington Silva"],
    "joao_sup": ["master456", "João Souza"],
    "maria_adm": ["master789", "Maria Oliveira"],
    "visitante": ["ver123", "Visitante"]
}

SETORES = ["Suporte", "Financeiro", "Administração", "Operacional", "Vendas"]

# Inicializa variáveis de sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome_colaborador" not in st.session_state:
    st.session_state["nome_colaborador"] = ""
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None

# --- LÓGICA DE LOGIN ---
def login():
    st.title("🔐 Login do Sistema")
    u_input = st.text_input("Usuário").lower().strip()
    s_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if u_input in USUARIOS and USUARIOS[u_input][0] == s_input:
            st.session_state["logado"] = True
            st.session_state["perfil"] = u_input
            st.session_state["nome_colaborador"] = USUARIOS[u_input][1]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

# Bloqueio de segurança
if not st.session_state["logado"]:
    login()
    st.stop()

# --- FUNÇÕES DE DADOS ---
def load_data():
    arquivo = "avisos.csv"
    colunas = ["Data", "Autor", "Setor", "Aviso"]
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo)
            # Garante que colunas novas existam se o arquivo for antigo
            for col in colunas:
                if col not in df.columns:
                    df[col] = "N/A"
            return df
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

def save_data(df):
    df.to_csv("avisos.csv", index=False)

# --- INTERFACE ---
with st.sidebar:
    st.write(f"👤 Logado como: **{st.session_state['nome_colaborador']}**")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    st.divider()

st.title("📢 Mural de Avisos Digital")

# Área de Postagem para Masters
if st.session_state["perfil"] != "visitante":
    st.sidebar.header("📝 Novo Aviso")
    st.sidebar.text_input("Colaborador", value=st.session_state['nome_colaborador'], disabled=True)
    setor_sel = st.sidebar.selectbox("Setor Responsável", SETORES)
    texto = st.sidebar.text_area("Mensagem")

    if st.sidebar.button("Publicar Aviso"):
        if texto:
            novo = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Autor": st.session_state['nome_colaborador'],
                "Setor": setor_sel,
                "Aviso": texto
            }
            df_atual = load_data()
            df_novo = pd.concat([pd.DataFrame([novo]), df_atual], ignore_index=True)
            save_data(df_novo)
            st.sidebar.success("Publicado!")
            st.rerun()
        else:
            st.sidebar.error("Escreva algo.")
else:
    st.sidebar.info("Apenas visualização.")

# --- EXIBIÇÃO ---
st.subheader("Avisos Recentes")
df_display = load_data()

if not df_display.empty:
    for i, row in df_display.iterrows():
        with st.container():
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                st.markdown(f"### {row['Autor']} | {row['Setor']}")
                st.caption(f"📅 {row['Data']}")
                st.info(row['Aviso'])
            with c2:
                if st.session_state["perfil"] != "visitante":
                    st.write("")
                    if st.button("🗑️", key=f"del_{i}"):
                        df_res = df_display.drop(i)
                        save_data(df_res)
                        st.rerun()
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
