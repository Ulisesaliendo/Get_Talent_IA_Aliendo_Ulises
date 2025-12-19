import cohere 
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(api_key)
chroma_client = chromadb.PersistentClient(path="./chroma_db")



def create_vector_store(documents, metadatas, ids, name):
   # Generar embeddings con Cohere
   resp = co.embed(
       model="embed-v4.0",
       texts=documents,
       input_type="search_document",
       output_dimension=1024

   )
   embeddings = resp.embeddings.float_
   # Crear o recuperar colección (sin embedding_function)
   collection = chroma_client.get_or_create_collection(name=name)
   # Insertar documentos con embeddings
   collection.add(
       documents=documents,
       metadatas=metadatas,
       ids=ids,
       embeddings=embeddings
   )
   return collection




