#from fastapi import APIRouter, HTTPException
#from app.business.chat import chatbot_pi
#from app.api.schemas import ChatRequest
#from app.business.chat_turno import turnos_chat_response  
#import uuid
#router = APIRouter()
#
#
#@router.post("/chat")
#async def chat_endpoint(request: ChatRequest):
#    try:
#        response = chatbot_pi(request.message)  
#        return {"response": response}
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
#    
#
## ============================================
## Endpoint del turnero (solo chat por ahora)
## ============================================
#
## Lista global de turnos confirmados
#TURNOS = []
#
#@router.post("/turnero")
#async def turnero_chat_endpoint(request: ChatRequest):
#    try:
#        result = turnos_chat_response(request.message)
#
#        # Caso: la IA devolvió un JSON completo
#        if isinstance(result, dict) and result.get("completado"):
#            turno = result
#            return {
#                "response": f"Confirma este turno? {turno['paciente']} el {turno['dia']} de {turno['start_time']} a {turno['end_time']} (sí/no)",
#                "turno_pendiente": turno
#            }
#
#        # Caso: el usuario responde "sí"
#        if isinstance(result, str) and result.lower().strip() == "sí":
#            # Recuperar el último turno pendiente del historial
#            # Aquí asumimos que lo guardaste en la sesión o lo recibiste en el request
#            # Para simplificar, tomamos el último turno confirmado en memoria
#            if TURNOS and not TURNOS[-1].get("confirmado"):
#                turno = TURNOS[-1]
#                turno["id"] = str(uuid.uuid4())
#                turno["confirmado"] = True
#                return {"response": "Turno confirmado y guardado.", "turno": turno}
#            else:
#                return {"response": "No hay turno pendiente para confirmar."}
#
#        # Caso: el usuario responde "no"
#        if isinstance(result, str) and result.lower().strip() == "no":
#            return {"response": "Turno cancelado. Puede volver a intentarlo."}
#
#        # Caso general: respuesta normal del agente
#        return {"response": result}
#
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
#
#
## Endpoint para listar turnos confirmados
#@router.get("/turnos")
#async def listar_turnos():
#    return {"turnos": TURNOS}

from fastapi import APIRouter, HTTPException
from app.api.schemas import ChatRequest, ChatResponse, TurneroResponse, TurnosListResponse, TurnoConfirmedResponse
from app.business.chat import chatbot_pi
from app.business.chat_turno import turnos_chat_response
import uuid

router = APIRouter()

TURNOS = []

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = chatbot_pi(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/turnero", response_model=TurneroResponse)
async def turnero_chat_endpoint(request: ChatRequest):
    try:
        result = turnos_chat_response(request.message)

        if isinstance(result, dict) and result.get("completado"):
            turno = result
            return {
                "response": f"Confirma este turno? {turno['paciente']} el {turno['dia']} de {turno['start_time']} a {turno['end_time']} (sí/no)",
                "turno_pendiente": turno
            }

        if isinstance(result, str) and result.lower().strip() == "sí":
            if TURNOS and not TURNOS[-1].get("confirmado"):
                turno = TURNOS[-1]
                turno["id"] = str(uuid.uuid4())
                turno["confirmado"] = True
                return {"response": "Turno confirmado y guardado.", "turno": turno}
            else:
                return {"response": "No hay turno pendiente para confirmar."}

        if isinstance(result, str) and result.lower().strip() == "no":
            return {"response": "Turno cancelado. Puede volver a intentarlo."}

        return {"response": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/turnos", response_model=TurnosListResponse)
async def listar_turnos():
    return {"turnos": TURNOS}
