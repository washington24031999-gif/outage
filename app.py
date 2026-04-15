import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO RETRÔ E LEVE) ---
st.set_page_config(page_title="Outage St1", layout="wide")

# Link da sua logo
URL_LOGO = "https://lp.st1.net.br/_assets/v11/5ed2c17da035a77db190d04005e3598e98c2cb7a.png"
st.logo(URL_LOGO) # Coloca a logo no topo da barra lateral

# CSS para visual de terminal/sistema antigo
st.markdown("""
    <style>
    * { border-radius: 0px !important; }
    .stButton>button { border: 1px solid #333; background: #f0f0f0; color: black; font-family: monospace; width: 100%; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { border: 1px solid #333 !important; font-family: monospace; }
    .aviso-box { border: 1px solid #000; padding: 10px; margin-bottom: 5px; background-color: #fff; color: #000; font-family: monospace; }
    .aviso-header { border-bottom: 1px solid #000; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    .status-pendente { color: #d00; }
    .status-resolvido { color: #008000; }
    </style>
""", unsafe_allow_html=True)

# --- USUÁRIOS ---
USUARIOS = {
    "admin": ["notgnihsaw", "Washington Muniz"],
    "victor melo": ["12345678", "Victor Melo"],
    "visitante": ["ver123", "Visitante"]
}

SETORES = ["Sup. Campo", "Suporte", "Financeiro", "Administração", "Operacional"]

if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome_colaborador" not in st.session_state:
    st.session_state["nome_colaborador"] = ""
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None

def get_brasilia_time():
    return datetime.utcnow() - timedelta(hours=3)

# --- LOGIN ---
def login():
    # Exibe a logo centralizada na tela de login
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.image(URL_LOGO, use_container_width=True)
    
    st.markdown("<h2 style='text-align: center;'>🔐 LOGIN DO SISTEMA</h2>", unsafe_allow_html=True)
    
    u_input = st.text_input("USUÁRIO:").lower().strip()
    s_input = st.text_input("SENHA:", type="password")
    
    if st.button("EXECUTAR AUTENTICAÇÃO", use_container_width=True):
        if u_input in USUARIOS and USUARIOS[u_input][0] == s_input:
            st.session_state["logado"] = True
            st.session_state["perfil"] = u_input
            st.session_state["nome_colaborador"] = USUARIOS[u_input][1]
            st.rerun()
        else:
            st.error("USUÁRIO OU SENHA INCORRETOS")

# Bloqueio: Se não estiver logado, para o script e mostra a tela de login
if not st.session_state["logado"]:
    login()
    st.stop()

# --- FUNÇÕES DE DADOS ---
def load_data():
    arquivo = "avisos.csv"
    cols = ["Data", "Autor", "Setor", "Aviso", "Status", "Resolvido_Por"]
    if os.path.exists(arquivo):
        try:
            # Força leitura como string para evitar erros de tipo
            df = pd.read_csv(arquivo, dtype=str).fillna("")
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.astype(str).to_csv("avisos.csv", index=False)

# --- INTERFACE PRINCIPAL ---
with st.sidebar:
    # Logo também no topo da sidebar
    st.image(URL_LOGO, width=150)
    st.write(f"👤 **{st.session_state['nome_colaborador']}**")
    if st.button("SAIR"):
        st.session_state.clear()
        st.rerun()
    st.divider()

st.title("📢 Outage St1")

# --- ÁREA DE POSTAGEM (APENAS NÃO-VISITANTES) ---
if st.session_state["perfil"] != "visitante":
    st.sidebar.header("📝 Novo Aviso")
    
    # Nome automático e travado conforme o login
    st.sidebar.text_input("Colaborador", value=st.session_state['nome_colaborador'], disabled=True)
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
            st.sidebar.success("Aviso publicado!")
            st.rerun()
else:
    st.sidebar.info("Modo Visualização")

# --- EXIBIÇÃO ---
st.subheader("Avisos Recentes")
df_display = load_data()

if not df_display.empty:
    for i, row in df_display.iterrows():
        is_resolvido = str(row["Status"]) == "Resolvido"
        
        with st.container():
            c1, c2 = st.columns([0.80, 0.20])
            with c1:
                status_txt = "✅ RESOLVIDO" if is_resolvido else "⏳ PENDENTE"
                st.markdown(f"### {row['Autor']} | {row['Setor']} | {status_txt}")
                st.caption(f"📅 Postado em: {row['Data']}")
                
                if is_resolvido:
                    st.success(f"{row['Aviso']}\n\n*Resolvido por: {row['Resolvido_Por']}*")
                else:
                    st.info(row['Aviso'])
            
            with c2:
                if st.session_state["perfil"] != "visitante":
                    st.write("")
                    # Botão Resolvido
                    if not is_resolvido:
                        if st.button("✅", key=f"res_{i}", help="Marcar como Resolvido"):
                            # Evita erro de tipo de coluna
                            df_display = df_display.astype(object)
                            df_display.at[i, "Status"] = "Resolvido"
                            df_display.at[i, "Resolvido_Por"] = f"{st.session_state['nome_colaborador']} em {get_brasilia_time().strftime('%d/%m %H:%M')}"
                            save_data(df_display)
                            st.rerun()
                    
                    # Botão Excluir
                    if st.button("🗑️", key=f"del_{i}", help="Excluir Aviso"):
                        df_res = df_display.drop(i)
                        save_data(df_res)
                        st.rerun()
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
