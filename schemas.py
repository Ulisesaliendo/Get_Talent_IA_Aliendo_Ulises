# schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
#from datetime import datetime, timedelta  #Por el momento no se usa


class DocumentUploadRequest(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)

class DocumentUploadResponse(BaseModel):
    message: str  
    document_id: str


class GenerateEmbeddingsRequest(BaseModel):
    document_id: str = Field(
        pattern=r"^doc_[0-9a-fA-F-]{36}$",
        description="Public document identifier"
    )


class GenerateEmbeddingsResponse(BaseModel):
    message: str
    document_id: str


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: Optional[int] = Field(default=3, gt=0)



class SearchResultItem(BaseModel):
    document_id: str
    title: str
    content_snippet: str
    similarity_score: float


class SearchResponse(BaseModel):
    results: List[SearchResultItem]


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class AskResponse(BaseModel):
    answer: str
    context_used: str
    similarity_score: float
    grounded: bool


####### EXAMPLE from previous exercise ######
#class Subtask(BaseModel):
#    id: int
#    title: str
#    completed: bool = False
#
#class Task(BaseModel):
#    id: Optional[int] = None
#    title: str
#    description: str
#    completed: bool = False
#    priority: Optional[int] = Field(None, ge=1, le=5, description="Prioridad entre 1 y 5")
#    due_date: Optional[datetime] = None
#    category: Optional[str] = None
#    subtasks: List[Subtask] = []
#    
#class TaskUpdate(BaseModel):
#    title: Optional[str] = None
#    description: Optional[str] = None
#    completed: Optional[bool] = None
#    priority: Optional[int] = Field(None, ge=1, le=5, description="Prioridad entre 1 y 5")
#    due_date: Optional[datetime] = None
#    category: Optional[str] = None
#    subtasks: Optional[List[Subtask]] = None