from fastapi import FastAPI, HTTPException
from typing import List
from schemas import DocumentUploadRequest, DocumentUploadResponse, GenerateEmbeddingsRequest, GenerateEmbeddingsResponse, SearchRequest, SearchResponse, SearchResultItem, AskRequest, AskResponse
from uuid import uuid4
from vectorstore import collection
from llm_config import SYSTEM_PROMPT, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from llm_client import co

app = FastAPI(title="Get Talent: Challenge_3_API", version="1.0.0")




# --- BASE DE DATOS EN MEMORIA ---
DOCUMENT_DB = {}
NEXT_DOCUMENT_ID = 1

#################### EXAMPLE from previous exercise ####################
#    {
#        "id": 1,
#        "title": "Configurar Entorno de Desarrollo",
#        "description": "Instalar Python, FastAPI, Uvicorn y configurar el IDE.",
#        "completed": False,
#        "priority": 5,
#        "due_date": "2025-12-15T10:00:00Z",
#        "category": "Trabajo",
#        "subtasks": [
#            {"id": 101, "title": "Instalar dependencias con pip", "completed": True},
#            {"id": 102, "title": "Crear proyecto base de FastAPI", "completed": False}
#        ]
#    },
#
############################################################################




@app.post("/upload", response_model=DocumentUploadResponse, status_code=201)
def upload_document(payload: DocumentUploadRequest):
    global NEXT_DOCUMENT_ID

    # Generación de IDs
    internal_id = NEXT_DOCUMENT_ID
    NEXT_DOCUMENT_ID += 1

    document_id = f"doc_{uuid4()}"

    # Almacenamiento interno
    DOCUMENT_DB[document_id] = {
        "id": internal_id,
        "document_id": document_id,
        "title": payload.title,
        "content": payload.content,
        "indexed": False
    }

    return DocumentUploadResponse(
        message="Documento cargado correctamente",
        document_id=document_id
    )





@app.post("/generate-embeddings",response_model=GenerateEmbeddingsResponse, status_code=201)
def generate_embeddings(payload: GenerateEmbeddingsRequest):

    document_id = payload.document_id

    # 1. Validar existencia del documento
    if document_id not in DOCUMENT_DB:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document = DOCUMENT_DB[document_id]

    # 2. Verificar si ya fue indexado
    if document.get("indexed"):
        raise HTTPException(
            status_code=409,
            detail="Document already indexed"
        )

    # 3. Indexar documento en Chroma (Cohere genera el embedding)
    collection.add(
        documents=[document["content"]],
        metadatas=[{
            "title": document["title"],
            "granularity": "document",
            "indexed": True
            # futuros: grounded, source, version, etc.
        }],
        ids=[document_id]
    )

    # 4. Marcar como indexado en memoria
    document["indexed"] = True

    return {
        "message": "Document indexed successfully",
        "document_id": document_id
    }



@app.post("/search", response_model=SearchResponse)
def search_documents(payload: SearchRequest):

    try:
        results = collection.query(
            query_texts=[payload.query],
            n_results=payload.top_k
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="El servicio externo no pudo procesar la solicitud en este momento."
        )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    response_items = []

    for doc_id, doc, meta, dist in zip(ids, documents, metadatas, distances):

        snippet = doc[:200] if doc else ""

        response_items.append(
            SearchResultItem(
                document_id=doc_id,
                title=meta.get("title", ""),
                content_snippet=snippet,
                similarity_score=round(1 - dist, 3)
            )
        )

    return SearchResponse(results=response_items)


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):

    # 1. Buscar contexto relevante
    try:
        results = collection.query(
            query_texts=[payload.question],
            n_results=3
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="El servicio externo no pudo procesar la solicitud en este momento."
        )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # 2. Verificar grounding mínimo
    if not documents or distances[0] > 0.5:
        return AskResponse(
            answer="No cuento con información suficiente para responder a esta consulta.",
            context_used="",
            similarity_score=0.0,
            grounded=False
        )

    # 3. Construir contexto
    context = "\n".join(documents)
    similarity_score = round(1 - distances[0], 3)

    # 4. Prompt RAG
    prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO:
{context}

PREGUNTA:
{payload.question}

RESPUESTA:
"""

    # 5. Llamada al LLM
    try:
        response = co.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="El servicio externo no pudo procesar la solicitud en este momento."
        )

    answer = response.message.content[0].text.strip()

    grounded = answer != "No cuento con información suficiente para responder a esta consulta."

    return AskResponse(
        answer=answer,
        context_used=context,
        similarity_score=similarity_score,
        grounded=grounded
    )



#para debuggear y ver los documentos indexado
@app.get("/debug/index")
def debug_index():
    data = collection.get()
    return {
        "total_documents": len(data["ids"]),
        "documents": [
            {"document_id": doc_id, "title": meta.get("title")}
            for doc_id, meta in zip(data["ids"], data["metadatas"])
        ]
    }




#@app.get("/tasks", response_model=List[Task])
#def get_all_tasks():
#    return TASK_DB
#
#@app.get("/tasks/{task_id}", response_model=Task)
#def get_task_by_id(task_id: int):
#    task = list(filter(lambda x: x['id'] == task_id, TASK_DB))
#    if len(task) > 0:
#        return task[0]
#    raise HTTPException(status_code=404, detail='Tarea no encontrada')
#
#@app.post("/tasks", response_model=Task, status_code=201)
#def create_task(task: Task):
#    if TASK_DB:
#        new_id = max(t["id"] for t in TASK_DB) + 1
#    else:
#        new_id = 1
#
#    task_dict = task.model_dump()
#    task_dict["id"] = new_id
#    
#    TASK_DB.append(task_dict)
#    return task_dict
#
#@app.put("/tasks/{task_id}", response_model=Task)
#def update_task(task_id: int, updated_task: Task):
#    for index, task in enumerate(TASK_DB):
#        if task["id"] == task_id:
#            task_data = updated_task.model_dump()
#            task_data["id"] = task_id 
#            
#            TASK_DB[index] = task_data
#            return task_data
#            
#    raise HTTPException(status_code=404, detail="Tarea no encontrada para actualizar")
#
#@app.patch("/tasks/{task_id}", response_model=Task)
#def patch_task(task_id: int, updated_fields: TaskUpdate):
#
#    for index, task in enumerate(TASK_DB):
#        if task["id"] == task_id:
#            update_data = updated_fields.model_dump(exclude_unset=True)
#            for key, value in update_data.items():
#                task[key] = value                
#            TASK_DB[index] = task
#            return task
#            
#    raise HTTPException(status_code=404, detail="Tarea no encontrada para actualización parcial")
#
#@app.delete("/tasks/{task_id}", status_code=204)
#def delete_task(task_id: int):
#    for index, task in enumerate(TASK_DB):
#        if task["id"] == task_id:
#            TASK_DB.pop(index)
#            return
#            
#    raise HTTPException(status_code=404, detail="Tarea no encontrada para eliminar!!!")
#
#
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)

