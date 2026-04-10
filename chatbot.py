"""
Módulo de Chatbot Inteligente para Water Intelligence
Funciona en dos modos:
  1. MODO GRATUITO: Respuestas predefinidas inteligentes basadas en keywords
  2. MODO IA: Usa API de Claude si se configura ANTHROPIC_API_KEY en secrets
"""

import re
import json

# ─── Base de conocimiento para modo gratuito ───
KNOWLEDGE_BASE = {
    # Conceptos técnicos
    "conductividad|ce |ce?|dS/m|salinidad": 
        "La Conductividad Eléctrica (CE) mide la cantidad de sales disueltas en el agua. Se mide en dS/m (deciSiemens por metro). Un agua con CE < 0.5 es excelente, entre 0.5-1.5 es aceptable para la mayoría de usos, y sobre 2.5 ya genera problemas en muchos procesos. Para medirla necesitas un conductímetro portátil — cuestan entre $30-80 USD y cualquier operador puede usarlo.",

    "ph|acidez|alcalin":
        "El pH indica qué tan ácida o alcalina es el agua. El rango ideal para la mayoría de procesos industriales es 6.5-7.5. Un pH bajo (<6) es corrosivo para tuberías, y un pH alto (>8.5) favorece la formación de sarro. Se mide con un pHmetro portátil o con tirillas indicadoras.",

    "turbidez|ntu|turbia|clara":
        "La turbidez mide qué tan 'turbia' o 'clara' está el agua — indica la presencia de partículas suspendidas. Se mide en NTU. Un agua potable tiene <1 NTU, y para procesos industriales generalmente queremos <5 NTU. Si el agua se ve turbia a simple vista, probablemente tiene >10 NTU.",

    "dqo|dbo|carga orgánica|materia orgánica":
        "La DQO (Demanda Química de Oxígeno) mide cuánta materia orgánica tiene el agua. Es un indicador clave de qué tan 'sucia' está. Un agua natural tiene DQO < 20 mg/L, agua residual doméstica ~300-500 mg/L, y agua residual industrial puede superar los 1000 mg/L. Este dato normalmente sale de un análisis de laboratorio.",

    "estruvita|fertilizante|cristalización|fosfato|amonio":
        "La estruvita (MgNH₄PO₄) es un fertilizante que se puede cristalizar a partir de agua residual rica en nitrógeno y fósforo. Para evaluarlo necesitamos medir: NH₄-N (debe ser >100 mg/L), PO₄-P (>50 mg/L), Mg (>15 mg/L) y el ratio Ca/Mg (<1). Si tu agua tiene estos niveles, podemos transformar un desecho en un producto con valor comercial.",

    "ptar|tratamiento|planta de tratamiento":
        "Una PTAR (Planta de Tratamiento de Aguas Residuales) puede incluir varias tecnologías: coagulación-floculación (remueve sólidos), ultrafiltración (barrera física), UV (desinfección), ozono (oxidación avanzada), y ósmosis inversa o nanofiltración (remueve sales). No todas las plantas necesitan todas las etapas — depende de la calidad que requieres.",

    "ósmosis|nanofiltración|ro |nf |membrana|desalinizar":
        "La Ósmosis Inversa (RO) y la Nanofiltración (NF) son tecnologías de membrana que remueven sales disueltas. La RO produce agua ultrapura pero consume más energía y genera más rechazo (20-30%). La NF es más económica y suficiente para muchas aplicaciones industriales donde no necesitas agua ultrapura, solo controlar la CE.",

    "costo|precio|inversión|capex|opex|cuánto cuesta|valor":
        "Los costos dependen de la escala de tu planta. Como referencia: el servicio de diagnóstico + balance hídrico + dashboard parte desde $3.500 USD (Plan Esencial). Un sistema de nanofiltración pequeño puede costar $15.000-50.000 USD. Pero primero hacemos el diagnóstico para saber exactamente qué necesitas — muchas veces las 'quick wins' (ajustes operacionales sin inversión) ya generan ahorros significativos.",

    "huella hídrica|iso 14046|water footprint|huella":
        "La huella hídrica mide cuánta agua se usa por unidad de producto. Tiene tres componentes: azul (agua fresca consumida), verde (agua de lluvia) y gris (agua para diluir contaminantes). Se calcula según ISO 14046. Es cada vez más requerida por compradores internacionales y para reportes ESG.",

    # Sobre datos y medición
    "no sé|no tengo dato|no mido|cómo mido|cómo sé|estimar|aproximar|no tengo medidor":
        "No te preocupes, es normal no tener todos los datos. Aquí van algunas formas de estimar:\n\n• Consumo de agua: revisa tu boleta de agua o el medidor general. Si es pozo, multiplica caudal de la bomba × horas de operación.\n• CE: un conductímetro portátil cuesta ~$50 USD.\n• Caudales por proceso: cronometra cuánto tarda en llenarse un balde de volumen conocido.\n\nIngresa lo que tengas, aunque sea aproximado — una estimación informada es mejor que un vacío.",

    "foto|fotografía|imagen|subir":
        "Las fotos nos ayudan mucho para el diagnóstico remoto. Lo ideal es fotografiar: tu PTAR o sistema de tratamiento, los estanques de acumulación, los medidores de agua, la sala de calderas, y cualquier equipo relevante. Toma las fotos con buena luz y trata de que se vean los equipos completos.",

    # Industrias específicas
    "huevo|gallina|ave|galpon|galpón|avícola|ponedora":
        "En avícolas de huevos, los puntos críticos de agua son: 1) Lavado de huevos — el SAG exige agua potable, no se puede usar reciclada directamente. 2) Cooling pads — evaporan grandes volúmenes, especialmente en verano. 3) Bebederos — la calidad del agua afecta directamente la producción de huevos (CE alta = menor postura). 4) Lavado de galpones — genera agua muy sucia con guano que tiene alto contenido de N y P.",

    "champiñón|hongo|compost|casing":
        "En plantas de champiñones, el agua es crítica en: riego de casing (CE < 1.5 dS/m obligatorio), humidificadores (agua limpia para evitar mancha bacteriana), y compostaje Fase 1 (mayor consumidor, acepta agua reciclada de menor calidad).",

    "leche|lácteo|quesería|yogur":
        "En la industria láctea, el CIP (Clean In Place) consume el 50-70% del agua. Recuperar el último enjuague para usarlo como primer enjuague del siguiente ciclo puede ahorrar 15-25%. El agua residual tiene alta DBO por los residuos de leche.",

    # Default
    ".*": "Entiendo tu consulta. Te sugiero que ingreses la información que tengas disponible en el formulario, aunque sea aproximada. Si necesitas ayuda con algún campo específico, pregúntame indicando el nombre del campo y te explico qué necesitamos y cómo obtener ese dato."
}


