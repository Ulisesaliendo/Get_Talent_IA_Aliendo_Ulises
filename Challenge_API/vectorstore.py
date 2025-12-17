import os
import chromadb
from dotenv import load_dotenv
from chromadb.utils import embedding_functions

# Cargar variables de entorno
load_dotenv()

# Leer API Key
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise RuntimeError("COHERE_API_KEY not found in environment variables")

# Directorio de persistencia
CHROMA_PATH = "./chroma_db"

# Función de embeddings (Cohere)
embedding_function = embedding_functions.CohereEmbeddingFunction(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0"
)

# Cliente persistente de Chroma
chroma_client = chromadb.Client(
    settings=chromadb.Settings(
        persist_directory=CHROMA_PATH
    )
)

# Colección principal
collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_function
)
