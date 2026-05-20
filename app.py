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
# CONFIG STREAMLIT — WIDE LAYOUT, NO SCROLL
# =====================================================

st.set_page_config(
    page_title="VAULT//SYSTEM",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<style>
.block-container {
    max-width: 1230px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# CYBERPUNK CSS — DASHBOARD FULL-SCREEN
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

:root {
    --cyan:    #68a2eb;
    --magenta: #c231c9;
    --dark:    #080b14;
    --glass:   rgba(0, 245, 255, 0.04);
    --border:  rgba(0, 245, 255, 0.22);
    --text:    #c8f0f5;
    --dim:     rgba(200, 240, 245, 0.42);
}

/* ── BACKGROUND ── */
.stApp {
    background-color: var(--dark) !important;
    background-image:
        repeating-linear-gradient(
            0deg, transparent, transparent 2px,
            rgba(0,245,255,0.016) 2px, rgba(0,245,255,0.016) 4px
        ),
        radial-gradient(ellipse 70% 50% at 50% -10%, rgba(255,45,120,0.13) 0%, transparent 65%),
        radial-gradient(ellipse 50% 40% at 95% 100%, rgba(0,245,255,0.09) 0%, transparent 65%);
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text) !important;
}

/* ── SCANLINES ── */
.stApp::after {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
        to bottom,
        transparent 0px, transparent 3px,
        rgba(0,0,0,0.06) 3px, rgba(0,0,0,0.06) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ── HIDE CHROME, REMOVE PADDING ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0.6rem 1.2rem 0.5rem 1.2rem !important;
    max-width: 100% !important;
}

/* ── TITLE ── */
h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    font-size: 1.6rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase;
    background: linear-gradient(90deg, var(--cyan) 30%, var(--magenta) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
    filter: drop-shadow(0 0 14px rgba(0,245,255,0.5));
}

/* ── SUBHEADERS ── */
h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.26em !important;
    text-transform: uppercase;
    color: var(--cyan) !important;
    border-left: 2px solid var(--magenta);
    padding-left: 0.55rem;
    margin-top: 0.7rem !important;
    margin-bottom: 0.4rem !important;
    text-shadow: 0 0 10px rgba(0,245,255,0.5);
}

/* ── HUD PANEL ── */
.hud-panel {
    background: var(--glass);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0.9rem 1rem;
    height: 100%;
    position: relative;
    box-shadow:
        inset 0 1px 0 rgba(0,245,255,0.1),
        0 4px 28px rgba(0,0,0,0.55);
}
.hud-panel::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px;
    width: 14px; height: 14px;
    border-top: 2px solid var(--cyan);
    border-left: 2px solid var(--cyan);
}
.hud-panel::after {
    content: '';
    position: absolute;
    bottom: -1px; right: -1px;
    width: 14px; height: 14px;
    border-bottom: 2px solid var(--magenta);
    border-right: 2px solid var(--magenta);
}

/* ── HUD LABEL (module tag) ── */
.hud-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.58rem;
    letter-spacing: 0.32em;
    color: var(--magenta);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.hud-label::before {
    content: '';
    display: inline-block;
    width: 14px; height: 1px;
    background: var(--magenta);
    flex-shrink: 0;
}
.hud-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--magenta), transparent);
}

/* ── HEADER BAR ── */
.header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.8rem 0.5rem 0.8rem;
    border-bottom: 1px solid rgba(0,245,255,0.12);
    margin-bottom: 0.6rem;
}
.header-right {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: var(--dim);
    letter-spacing: 0.14em;
    text-align: right;
    line-height: 1.7;
}
.header-right span { color: var(--cyan); }

/* ── STREAMLIT BUTTONS ── */
.stButton > button {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase;
    background: transparent !important;
    color: var(--cyan) !important;
    border: 1px solid var(--cyan) !important;
    border-radius: 2px !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 8px rgba(0,245,255,0.18) !important;
    width: 100%;
}
.stButton > button:hover {
    background: rgba(0,245,255,0.08) !important;
    box-shadow: 0 0 18px rgba(0,245,255,0.45) !important;
    color: #fff !important;
}

