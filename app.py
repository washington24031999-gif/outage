import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Outage St1", layout="wide")

URL_LOGO = "https://lp.st1.net.br/_assets/v11/5ed2c17da035a77db190d04005e3598e98c2cb7a.png"
st.logo(URL_LOGO)

st.markdown("""
    <style>
    * { border-radius: 0px !important; }
    .stButton>button { border: 1px solid #333; background: #f0f0f0; color: black; font-family: monospace; width: 100%; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { border: 1px solid #333 !important; font-family: monospace; }
    .aviso-box { border: 1px solid #000; padding: 10px; margin-bottom: 5px; background-color: #fff; color: #000; font-family: monospace; }
    .aviso-header { border-bottom: 1px solid #000; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
    .status-pendente { color: #d00; }
    .btn-perigo>div>button { background-color: #ffcccc !important; border: 1px solid #d00 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- USUÁRIOS ---
USUARIOS = {
    "admin": ["notgnihsaw", "Washington Muniz", "Supervisor de Campo"],
    "victor melo": ["12345678", "Victor Melo", "Suporte"],
    "visitante": ["ver123", "Visitante", "Operacional"]
}

# Inicialização de estados
if "logado" not in st.session_state: st.session_state["logado"] = False
if "user_id" not in st.session_state: st.session_state["user_id"] = ""
if "nome_colaborador" not in st.session_state: st.session_state["nome_colaborador"] = ""
if "setor_colaborador" not in st.session_state: st.session_state["setor_colaborador"] = ""
if "mostrar_historico" not in st.session_state: st.session_state["mostrar_historico"] = True
if "edit_index" not in st.session_state: st.session_state["edit_index"] = None
if "edit_text" not in st.session_state: st.session_state["edit_text"] = ""

def get_brasilia_time():
    return datetime.utcnow() - timedelta(hours=3)

# --- ACESSO ---
if not st.session_state["logado"]:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c: st.image(URL_LOGO, use_container_width=True)
    st.write("### LOGIN TERMINAL OUTAGE")
    u = st.text_input("ID USUARIO:").lower().strip()
    p = st.text_input("SENHA:", type="password")
    if st.button("EXECUTAR AUTENTICACAO"):
        if u in USUARIOS and USUARIOS[u][0] == p:
            st.session_state["logado"], st.session_state["user_id"] = True, u
            st.session_state["nome_colaborador"], st.session_state["setor_colaborador"] = USUARIOS[u][1], USUARIOS[u][2]
            st.rerun()
        else: st.error("ACESSO NEGADO")
    st.stop()

# --- DADOS ---
def load_data():
    arquivo = "avisos.csv"
    if os.path.exists(arquivo):
        try: return pd.read_csv(arquivo, dtype=str).fillna("")
        except: return pd.DataFrame(columns=["Data", "Autor", "Setor", "Aviso", "Status", "Resolvido_Por"])
    return pd.DataFrame(columns=["Data", "Autor", "Setor", "Aviso", "Status", "Resolvido_Por"])

def save_data(df):
    df.astype(str).to_csv("avisos.csv", index=False)

# --- INTERFACE ---
st.write(f"**USUARIO:** {st.session_state['nome_colaborador']} | **SETOR:** {st.session_state['setor_colaborador']}")
if st.button("SAIR"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")
st.write("# 📢 OUTAGE ST1")

col_in, col_out = st.columns([1, 2])

with col_in:
    # Se estiver em modo edição, muda o título
    st.write("### EDITAR ALARME" if st.session_state["edit_index"] is not None else "### ENTRADA DE DADOS")
    st.text_input("SETOR:", value=st.session_state['setor_colaborador'], disabled=True)
    
    # Campo de texto recebe o valor do alarme em edição, se houver
    msg = st.text_area("MENSAGEM:", value=st.session_state["edit_text"])
    
    col_btn1, col_btn2 = st.columns(2)
    if st.session_state["edit_index"] is not None:
        if col_btn1.button("SALVAR ALTERAÇÃO"):
            df = load_data()
            df.at[st.session_state["edit_index"], "Aviso"] = msg
            save_data(df)
            st.session_state["edit_index"], st.session_state["edit_text"] = None, ""
            st.rerun()
        if col_btn2.button("CANCELAR"):
            st.session_state["edit_index"], st.session_state["edit_text"] = None, ""
            st.rerun()
    else:
        if st.button("SALVAR NO DISCO"):
            if msg:
                novo = {"Data": get_brasilia_time().strftime("%d/%m/%Y %H:%M"), "Autor": st.session_state['nome_colaborador'], 
                        "Setor": st.session_state['setor_colaborador'], "Aviso": msg, "Status": "Pendente", "Resolvido_Por": ""}
                df = load_data()
                save_data(pd.concat([pd.DataFrame([novo]), df], ignore_index=True))
                st.rerun()

with col_out:
    df_all = load_data()
    st.write("### LOGS ATIVOS")
    df_p = df_all[df_all["Status"] == "Pendente"].copy()
    
    if not df_p.empty:
        # Ações em massa
        if st.session_state["user_id"] != "visitante":
            with st.expander("🛠️ AÇÕES EM MASSA"):
                st.write("Selecione para resolver em lote:")
                selecionados = []
                for i, row in df_p.iterrows():
                    if st.checkbox(f"{row['Data']} - {row['Aviso'][:30]}...", key=f"ch_{i}"): selecionados.append(i)
                if selecionados and st.button(f"RESOLVER {len(selecionados)} SELECIONADOS"):
                    for idx in selecionados:
                        df_all.at[idx, "Status"] = "Resolvido"
                        df_all.at[idx, "Resolvido_Por"] = f"{st.session_state['nome_colaborador']} (Lote)"
                    save_data(df_all)
                    st.rerun()

        # Cards individuais
        for i, row in df_p.iterrows():
            st.markdown(f'<div class="aviso-box"><div class="aviso-header"><span class="status-pendente">PENDENTE</span> {row["Data"]} | AUTOR: {row["Autor"]}</div>{row["Aviso"]}</div>', unsafe_allow_html=True)
            
            c_res, c_edit, c_del = st.columns([0.3, 0.3, 0.4])
            if c_res.button("RESOLVER", key=f"r_{i}"):
                df_all.at[i, "Status"] = "Resolvido"
                df_all.at[i, "Resolvido_Por"] = f"{st.session_state['nome_colaborador']} em {get_brasilia_time().strftime('%H:%M')}"
                save_data(df_all)
                st.rerun()
            # Função EDITAR
            if c_edit.button("EDITAR", key=f"e_{i}"):
                st.session_state["edit_index"] = i
                st.session_state["edit_text"] = row["Aviso"]
                st.rerun()
            if c_del.button("EXCLUIR", key=f"d_{i}"):
                save_data(df_all.drop(i))
                st.rerun()
    else:
        st.write("Nenhuma pendência.")

    # Histórico
    st.markdown("---")
    c_h1, c_h2 = st.columns([0.7, 0.3])
    c_h1.write("### ARQUIVO HISTORICO")
    if c_h2.button("OCULTAR / EXIBIR"):
        st.session_state["mostrar_historico"] = not st.session_state["mostrar_historico"]
        st.rerun()

    if st.session_state["mostrar_historico"]:
        df_r = df_all[df_all["Status"] == "Resolvido"].head(1000)
        for i, row in df_r.iterrows():
            with st.expander(f"OK: {row['Resolvido_Por']}"):
                st.write(f"**Original:** {row['Aviso']}")
                if st.button("EXCLUIR PERMANENTE", key=f"del_h_{i}"):
                    save_data(df_all.drop(i))
                    st.rerun()
