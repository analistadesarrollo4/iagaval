import streamlit as st
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=st.secrets["OPENAI_URL"],
    api_key=st.secrets["OPENAI_API_KEY"],
    api_version="2024-05-01-preview"
)

thread_id: str
assistant_id: str = ""

#==== Config UI =====
st.title("IAgaval")

st.subheader("Selecciona el área con la que deseas chatear ...")

opciones = ["Selecciona una opción", "Crédito"]
seleccion = st.selectbox("Área:", opciones, index=0)

if seleccion == "Selecciona una opción":
    st.warning("Por favor, elige una opción válida.")
else:
    if st.button("Iniciar Chat ..."):
        st.session_state.agaval_start_chat = True