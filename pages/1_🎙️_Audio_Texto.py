import streamlit as st
from streamlit_tags import st_tags
import warnings
warnings.filterwarnings('ignore')

import whisper
from whisper.utils import get_writer
import tempfile
import os
import time

st.set_page_config(page_title='Speech To Text', page_icon=':studio_microphone:')

model = whisper.load_model('base')

def upload_audio():
    file = st.file_uploader('Subir un audio', type=['.wav', '.mp3', '.wave'])
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(file.read())
            return tmp_file.name

def get_transcribe(audio: str, language: str = 'es'):
    return model.transcribe(audio=audio, language=language, verbose=True)

def save_file(results, format='tsv'):
    writer = get_writer(format, './')
    writer(results, f'transcribe.{format}')
    if format == 'srt':
        return f'transcribe.{format}'


# def opciones():
#    options = st.multiselect('Escoger las palabras que desea analizar', ['Auxilio', 'Rescate', 'Drogas', 'Robo', 'robos', 'extorsion', 'emergencia'], key='seleccion1')
#    return options

def opciones():
    keywords = st_tags(label='Escoger las palabras que desea analizar :',
                           text='Presionar enter o anadir mas',
                           value=['emergencia', 'robo', 'drogas'],
                           suggestions=['extorsion', 'robos', 'rescate'],
                           maxtags=5,
                           key="opciones")
        
    return keywords

def search_and_highlight_text(text, search_terms):
    highlighted_text = text
    found_terms = set()
    highlighted_times = set()

    for term in search_terms:
        if term.lower() in highlighted_text.lower():
            found_terms.add(term)
            highlighted_text = highlighted_text.replace(term, f'<span style="color:red; text-decoration: underline;">{term}</span>')
            highlighted_text = highlighted_text.replace(term.capitalize(), f'<span style="color:red; text-decoration: underline;">{term.capitalize()}</span>')
            highlighted_text = highlighted_text.replace(term.upper(), f'<span style="color:red; text-decoration: underline;">{term.upper()}</span>')

     # Resalta tiempos en rojo
    import re
    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})')
    time_matches = time_pattern.finditer(highlighted_text)

    for match in time_matches:
        time_block = match.group(0)
        start_index = match.start()
        end_index = match.end()
        # Encuentra el texto asociado con el bloque de tiempo
        time_text = highlighted_text[end_index:].split('\n\n', 1)[0]
        if any(term.lower() in time_text.lower() for term in search_terms):
            highlighted_text = highlighted_text[:start_index] + f'<span style="color:red;">{time_block}</span>' + highlighted_text[end_index:]
            highlighted_times.add(time_block)

    return highlighted_text, found_terms, highlighted_times

def display_srt_file(srt_file_path, search_terms):
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        formatted_text = ""
        for line in lines:
            formatted_text += line
            if line.strip() == "":
                formatted_text += "\n"  # Add an extra blank line for better readability
        
        # Highlight search terms and times in the entire formatted text
        highlighted_text, found_terms, highlighted_times = search_and_highlight_text(formatted_text, search_terms)
        st.markdown(f"<pre>{highlighted_text}</pre>", unsafe_allow_html=True)
        

if __name__ == "__main__":
    st.title('Transcripción de Audio a Texto')
    audio_transcribir = upload_audio()

    if audio_transcribir is not None:
        st.success("Audio Cargado")

        opciones_elegidas = opciones()

        st.write(f"Términos seleccionados: {', '.join(opciones_elegidas)}")

        if st.button('Ejecutar'):
            with st.status('Ejecutando...', expanded=True) as status:
                start_time = time.time()
                result = get_transcribe(audio=audio_transcribir)
                end_time = time.time()
                status.update(label=f'Transcripción lista en {end_time - start_time:.2f} segundos.', state='complete', expanded=False)

            texto = result.get('text', '')
            save_file(result)
            save_file(result, 'txt')
            srt_path = save_file(result, 'srt')
            highlights, found_terms, highlights_times = search_and_highlight_text(texto, opciones_elegidas)

            if found_terms:
                st.markdown(highlights, unsafe_allow_html=True)
                with st.popover("Texto con tiempo"):
                    display_srt_file(srt_path, opciones_elegidas)

            else:
                with st.container():
                    st.error("Términos no encontrados.")
                    st.write("Por favor, intente con diferentes términos.")
                    st.button("Cerrar", key="close_popup")

            os.remove(audio_transcribir)

    else:
        st.warning('Cargar un audio')