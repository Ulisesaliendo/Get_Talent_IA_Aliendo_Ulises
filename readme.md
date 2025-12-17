# Challenge API RAG — Semana 4

Este proyecto implementa una API REST basada en **FastAPI** que permite:
- Cargar documentos
- Generar embeddings semánticos
- Realizar búsquedas semánticas
- Responder preguntas usando un enfoque **RAG (Retrieval-Augmented Generation)**

El sistema utiliza **Cohere** para embeddings y generación de texto, y **ChromaDB** como vector store persistente.

---

## 🧱 Arquitectura general

- **FastAPI**: API REST
- **Cohere**: embeddings + LLM
- **ChromaDB**: almacenamiento vectorial persistente
- **RAG**: recuperación de contexto + respuesta basada en documentos

Los embeddings se generan automáticamente al indexar documentos en ChromaDB mediante una `embedding_function`.

---

## 📁 Estructura del proyecto

```text
.
├── main.py              # API principal (endpoints)
├── schemas.py           # Modelos Pydantic (requests / responses)
├── vectorstore.py       # Configuración de ChromaDB + embeddings Cohere
├── llm_client.py        # Cliente Cohere
├── llm_config.py        # Prompt del sistema y parámetros del LLM
├── logger.py            # Logger del sistema, incompleto , no se sube a github
├── seed_documents.py    # Script para cargar documentos desde .txt , no se sube a github
├── data/           # Archivos .txt de ejemplo
├── chroma_db/           # Persistencia local de ChromaDB, no se sube a github
├── .env                 # Variables de entorno (no versionado), no se sube a github
└── README.md


