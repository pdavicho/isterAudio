import streamlit as st
from streamlit_tags import st_tags
import zipfile
import os
import tempfile
import whisper
from whisper.utils import get_writer
import time
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title='Speech To Text', page_icon=':studio_microphone:')

# Cargar modelo Whisper
model = whisper.load_model('base')

# Función para subir y extraer un archivo ZIP (actualizada)
def upload_and_extract_zip():
    zip_file = st.file_uploader('Sube un archivo ZIP con audios', type=['zip'])
    if zip_file is not None:
        # Crear un directorio temporal persistente
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())

        # Extraer el ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_dir)
            
        # Obtener archivos de audio extraídos
        audio_files = [
                os.path.join(temp_dir, f) for f in os.listdir(temp_dir)
                if f.endswith(('.wav', '.mp3', '.wave'))
            ]
        return audio_files, temp_dir  # Retorna también el directorio
    return None, None

# Función para transcribir audio
def get_transcribe(audio, language='es'):
    return model.transcribe(audio=audio, language=language, verbose=True)

# Función para guardar transcripciones
def save_file(results, format='tsv'):
    writer = get_writer(format, './')
    writer(results, f'transcribe.{format}')
    return f'transcribe.{format}'

# Función para seleccionar palabras clave
def opciones():
    keywords = st_tags(
        label='Escoge las palabras que deseas analizar:',
        text='Presiona Enter o añade más',
        value=['emergencia', 'robo', 'drogas'],
        suggestions=['extorsión', 'robos', 'rescate'],
        maxtags=5,
        key="opciones"
        )
    return keywords

# Función para mostrar transcripción y resaltar términos
def search_and_highlight_text(text, search_terms):
    highlighted_text = text
    for term in search_terms:
        highlighted_text = highlighted_text.replace(
            term, f'<span style="color:red; text-decoration: underline;">{term}</span>'
            )
    return highlighted_text

# Interfaz principal (modificada para procesar el directorio persistente)
if __name__ == "__main__":
    st.title('Transcripción de Audio a Texto desde ZIP')

    audio_files, temp_dir = upload_and_extract_zip()

    if audio_files is not None:
        st.success(f"{len(audio_files)} archivos cargados y extraídos correctamente.")
            
        opciones_elegidas = opciones()
        st.write(f"Términos seleccionados: {', '.join(opciones_elegidas)}")
            
        if st.button('Ejecutar'):
            results = []
            with st.spinner("Procesando audios..."):
                for audio_path in audio_files:
                    st.write(f"Procesando: {os.path.basename(audio_path)}")
                    result = get_transcribe(audio_path)
                    results.append(result)
                        
                    # Guardar transcripción individual
                    save_file(result)
                    save_file(result, 'txt')
                    srt_path = save_file(result, 'srt')

                    # Mostrar texto resaltado
                    highlighted_text = search_and_highlight_text(result.get('text', ''), opciones_elegidas)
                    st.markdown(f"<pre>{highlighted_text}</pre>", unsafe_allow_html=True)
                        
                st.success("Procesamiento completado.")
    else:
        st.warning('Sube un archivo ZIP con audios para comenzar.')
