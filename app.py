import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO RETRÔ E LEVE) ---
st.set_page_config(page_title="Outage St1", layout="wide")

# Link da logo
URL_LOGO = "https://lp.st1.net.br/_assets/v11/5ed2c17da035a77db190d04005e3598e98c2cb7a.png"
st.logo(URL_LOGO)

# CSS para visual limpo e retrô
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

# --- USUÁRIOS E SETORES FIXOS ---
USUARIOS = {
    "admin": ["notgnihsaw", "Washington Muniz", "Supervisor de Campo"], # Setor atualizado aqui
    "victor melo": ["12345678", "Victor Melo", "Suporte"],
    "visitante": ["ver123", "Visitante", "Operacional"]
}

if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "nome_colaborador" not in st.session_state:
    st.session_state["nome_colaborador"] = ""
if "setor_colaborador" not in st.session_state:
    st.session_state["setor_colaborador"] = ""

def get_brasilia_time():
    return datetime.utcnow() - timedelta(hours=3)

# --- SISTEMA DE ACESSO ---
if not st.session_state["logado"]:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.image(URL_LOGO, use_container_width=True)
    st.write("### LOGIN TERMINAL OUTAGE")
    u = st.text_input("ID USUARIO:").lower().strip()
    p = st.text_input("SENHA:", type="password")
    if st.button("EXECUTAR AUTENTICACAO"):
        if u in USUARIOS and USUARIOS[u][0] == p:
            st.session_state["logado"] = True
            st.session_state["nome_colaborador"] = USUARIOS[u][1]
            st.session_state["setor_colaborador"] = USUARIOS[u][2]
            st.rerun()
        else:
            st.error("ACESSO NEGADO: CREDENCIAIS INVALIDAS")
    st.stop()

# --- CARREGAMENTO DE DADOS ---
def load_data():
    arquivo = "avisos.csv"
    cols = ["Data", "Autor", "Setor", "Aviso", "Status", "Resolvido_Por"]
    if os.path.exists(arquivo):
        try:
            return pd.read_csv(arquivo, dtype=str).fillna("")
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.astype(str).to_csv("avisos.csv", index=False)

# --- INTERFACE PRINCIPAL ---
st.write(f"**USUARIO ATIVO:** {st.session_state['nome_colaborador']} | **SETOR:** {st.session_state['setor_colaborador']}")
if st.button("ENCERRAR SESSAO"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")
st.write("# 📢 OUTAGE ST1")

col_in, col_out = st.columns([1, 2])

with col_in:
    st.write("### ENTRADA DE DADOS")
    # Campo de setor travado para edição
    st.text_input("SETOR ALVO:", value=st.session_state['setor_colaborador'], disabled=True)
    msg = st.text_area("DESCRICAO LOG:")
    if st.button("SALVAR NO DISCO"):
        if msg:
            novo = {
                "Data": get_brasilia_time().strftime("%d/%m/%Y %H:%M"),
                "Autor": st.session_state['nome_colaborador'],
                "Setor": st.session_state['setor_colaborador'],
                "Aviso": msg,
                "Status": "Pendente",
                "Resolvido_Por": ""
            }
            df = load_data()
            df = pd.concat([pd.DataFrame([novo]), df], ignore_index=True)
            save_data(df)
            st.rerun()

with col_out:
    df_all = load_data()
    st.write("### LOGS ATIVOS")
    df_p = df_all[df_all["Status"] == "Pendente"]
    
    if not df_p.empty:
        for i, row in df_p.iterrows():
            st.markdown(f"""
            <div class="aviso-box">
                <div class="aviso-header">
                    <span class="status-pendente">PENDENTE</span> {row['Data']} | SETOR: {row['Setor']}
                </div>
                <b>AUTOR:</b> {row['Autor']}<br>
                <b>MSG:</b> {row['Aviso']}
            </div>
            """, unsafe_allow_html=True)
            c1, c2, _ = st.columns([0.2, 0.2, 0.6])
            if c1.button("RESOLVER", key=f"r_{i}"):
                df_all = df_all.astype(object)
                df_all.at[i, "Status"] = "Resolvido"
                df_all.at[i, "Resolvido_Por"] = f"{st.session_state['nome_colaborador']} em {get_brasilia_time().strftime('%d/%m/%Y %H:%M')}"
                save_data(df_all)
                st.rerun()
            if c2.button("EXCLUIR", key=f"d_{i}"):
                save_data(df_all.drop(i))
                st.rerun()
    else:
        st.write("> NENHUMA PENDENCIA ENCONTRADA.")

    st.markdown("---")
    st.write("### ARQUIVO HISTORICO")
    df_r = df_all[df_all["Status"] == "Resolvido"].head(10)
    for i, row in df_r.iterrows():
        st.markdown(f"""
        <div class="aviso-box" style="background-color: #f9f9f9; border: 1px dashed #999;">
            <div class="aviso-header">
                <span class="status-resolvido">RESOLVIDO POR:</span> {row['Resolvido_Por']}
            </div>
            <b>AUTOR ORIGINAL:</b> {row['Autor']}<br>
            <b>SETOR:</b> {row['Setor']}<br>
            <b>MSG:</b> {row['Aviso']}
        </div>
        """, unsafe_allow_html=True)
