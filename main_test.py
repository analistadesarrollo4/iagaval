from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()

model = "gpt-4o-mini"

PROMPT_ASSISTANT="""Eres un Business Analyst con amplia experiencia trabajando de la mano con Product Owners para la elaboración de historias de usuario basadas en buenas prácticas y estándares. Para cada tarea proporcionada, harás las preguntas necesarias para obtener el contexto completo y luego redactarás historias de usuario con todos los criterios relevantes definidos claramente.

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

#== Creacion de nuestro asistente ==

# po_assistant = client.beta.assistants.create(
#     name="Product Owner Assistant",
#     instructions=PROMPT_ASSISTANT,
#     model=model,
#     tools=[{"type": "code_interpreter"}],
#     temperature=0.8,
#     top_p=0.95
# )
# assistant_id = po_assistant.id
# print(f"Asistente ID: {assistant_id}")


# thread = client.beta.threads.create()
# thread_id = thread.id
# print(f"Hilo ID: {thread_id}")


assistant_id="asst_8xPip75rF93PoSaHZQvyy0n8"
thread_id="thread_MH85zqAVQSAyzbFrlMTCEeaI"


#=====Creacion de un mensaje====
user_message="Necesito adicionar un campo llamado Ciudad en la tabla de cxc_clientes, de la base de datos PRIVADA, para tener en el sistema la ciudad donde vive el usuario"

assistant_message= client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=user_message
)

# #====== Correr nuestro asistente ======

run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id
)


def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """

    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)

# === Run ===
# run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
# print(run)

wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

#==== Steps --- Logs ==
run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
print(f"Steps---> {run_steps.data[0]}")