def get_smart_response(user_message: str, industry: str = "", current_step: str = "") -> str:
    """Busca la mejor respuesta predefinida basada en keywords."""
    msg_lower = user_message.lower().strip()
    
    # Saludos
    if any(w in msg_lower for w in ["hola", "buenas", "buenos días", "hey", "hi"]):
        return f"¡Hola! Estoy aquí para ayudarte con el levantamiento de datos hídricos. ¿Tienes alguna duda sobre algún campo del formulario o sobre algún concepto técnico? Pregúntame lo que necesites."
    
    # Buscar en knowledge base
    for pattern, response in KNOWLEDGE_BASE.items():
        if pattern == ".*":
            continue
        if re.search(pattern, msg_lower):
            return response
    
    # Context-aware hints based on current step
    step_hints = {
        "Datos Generales": "En este paso necesito los datos básicos de tu planta: nombre, ubicación, contacto y producción actual. Si no sabes la producción exacta, una estimación mensual promedio está bien.",
        "Fuente de Agua": "Necesito saber de dónde viene el agua: ¿pozo, red pública, río? Y si puedes, la calidad básica (CE y pH). Si tienes un medidor general, revisa cuántos m³ consumes al día.",
        "Procesos": "Aquí mapeamos cada proceso que usa agua. Ya te cargué los procesos típicos de tu industria. Para cada uno, necesito cuánta agua entra y cuánta sale. Si no tienes medidores individuales, estima: ¿cuántas horas opera esa máquina? ¿A qué caudal aproximado?",
        "Tratamiento Actual": "Cuéntame si tienen algún sistema de tratamiento de agua residual (PTAR). Puede ser algo simple como un decantador o algo más completo con filtros, UV, etc. También dime si reciclan alguna parte del agua.",
        "Calidad del Agua": "Si tienen un análisis de laboratorio reciente, perfecto — ingresa los valores de CE, pH, turbidez y DQO. Si no, los valores aproximados que maneje el operador de PTAR también sirven como punto de partida.",
        "Costos": "Necesito los costos para calcular el ROI de las mejoras. Lo más importante es: ¿cuánto pagas por m³ de agua fresca? Y si tienes PTAR: ¿cuánto gastas en químicos y energía al mes?",
    }
    
    if current_step in step_hints:
        return step_hints[current_step]
    
    # Default
    return KNOWLEDGE_BASE[".*"]


def get_ai_response(user_message: str, industry: str, current_step: str, api_key: str) -> str:
    """Usa la API de Claude para respuestas contextuales. Requiere API key."""
    import requests
    
    system_prompt = f"""Eres un asistente técnico de Water Intelligence, especializado en gestión hídrica industrial.
El cliente tiene una planta de tipo: {industry}.
Está en el paso '{current_step}' del formulario de levantamiento de datos.

Tu rol es:
1. Responder preguntas técnicas sobre agua, tratamiento, calidad, procesos.
2. Guiar al cliente sobre qué datos necesita y dónde encontrarlos en su planta.
3. Explicar conceptos técnicos en lenguaje simple.
4. Si no sabe un dato, sugerirle cómo estimarlo.
5. Ser amable, conciso y práctico.

Responde en español, máximo 3-4 oraciones."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=15,
        )
        data = response.json()
        return data.get("content", [{}])[0].get("text", "Disculpa, no pude procesar tu pregunta. ¿Puedes reformularla?")
    except Exception as e:
        return f"Error de conexión con el asistente IA. Usando respuesta automática.\n\n{get_smart_response(user_message, industry, current_step)}"
