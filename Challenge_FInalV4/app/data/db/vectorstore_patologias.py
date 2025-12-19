import PyPDF2 #Extracción de texto desde PDF
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter #División de texto en chunks con langchain
from app.services.vector_clients import create_vector_store


# ===============================================
# CARGA DE DOCUMENTOS
# ===============================================

# Cargar PDF
def load_pdf(path):
    text = ""
    with open(path, "rb") as f:
        pdf = PyPDF2.PdfReader(f)
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

path_pdf = "app/data/raw_data/Patologias.pdf"
raw_text = load_pdf(path_pdf)
#print(raw_text)

# ===============================================
# SEPARACIÓN DE HISTORIAS POR POSICIONES
# ===============================================


patrones = [
    r"1\.1\.\s*Caries",
    r"1\.2\.\s*Hipoplasias",
    r"1\.3\.\s*Erosión",
    r"2\.1\.\s*Pulpitis",
    r"2\.2\.\s*Necrosis",
    r"2\.3\.\s*Periodontitis Apical",
    r"3\.1\.\s*Gingivitis",
    r"3\.2\.\s*Periodontitis",
    r"4\.1\.\s*Leucoplasia",
    r"4\.2\.\s*Estomatitis",
    r"5\.1\.\s*Bruxismo",
    r"6\.1\.\s*Avulsión",
    r"TABLA SINTÉTICA PARA TRIAJE VIRTUAL"
]

posiciones = []
for patron in patrones:
    match = re.search(patron, raw_text, re.IGNORECASE)
    if match:
        posiciones.append((patron, match.start()))

posiciones.sort(key=lambda x: x[1])

#titulos_patologias = [
#    "1.1. Caries Dental",
#    "1.2. Hipoplasias y Defectos del Esmalte",
#    "1.3. Erosión Química Dental",
#
#    "2.1. Pulpitis (Inflamación del Nervio)",
#    "2.2. Necrosis Pulpar",
#    "2.3. Periodontitis Apical",
#
#    "3.1. Gingivitis",
#    "3.2. Periodontitis",
#
#    "4.1. Leucoplasia",
#    "4.2. Estomatitis Aftosa",
#
#    "5.1. Bruxismo",
#
#    "6.1. Avulsión Dental",
#
#    "TABLA SINTÉTICA PARA TRIAJE VIRTUAL"
#]
#
#
#posiciones = [(t, raw_text.find(t)) for t in titulos_patologias]
#posiciones = sorted([p for p in posiciones if p[1] != -1], key=lambda x: x[1])

temas_procesados = []
for i in range(len(posiciones)):
    titulo, start = posiciones[i]
    if i < len(posiciones) - 1:
        _, next_start = posiciones[i+1]
        texto_tema = raw_text[start:next_start]
    else:
        texto_tema = raw_text[start:]
    
    temas_procesados.append({
        "title": titulo,
        "text": texto_tema.strip()
    })

print(temas_procesados)

# ===============================================
# CHUNKING - ETIQUETADO
# ===============================================

final_documents = []

# --- ETIQUETA 3: "general" (Para resúmenes globales o contexto total) ---
final_documents.append({
    "content": raw_text,
    "metadata": {
        "granularity": "general",
        "title": "Catálogo Completo de Patologías",
        "source": path_pdf
    }
})

# --- ETIQUETA 2: "tema" (Para preguntas sobre una patología específica) ---
for t in temas_procesados:
    final_documents.append({
        "content": t["text"],
        "metadata": {
            "granularity": "tema",
            "title": t["title"],
            "source": path_pdf
        }
    })

# --- ETIQUETA 1: "chunk" (Para búsqueda de detalles técnicos o síntomas) ---
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=120,
    separators=["\n\n", "\n", ".", " "] # Optimiza el corte en puntos seguidos
)

for t in temas_procesados:
    chunks = splitter.split_text(t["text"])
    for i, chunk_text in enumerate(chunks):
        final_documents.append({
            "content": chunk_text,
            "metadata": {
                "granularity": "chunk",
                "title": t["title"],
                "chunk_id": i,
                "source": path_pdf
            }
        })


# ===============================================
# VECTOR STORE
# ===============================================

collection = create_vector_store(
    documents=[d["content"] for d in final_documents],
    metadatas=[d["metadata"] for d in final_documents],
    ids=[f"doc_{i}" for i in range(len(final_documents))],
    name="patologias_rag_2"
)

# Retrieve 
#def retrieve_patologias(query, granularity="chunk", k=5):
#    return collection.query(
#        query_texts=[query],
#        n_results=k,
#        where={"granularity": granularity}
#    )
