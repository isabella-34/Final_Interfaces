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
# ESTILOS CYBERPUNK
# =====================================================

st.markdown("""
<style>

/* =========================
   FONDO GENERAL
========================= */

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(255, 0, 220, 0.18), transparent 28%),
        radial-gradient(circle at 85% 20%, rgba(0, 229, 255, 0.16), transparent 30%),
        linear-gradient(135deg, #050713 0%, #080b1f 45%, #120019 100%);
    color: #e8faff;
    font-family: 'Segoe UI', sans-serif;
}

/* Efecto grilla tipo HUD */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(0, 229, 255, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 0, 220, 0.035) 1px, transparent 1px);
    background-size: 34px 34px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,0.9), rgba(0,0,0,0.25));
    z-index: 0;
}

/* Contenedor principal */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

/* =========================
   TEXTOS
========================= */

h1, h2, h3 {
    color: #e8faff !important;
    letter-spacing: 1px;
}

h1 {
    text-align: center;
    text-transform: uppercase;
    font-size: 2.5rem !important;
    text-shadow:
        0 0 8px rgba(0, 229, 255, 0.9),
        0 0 20px rgba(255, 0, 220, 0.45);
}

h2, h3 {
    text-shadow: 0 0 10px rgba(0, 229, 255, 0.55);
}

p, label, span, div {
    color: #dffcff;
}

/* =========================
   PANEL SUPERIOR
========================= */

.cyber-header {
    position: relative;
    border: 1px solid rgba(0, 229, 255, 0.55);
    border-radius: 18px;
    padding: 26px 28px;
    margin-bottom: 28px;
    background:
        linear-gradient(135deg, rgba(6, 12, 32, 0.92), rgba(18, 0, 28, 0.88));
    box-shadow:
        0 0 18px rgba(0, 229, 255, 0.28),
        inset 0 0 24px rgba(255, 0, 220, 0.10);
    overflow: hidden;
}

.cyber-header::before {
    content: "";
    position: absolute;
    left: -20%;
    top: 0;
    width: 140%;
    height: 4px;
    background: linear-gradient(90deg, transparent, #00e5ff, #ff00dc, transparent);
    box-shadow: 0 0 16px #00e5ff;
}

.cyber-title {
    font-size: 2.2rem;
    font-weight: 800;
    text-align: center;
    color: #ffffff;
    letter-spacing: 3px;
    text-transform: uppercase;
    text-shadow:
        0 0 8px #00e5ff,
        0 0 22px rgba(255, 0, 220, 0.75);
}

.cyber-subtitle {
    text-align: center;
    margin-top: 8px;
    font-size: 1rem;
    color: #aef7ff;
    letter-spacing: 1px;
}

/* =========================
   TARJETAS / PANELES
========================= */

.cyber-panel {
    border: 1px solid rgba(0, 229, 255, 0.42);
    border-radius: 16px;
    padding: 20px;
    margin: 14px 0 22px 0;
    background:
        linear-gradient(145deg, rgba(7, 12, 31, 0.94), rgba(21, 3, 35, 0.90));
    box-shadow:
        0 0 16px rgba(0, 229, 255, 0.18),
        inset 0 0 18px rgba(255, 0, 220, 0.07);
}

.cyber-panel-title {
    display: inline-block;
    padding: 6px 14px;
    margin-bottom: 14px;
    border-left: 4px solid #00e5ff;
    border-right: 4px solid #ff00dc;
    background: rgba(255, 255, 255, 0.035);
    color: #ffffff;
    font-weight: 700;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.9);
}

.cyber-note {
    color: #b9f8ff;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* =========================
   SEPARADORES
========================= */

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00e5ff, #ff00dc, transparent);
    margin: 28px 0;
}

/* =========================
   ALERTAS STREAMLIT
========================= */

div[data-testid="stAlert"] {
    border-radius: 14px;
    border: 1px solid rgba(0, 229, 255, 0.35);
    box-shadow: 0 0 14px rgba(0, 229, 255, 0.14);
    background: rgba(8, 13, 34, 0.88);
}

/* =========================
   CÁMARA / INPUTS
========================= */

div[data-testid="stCameraInput"] {
    border: 1px solid rgba(255, 0, 220, 0.45);
    border-radius: 16px;
    padding: 16px;
    background: rgba(8, 13, 34, 0.72);
    box-shadow:
        0 0 14px rgba(255, 0, 220, 0.16),
        inset 0 0 18px rgba(0, 229, 255, 0.05);
}

button[kind="secondary"], button[kind="primary"] {
    border-radius: 12px !important;
    border: 1px solid #00e5ff !important;
    background: linear-gradient(90deg, #111934, #2a0c3f) !important;
    color: #ffffff !important;
    box-shadow:
        0 0 12px rgba(0, 229, 255, 0.35),
        inset 0 0 10px rgba(255, 0, 220, 0.12);
    text-transform: uppercase;
    letter-spacing: 1px;
}

button:hover {
    border-color: #ff00dc !important;
    box-shadow:
        0 0 14px rgba(255, 0, 220, 0.55),
        0 0 20px rgba(0, 229, 255, 0.25);
}

/* =========================
   MÉTRICAS / ESTADOS
========================= */

.status-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin: 16px 0 24px 0;
}

.status-card {
    border: 1px solid rgba(0, 229, 255, 0.40);
    border-radius: 15px;
    padding: 16px;
    background: rgba(4, 8, 24, 0.78);
    box-shadow:
        0 0 14px rgba(0, 229, 255, 0.16),
        inset 0 0 12px rgba(255, 0, 220, 0.06);
    text-align: center;
}

.status-label {
    font-size: 0.78rem;
    color: #88ecff;
    letter-spacing: 1.4px;
    text-transform: uppercase;
}

.status-value {
    margin-top: 6px;
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    text-shadow: 0 0 8px rgba(255, 0, 220, 0.65);
}

/* =========================
   IMAGEN DEL COFRE
========================= */

.safe-frame {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 340px;
    border: 1px solid rgba(255, 0, 220, 0.48);
    border-radius: 18px;
    background:
        radial-gradient(circle, rgba(0, 229, 255, 0.10), transparent 58%),
        linear-gradient(145deg, rgba(5, 9, 28, 0.94), rgba(19, 0, 30, 0.92));
    box-shadow:
        0 0 22px rgba(255, 0, 220, 0.22),
        inset 0 0 24px rgba(0, 229, 255, 0.08);
}

.safe-glow {
    filter:
        drop-shadow(0 0 10px rgba(0, 229, 255, 0.8))
        drop-shadow(0 0 18px rgba(255, 0, 220, 0.55));
}

/* =========================
   TEXTO ESCUCHADO
========================= */

.voice-result {
    text-align: center;
    color: #ffffff;
    font-size: 1.15rem;
    padding: 12px;
    margin-top: 10px;
    border: 1px solid rgba(0, 229, 255, 0.45);
    border-radius: 14px;
    background: rgba(0, 229, 255, 0.06);
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.8);
}

.neon-command {
    color: #ff4df0;
    font-weight: 800;
}

/* =========================
   FOOTER HUD
========================= */

.cyber-footer {
    text-align: center;
    margin-top: 28px;
    padding: 10px;
    color: #7eefff;
    font-size: 0.8rem;
    letter-spacing: 1px;
    opacity: 0.78;
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
        Reconocimiento facial · Control por voz · Estado remoto vía MQTT
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

estado_usuario = "DUEÑO AUTORIZADO" if st.session_state.autorizado else "SIN AUTORIZACIÓN"
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
# LAYOUT PRINCIPAL
# =====================================================

col1, col2 = st.columns([1.05, 0.95], gap="large")

# =====================================================
# RECONOCIMIENTO FACIAL
# =====================================================

with col1:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-panel-title">Módulo biométrico facial</div>
        <div class="cyber-note">
            Capture una imagen para validar si la persona corresponde a un dueño autorizado.
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

        st.markdown(f"""
        <div class="cyber-panel">
            <div class="cyber-panel-title">Resultado del escaneo</div>
            <div class="cyber-note">
                Clase detectada: <b>{class_name}</b><br>
                Confianza: <b>{confidence_score:.2f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if (
            ("Dueño 1" in class_name or "Dueño 2" in class_name)
            and confidence_score > 0.85
        ):
            st.success("Dueño reconocido. Acceso biométrico concedido.")
            publicar(TOPIC_ESTADO, {"estado": "DUENO"})
            st.session_state.autorizado = True
        else:
            st.error("Intruso detectado. Acceso biométrico denegado.")
            publicar(TOPIC_ESTADO, {"estado": "INTRUSO"})
            st.session_state.autorizado = False

# =====================================================
# CONTROL POR VOZ
# =====================================================

with col2:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-panel-title">Control por voz</div>
        <div class="cyber-note">
            Una vez reconocido el dueño, puede emitir la orden de apertura o cierre del cofre.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.autorizado:

        st.markdown("""
        <div class="cyber-panel">
            <div class="cyber-note" style="text-align:center;">
                Presiona el botón y di <b class="neon-command">ábrete</b> o 
                <b class="neon-command">ciérrate</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        stt_button = Button(
            label="INICIAR COMANDO DE VOZ",
            width=250,
            button_type="primary"
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
            override_height=75,
            debounce_time=0
        )

        # =====================================================
        # PROCESAR COMANDO DE VOZ
        # =====================================================

        if result and "GET_TEXT" in result:
            texto = result.get("GET_TEXT").strip().lower()

            st.markdown(
                f"""
                <div class="voice-result">
                    Comando escuchado: <span class="neon-command">{texto}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            comandos_abrir = ["ábrete", "abrete", "abrir", "abre"]
            comandos_cerrar = ["ciérrate", "cierrate", "cerrar", "cierra"]

            if any(cmd in texto for cmd in comandos_abrir):
                publicar(TOPIC_VOZ, {"cofre": "ABRIR"})
                st.session_state.cofre_abierto = True
                st.success("Cofre abierto.")

            elif any(cmd in texto for cmd in comandos_cerrar):
                publicar(TOPIC_VOZ, {"cofre": "CERRAR"})
                st.session_state.cofre_abierto = False
                st.warning("Cofre cerrado.")

            else:
                st.error(f"Comando no reconocido: '{texto}'")

    else:
        st.warning("Debe reconocerse un dueño primero para habilitar el control por voz.")

# =====================================================
# ESTADO VISUAL DEL COFRE
# =====================================================

st.markdown("---")

st.markdown("""
<div class="cyber-panel">
    <div class="cyber-panel-title">Estado visual del cofre</div>
    <div class="cyber-note">
        El panel muestra una transición visual entre cofre cerrado y cofre abierto según el estado actual.
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
        }}

        .safe-frame {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 350px;
            border: 1px solid rgba(255, 0, 220, 0.55);
            border-radius: 18px;
            background:
                radial-gradient(circle, rgba(0, 229, 255, 0.13), transparent 58%),
                linear-gradient(145deg, rgba(5, 9, 28, 0.96), rgba(19, 0, 30, 0.94));
            box-shadow:
                0 0 22px rgba(255, 0, 220, 0.26),
                inset 0 0 28px rgba(0, 229, 255, 0.10);
            position: relative;
            overflow: hidden;
        }}

        .safe-frame::before {{
            content: "";
            position: absolute;
            width: 120%;
            height: 3px;
            top: 20px;
            background: linear-gradient(90deg, transparent, #00e5ff, #ff00dc, transparent);
            box-shadow: 0 0 18px #00e5ff;
        }}

        .safe-box {{
            position: relative;
            width: 300px;
            height: 300px;
            filter:
                drop-shadow(0 0 10px rgba(0, 229, 255, 0.85))
                drop-shadow(0 0 20px rgba(255, 0, 220, 0.60));
        }}

        .safe-box img {{
            position: absolute;
            top: 0;
            left: 0;
            width: 300px;
            transition: opacity 0.5s ease;
        }}

        .status-text {{
            position: absolute;
            bottom: 18px;
            left: 50%;
            transform: translateX(-50%);
            font-family: Segoe UI, sans-serif;
            letter-spacing: 2px;
            color: #ffffff;
            font-weight: 800;
            text-shadow:
                0 0 8px #00e5ff,
                0 0 16px #ff00dc;
        }}
    </style>

    <div class="safe-frame">
        <div class="safe-box">
            <img
                src="data:image/png;base64,{b64_cerrado}"
                style="opacity: {op_cerrado};"
            />

            <img
                src="data:image/png;base64,{b64_abierto}"
                style="opacity: {op_abierto};"
            />
        </div>

        <div class="status-text">
            {"COFRE ABIERTO" if st.session_state.cofre_abierto else "COFRE CERRADO"}
        </div>
    </div>
""", height=370)

if st.session_state.cofre_abierto:
    st.success("Cofre abierto.")
else:
    st.warning("Cofre cerrado.")

st.markdown("""
<div class="cyber-footer">
    SISTEMA DE SEGURIDAD INTELIGENTE · HUD CYBERPUNK INTERFACE
</div>
""", unsafe_allow_html=True)
