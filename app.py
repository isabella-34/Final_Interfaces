import streamlit as st
import numpy as np
from PIL import Image
from keras.models import load_model
import paho.mqtt.client as mqtt
import json
import platform
import base64

# =====================================================
# CONFIG STREAMLIT
# =====================================================

st.set_page_config(page_title="Cofre Inteligente")
st.title("🔐 Cofre Inteligente con IA")
st.write("Python:", platform.python_version())

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

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# =====================================================
# FUNCIÓN MQTT
# =====================================================

def publicar(topic, mensaje):
    client.publish(topic, json.dumps(mensaje))

# =====================================================
# FUNCIÓN IMAGEN A BASE64
# (necesario para incrustar en HTML dentro de Streamlit)
# =====================================================

def imagen_a_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# =====================================================
# RECONOCIMIENTO FACIAL
# =====================================================

st.subheader("📷 Reconocimiento Facial")

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

    st.write(f"Clase detectada: {class_name}")
    st.write(f"Confianza: {confidence_score:.2f}")

    if (
        ("Dueño 1" in class_name or "Dueño 2" in class_name)
        and confidence_score > 0.85
    ):
        st.success("✅ Dueño reconocido")
        publicar(TOPIC_ESTADO, {"estado": "DUENO"})
        st.session_state.autorizado = True
    else:
        st.error("🚨 Intruso detectado")
        publicar(TOPIC_ESTADO, {"estado": "INTRUSO"})
        st.session_state.autorizado = False

# =====================================================
# COMANDOS DEL COFRE
# =====================================================

st.markdown("---")
st.subheader("🎤 Control del Cofre")

if st.session_state.autorizado:

    comando = st.text_input(
        "Escribe un comando",
        placeholder="Abrete o Cierrate",
        key=f"comando_{st.session_state.input_key}"
    )

    if comando.lower() == "abrete":
        publicar(TOPIC_VOZ, {"cofre": "ABRIR"})
        st.session_state.cofre_abierto = True
        st.session_state.input_key += 1

    elif comando.lower() == "cierrate":
        publicar(TOPIC_VOZ, {"cofre": "CERRAR"})
        st.session_state.cofre_abierto = False
        st.session_state.input_key += 1

else:
    st.warning("⚠️ Debe reconocerse un dueño primero")

# =====================================================
# ESTADO VISUAL DEL COFRE — HTML con opacidad
# =====================================================

st.markdown("---")
st.subheader("📦 Estado del Cofre")

# Convertir imágenes a base64 para incrustarlas en HTML
b64_cerrado = imagen_a_base64("cofre_cerrado.png")
b64_abierto = imagen_a_base64("cofre_abierto.png")

# Opacidad según estado actual
op_cerrado = 0 if st.session_state.cofre_abierto else 1
op_abierto = 1 if st.session_state.cofre_abierto else 0

st.components.v1.html(f"""
    <div style="position: relative; width: 300px; height: 300px;">

        <img
            src="data:image/png;base64,{b64_cerrado}"
            style="
                position: absolute;
                top: 0; left: 0;
                width: 300px;
                opacity: {op_cerrado};
                transition: opacity 0.5s ease;
            "
        />

        <img
            src="data:image/png;base64,{b64_abierto}"
            style="
                position: absolute;
                top: 0; left: 0;
                width: 300px;
                opacity: {op_abierto};
                transition: opacity 0.5s ease;
            "
        />

    </div>
""", height=320)

if st.session_state.cofre_abierto:
    st.success("📦 Cofre abierto")
else:
    st.warning("📦 Cofre cerrado")
