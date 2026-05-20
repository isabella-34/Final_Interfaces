# =====================================================
# IMPORTS
# =====================================================

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
    page_title="VAULT//SYSTEM",
    page_icon="🔐",
    layout="wide"
)

# =====================================================
# CYBERPUNK CSS
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

:root {
    --cyan:    #00f5ff;
    --magenta: #ff2d78;
    --dark:    #080b14;
    --panel:   rgba(8, 11, 20, 0.85);
    --glass:   rgba(0, 245, 255, 0.05);
    --border:  rgba(0, 245, 255, 0.25);
    --text:    #c8f0f5;
    --dim:     rgba(200, 240, 245, 0.45);
}

/* BACKGROUND */
.stApp {
    background-color: var(--dark) !important;
    background-image:
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 245, 255, 0.018) 2px,
            rgba(0, 245, 255, 0.018) 4px
        ),
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(255,45,120,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,245,255,0.10) 0%, transparent 70%);
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text) !important;
}

/* HIDE STREAMLIT */
#MainMenu, footer, header {
    visibility: hidden;
}

/* FULLSCREEN */
.block-container {
    max-width: 100vw !important;
    padding-top: 0.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 0rem !important;
}

html, body, [class*="css"] {
    overflow: hidden !important;
}

/* TITLE */
h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    font-size: 2rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase;
    background: linear-gradient(90deg, var(--cyan), var(--magenta));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.15rem !important;
}

/* SUBHEADERS */
h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.8rem !important;
    color: var(--cyan) !important;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

/* PANELS */
.hud-panel {
    background: var(--glass);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow:
        0 0 0 1px rgba(0,245,255,0.06),
        inset 0 1px 0 rgba(0,245,255,0.12),
        0 4px 32px rgba(0,0,0,0.6);
}

.hud-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: var(--magenta);
    margin-bottom: 1rem;
    text-transform: uppercase;
}

/* BUTTONS */
.stButton > button {
    width: 100%;
    background: transparent !important;
    color: var(--cyan) !important;
    border: 1px solid var(--cyan) !important;
}

/* VERSION */
.version-tag {
    text-align: center;
    font-size: 0.65rem;
    color: var(--dim);
    margin-bottom: 1rem;
}

/* STATUS */
.status-badge {
    text-align: center;
    padding: 0.5rem;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 0.15em;
    margin-top: 0.5rem;
}

.authorized {
    border: 1px solid #00ff88;
    color: #00ff88;
}

.locked {
    border: 1px solid #ff2d78;
    color: #ff2d78;
}

/* VOICE */
.voice-detected {
    text-align: center;
    padding: 0.5rem;
    border: 1px solid rgba(0,245,255,0.2);
    margin-top: 1rem;
}

/* REMOVE EXTRA SPACE */
.element-container {
    margin-bottom: 0.3rem !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("<h1>VAULT // SYSTEM</h1>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class='version-tag'>
    ◈ PYTHON {platform.python_version()} · AI-SECURED · MQTT ONLINE ◈
    </div>
    """,
    unsafe_allow_html=True
)

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
# MODELO IA
# =====================================================

model = load_model("keras_model.h5", compile=False)

with open("labels.txt", "r") as f:
    class_names = f.read().splitlines()

# =====================================================
# SESSION STATE
# =====================================================

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "cofre_abierto" not in st.session_state:
    st.session_state.cofre_abierto = False

# =====================================================
# FUNCIONES
# =====================================================

def publicar(topic, mensaje):
    client.publish(topic, json.dumps(mensaje))

def imagen_a_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# =====================================================
# LAYOUT
# =====================================================

left_col, center_col, right_col = st.columns([1,2,1])

# =====================================================
# LEFT COLUMN
# =====================================================

with left_col:

    st.markdown("""
    <div class='hud-panel'>
      <div class='hud-label'>estado del cofre</div>
    """, unsafe_allow_html=True)

    st.subheader("📦 Estado")

    if st.session_state.cofre_abierto:
        st.markdown("""
        <div class='status-badge authorized'>
            COFRE ABIERTO
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='status-badge locked'>
            COFRE CERRADO
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# CENTER COLUMN
# =====================================================

with center_col:

    st.markdown("""
    <div class='hud-panel'>
      <div class='hud-label'>núcleo visual</div>
    """, unsafe_allow_html=True)

    b64_cerrado = imagen_a_base64("safe_closed.png")
    b64_abierto = imagen_a_base64("safe_opened.png")

    op_cerrado = 0 if st.session_state.cofre_abierto else 1
    op_abierto = 1 if st.session_state.cofre_abierto else 0

    st.components.v1.html(f"""
    <div style="
        position:relative;
        width:500px;
        height:500px;
        margin:auto;
    ">

        <img
            src="data:image/png;base64,{b64_cerrado}"
            style="
                position:absolute;
                width:500px;
                opacity:{op_cerrado};
                transition:0.5s;
            "
        />

        <img
            src="data:image/png;base64,{b64_abierto}"
            style="
                position:absolute;
                width:500px;
                opacity:{op_abierto};
                transition:0.5s;
            "
        />

    </div>
    """, height=520)

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# RIGHT COLUMN
# =====================================================

with right_col:

    # =====================================================
    # RECONOCIMIENTO FACIAL
    # =====================================================

    st.markdown("""
    <div class='hud-panel'>
      <div class='hud-label'>reconocimiento facial</div>
    """, unsafe_allow_html=True)

    st.subheader("📷 Facial")

    img_file_buffer = st.camera_input("ESCANEAR")

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

        st.write(f"Clase: {class_name}")
        st.write(f"Confianza: {confidence_score:.2f}")

        if (
            ("Dueño 1" in class_name or "Dueño 2" in class_name)
            and confidence_score > 0.85
        ):

            st.success("Dueño reconocido")
            publicar(TOPIC_ESTADO, {"estado": "DUENO"})
            st.session_state.autorizado = True

        else:

            st.error("Intruso detectado")
            publicar(TOPIC_ESTADO, {"estado": "INTRUSO"})
            st.session_state.autorizado = False

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # VOZ
    # =====================================================

    st.markdown("""
    <div class='hud-panel'>
      <div class='hud-label'>control por voz</div>
    """, unsafe_allow_html=True)

    st.subheader("🎤 Voz")

    if st.session_state.autorizado:

        stt_button = Button(
            label="INICIAR ESCUCHA",
            width=220,
            button_type="success"
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
                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", {detail: value})
                    );
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

        if result and "GET_TEXT" in result:

            texto = result.get("GET_TEXT").strip().lower()

            st.markdown(
                f"""
                <div class='voice-detected'>
                {texto.upper()}
                </div>
                """,
                unsafe_allow_html=True
            )

            comandos_abrir  = ["ábrete", "abrete", "abrir", "abre"]
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

                st.error("Comando no reconocido")

    else:

        st.markdown("""
        <div class='status-badge locked'>
            ACCESO DENEGADO
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div style="
    text-align:center;
    font-size:0.6rem;
    color:rgba(0,245,255,0.25);
    margin-top:-1rem;
">
◈ VAULT SYSTEM v2.4 · SECURED BY AI ◈
</div>
""", unsafe_allow_html=True)
