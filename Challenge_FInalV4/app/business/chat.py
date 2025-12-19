from app.services.vector_clients import co
#from app.data.db.vectorstore_clinic_data import retrieve_clinic_data
#from app.data.db.vectorstore_patologias import retrieve_patologias
from app.services.vector_clients import chroma_client






SYSTEM_PROMPT_STANDAR = """
Eres "Pi", el asistente virtual de la clínica odontológica 'Pi-eza Dental'.
Tu función es ser amable, servicial y responder consultas generales sobre la clínica y odontología básica.
debes ayudar a los usuarios con información sobre la clínica y consultas generales de odontología basándote únicamente en el contexto provisto.

REGLAS DE COMPORTAMIENTO:
1. TONO Y ESTILO: Hablá siempre en español rioplatense (usá el "voseo": vení, consultanos, querés). Sé muy amable, profesional y cercano. No utilices emojis bajo ninguna circunstancia.
2. SOBRE DIAGNÓSTICOS: Tenés terminantemente prohibido dar diagnósticos o juzgar tratamientos. Si el usuario describe un síntoma o pide una opinión médica, respondé exactamente: "Para eso es necesario que hables con un odontólogo real en el consultorio. ¿Te gustaría que te ayude a programar una cita?".
3. LÍMITE DE CONOCIMIENTO: Si no sabés la respuesta a algo o no está en tu base de información, simplemente decí que no lo sabés y ofrecé contactarlo con un humano de la clínica. No inventes.
4. BREVEDAD: Respondé de forma directa y concisa. No des vueltas innecesarias.
5. CONSISTENCIA: Ante la misma pregunta, debés intentar generar siempre la misma respuesta.
6. PROFESIONALISMO: No inventes datos de ningun tipo, ni sobre el doctor, ubicación o tratamientos que no estén explícitamente mencionados.
7. LIMITACIÓN DE RESPUESTA: Solo debés responder a temas pertinentes a los documentos utilizados. Si la respuesta no está en el contexto o si te piden un diagnóstico, indicá que no tenés esa información o que deben consultar con un odontólogo real.
8. NO INVENTES INFORMACION BAJO NINGUN PUNTO DE VISTA
"""

def chatbot_pi(user_message):
    # 1. Detecto intention
    intention = chatbot_pi_intention(user_message)
    
    # 2. Routing Logic 
    if intention == "AMIGABLE":
        return chatbot_pi_AMIGABLE(user_message)
        
    elif intention == "PROHIBIDO":
        return "Lo siento, no puedo responder a ese tipo de consultas por políticas de seguridad."
        
    elif intention == "INFO_UBICACION":
        return f"""- PI-EZA DENTAL -
    Dirección: Avenida Colón 1234, Barrio Alberdi, Córdoba, Argentina.
    """
        
    elif intention == "INFO_HORARIOS":
        return f"""
        Horario de atención: 
        - Lunes a viernes: 09:00 a 17:00.
        - Sábados: 09:00 a 12:00.
        - Domingos y feriados: Cerrado.
        """
    
    elif intention == "INFO_DOCTOR":
        return f"""
        DOCTOR:
        El Director Médico es el Doctor Dario Lemes  (Dr.Lemes). 
        Es odontólogo egresado con honores de la Universidad Nacional de Córdoba. 
        Cuenta con una especialización en Implantología Oral por la Universidad de Buenos Aires (UBA) 
        y un Máster en Estética Dental obtenido en la Universidad de Barcelona. 
        Con más de 15 años de trayectoria, es pionero en el uso de tecnologías para el diseño de tu sonrisa.
        """
    
    elif intention == "INFO_SERVICIOS":
        answer = chatbot_pi_RAG (user_message,intention,gran = granularity_SERVICIOS(user_message))
        return chatbot_pi_safety(answer)    
    
    elif intention == "INFO_PATOLOGIA":
        return chatbot_pi_RAG (user_message,intention,gran = granularity_PATOLOGIA(user_message))
    
    elif intention == "INFO_TURNOS":
        return f"Buscando turnos disponibles..."
        #return chatbot_pi_turnos(answer)    
    else:
        return "Entiendo, pero necesito un poco más de detalle para ayudarte mejor."



