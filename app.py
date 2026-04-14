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

# Função para salvar dados
def save_data(df):
    df.to_csv("avisos.csv", index=False)

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
        save_data(df)
        st.sidebar.success("Aviso publicado!")
        st.rerun()
    else:
        st.sidebar.error("Preencha todos os campos.")

# Exibição dos avisos
st.subheader("Avisos Recentes")
df_display = load_data()

if not df_display.empty:
    for i, row in df_display.iterrows():
        # Criamos um container para cada aviso
        with st.container():
            col1, col2 = st.columns([0.85, 0.15]) # Divide o espaço entre o texto e o botão
            
            with col1:
                st.markdown(f"### {row['Autor']}")
                st.caption(f"Postado em: {row['Data']}")
                st.info(row['Aviso'])
            
            with col2:
                # Botão de excluir usando o índice da linha
                st.write("") # Espaçamento para alinhar
                if st.button("🗑️", key=f"del_{i}"):
                    df_novo = df_display.drop(i)
                    save_data(df_novo)
                    st.toast(f"Aviso de {row['Autor']} excluído!")
                    st.rerun()
            st.divider()
else:
    st.write("Nenhum aviso no momento.")