/* ── CAMERA INPUT ── */
div[data-testid="stCameraInput"] {
    border: 1px solid var(--border) !important;
    border-radius: 3px;
    background: rgba(0,245,255,0.02) !important;
}
div[data-testid="stCameraInput"] label {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--dim) !important;
    font-size: 0.72rem !important;
}

/* ── ALERTS ── */
div[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    padding: 0.4rem 0.7rem !important;
}

/* ── TEXT ── */
p, .stMarkdown p {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text) !important;
    font-size: 0.76rem !important;
    margin-bottom: 0.3rem !important;
}

/* ── DIVIDER ── */
hr { border-color: rgba(0,245,255,0.1) !important; margin: 0.6rem 0 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--magenta); border-radius: 2px; }

/* ── STATUS BADGE ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 0.28rem 0.7rem;
    border-radius: 2px;
    margin: 0.3rem 0;
}
.status-badge.authorized {
    color: #00ff88;
    border: 1px solid rgba(0,255,136,0.35);
    background: rgba(0,255,136,0.05);
    text-shadow: 0 0 7px rgba(0,255,136,0.5);
}
.status-badge.locked {
    color: var(--magenta);
    border: 1px solid rgba(255,45,120,0.35);
    background: rgba(255,45,120,0.05);
    text-shadow: 0 0 7px rgba(255,45,120,0.5);
}
.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    animation: pulse-dot 1.4s ease-in-out infinite;
}
.status-badge.authorized .status-dot { background: #00ff88; box-shadow: 0 0 5px #00ff88; }
.status-badge.locked    .status-dot { background: var(--magenta); box-shadow: 0 0 5px var(--magenta); }
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.45; transform: scale(0.65); }
}

/* ── VOICE DETECTED ── */
.voice-detected {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.72rem;
    text-align: center;
    color: var(--cyan);
    letter-spacing: 0.1em;
    padding: 0.45rem 0.6rem;
    border: 1px solid rgba(0,245,255,0.18);
    background: rgba(0,245,255,0.03);
    border-radius: 2px;
    text-shadow: 0 0 10px rgba(0,245,255,0.65);
    margin-bottom: 0.4rem;
}

/* ── DATA READOUT ROWS ── */
.data-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.22rem 0;
    border-bottom: 1px solid rgba(0,245,255,0.07);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
}
.data-row .label { color: var(--dim); }
.data-row .value { color: var(--cyan); text-shadow: 0 0 6px rgba(0,245,255,0.5); }

/* ── BOTTOM VOZ PANEL ── */
.voice-instruction {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--dim);
    text-align: center;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.voice-instruction b { color: var(--magenta); letter-spacing: 0.05em; }

/* ── FOOTER ── */
.footer-bar {
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    color: rgba(0,245,255,0.2);
    padding: 0.35rem 0 0 0;
    border-top: 1px solid rgba(0,245,255,0.07);
    margin-top: 0.5rem;
}

