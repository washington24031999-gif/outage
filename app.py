import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Avisos", layout="centered")

# Link da sua logo
URL_LOGO = "https://lp.st1.net.br/_assets/v11/5ed2c17da035a77db190d04005e3598e98c2cb7a.png"
st.logo(URL_LOGO)

# Dicionário de Usuários: 'login': ['senha', 'Nome Completo']
USUARIOS = {
    "admin": ["master123", "Washington Muniz"],
    "visitante": ["ver123", "Visitante"]
}

SETORES = ["Sup. Campo", "Suporte", "Financeiro", "Administração", "Operacional"]

# Inicializa variáveis de sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome_colaborador" not in st.session_state:
    st.session_state["nome_colaborador"] = ""
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None

# --- LÓGICA DE LOGIN ---
def login():
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

if not st.session_state["logado"]:
    login()
    st.stop()

# --- FUNÇÕES DE DADOS ---
def load_data():
    arquivo = "avisos.csv"
    # Adicionada a coluna 'Status'
    colunas = ["Data", "Autor", "Setor", "Aviso", "Status"]
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo)
            for col in colunas:
                if col not in df.columns:
                    # Se for coluna nova, padrão é 'Pendente'
                    df[col] = "Pendente" if col == "Status" else "Geral"
            return df
        except:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

def save_data(df):
    df.to_csv("avisos.csv", index=False)

# --- INTERFACE PRINCIPAL ---
with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.write(f"👤 **{st.session_state['nome_colaborador']}**")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    st.divider()

st.title("📢 Mural de Avisos Digital")

# --- ÁREA DE POSTAGEM (MASTER) ---
if st.session_state["perfil"] != "visitante":
    st.sidebar.header("📝 Novo Aviso")
    st.sidebar.text_input("Colaborador", value=st.session_state['nome_colaborador'], disabled=True)
    setor_sel = st.sidebar.selectbox("Setor Responsável", SETORES)
    texto = st.sidebar.text_area("Mensagem do aviso")

    if st.sidebar.button("Publicar Aviso"):
        if texto:
            novo = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Autor": st.session_state['nome_colaborador'],
                "Setor": setor_sel,
                "Aviso": texto,
                "Status": "Pendente" # Todo aviso novo nasce pendente
            }
            df_atual = load_data()
            df_novo = pd.concat([pd.DataFrame([novo]), df_atual], ignore_index=True)
            save_data(df_novo)
            st.sidebar.success("Aviso publicado!")
            st.rerun()

# --- EXIBIÇÃO ---
st.subheader("Avisos Recentes")
df_display = load_data()

if not df_display.empty:
    for i, row in df_display.iterrows():
        # Define estilo visual baseado no status
        if row["Status"] == "Resolvido":
            label_status = "✅ RESOLVIDO"
            box_style = "success" # Verde
        else:
            label_status = "⏳ PENDENTE"
            box_style = "info" # Azul

        with st.container():
            c1, c2 = st.columns([0.80, 0.20])
            with c1:
                st.markdown(f"### {row['Autor']} | {row['Setor']} | {label_status}")
                st.caption(f"📅 {row['Data']}")
                
                if row["Status"] == "Resolvido":
                    st.success(row['Aviso'])
                else:
                    st.info(row['Aviso'])
            
            with c2:
                if st.session_state["perfil"] != "visitante":
                    st.write("")
                    # Botão para Alterar Status
                    if row["Status"] == "Pendente":
                        if st.button("✅", key=f"res_{i}", help="Marcar como Resolvido"):
                            df_display.at[i, "Status"] = "Resolvido"
                            save_data(df_display)
                            st.rerun()
                    
                    # Botão para Excluir
                    if st.button("🗑️", key=f"del_{i}", help="Excluir Aviso"):
                        df_res = df_display.drop(i)
                        save_data(df_res)
                        st.rerun()
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
