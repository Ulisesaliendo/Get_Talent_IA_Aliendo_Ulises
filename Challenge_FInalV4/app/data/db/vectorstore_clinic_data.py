import PyPDF2 #Extracción de texto desde PDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.data.raw_data.clinic_data import info_clinica_raw
from app.services.vector_clients import create_vector_store



# Configuración del Splitter según requerimiento del challenge (LangChain)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", ".", " "]
)


chunks_institucionales = text_splitter.split_text(info_clinica_raw)

#print(f"Se crearon {len(chunks_institucionales)} chunks para la información de la clínica.")

final_documents = []

final_documents.append({
    "content": info_clinica_raw,
    "metadata": {
        "granularity": "general",
        "title": "Catálogo Completo de servicios",
        "source": "clinic_data.py"
    }
})


# --- ETIQUETA "chunk" (Chunks individuales) ---
for i, chunk_text in enumerate(chunks_institucionales):
    final_documents.append({
        "content": chunk_text,
        "metadata": {
            "granularity": "chunk",
            "title": "Servicios Institucional",
            "chunk_id": i,
            "source": "clinic_data.py"
        }
    })

# ===============================================
# VECTOR STORE
# ===============================================

collection = create_vector_store(
    documents=[d["content"] for d in final_documents],
    metadatas=[d["metadata"] for d in final_documents],
    ids=[f"doc_{i}" for i in range(len(final_documents))],
    name="clinic_data_rag_3"
)

## Retrieve 
#def retrieve_clinic_data(query, granularity="chunk", k=5):
#    return collection.query(
#        query_texts=[query],
#        n_results=k,
#        where={"granularity": granularity}
#    )

    