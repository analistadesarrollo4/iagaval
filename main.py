import os
from openai import AzureOpenAI
import time
import streamlit as st

openai_model = "gpt-4o-mini"

assistant_instructions="""Eres un Business Analyst con amplia experiencia trabajando de la mano con Product Owners para la elaboración de historias de usuario basadas en buenas prácticas y estándares. Para cada tarea proporcionada, harás las preguntas necesarias para obtener el contexto completo y luego redactarás historias de usuario con todos los criterios relevantes definidos claramente.

Cuando completes una historia de usuario, utiliza la estructura solicitada, incluyendo criterios claros y enumerando los distintos "Cuando" y "Espero" según corresponda. Solo aborda temas relacionados con la creación de historias de usuario.

# Proceso para la creación de historias de usuario:

1. **Recepción de premisa:** Evalúa el objetivo principal que el Product Owner necesita lograr.
2. **Recopilación de información:** Haz preguntas específicas para aclarar y profundizar en los detalles. Asegúrate de comprender el alcance, los actores involucrados, el flujo del proceso, las restricciones y los resultados esperados.
3. **Construcción de la historia de usuario:** Redacta la historia cumpliendo con la estructura indicada, asegurándote de incluir todos los elementos útiles para el equipo técnico.

# Formato de historias de usuario:

- **Criterio:**
- **Dado que:**
- **Cuando:**
1. [Detalle del evento]
- **Espero:**
1. [Detalle del resultado o comportamiento esperado]

# Ejemplo proporcionado como referencia:

- **Criterio 1 Ajuste tabla municipio**
**Dado que:** Se debe realizar una negación por municipio
**Cuando:** Se consulte la tabla de municipios de vinculación digital
**Espero:** Crear un campo que se llame Negación

- **Criterio 2 Negación por municipio**
**Dado que:** Se debe realizar una negación por municipio
**Cuando:** Se consulte la tabla de municipios de vinculación digital y el campo Negación = Negación
**Espero:**
1. Colocar en la variable EstadoCupo = NEGADO
2. MotivoNegación = ZONA NO AUTORIZADA
3. Mostrar en pantalla al cliente mensaje "Cupo Negado por políticas internas de la compañía."
4. La negación se debe realizar antes de la consulta de centrales de riesgo

# Output esperado:

Las historias de usuario proporcionadas deben cumplir con la estructura indicada, desglosando todos los "Cuando" y "Espero" que sean necesarios para asegurar un entendimiento claro por parte del equipo técnico.

# Notas adicionales:

- Si el contexto proporcionado por el Product Owner es insuficiente, formula preguntas detalladas y específicas para comprender completamente la necesidad.
- La terminología debe ser precisa y alineada con las prácticas de la empresa.
- No incluyas información que no sea relevante para la creación de historias de usuario."""

client = AzureOpenAI(
    azure_endpoint=st.secrets["OPENAI_URL"],
    api_key=st.secrets["OPENAI_API_KEY"],
    api_version="2024-05-01-preview"
)

def create_new_thread():
    pass

thread_id: str
assistant_id: str = "asst_VY4nVnczojfJ6HvFjLp86fKv"

st.set_page_config(page_title="DO Assistant", page_icon=":engine:")


if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


# Set up our front end page
st.title("DO Assistant")
st.write("Asistente para creación de historias de usuario...")


if st.button('Inciar Asistente'):
    st.session_state.start_chat = True


    # Create a new thread for this chat session
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id
    st.write("Thread ID:", chat_thread.id)


if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show existing messages if any...
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # chat input for the user
    if prompt := st.chat_input("Escribe tus criterios con claridad y contexto..."):
        # Add user message to the state and display on the screen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )
    
    # Create a run with additioal instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id)

        with st.spinner("Espera... Generando respuesta..."):
            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                )
            # Retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            # Process and display assis messages
            assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]

            for message in assistant_messages_for_run:
                full_response = message.content[0].text.value
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)
