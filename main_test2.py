import json
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
import time
import os

load_dotenv()

model = "gpt-4o-mini"

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
    azure_endpoint=os.getenv('OPENAI_URL', "https://default.endpoint.com"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-05-01-preview"
)

def get_news(topic):
    pass


class AssistantManager:
    thread_id: str= "thread_nfmQ1iSLpefeHRdJayzwmFyc"
    assistant_id: str = "asst_R4ZF2YRUYBlIravD3Tsw1m2I"

    def __init__(self, model: str= model):
        self.client= client
        self.model= model
        self.assistant= None
        self.thread= None
        self.run= None
        self.summary= None

        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id= AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj= self.client.beta.assistants.create(
                name= name,
                instructions= instructions,
                tools= tools,
                model= model,
                temperature=0.8,
                top_p=0.95
            )
            AssistantManager.assistant_id= assistant_obj.id
            self.assistant= assistant_obj
            print(f"AssistantID::::{self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj= self.client.beta.threads.create()
            AssistantManager.thread_id= thread_obj.id
            self.thread= thread_obj
            print(f"ThreadID::::{self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id= self.thread.id,
                role= role,
                content= content
            )

    def run_assistant(self):
        if self.thread and self.assistant:
            self.run= self.client.beta.threads.runs.create(
                thread_id= self.thread.id,
                assistant_id= self.assistant.id,
            )

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            summary = []

            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)

            self.summary = "\n".join(summary)
            print(f"SUMMARY-----> {role.capitalize()}: ==> {response}")

    def call_required_actions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name= action["function"]["name"]
            arguments= json.load(action["functions"]["arguments"])

            if func_name == "get_news":
                output= get_news(topic= arguments["topic"])
                print(f"STUFFFFF;;;;{output}")
                final_str= ""
                for item in output:
                    final_str+= "".join(item)

                tool_outputs.append({"tool_call_id": action["id"],
                                     "output": final_str})
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the assistant ...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id= self.thread.id,
            run_id= self.run.id,
            tool_outputs= tool_outputs
        )

    #for Streamlit
    def get_summary(self):
        return self.summary

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )
                print(f"RUN STATUS:: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING NOW...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

    #Run Steps
    def run_steps(self):
        run_steps= self.client.beta.threads.runs.steps.list(
            thread_id= self.thread.id,
            run_id= self.run.id
        )
        print(f"Run-Steps::: {run_steps}")


def main():
    manager= AssistantManager()

    #===== Streamlit Interface =====

    st.title("Product Owner Assistant")
    with st.form(key="user_input_form"):
        instructions= st.text_input("Send message:")
        submit_button= st.form_submit_button(label="Run Assistant")

        if submit_button:
            manager.create_assistant(
                name= "DO Assistant",
                instructions= assistant_instructions,
                tools= [
                    {
                        "type": "function",
                        "function": {
                            "name": "get_news",
                            "description": "get list of articles/news",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "topic": {
                                        "type": "string",
                                        "descripcion": "The topic for the article/news"
                                    }
                                },
                                "required": ["topic"]
                            }
                        }
                    }
                ]
            )

            manager.create_thread()

            # Add the messages and run the Assistant

            manager.add_message_to_thread(
                role= "user",
                content= instructions
            )

            manager.run_assistant()

            # Wait for completions and process messages

            manager.wait_for_completion()

            summary= manager.get_summary()

            st.write(summary)

            st.text("Run Steps:")
            st.code(manager.run_steps(), line_numbers= True)


if __name__ == "__main__":
    main()