import os
import streamlit as st
import numpy as np
from PIL import Image
from keras.models import load_model
import paho.mqtt.client as mqtt
import json
import platform
import base64
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# =====================================================
# CONFIG STREAMLIT
# =====================================================

st.set_page_config(
    page_title="Cofre Inteligente",
    page_icon="🔐",
    layout="wide"
)

# =====================================================
# ESTILOS CYBERPUNK + SHARE TECH MONO
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

/* =========================
   BASE GLOBAL
========================= */
html, body, [class*="css"], .stApp {
    font-family: 'Share Tech Mono', monospace !important;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(255, 0, 220, 0.16), transparent 26%),
        radial-gradient(circle at 85% 20%, rgba(0, 229, 255, 0.14), transparent 28%),
        linear-gradient(135deg, #040611 0%, #090d20 45%, #140019 100%);
    color: #e8faff;
}

/* grilla cyberpunk sutil */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(0, 229, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 0, 220, 0.03) 1px, transparent 1px);
    background-size: 30px 30px;
    z-index: 0;
}

.block-container {
    max-width: 1380px;
    padding-top: 0.9rem;
    padding-bottom: 1rem;
}

/* Quitar espacio extra arriba */
section.main > div {
    padding-top: 0.5rem;
}

/* =========================
   TEXTO
========================= */
h1, h2, h3, h4, p, span, div, label {
    font-family: 'Share Tech Mono', monospace !important;
    color: #dffcff;
}

.cyber-header {
    position: relative;
    border: 1px solid rgba(0, 229, 255, 0.55);
    border-radius: 16px;
    padding: 16px 22px;
    margin-bottom: 12px;
    background:
        linear-gradient(135deg, rgba(6, 12, 32, 0.94), rgba(18, 0, 28, 0.90));
    box-shadow:
        0 0 18px rgba(0, 229, 255, 0.24),
        inset 0 0 24px rgba(255, 0, 220, 0.10);
    overflow: hidden;
}

.cyber-header::before {
    content: "";
    position: absolute;
    left: -20%;
    top: 0;
    width: 140%;
    height: 3px;
    background: linear-gradient(90deg, transparent, #00e5ff, #ff00dc, transparent);
    box-shadow: 0 0 14px #00e5ff;
}

.cyber-title {
    text-align: center;
    font-size: 1.9rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #ffffff;
    text-shadow:
        0 0 8px #00e5ff,
        0 0 22px rgba(255, 0, 220, 0.65);
}

.cyber-subtitle {
    text-align: center;
    margin-top: 5px;
    font-size: 0.84rem;
    color: #9befff;
    letter-spacing: 1px;
}

/* =========================
   PANEL / TARJETAS
========================= */
.cyber-panel {
    border: 1px solid rgba(0, 229, 255, 0.42);
    border-radius: 14px;
    padding: 12px 14px;
    margin: 8px 0 12px 0;
    background:
        linear-gradient(145deg, rgba(7, 12, 31, 0.95), rgba(21, 3, 35, 0.92));
    box-shadow:
        0 0 16px rgba(0, 229, 255, 0.16),
        inset 0 0 18px rgba(255, 0, 220, 0.06);
}

.cyber-panel-title {
    display: inline-block;
    padding: 4px 10px;
    margin-bottom: 8px;
    border-left: 3px solid #00e5ff;
    border-right: 3px solid #ff00dc;
    background: rgba(255,255,255,0.03);
    color: #ffffff;
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.8);
}

.cyber-note {
    font-size: 0.82rem;
    color: #b9f8ff;
    line-height: 1.45;
}

/* =========================
   STATUS CARDS
========================= */
.status-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 6px 0 12px 0;
}

.status-card {
    border: 1px solid rgba(0, 229, 255, 0.35);
    border-radius: 12px;
    padding: 10px 8px;
    background: rgba(4, 8, 24, 0.78);
    box-shadow:
        0 0 12px rgba(0, 229, 255, 0.12),
        inset 0 0 10px rgba(255, 0, 220, 0.05);
    text-align: center;
}

.status-label {
    font-size: 0.72rem;
    color: #88ecff;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.status-value {
    margin-top: 4px;
    font-size: 0.98rem;
    font-weight: 800;
    color: #ffffff;
    text-shadow: 0 0 8px rgba(255, 0, 220, 0.55);
}

