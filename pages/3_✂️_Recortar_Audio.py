import streamlit as st
from pydub import AudioSegment, silence
import os
import zipfile

# Función para dividir el audio
def divide_audio(file_path, interval_minutes=2):
    # Cargar el archivo de audio
    audio = AudioSegment.from_file(file_path)
    # Convertir minutos a milisegundos
    interval_ms = interval_minutes * 60 * 1000
    # Configurar automáticamente el umbral de silencio
    silence_thresh = audio.dBFS - 16
    # Crear una carpeta de salida
    output_folder = "audio_segments"
    os.makedirs(output_folder, exist_ok=True)

    # Variables para segmentación
    start = 0
    segment_count = 1
    segment_files = []

    while start < len(audio):
        end = start + interval_ms
        segment = audio[start:end]

        # Detectar silencios
        silent_ranges = silence.detect_silence(segment, min_silence_len=1000, silence_thresh=silence_thresh)
        if silent_ranges and silent_ranges[-1][0] >= (interval_ms - 10 * 1000):
            end = start + silent_ranges[-1][0]
        
        # Guardar el segmento ajustado
        segment_file = os.path.join(output_folder, f"audio_seg_{segment_count}.mp3")
        audio[start:end].export(segment_file, format="mp3")
        segment_files.append(segment_file)

        # Actualizar los contadores
        start = end
        segment_count += 1

    return segment_files

# Función para comprimir los segmentos en un archivo ZIP
def create_zip(segments, zip_name="audio_segments.zip"):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for segment in segments:
            zipf.write(segment, os.path.basename(segment))
    return zip_name

# Interfaz de usuario con Streamlit
st.title("✂️División de Audio por Intervalos")
st.write("Sube un archivo de audio y selecciona la duración del intervalo para dividirlo en segmentos.")

# Cargar archivo de audio
uploaded_file = st.file_uploader("Sube tu archivo de audio (formatos soportados: mp3, wav)", type=["mp3", "wav"])

if uploaded_file is not None:
    # Seleccionar duración del intervalo
    interval = st.number_input("Duración del intervalo (en minutos):", min_value=1, max_value=10, value=2, step=1)
    file_path = f"temp_{uploaded_file.name}"
    
    # Guardar el archivo subido en una ubicación temporal
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Dividir el archivo de audio
    if st.button("Dividir Audio"):
        st.write("Procesando el archivo, por favor espera...")
        segments = divide_audio(file_path, interval_minutes=interval)
        
        # Comprimir los segmentos en un archivo ZIP
        zip_file = create_zip(segments)
        
        # Botón para descargar el archivo ZIP
        with open(zip_file, "rb") as zipf:
            st.download_button(
                label="Descargar Todos los Segmentos",
                data=zipf,
                file_name="audio_segments.zip",
                mime="application/zip"
            )
