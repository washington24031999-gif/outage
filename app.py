import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Avisos", layout="centered")

# Link da sua logo
URL_LOGO = "https://lp.st1.net.br/_assets/v11/5ed2c17da035a77db190d04005e3598e98c2cb7a.png"

# Coloca a logo no topo do menu lateral
st.logo(URL_LOGO)

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
    # Exibe a logo centralizada na tela de login
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.image(URL_LOGO, use_container_width=True)
    
    st.markdown("<h2 style='text-align: center;'>🔐 Login do Sistema</h2>", unsafe_allow_html=True)
    
    u_input = st.text_input("Usuário").lower().strip()
    s_input = st.text_input("Senha", type="password")
    
    if st.button("Entrar", use_container_width=True):
        if u_input in USUARIOS and USUARIOS[u_input][0] == s_input:
            st.session_state["logado"] = True
            st.session_state["perfil"] = u_input
            st.session_state["nome_colaborador"] = USUARIOS[u_input][1]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

# Bloqueio: Se não estiver logado, para o script e mostra a tela de login
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
            for col in colunas:
                if col not in df.columns:
                    df[col] = "Geral"
            return df
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

def save_data(df):
    df.to_csv("avisos.csv", index=False)

# --- INTERFACE PRINCIPAL ---
with st.sidebar:
    # Logo também no topo da sidebar
    st.image(URL_LOGO, width=150)
    st.write(f"👤 **{st.session_state['nome_colaborador']}**")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    st.divider()

st.title("📢 Mural de Avisos Digital")

# --- ÁREA DE POSTAGEM (APENAS MASTER) ---
if st.session_state["perfil"] != "visitante":
    st.sidebar.header("📝 Novo Aviso")
    
    # Nome automático e travado conforme o login
    st.sidebar.text_input("Colaborador", value=st.session_state['nome_colaborador'], disabled=True)
    setor_sel = st.sidebar.selectbox("Setor Responsável", SETORES)
    texto = st.sidebar.text_area("Mensagem do aviso")

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
            st.sidebar.success("Aviso publicado!")
            st.rerun()
        else:
            st.sidebar.error("Por favor, escreva a mensagem.")
else:
    st.sidebar.info("Você está no modo de visualização.")

# --- EXIBIÇÃO DOS AVISOS ---
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
                # Apenas masters podem excluir
                if st.session_state["perfil"] != "visitante":
                    st.write("")
                    if st.button("🗑️", key=f"del_{i}"):
                        df_res = df_display.drop(i)
                        save_data(df_res)
                        st.rerun()
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