/* =========================
   STREAMLIT ALERTS
========================= */
div[data-testid="stAlert"] {
    border-radius: 12px;
    border: 1px solid rgba(0, 229, 255, 0.35);
    background: rgba(8, 13, 34, 0.88);
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.12);
    padding-top: 0.45rem;
    padding-bottom: 0.45rem;
    font-size: 0.86rem;
}

/* =========================
   CÁMARA
========================= */
div[data-testid="stCameraInput"] {
    border: 1px solid rgba(255, 0, 220, 0.40);
    border-radius: 14px;
    padding: 10px;
    background: rgba(8, 13, 34, 0.72);
    box-shadow:
        0 0 12px rgba(255, 0, 220, 0.14),
        inset 0 0 14px rgba(0, 229, 255, 0.05);
}

/* compacto general */
div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stCameraInput"]) {
    margin-bottom: 0.2rem;
}

/* =========================
   BOTONES STREAMLIT
========================= */
button[kind="secondary"], button[kind="primary"] {
    border-radius: 10px !important;
    border: 1px solid #00e5ff !important;
    background: linear-gradient(90deg, #111934, #2a0c3f) !important;
    color: #ffffff !important;
    box-shadow:
        0 0 10px rgba(0, 229, 255, 0.30),
        inset 0 0 10px rgba(255, 0, 220, 0.10);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Share Tech Mono', monospace !important;
}

button:hover {
    border-color: #ff00dc !important;
    box-shadow:
        0 0 14px rgba(255, 0, 220, 0.45),
        0 0 18px rgba(0, 229, 255, 0.22);
}

/* =========================
   BOTÓN BOKEH (voz) - IMPORTANTE
========================= */
.bk-btn, .bk-btn-default, .bk-btn-primary, button.bk-btn {
    background: linear-gradient(90deg, #0f1734, #2b0d41) !important;
    color: #eaffff !important;
    border: 1px solid #00e5ff !important;
    border-radius: 10px !important;
    box-shadow:
        0 0 12px rgba(0, 229, 255, 0.35),
        inset 0 0 10px rgba(255, 0, 220, 0.08) !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 1px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 10px 14px !important;
}

.bk-btn:hover, .bk-btn-default:hover, .bk-btn-primary:hover {
    background: linear-gradient(90deg, #161d42, #411055) !important;
    border: 1px solid #ff00dc !important;
    color: white !important;
    box-shadow:
        0 0 14px rgba(255, 0, 220, 0.50),
        0 0 18px rgba(0, 229, 255, 0.25) !important;
}

/* elimina marco feo del componente */
iframe {
    border-radius: 12px !important;
}

/* =========================
   RESULTADO VOZ
========================= */
.voice-result {
    text-align: center;
    color: #ffffff;
    font-size: 0.95rem;
    padding: 10px;
    margin-top: 8px;
    border: 1px solid rgba(0, 229, 255, 0.45);
    border-radius: 12px;
    background: rgba(0, 229, 255, 0.06);
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.8);
}

.neon-command {
    color: #ff4df0;
    font-weight: 800;
}

/* =========================
   COFRE
========================= */
.safe-status-chip {
    text-align: center;
    margin-top: 8px;
    padding: 8px 10px;
    border: 1px solid rgba(255, 0, 220, 0.45);
    border-radius: 10px;
    background: rgba(255, 0, 220, 0.05);
    color: white;
    letter-spacing: 1px;
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.8);
    font-size: 0.88rem;
}

/* =========================
   FOOTER
========================= */
.cyber-footer {
    text-align: center;
    margin-top: 8px;
    padding: 4px;
    color: #7eefff;
    font-size: 0.72rem;
    letter-spacing: 1px;
    opacity: 0.75;
}

/* reduce espacios entre elementos */
.element-container {
    margin-bottom: 0.35rem !important;
}

hr {
    margin: 8px 0 !important;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00e5ff, #ff00dc, transparent);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER VISUAL
# =====================================================

st.markdown("""
<div class="cyber-header">
    <div class="cyber-title">Cofre Inteligente con IA</div>
    <div class="cyber-subtitle">
        Reconocimiento facial · Control por voz · Estado remoto MQTT
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MQTT
# =====================================================

BROKER = "broker.mqttdashboard.com"
PUERTO = 1883
TOPIC_ESTADO = "cofre/estado"
TOPIC_VOZ = "cofre/voz"

client = mqtt.Client()
client.connect(BROKER, PUERTO, 60)
client.loop_start()

# =====================================================
# CARGAR MODELO
# =====================================================

model = load_model("keras_model.h5", compile=False)

with open("labels.txt", "r") as f:
    class_names = f.read().splitlines()

# =====================================================
# VARIABLES DE ESTADO
# =====================================================

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "cofre_abierto" not in st.session_state:
    st.session_state.cofre_abierto = False

if "ultima_clase" not in st.session_state:
    st.session_state.ultima_clase = "SIN LECTURA"

if "ultima_confianza" not in st.session_state:
    st.session_state.ultima_confianza = 0.0

if "ultimo_texto" not in st.session_state:
    st.session_state.ultimo_texto = ""

# =====================================================
# FUNCIÓN MQTT
# =====================================================

def publicar(topic, mensaje):
    client.publish(topic, json.dumps(mensaje))

# =====================================================
# FUNCIÓN IMAGEN A BASE64
# =====================================================

def imagen_a_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# =====================================================
# PANEL DE ESTADO GENERAL
# =====================================================

estado_usuario = "AUTORIZADO" if st.session_state.autorizado else "NO AUTORIZADO"
estado_cofre = "ABIERTO" if st.session_state.cofre_abierto else "CERRADO"
estado_mqtt = "ONLINE"

st.markdown(f"""
<div class="status-grid">
    <div class="status-card">
        <div class="status-label">Identidad</div>
        <div class="status-value">{estado_usuario}</div>
    </div>
    <div class="status-card">
        <div class="status-label">Cofre</div>
        <div class="status-value">{estado_cofre}</div>
    </div>
    <div class="status-card">
        <div class="status-label">MQTT</div>
        <div class="status-value">{estado_mqtt}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# LAYOUT PRINCIPAL COMPACTO
# izquierda: facial
# centro: cofre
# derecha: voz
# =====================================================

col1, col2, col3 = st.columns([1.05, 1.0, 0.95], gap="medium")

# =====================================================
# RECONOCIMIENTO FACIAL
# =====================================================

with col1:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-panel-title">Reconocimiento facial</div>
        <div class="cyber-note">
            Captura una imagen para identificar si quien intenta acceder es dueño o intruso.
        </div>
    </div>
    """, unsafe_allow_html=True)

    img_file_buffer = st.camera_input("Tomar foto")

    if img_file_buffer is not None:
        image = Image.open(img_file_buffer).convert("RGB")
        image = image.resize((224, 224))
        image_array = np.array(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array

        prediction = model.predict(data)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        st.session_state.ultima_clase = class_name
        st.session_state.ultima_confianza = confidence_score

        if (
            ("Dueño 1" in class_name or "Dueño 2" in class_name)
            and confidence_score > 0.85
        ):
            st.session_state.autorizado = True
            publicar(TOPIC_ESTADO, {"estado": "DUENO"})
            st.success("Dueño reconocido")
        else:
            st.session_state.autorizado = False
            publicar(TOPIC_ESTADO, {"estado": "INTRUSO"})
            st.error("Intruso detectado")

    st.markdown(f"""
    <div class="cyber-panel">
        <div class="cyber-panel-title">Resultado</div>
        <div class="cyber-note">
            Clase detectada: <b>{st.session_state.ultima_clase}</b><br>
            Confianza: <b>{st.session_state.ultima_confianza:.2f}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# ESTADO VISUAL DEL COFRE
# =====================================================

with col2:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-panel-title">Estado del cofre</div>
        <div class="cyber-note">
            Visualización central del sistema de apertura y cierre.
        </div>
    </div>
    """, unsafe_allow_html=True)

    b64_cerrado = imagen_a_base64("safe_closed.png")
    b64_abierto = imagen_a_base64("safe_opened.png")

    op_cerrado = 0 if st.session_state.cofre_abierto else 1
    op_abierto = 1 if st.session_state.cofre_abierto else 0

    st.components.v1.html(f"""
        <style>
            body {{
                margin: 0;
                background: transparent;
                font-family: 'Share Tech Mono', monospace;
            }}

            .safe-frame {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 300px;
                border: 1px solid rgba(255, 0, 220, 0.55);
                border-radius: 16px;
                background:
                    radial-gradient(circle, rgba(0, 229, 255, 0.12), transparent 58%),
                    linear-gradient(145deg, rgba(5, 9, 28, 0.96), rgba(19, 0, 30, 0.94));
                box-shadow:
                    0 0 18px rgba(255, 0, 220, 0.20),
                    inset 0 0 24px rgba(0, 229, 255, 0.08);
                position: relative;
                overflow: hidden;
            }}

            .safe-frame::before {{
                content: "";
                position: absolute;
                width: 120%;
                height: 3px;
                top: 16px;
                background: linear-gradient(90deg, transparent, #00e5ff, #ff00dc, transparent);
                box-shadow: 0 0 16px #00e5ff;
            }}

            .safe-box {{
                position: relative;
                width: 230px;
                height: 230px;
                filter:
                    drop-shadow(0 0 10px rgba(0, 229, 255, 0.85))
                    drop-shadow(0 0 18px rgba(255, 0, 220, 0.55));
            }}

            .safe-box img {{
                position: absolute;
                top: 0;
                left: 0;
                width: 230px;
                transition: opacity 0.5s ease;
            }}

            .status-text {{
                position: absolute;
                bottom: 16px;
                left: 50%;
                transform: translateX(-50%);
                letter-spacing: 2px;
                color: #ffffff;
                font-weight: 800;
                text-shadow:
                    0 0 8px #00e5ff,
                    0 0 16px #ff00dc;
                font-size: 13px;
                white-space: nowrap;
            }}
        </style>

        <div class="safe-frame">
            <div class="safe-box">
                <img src="data:image/png;base64,{b64_cerrado}" style="opacity: {op_cerrado};" />
                <img src="data:image/png;base64,{b64_abierto}" style="opacity: {op_abierto};" />
            </div>

            <div class="status-text">
                {"COFRE ABIERTO" if st.session_state.cofre_abierto else "COFRE CERRADO"}
            </div>
        </div>
    """, height=310)

    st.markdown(
        f"""
        <div class="safe-status-chip">
            ESTADO ACTUAL: {"ABIERTO" if st.session_state.cofre_abierto else "CERRADO"}
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# CONTROL POR VOZ
# =====================================================

with col3:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-panel-title">Control por voz</div>
        <div class="cyber-note">
            Solo se habilita después del reconocimiento facial exitoso del dueño.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.autorizado:
        st.markdown("""
        <div class="cyber-panel">
            <div class="cyber-note" style="text-align:center;">
                Di <b class="neon-command">ábrete</b> o <b class="neon-command">ciérrate</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        stt_button = Button(
            label="INICIAR COMANDO DE VOZ",
            width=280,
            button_type="default"
        )

        stt_button.js_on_event("button_click", CustomJS(code="""
            var recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'es-ES';

            recognition.onresult = function(e) {
                var value = "";
                for (var i = e.resultIndex; i < e.results.length; ++i) {
                    if (e.results[i].isFinal) {
                        value += e.results[i][0].transcript;
                    }
                }
                if (value != "") {
                    document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
                }
            }
            recognition.start();
        """))

        result = streamlit_bokeh_events(
            stt_button,
            events="GET_TEXT",
            key="listen",
            refresh_on_update=False,
            override_height=70,
            debounce_time=0
        )

        if result and "GET_TEXT" in result:
            texto = result.get("GET_TEXT").strip().lower()
            st.session_state.ultimo_texto = texto

            comandos_abrir = ["ábrete", "abrete", "abrir", "abre"]
            comandos_cerrar = ["ciérrate", "cierrate", "cerrar", "cierra"]

            if any(cmd in texto for cmd in comandos_abrir):
                publicar(TOPIC_VOZ, {"cofre": "ABRIR"})
                st.session_state.cofre_abierto = True
                st.success("Cofre abierto")

            elif any(cmd in texto for cmd in comandos_cerrar):
                publicar(TOPIC_VOZ, {"cofre": "CERRAR"})
                st.session_state.cofre_abierto = False
                st.warning("Cofre cerrado")

            else:
                st.error(f"Comando no reconocido: '{texto}'")

        st.markdown(
            f"""
            <div class="voice-result">
                Último comando: <span class="neon-command">
                {st.session_state.ultimo_texto if st.session_state.ultimo_texto else "SIN REGISTRO"}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.warning("Primero debe reconocerse un dueño")

st.markdown("""
<div class="cyber-footer">
    SMART SAFE INTERFACE · CYBERPUNK HUD
</div>
""", unsafe_allow_html=True)