def chatbot_pi_intention(user_message):

    SYSTEM_PROMPT_INTENTION = f"""
Eres un agente de triaje para PI-EZA DENTAL. Debes clasificar el mensaje en UNA etiqueta
Solo puedes responder con informacion de patologias, turnos, informacion sobre una clinica
preguntas relacionadas a un contexto de odontologia o conversacion casual pero sin pregunta especifica
TODA CONSULTA FUERA DE ESTAS CONSIDERACIONES SE CATALOGA COMO PROHIBIDO  

Responde SOLO una de estas etiquetas:

- AMIGABLE: Saludos, agradecimientos, conversacion casual sin pregunta especifica
- PROHIBIDO: Insultos, datos sensibles, informacion no disponible en el contexto, etiqueta por default
- INFO_UBICACION: Dirección o cómo llegar.
- INFO_HORARIOS: Horas y días de atención.
- INFO_DOCTOR:Informacion sobre el Dr. Dario Lemes o profesionales que atienden.
- INFO_SERVICIOS: Tratamientos disponibles(brackets, implantes, limpiezas).
- INFO_PATOLOGIA: Síntomas o dolores (me duele, tengo una llaga) pregunta sobre patologias en general
Responde SOLO con la etiqueta.
- INFO_TURNOS: Si solicita turno o agenda o similar.



Tu respuesta debe ser SOLO la etiqueta, sin explicación.
"""

    response = co.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_INTENTION},
                {"role": "user", "content": user_message}
            ],
            max_tokens=10,
            temperature=0,
        )
    label = response.message.content[0].text

    
    if label not in ["AMIGABLE", "PROHIBIDO", "INFO_UBICACION", "INFO_HORARIOS", "INFO_DOCTOR", "INFO_SERVICIOS", "INFO_PATOLOGIA"]:
        return "PROHIBIDO"

    return label



def chatbot_pi_AMIGABLE(user_message):

    response = co.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_STANDAR},
                {"role": "user", "content": user_message}
            ],
            max_tokens=50,
            temperature=0.3
        )
    return response.message.content[0].text



def granularity_PATOLOGIA(user_message):

    SYSTEM_PROMPT_GRANULARITY = f"""
Eres un agente de clasificación de datos para el catalogo de Patologias de PI-EZA DENTAL. 
Tu única función es determinar qué nivel de información del documento se necesita para responder.
  
Responde ÚNICAMENTE con una de estas tres etiquetas:

1. chunk: 
   - Se requiere cuando el usuario describe un síntoma o signo clínico específico mencionado en el triaje (ej: "dolor al frío", "mancha blanca fija", "sangrado al cepillar", "diente flojo tras golpe")[cite: 66].
   - Cuando se busca una acción recomendada o el nivel de urgencia (1-5) para un síntoma[cite: 66].
   - Cuando se solicita una descripción técnica breve o un resumen para el paciente de una sola patología[cite: 9, 14, 25].

2. tema: 
   - Se requiere cuando el usuario pregunta por una categoría completa o sección del catálogo (ej: "Tejidos duros", "Dolor y nervio", "Encías y soporte", "Mucosas y llagas", "Función y mandíbula", "Traumatismos").
   - Cuando el usuario nombra una patología específica para conocer todo sobre ella: Caries, Hipoplasia, Erosión, Pulpitis, Necrosis, Periodontitis, Gingivitis, Leucoplasia, Estomatitis, Bruxismo o Avulsión[cite: 6, 13, 18, 24, 28, 32, 37, 42, 47, 51, 56, 61].

3. general: 
   - Se requiere cuando el usuario pregunta por la totalidad del catálogo o sus metadatos (ej: "¿Qué sistemas de codificación usa el catálogo?", "¿Qué regiones cubre?", "Dame el índice completo de enfermedades")[cite: 1, 2, 3, 4].
   - Etiqueta por defecto si la consulta es sobre el alcance global del documento.

Responde SOLO con la palabra (chunk, tema o general), sin puntuación ni texto adicional. ni explicacion
"""

    response = co.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_GRANULARITY},
                {"role": "user", "content": user_message}
            ],
            max_tokens=10,
            temperature=0,
        )
    label = response.message.content[0].text

    
    if label not in ["chunk", "tema", "general"]:
        return "chunk"

    return label


