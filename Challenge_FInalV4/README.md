# Pi-eza Dental – AI Chatbot & Turnero API

Pi-eza Dental es una API  **FastAPI** que provee un asistente virtual odontológico con:
- Chat informativo con RAG (Retrieval-Augmented Generation)
- Clasificación de intención
- Agendamiento conversacional de turnos
- Protección estricta de datos sensibles (PII)
- Arquitectura modular y extensible

El sistema está diseñado para clínicas odontológicas que deseen automatizar atención inicial, información médica general y pre-agendamiento de turnos sin reemplazar al profesional humano.
---

## Arquitectura General

- **Framework:** FastAPI  
- **LLM:** Cohere (Command + Embed)  
- **Vector DB:** ChromaDB (persistente)  
- **Paradigma:** Multi-agente + RAG  
- **Idioma:** Español rioplatense (voseo)  
- **Seguridad:** Filtro anti-PII y anti-diagnóstico  
- **GUI:** Chat window en jupyter notebook  
---

##  Estructura del Proyecto
```
app/
├
├── api/
│   ├── chat.py
│   └── schemas.py
├── business/
│   ├── chat.py
│   └── chat_turno.py
├── data
│   ├── db
│   │   ├──vectorstore_clinic_data.py
│   │   └──vectorstore_patologias.py
│   └── raw_data
│       ├──clinic_data.py
│       └──Patologias.pdf
├── services/
│   └── vector_clients.py
├── chroma_db/
├── README.md
├──main.py
└──gui.ipynb
```

---
##  Endpoints Disponibles

### 1. Chat General  
Este endpoint (`POST /api/chat`) permite que el usuario envíe un mensaje de texto con cualquier consulta general sobre la clínica o los servicios odontológicos. El sistema clasifica la intención, busca la información en la base de conocimiento (RAG) y devuelve una respuesta en formato JSON.  
Ejemplo: si el paciente pregunta *“¿Qué tratamientos hacen?”*, la API responderá con un texto informativo extraído del contexto entrenado.

---

### 2. Turnero Conversacional  
El endpoint (`POST /api/turnero`) gestiona el proceso de agendamiento de turnos de manera conversacional. El asistente va solicitando los datos necesarios paso a paso: día, nombre del paciente, horario de inicio y fin, y una nota opcional.  
Cuando la información está completa y validada, devuelve un JSON con el turno confirmado. Este flujo evita errores y asegura que el paciente confirme explícitamente la reserva antes de registrarla.

---

### 3. Listado de Turnos  
El endpoint (`GET /api/turnos`) devuelve un listado de todos los turnos registrados en el sistema. La respuesta es un arreglo en formato JSON con cada turno, incluyendo fecha, paciente, horarios y notas.  

---

### 4. Estado del Sistema  
El endpoint (`GET /api/status`) es auxiliar y se utiliza para verificar que la API está funcionando correctamente. Devuelve un JSON simple con un estado “ok” y un mensaje confirmando que el servicio está activo.  

---



