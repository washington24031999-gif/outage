import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="Sistema de Avisos Online", layout="centered")

st.title("📢 Mural de Avisos Digital")

# Função para carregar dados
def load_data():
    if os.path.exists("avisos.csv"):
        return pd.read_csv("avisos.csv")
    else:
        return pd.DataFrame(columns=["Data", "Autor", "Aviso"])

# Interface lateral para novos avisos
st.sidebar.header("Novo Aviso")
autor = st.sidebar.text_input("Seu nome/setor")
texto_aviso = st.sidebar.text_area("Mensagem do aviso")

if st.sidebar.button("Publicar Aviso"):
    if autor and texto_aviso:
        nova_linha = {
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Autor": autor,
            "Aviso": texto_aviso
        }
        df = load_data()
        df = pd.concat([pd.DataFrame([nova_linha]), df], ignore_index=True)
        df.to_csv("avisos.csv", index=False)
        st.sidebar.success("Aviso publicado!")
        st.rerun()
    else:
        st.sidebar.error("Preencha todos os campos.")

# Exibição dos avisos
st.subheader("Avisos Recentes")
df_display = load_data()

if not df_display.empty:
    for i, row in df_display.iterrows():
        with st.container():
            st.markdown(f"### {row['Autor']}")
            st.caption(f"Postado em: {row['Data']}")
            st.info(row['Aviso'])
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