iframe { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# MQTT
# =====================================================

BROKER = "broker.mqttdashboard.com"
PUERTO = 1883
TOPIC_ESTADO = "cofre/estado"
TOPIC_VOZ    = "cofre/voz"

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

if "clase_detectada" not in st.session_state:
    st.session_state.clase_detectada = "—"

if "confianza" not in st.session_state:
    st.session_state.confianza = "—"

# =====================================================
# FUNCIONES
# =====================================================

def publicar(topic, mensaje):
    client.publish(topic, json.dumps(mensaje))

def imagen_a_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# =====================================================
# HEADER BAR
# =====================================================

st.markdown(f"""
<div class="header-bar">
    <h1>VAULT // SYSTEM</h1>
    <div class="header-right">
        PYTHON <span>{platform.python_version()}</span> &nbsp;·&nbsp;
        MQTT <span>ONLINE</span> &nbsp;·&nbsp;
        AI-SECURED<br>
        BROKER <span>mqttdashboard.com</span> &nbsp;·&nbsp;
        PORT <span>{PUERTO}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# MAIN LAYOUT — 2 COLUMNS TOP + BOTTOM VOZ
# =====================================================

col_left, col_right = st.columns([1.1, 0.9], gap="medium")

# ─────────────────────────────────────────
# COL LEFT — MÓDULO 01: RECONOCIMIENTO FACIAL
# ─────────────────────────────────────────
with col_left:
    st.markdown("""
    <div class="hud-panel">
      <div class="hud-label">módulo 01 — identificación biométrica</div>
    """, unsafe_allow_html=True)

    st.subheader("📷 Reconocimiento Facial")

    img_file_buffer = st.camera_input("ACTIVAR ESCÁNER FACIAL")

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

        # Guardar en session_state para mostrar persistente
        st.session_state.clase_detectada = class_name
        st.session_state.confianza = f"{confidence_score:.2f}"

        if (
            ("Dueño 1" in class_name or "Dueño 2" in class_name)
            and confidence_score > 0.85
        ):
            st.success("✅ Dueño reconocido — acceso concedido")
            publicar(TOPIC_ESTADO, {"estado": "DUENO"})
            st.session_state.autorizado = True
        else:
            st.error("🚨 Identidad no autorizada — alerta activada")
            publicar(TOPIC_ESTADO, {"estado": "INTRUSO"})
            st.session_state.autorizado = False

    # Readout de datos de detección (siempre visible)
    st.markdown(f"""
    <div style="margin-top:0.6rem;">
        <div class="data-row">
            <span class="label">› IDENTIDAD</span>
            <span class="value">{st.session_state.clase_detectada}</span>
        </div>
        <div class="data-row">
            <span class="label">› CONFIANZA</span>
            <span class="value">{st.session_state.confianza}</span>
        </div>
        <div class="data-row">
            <span class="label">› ACCESO</span>
            <span class="value" style="color:{'#b9ffb5' if st.session_state.autorizado else '#5b2a62'}">
                {'AUTORIZADO' if st.session_state.autorizado else 'DENEGADO'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)   # cierra hud-panel

# ─────────────────────────────────────────
# COL RIGHT — MÓDULO 03: ESTADO DEL COFRE
# ─────────────────────────────────────────
with col_right:
    st.markdown("""
    <div class="hud-panel">
      <div class="hud-label">módulo 03 — estado del sistema</div>
    """, unsafe_allow_html=True)

    st.subheader("📦 Estado del Cofre")

    # Badge de estado
    if st.session_state.cofre_abierto:
        st.markdown("""
            <div class='status-badge authorized'>
                <span class='status-dot'></span>COFRE: ABIERTO
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='status-badge locked'>
                <span class='status-dot'></span>COFRE: CERRADO
            </div>
        """, unsafe_allow_html=True)

    b64_cerrado = imagen_a_base64("safe_closed.png")
    b64_abierto = imagen_a_base64("safe_opened.png")

    op_cerrado = 0 if st.session_state.cofre_abierto else 1
    op_abierto = 1 if st.session_state.cofre_abierto else 0

    st.components.v1.html(f"""
        <style>
            body {{ margin: 0; background: transparent; }}
            .vault-wrap {{
                position: relative;
                width: 240px; height: 240px;
                margin: 0.4rem auto 0 auto;
                filter: drop-shadow(0 0 16px rgba(0,245,255,0.32));
            }}
            .vault-wrap::before {{
                content: '';
                position: absolute;
                inset: -6px;
                border: 1px solid rgba(0,245,255,0.18);
                border-radius: 3px;
            }}
            .vault-wrap::after {{
                content: '';
                position: absolute;
                top: -6px; left: -6px;
                width: 12px; height: 12px;
                border-top: 2px solid #ff2d78;
                border-left: 2px solid #ff2d78;
            }}
        </style>
        <div class="vault-wrap">
            <img src="data:image/png;base64,{b64_cerrado}"
                style="position:absolute;top:0;left:0;width:240px;
                       opacity:{op_cerrado};transition:opacity 0.5s ease;"/>
            <img src="data:image/png;base64,{b64_abierto}"
                style="position:absolute;top:0;left:0;width:240px;
                       opacity:{op_abierto};transition:opacity 0.5s ease;"/>
        </div>
    """, height=268)

    st.markdown("</div>", unsafe_allow_html=True)   # cierra hud-panel

# =====================================================
# BOTTOM ROW — MÓDULO 02: CONTROL POR VOZ (full width)
# =====================================================

st.markdown("""
<div class="hud-panel" style="margin-top:0.6rem;">
  <div class="hud-label">módulo 02 — interfaz de voz</div>
""", unsafe_allow_html=True)

st.subheader("🎤 Control por Voz del Cofre")

if st.session_state.autorizado:

    col_v1, col_v2, col_v3 = st.columns([1, 1.2, 1], gap="medium")

    with col_v2:
        st.markdown("""
            <div class="voice-instruction">
                DI <b>ÁBRETE</b> o <b>CIÉRRATE</b> para controlar el cofre
            </div>
        """, unsafe_allow_html=True)

        stt_button = Button(
            label="◉  INICIAR ESCUCHA",
            width=220,
            button_type="success",
            stylesheets=["""
                .bk-btn {
                    font-family: 'Orbitron', sans-serif !important;
                    font-size: 11px !important;
                    letter-spacing: 3px !important;
                    text-transform: uppercase;
                    background: transparent !important;
                    color: #00f5ff !important;
                    border: 1px solid #00f5ff !important;
                    border-radius: 2px !important;
                    padding: 10px 20px !important;
                    box-shadow: 0 0 12px rgba(0,245,255,0.28) !important;
                    transition: all 0.2s !important;
                    width: 100%;
                }
                .bk-btn:hover {
                    background: rgba(0,245,255,0.09) !important;
                    box-shadow: 0 0 22px rgba(0,245,255,0.55) !important;
                }
            """]
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

    # Resultado de voz — ocupa las 3 columnas
    if result and "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip().lower()

        col_r1, col_r2, col_r3 = st.columns([1, 1.2, 1])
        with col_r2:
            st.markdown(
                f"<div class='voice-detected'>⬡ AUDIO CAPTADO: <i>{texto.upper()}</i></div>",
                unsafe_allow_html=True
            )

        comandos_abrir  = ["ábrete", "abrete", "abrir", "abre"]
        comandos_cerrar = ["ciérrate", "cierrate", "cerrar", "cierra"]

        if any(cmd in texto for cmd in comandos_abrir):
            publicar(TOPIC_VOZ, {"cofre": "ABRIR"})
            st.session_state.cofre_abierto = True
            st.success("📦 Cofre abierto")

        elif any(cmd in texto for cmd in comandos_cerrar):
            publicar(TOPIC_VOZ, {"cofre": "CERRAR"})
            st.session_state.cofre_abierto = False
            st.warning("📦 Cofre cerrado")

        else:
            st.error(f"❌ Comando no reconocido: '{texto}'")

else:
    st.markdown("""
        <div class='status-badge locked' style="margin-left:0;">
            <span class='status-dot'></span>
            ACCESO DENEGADO — AUTENTICACIÓN BIOMÉTRICA REQUERIDA
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)   # cierra hud-panel

# =====================================================
# FOOTER
# =====================================================

st.markdown("""
<div class="footer-bar">
    ◈ VAULT SYSTEM v2.4 &nbsp;·&nbsp; SECURED BY AI &nbsp;·&nbsp; ALL ACCESS LOGGED ◈
</div>
""", unsafe_allow_html=True)
