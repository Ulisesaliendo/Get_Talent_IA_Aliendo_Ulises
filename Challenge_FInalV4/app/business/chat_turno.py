from app.services.vector_clients import co
import json
from pydantic import BaseModel, ValidationError

# Historial de conversación
conversation_history = []

# Modelo de turno para validar el JSON
class TurnoState(BaseModel):
    dia: str
    paciente: str
    start_time: str
    end_time: str
    nota: str | None = None

SYSTEM_TURNO_PROMPT = """
Eres un asistente especializado en agendamiento de turnos.

Tu objetivo es construir un JSON válido con los siguientes campos:
- dia (YYYY-MM-DD)
- paciente
- start_time (HH:MM, 24h)
- end_time (HH:MM, 24h)
- nota (opcional, puede ser null)

Reglas estrictas:
1. Nunca inventes valores.
2. Si falta información, pregunta de forma clara.
3. Usa el historial para completar los campos.
4. No muestres turnos ocupados a menos que el usuario lo solicite.
5. Cuando todos los campos obligatorios estén completos, responde SOLO con el JSON.
6. No expliques el JSON ni agregues texto adicional.
7. No asignes IDs ni intentes guardar el turno.

Estado actual del turno:
{state}

Turnos ocupados (uso interno, no mostrar):
{turnos_ocupados}

Historial de conversación:
{historial}
"""

def turnos_chat_response(user_message, state={}, turnos_ocupados=[]):
    global conversation_history

    # Añade el mensaje del usuario al historial global
    conversation_history.append({"role": "user", "content": user_message})

    # Tomamos solo los últimos 5 elementos del historial para enviar al modelo
    last_messages = conversation_history[-5:]

    # Construimos el prompt interpolando estado y historial
    prompt = SYSTEM_TURNO_PROMPT.format(
        state=state,
        turnos_ocupados=turnos_ocupados,
        historial="\n".join([m["role"] + ": " + m["content"] for m in conversation_history])
    )

    messages = [{"role": "system", "content": prompt}] + last_messages

    # Llamada al modelo de Cohere
    response = co.chat(
        model="command-r-plus-08-2024",
        max_tokens=200,
        temperature=0.4,
        messages=messages
    )

    # Extraemos el texto devuelto por el modelo
    respuesta = response.message.content[0].text

    # Guardamos la respuesta en el historial
    conversation_history.append({"role": "assistant", "content": respuesta})

    # Intentar parsear JSON
    try:
        parsed = json.loads(respuesta)
        if isinstance(parsed, dict):
            try:
                turno = TurnoState(**parsed)
                result = turno.model_dump()
                result["completado"] = True
                return result
            except ValidationError:
                return {"completado": False, "respuesta": respuesta}
    except Exception:
        # No era JSON válido
        return {"completado": False, "respuesta": respuesta}

    return {"completado": False, "respuesta": respuesta}
