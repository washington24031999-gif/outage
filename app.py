import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO RETRÔ E LEVE) ---
st.set_page_config(page_title="Outage St1", layout="wide")

# CSS para visual de terminal/sistema antigo em PT-BR
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

# --- DICIONÁRIO DE USUÁRIOS ---
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

def get_brasilia_time():
    return datetime.utcnow() - timedelta(hours=3)

# --- SISTEMA DE ACESSO ---
if not st.session_state["logado"]:
    st.write("### [ LOGIN_TERMINAL_OUTAGE ]")
    u = st.text_input("ID_USUARIO:").lower().strip()
    p = st.text_input("SENHA:", type="password")
    if st.button("EXECUTAR_AUTENTICACAO"):
        if u in USUARIOS and USUARIOS[u][0] == p:
            st.session_state["logado"] = True
            st.session_state["nome_colaborador"] = USUARIOS[u][1]
            st.rerun()
        else:
            st.error("ACESSO_NEGADO: CREDENCIAIS_INVALIDAS")
    st.stop()

# --- CARREGAMENTO DE DADOS ---
def load_data():
    arquivo = "avisos.csv"
    cols = ["Data", "Autor", "Setor", "Aviso", "Status", "Resolvido_Por"]
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo, dtype=str).fillna("")
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.astype(str).to_csv("avisos.csv", index=False)

# --- INTERFACE PRINCIPAL ---
st.write(f"**USUARIO_ATIVO:** {st.session_state['nome_colaborador']} | **PORTA:** 8501")
if st.button("[ ENCERRAR_SESSAO ]"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")
st.write("# 📢 OUTAGE ST1")

col_input, col_mural = st.columns([1, 2])

with col_input:
    st.write("### [ ENTRADA_DE_DADOS ]")
    setor_sel = st.selectbox("SETOR_ALVO:", SETORES)
    texto = st.text_area("DESCRICAO_LOG:")
    if st.button("SALVAR_NO_DISCO"):
        if texto:
            novo = {
                "Data": get_brasilia_time().strftime("%d/%m/%Y %H:%M"),
                "Autor": st.session_state['nome_colaborador'],
                "Setor": setor_sel,
                "Aviso": texto,
                "Status": "Pendente",
                "Resolvido_Por": ""
            }
            df = load_data()
            df = pd.concat([pd.DataFrame([novo]), df], ignore_index=True)
            save_data(df)
            st.rerun()

with col_mural:
    df_all = load_data()
    
    st.write("### [ LOGS_ATIVOS ]")
    df_pendentes = df_all[df_all["Status"] == "Pendente"]
    
    if not df_pendentes.empty:
        for i, row in df_pendentes.iterrows():
            st.markdown(f"""
            <div class="aviso-box">
                <div class="aviso-header">
                    <span class="status-pendente">[PENDENTE]</span> {row['Data']} | SETOR: {row['Setor']}
                </div>
                {row['Aviso']}
            </div>
            """, unsafe_allow_html=True)
            
            c_res, c_del, _ = st.columns([0.2, 0.2, 0.6])
            if c_res.button("RESOLVER", key=f"res_{i}"):
                df_all = df_all.astype(object) # Correção de erro de tipo
                df_all.loc[i, "Status"] = "Resolvido"
                df_all.loc[i, "Resolvido_Por"] = get_brasilia_time().strftime("%d/%m/%Y %H:%M")
                save_data(df_all)
                st.rerun()
            if c_del.button("EXCLUIR", key=f"del_{i}"):
                save_data(df_all.drop(i))
                st.rerun()
    else:
        st.write("> NENHUMA_PENDENCIA_ENCONTRADA.")

    st.markdown("---")
    st.write("### [ ARQUIVO_HISTORICO ]")
    df_resolvidos = df_all[df_all["Status"] == "Resolvido"].head(10)
    
    if not df_resolvidos.empty:
        for i, row in df_resolvidos.iterrows():
            st.markdown(f"""
            <div class="aviso-box" style="background-color: #f9f9f9; border: 1px dashed #999;">
                <div class="aviso-header">
                    <span class="status-resolvido">[RESOLVIDO]</span> {row['Resolvido_Por']} | SETOR: {row['Setor']}
                </div>
                {row['Aviso']}
            </div>
            """, unsafe_allow_html=True)
