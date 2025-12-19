
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensaje enviado por el usuario")
    session_id: Optional[str] = Field(None, description="Identificador de sesión opcional")


# ============================
# Turno schemas
# ============================

class TurnoBase(BaseModel):
    dia: str = Field(..., description="Fecha en formato YYYY-MM-DD")
    paciente: str = Field(..., description="Nombre del paciente")
    start_time: str = Field(..., description="Hora de inicio en formato HH:MM")
    end_time: str = Field(..., regex=r"^\d{2}:\d{2}$", description="Hora de fin en formato HH:MM")
    nota: Optional[str] = Field(None, description="Nota opcional")


class TurnoCreateResponse(TurnoBase):
    completado: bool = Field(..., description="Indica si el turno está completo y listo para confirmar")


class TurnoConfirmedResponse(TurnoBase):
    id: str = Field(..., description="Identificador único del turno")
    confirmado: bool = Field(..., description="Indica si el turno fue confirmado")


# ============================
# Response schemas
# ============================

class ChatResponse(BaseModel):
    response: str = Field(..., description="Respuesta del agente")


class TurneroResponse(BaseModel):
    response: str = Field(..., description="Respuesta del agente")
    turno_pendiente: Optional[TurnoCreateResponse] = None


class TurnosListResponse(BaseModel):
    turnos: List[TurnoConfirmedResponse]


class ChatRequest(BaseModel):
    message: str