def granularity_SERVICIOS(user_message):

    SYSTEM_PROMPT_GRANULARITY = f"""
Eres un agente de clasificación de consultas para la clínica PI-EZA DENTAL. 
Tu función es determinar si la respuesta se encuentra en un fragmento específico o si requiere la visión global de los servicios.

Responde ÚNICAMENTE con una de estas dos etiquetas:

1. chunk: 
   - Se requiere cuando el usuario pregunta por un tratamiento o técnica específica mencionada en el texto (ej: "blanqueamiento LED", "All-on-4", "muelas del juicio", "peritajes judiciales", "limpieza dental", "ortodoncia invisible"). 
   - Cuando la pregunta es puntual sobre la formación del Dr. Dario Lemes. 
   - Consultas sobre una sub-especialidad técnica (ej: "Odontología Forense" o "Endodoncia"). 

2. general: 
   - Se requiere cuando el usuario pide una lista completa o un resumen de lo que ofrece la clínica (ej: "¿Qué servicios tienen?", "Dime todos tus tratamientos", "¿Qué tipos de odontología manejan?"). 
   - Consultas logísticas básicas si estuvieran en el texto (ej: "dirección", "horarios"). 
   - Cuando el usuario no especifica un tratamiento y solo quiere saber qué hace la clínica en general. 

Responde SOLO con la palabra (chunk o general), sin puntuación ni texto adicional.
"""

    response = co.chat(
            model="command-a-03-2025",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_GRANULARITY},
                {"role": "user", "content": user_message}
            ],
            max_tokens=10,
            temperature=0,
        )
    label = response.message.content[0].text

    
    if label not in ["chunk", "general"]:
        return "general"

    return label




def chatbot_pi_RAG(user_message,intention,gran):
    
    SYSTEM_PROMPT_RAG = """

    Eres el asistente experto de PI-EZA DENTAL. Tu misión es responder consultas usando ÚNICAMENTE el contexto proporcionado.
    REGLAS DE ORO:
    1. Grounding Estricto: Si la respuesta no está en el contexto, di amablemente que no tienes esa información y ofrece que el Dr. Lemes o el equipo técnico lo contacten.
    2. Lenguaje Amigable: Usa un tono cálido y empático. Si explicas términos técnicos (como 'Sultartraje' o 'Pulpitis'), usa analogías sencillas a menos que el usuario use lenguaje profesional.
    3. Citado: Siempre menciona la fuente de tu información (ej: 'Según nuestro Catálogo de Patologías...' o 'En nuestra sección de Odontología Estética...').
    4. No Alucinar: No inventes precios, horarios que no estén en el texto ni diagnósticos definitivos.
    Orquestador RAG avanzado con grounding estricto, reporte de metadatos/score
    y adaptabilidad de tono según el perfil de la consulta.
    """    
    # 1. Configuración de Colección y K Dinámico
