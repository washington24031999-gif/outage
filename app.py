import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Outage St1", layout="centered")

# Link da logo
URL_LOGO = "https://lp.st1.net.br/_assets/v11/5ed2c17da035a77db190d04005e3598e98c2cb7a.png"
st.logo(URL_LOGO)

# --- DICIONÁRIO DE USUÁRIOS ---
USUARIOS = {
    "admin": ["master123", "Washington Muniz"],
    "victor melo": ["12345678", "Victor Melo"],
    "visitante": ["12345", "Visitante"]
}

SETORES = ["Sup. Campo", "Suporte", "Financeiro", "Administração", "Operacional"]

# Inicialização de variáveis de sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome_colaborador" not in st.session_state:
    st.session_state["nome_colaborador"] = ""
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None

# --- FUNÇÃO PARA PEGAR HORA DE BRASÍLIA ---
def get_brasilia_time():
    # Ajusta para UTC-3 (Horário de Brasília)
    return datetime.utcnow() - timedelta(hours=3)

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
    colunas_obrigatorias = ["Data", "Autor", "Setor", "Aviso", "Status", "Resolvido_Por"]
    if os.path.exists(arquivo):
        try:
            # Força leitura como string para evitar erros de tipo
            df = pd.read_csv(arquivo, dtype=str).fillna("")
            for col in colunas_obrigatorias:
                if col not in df.columns:
                    df[col] = "Pendente" if col == "Status" else ""
            return df
        except:
            return pd.DataFrame(columns=colunas_obrigatorias)
    return pd.DataFrame(columns=colunas_obrigatorias)

def save_data(df):
    df.astype(str).to_csv("avisos.csv", index=False)

# --- INTERFACE LATERAL ---
with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.write(f"👤 **{st.session_state['nome_colaborador']}**")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    st.divider()

# --- TÍTULO DO SISTEMA ---
st.title("📢 Outage St1")

# --- ÁREA DE POSTAGEM (APENAS NÃO-VISITANTES) ---
if st.session_state["perfil"] != "visitante":
    st.sidebar.header("📝 Novo Aviso")
    setor_sel = st.sidebar.selectbox("Setor Responsável", SETORES)
    texto = st.sidebar.text_area("Mensagem do aviso")

    if st.sidebar.button("Publicar Aviso"):
        if texto:
            novo = {
                "Data": get_brasilia_time().strftime("%d/%m/%Y %H:%M"),
                "Autor": st.session_state['nome_colaborador'],
                "Setor": setor_sel,
                "Aviso": texto,
                "Status": "Pendente",
                "Resolvido_Por": ""
            }
            df_atual = load_data()
            df_novo = pd.concat([pd.DataFrame([novo]), df_atual], ignore_index=True)
            save_data(df_novo)
            st.rerun()

# --- SISTEMA DE ABAS (MURAL vs HISTÓRICO) ---
tab_mural, tab_historico = st.tabs(["📌 Avisos Ativos", "📂 Histórico (Resolvidos)"])

df_all = load_data()

# --- ABA 1: MURAL DE ATIVOS ---
with tab_mural:
    df_pendentes = df_all[df_all["Status"] == "Pendente"]
    if not df_pendentes.empty:
        for i, row in df_pendentes.iterrows():
            with st.container():
                c1, c2 = st.columns([0.80, 0.20])
                with c1:
                    st.markdown(f"### ⏳ PENDENTE | {row['Setor']}")
                    st.caption(f"📅 {row['Data']}")
                    st.info(row['Aviso'])
                with c2:
                    if st.session_state["perfil"] != "visitante":
                        st.write("")
                        # Botão para resolver o aviso
                        if st.button("✅", key=f"res_{i}", help="Marcar como resolvido"):
                            df_all = df_all.astype(object) # Evita erro de tipo
                            df_all.at[i, "Status"] = "Resolvido"
                            df_all.at[i, "Resolvido_Por"] = get_brasilia_time().strftime("%d/%m/%Y %H:%M")
                            save_data(df_all)
                            st.rerun()
                        # Botão para excluir
                        if st.button("🗑️", key=f"del_{i}"):
                            df_all = df_all.drop(i)
                            save_data(df_all)
                            st.rerun()
                st.divider()
    else:
        st.write("Não há avisos pendentes no momento.")

# --- ABA 2: HISTÓRICO (SOMENTE DATA E HORA NO TÍTULO) ---
with tab_historico:
    df_resolvidos = df_all[df_all["Status"] == "Resolvido"]
    if not df_resolvidos.empty:
        for i, row in df_resolvidos.iterrows():
            # Mostra apenas a data da resolução no título do expander
            with st.expander(f"✅ Resolvido em {row['Resolvido_Por']} - {row['Setor']}"):
                st.write(f"**Mensagem Original:**")
                st.write(row['Aviso'])
                st.caption(f"Postado originalmente em: {row['Data']}")
                
                if st.session_state["perfil"] != "visitante":
                    if st.button("Excluir Permanentemente", key=f"del_hist_{i}"):
                        df_all = df_all.drop(i)
                        save_data(df_all)
                        st.rerun()
    else:
        st.write("O histórico de resolvidos está vazio.")
