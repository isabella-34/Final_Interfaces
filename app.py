import streamlit as st
import numpy as np
from PIL import Image
from keras.models import load_model
import paho.mqtt.client as mqtt
import json
import platform

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
        st.rerun()  # ← ahora SÍ es seguro porque el estado ya cambió arriba

    elif comando.lower() == "cierrate":
        publicar(TOPIC_VOZ, {"cofre": "CERRAR"})
        st.session_state.cofre_abierto = False
        st.session_state.input_key += 1
        st.rerun()  # ← igual aquí

else:
    st.warning("⚠️ Debe reconocerse un dueño primero")

# =====================================================
# ESTADO VISUAL DEL COFRE (al final, ya ve el estado actualizado)
# =====================================================

st.markdown("---")
st.subheader("📦 Estado del Cofre")

if st.session_state.cofre_abierto:
    st.image("cofre_abierto.png", width=300)
    st.success("📦 Cofre abierto")
else:
    st.image("cofre_cerrado.png", width=300)
    st.warning("📦 Cofre cerrado")
