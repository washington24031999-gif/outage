# --- INTERFACE ---
with st.sidebar:
    st.image(URL_LOGO, width=150)
    st.write(f"👤 **{st.session_state['nome_colaborador']}**")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    st.divider()

# AQUI ESTÁ A MUDANÇA DO TÍTULO
st.title("📢 Outage St1")

# --- SISTEMA DE ABAS (MURAL vs HISTÓRICO) ---
tab_mural, tab_historico = st.tabs(["📌 Avisos Ativos", "📂 Histórico (Resolvidos)"])
