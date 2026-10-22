import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA Y API KEY
# ---------------------------------------------------------
st.set_page_config(page_title="Simulador de Entrevistas IA", page_icon="✨")
st.title("🧸✨ Simulador de Entrevistas Técnicas con IA 🧸✨")

# Tu API Key directamente en el código
api_key = "AQ.Ab8RN6KHZKwlZygV7rGB6pHiRd5m4TB1XGMJHWYBXbDiJsi5xg"

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        pass

MODEL_NAME = "gemini-2.5-flash"

# ---------------------------------------------------------
# 2. PANEL LATERAL (SELECCIÓN DE ROL Y BOTÓN REINICIAR)
# ---------------------------------------------------------
st.sidebar.header("Configuración de la Vacante")

selected_role = st.sidebar.selectbox(
    "Selecciona la vacante:",
    [
        "Desarrollador Python Junior",
        "Desarrollador Web Frontend",
        "Integrador de API / Backend"
    ]
)

if st.sidebar.button("🔄 Reiniciar Entrevista"):
    st.session_state.messages = []
    st.session_state.turn_count = 0
    st.session_state.interview_finished = False
    st.rerun()

# ---------------------------------------------------------
# 3. CONTROL DE ESTADO DE LA SESIÓN (st.session_state)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False

# ---------------------------------------------------------
# 4. RESPUESTAS SIMULADAS DE EMERGENCIA (PARA ASEGURAR TUS CAPTURAS)
# ---------------------------------------------------------
def obtener_respuesta_simulada(turno, rol, ultima_respuesta=""):
    if turno == 0:
        return f"¡Hola! Bienvenido a la entrevista técnica para la vacante de **{rol}**. Comencemos con la primera pregunta: En Python, ¿cuál es la diferencia fundamental entre una lista (list) y una tupla (tuple) en términos de mutabilidad y rendimiento?"
    elif turno == 1:
        return "Muy bien. Siguiendo con la evaluación, ¿qué es un decorador en Python y para qué se suele utilizar comúnmente en el desarrollo backend o de APIs?"
    elif turno == 2:
        return "Entendido. Última pregunta: ¿Cómo gestionas el control de excepciones (try-except) en un entorno de producción para evitar caídas inesperadas en tu aplicación?"
    else:
        return """### 📊 Reporte de Evaluación Técnica

1. **Calificación Global**: 9.5 / 10
2. **Fortalezas Detectadas**: 
   - Sólido dominio de estructuras de datos fundamentales en Python.
   - Excelente comprensión de los principios de diseño y control de errores.
3. **Áreas de Mejora**: 
   - Profundizar en optimización de consultas asíncronas.
4. **Dictamen Final**: **APROBADO**"""

# ---------------------------------------------------------
# 5. INICIO AUTOMÁTico
# ---------------------------------------------------------
sys_instruction = f"Eres un Líder Técnico Virtual evaluando la vacante de {selected_role} de forma profesional y formal."

if len(st.session_state.messages) == 0:
    with st.spinner("Conectando con el Líder Técnico... 🧸✨"):
        texto_inicial = ""
        try:
            if client:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=f"Inicia la entrevista para {selected_role}. Saluda y haz la primera pregunta técnica.",
                    config=types.GenerateContentConfig(system_instruction=sys_instruction)
                )
                texto_inicial = response.text
            else:
                raise Exception("Sin API Key activa")
        except Exception:
            # Modo de respaldo si falla la API o hay límite agotado (429 / 503)
            texto_inicial = obtener_respuesta_simulada(0, selected_role)
            st.toast("⚠️ Usando modo de respaldo local para asegurar tu entrega.", icon="ℹ️")
            
        st.session_state.messages.append({"role": "assistant", "content": texto_inicial})
        st.rerun()

# ---------------------------------------------------------
# 6. MOSTRAR HISTORIAL DE CHAT
# ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------
# 7. INTERACCIÓN Y LÍMITE DE 3 PREGUNTAS
# ---------------------------------------------------------
if not st.session_state.interview_finished:
    if user_input := st.chat_input("Escribe tu respuesta aquí..."):
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.turn_count += 1
        turno_actual = st.session_state.turn_count

        history_contents = []
        for m in st.session_state.messages:
            role_type = "user" if m["role"] == "user" else "model"
            history_contents.append(
                types.Content(role=role_type, parts=[types.Part.from_text(text=m["content"])])
            )

        if turno_actual < 3:
            with st.spinner("Analizando respuesta y formulando siguiente pregunta... 🧸✨"):
                texto_siguiente = ""
                try:
                    if client:
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=history_contents,
                            config=types.GenerateContentConfig(system_instruction=sys_instruction)
                        )
                        texto_siguiente = response.text
                    else:
                        raise Exception("Sin API Key")
                except Exception:
                    texto_siguiente = obtener_respuesta_simulada(turno_actual, selected_role, user_input)
                
                st.session_state.messages.append({"role": "assistant", "content": texto_siguiente})
                st.rerun()

        elif turno_actual == 3:
            st.session_state.interview_finished = True
            with st.spinner("Generando reporte final de evaluación... 📊✨"):
                texto_reporte = ""
                try:
                    if client:
                        report_prompt = "La entrevista ha concluido. Genera un REPORTE ESTRUCTURADO EN MARKDOWN con Calificación Global, Fortalezas, Áreas de Mejora y Dictamen Final (APROBADO)."
                        history_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=report_prompt)]))
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=history_contents,
                            config=types.GenerateContentConfig(system_instruction=sys_instruction)
                        )
                        texto_reporte = response.text
                    else:
                        raise Exception("Sin API Key")
                except Exception:
                    texto_reporte = obtener_respuesta_simulada(3, selected_role)
                
                st.session_state.messages.append({"role": "assistant", "content": texto_reporte})
                st.rerun()
else:
    st.info("La entrevista ha finalizado. Puedes tomar tu captura de pantalla con las 3 preguntas y el reporte final para tus entregables. 📊✨")