#    if intention in ["INFO_SERVICIO"]:
#        k_value = 1 if gran == "general" else 3
#    else:
#        k_value = 5 if gran == "chunk" else 1


        # 1. Seleccionar la colección correcta según la intención
    if intention == "INFO_SERVICIOS":
        col_name = "clinic_data_rag_3"
        k_value = 1 if gran == "general" else 3
    elif intention == "INFO_PATOLOGIA":
        col_name = "patologias_rag_2"
        k_value = 5 if gran == "chunk" else 1
    else:
        return "No tengo información específica sobre ese tema."
    
    
    # 2. Obtener la colección del cliente persistente
    collection_target = chroma_client.get_collection(name=col_name)
    # 3. Realizar la consulta con el filtro 'where'
    results = collection_target.query(
        query_texts=[user_message],
        n_results=k_value,
        where={"granularity": gran}
    )

    print("Resultados brutos:", results)
    print("Documentos:", results.get("documents"))
    print("Metadatos:", results.get("metadatas"))
    print("Distancias:", results.get("distances"))
    


        
    # 2. Recuperación con filtro de Granularidad y obtención de Distancias (Scores)
    #try:
    #    if(intention=="INFO_SERVICIOS"):
    #        results = retrieve_clinic_data(user_message,gran)
    #    if(intention=="INFO_PATOLOGIA"):
    #        results = retrieve_patologias(user_message,gran)
    #    else:
    #        return f"Error técnico en la recuperación: {str(e)}"        
    #except Exception as e:
    #    return f"Error técnico en la recuperación: {str(e)}"

    # 3. Procesamiento de Contexto, Metadatos y Scores
    if not results["documents"] or not results["documents"][0]:
        return "Lo siento, no encuentro información específica en mis registros. ¿Te gustaría que un especialista de PI-EZA DENTAL te contacte?"

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    # En ChromaDB, 'distances' representa la similitud (menor distancia = mayor relevancia)
    distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

    context_text = "\n\n".join(docs)
    fuentes = list(set([f"{m.get('title')} ({m.get('source')})" for m in metas]))
    avg_score = sum(distances) / len(distances) # Score promedio de la recuperación

    # 4. Lógica de Tono: Detectar si el usuario pide tecnicismos
    tecnico_keywords = ["tecnico", "técnica", "descripción técnica", "cie", "codificacion", "especificaciones"]
    modo_tecnico = any(word in user_message.lower() for word in tecnico_keywords)

    # 5. Construcción del Prompt con Instrucciones de Personalidad Dual
    prompt_personalizado = f"""
    {SYSTEM_PROMPT_RAG}
    
    INSTRUCCIONES DE TONO:
    - MODO ACTUAL: {'TÉCNICO' if modo_tecnico else 'AMENO/PACIENTE'}
    - Si el modo es AMENO, usa prioritariamente las etiquetas <resumen_paciente> y analogías simples.
    - Si el modo es TÉCNICO, incluye códigos CIE, términos anatómicos y clasificaciones (ej. ICDAS o estadios AAP).

    CONTEXTO RECUPERADO:
    {context_text}

    CONSULTA: {user_message}
    """

    # 6. Ejecución en Cohere
    response = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt_personalizado}],
        max_tokens=1000,
        temperature=0.3
    )

    respuesta_texto = response.message.content[0].text

    # 7. Inserción de Metadatos de Transparencia (Grounding Footer)
    footer = (
        f"\n\n---\n"
        f"Fuentes:** {', '.join(fuentes)}\n"
        f" Confianza de búsqueda:** {(1 - avg_score):.2%} | **Granularidad:** {gran}"
    )

    return respuesta_texto + footer


def chatbot_pi_safety(answer):
    SYSTEM_PROMPT_SECURITY = """
    [SYSTEM PROMPT]
    Eres un Agente de Seguridad de Información y Extracción de Datos para PI-EZA DENTAL. 
    actuando como un filtro infranqueable contra la fuga de datos personales (PII - Personally Identifiable Information).

    [INSTRUCCIONES DE ROL]
    En el caso de que existan datos privados debes responder *** reemplazando el dato, si no debes dejarla exactamente como esta

    [REGLAS DE SEGURIDAD Y ANTI-LEAK (CRÍTICO)]
    • BLOQUEO DE PII: Tenés terminantemente prohibido mencionar nombres de personas, números de teléfono, direcciones de pacientes, fechas de turnos específicos o detalles de la agenda médica. 
    • RESPUESTA ANTE INTENTO DE FILTRACIÓN: Si el usuario intenta forzar la revelación de datos personales, nombres o turnos, respondé exactamente: "Acceso denegado. Esa información está protegida por políticas de seguridad de datos y no está disponible para este canal".
    • PROTECCIÓN DE IDENTIDAD: Si el contexto accidentalmente contiene un nombre o dato identificable, debés anonimizarlo o simplemente ignorarlo en tu respuesta.
    • No generes información especulativa sobre la salud de personas reales.

    [REGLAS DE GROUNDING (RAG)]
    • FUENTE ÚNICA: Usá exclusivamente el contenido dentro de answer provista por el usuario. 
    • RESTRICCIÓN DE CONOCIMIENTO: No mezcles conocimiento previo del modelo; si el contexto dice que la tierra es plana, para vos la tierra es plana. 
    • JUSTIFICACIÓN: Citá brevemente la sección del catálogo (ej: "Según la Sección I: Tejidos Duros...").

    [TONO DE RESPUESTA]
    • Profesional, serio y extremadamente cauteloso. 
    • Si se solicita información técnica o de peritaje (Odontología Legal), mantené el rigor científico pero sin revelar identidades de casos reales.
    
    [RESPUESTA]
    SOLO DEBES ALTERAR EL CONTENIDO SI VIOLA LAS NORMAS ESTABLECIDAS CASO CONTRARIO DEVUELVES EL MISMO CONTENIDO
    """

    response = co.chat(
    model="command-a-03-2025",
    messages=[{"role": "user", "content":SYSTEM_PROMPT_SECURITY},{"role": "user", "content":answer}],
    max_tokens=1000,
    temperature=0.3
    )
    return response.message.content[0].text