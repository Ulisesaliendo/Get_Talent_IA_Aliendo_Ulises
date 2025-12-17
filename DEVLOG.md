# Development Log / Bitácora Técnica

## 2025-12-16 — Inicialización API
- Se define FastAPI como framework.
- Persistencia en memoria para simplificar el challenge.
- Se separan schemas con Pydantic.

---

## Document Upload
**Decisión**
- Se usa `document_id` como UUID string público.
- Se mantiene `id` entero interno.

**Motivo**
- UUID evita colisiones y exposición de IDs internos.

---

## Embeddings
**Decisión**
- Un embedding por documento.
- El endpoint falla si el embedding ya existe (`409 Conflict`).
- Se desarollo en embeddings.py

**Motivo**
- Evitar consumo innecesario de recursos.
- Preparar el diseño para versionado futuro.

**Pendiente**
- Evaluar chunking para documentos largos.
- Falta Embedding Response!
- Falta embedding real con cohere o chroma, implemetar antes de implementar Search
---

## Search
**Estado**
- Implementación en progreso.
- Se utilizará similitud coseno en memoria.


## 2025-12-15 — Estado actual del Challenge API RAG

### Avances
- Implementación completa de endpoints `/upload`, `/search` y `/ask`
- Integración de Cohere para embeddings y generación de respuestas
- Uso de ChromaDB con persistencia local
- Flujo RAG funcional con grounding obligatorio
- Manejo de errores y validaciones básicas
- Pruebas exitosas de búsqueda semántica y respuestas contextualizadas

### Observaciones técnicas
- Los embeddings se generan implícitamente al indexar documentos en Chroma mediante `embedding_function`
- La carga inicial de documentos vía script (`seed_documents.py`) funciona, pero no se refleja correctamente en el endpoint GET
- Se decide no profundizar este punto por el momento para no desviar foco del core del challenge

### Decisiones
- Priorizar estabilidad y claridad del flujo RAG sobre endpoints auxiliares
- Postergar revisión de sincronización entre seed y API
- Continuar mañana con mejoras incrementales

### Próximos pasos
- Refinar logging y modo DEBUG
- Agregar dataset de preguntas de prueba (edge cases)
- Revisar transparencia del endpoint `/ask`
