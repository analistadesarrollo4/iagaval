from openai import AzureOpenAI
import time
import streamlit as st

openai_model = "gpt-4o-mini"

client = AzureOpenAI(
    azure_endpoint=st.secrets["OPENAI_URL"],
    api_key=st.secrets["OPENAI_API_KEY"],
    api_version="2024-05-01-preview"
)

thread_id: str
assistant_id: str = "asst_R4ZF2YRUYBlIravD3Tsw1m2I"

st.set_page_config(page_title="DO Assistant", page_icon=":star:")


if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


# Set up our front end page
st.title("DO Assistant")
st.write("Asistente para creación de historias de usuario...")


if st.button('Iniciar Asistente'):
    st.session_state.start_chat = True


    # Create a new thread for this chat session
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id
    st.success(f"Sesión iniciada. Thread ID: {chat_thread.id}")


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
    if prompt := st.chat_input("En que te puedo ayudar hoy?"):
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