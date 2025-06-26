import streamlit as st
from streamlit_tags import st_tags
import warnings
warnings.filterwarnings('ignore')

import whisper
from whisper.utils import get_writer
import tempfile
import os
import time
import re
from dataclasses import dataclass
from typing import List, Set, Tuple

st.set_page_config(page_title='Speech To Text', page_icon=':studio_microphone:')

# Inicializar session state
if 'transcription_complete' not in st.session_state:
    st.session_state.transcription_complete = False
if 'srt_path' not in st.session_state:
    st.session_state.srt_path = None
if 'keywords' not in st.session_state:
    st.session_state.keywords = []

@st.cache_resource
def load_model():
    return whisper.load_model('base')

model = load_model()

@dataclass
class SRTSegment:
    index: int
    start_time: str
    end_time: str
    text: str
    contains_keywords: bool = False

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

def opciones():
    keywords = st_tags(
        label='Escoger las palabras que desea analizar:',
        text='Presionar enter o añadir más',
        value=['emergencia', 'robo', 'drogas'],
        suggestions=['extorsion', 'robos', 'rescate', 'auxilio'],
        maxtags=10,
        key="opciones"
    )
    return keywords

def parse_srt_file(srt_file_path: str) -> List[SRTSegment]:
    """Parse SRT file into structured segments"""
    segments = []
    
    try:
        if not os.path.exists(srt_file_path):
            return segments
            
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
    except Exception as e:
        st.error(f"Error leyendo archivo SRT: {e}")
        return segments
    
    if not content:
        return segments
    
    # Split by double newlines to get individual subtitle blocks
    blocks = re.split(r'\n\s*\n', content)
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                index = int(lines[0])
                time_line = lines[1]
                text = '\n'.join(lines[2:])
                
                # Parse time line
                time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
                if time_match:
                    start_time, end_time = time_match.groups()
                    segments.append(SRTSegment(index, start_time, end_time, text))
            except (ValueError, IndexError):
                continue
    
    return segments

def highlight_keywords_in_text(text: str, keywords: List[str]) -> Tuple[str, Set[str]]:
    """Highlight keywords in text and return found terms"""
    if not text or not keywords:
        return text, set()
        
    highlighted_text = text
    found_terms = set()
    
    for keyword in keywords:
        if keyword and keyword.strip():  # Verificar que el keyword no esté vacío
            # Create a case-insensitive pattern that preserves original case
            try:
                pattern = re.compile(re.escape(keyword.strip()), re.IGNORECASE)
                if pattern.search(text):
                    found_terms.add(keyword.strip())
                    # Reemplazar de manera más segura
                    highlighted_text = pattern.sub(
                        lambda m: f'<mark style="background-color: #ffeb3b; color: #d32f2f; font-weight: bold;">{m.group()}</mark>',
                        highlighted_text
                    )
            except re.error:
                # Si hay error en regex, continuar con el siguiente keyword
                continue
    
    return highlighted_text, found_terms

def check_segment_for_keywords(segment: SRTSegment, keywords: List[str]) -> bool:
    """Check if segment contains any keywords"""
    if not segment or not segment.text or not keywords:
        return False
        
    text_lower = segment.text.lower()
    return any(keyword.lower().strip() in text_lower for keyword in keywords if keyword and keyword.strip())

def format_srt_segment_html(segment: SRTSegment, keywords: List[str]) -> str:
    """Format a single SRT segment as HTML"""
    try:
        highlighted_text, _ = highlight_keywords_in_text(segment.text, keywords)
        
        # Style the time stamp based on whether it contains keywords
        time_style = "color: #d32f2f; font-weight: bold;" if segment.contains_keywords else "color: #666;"
        
        return f"""
        <div style="margin: 15px 0; padding: 10px; border-left: 3px solid {'#d32f2f' if segment.contains_keywords else '#ccc'}; background-color: {'#fff3e0' if segment.contains_keywords else '#f9f9f9'};">
            <div style="font-size: 12px; {time_style} margin-bottom: 5px;">
                <strong>{segment.index}</strong> | {segment.start_time} → {segment.end_time}
            </div>
            <div style="font-size: 14px; line-height: 1.4;">
                {highlighted_text}
            </div>
        </div>
        """
    except Exception as e:
        # Si hay error formateando, devolver versión básica
        return f"""
        <div style="margin: 15px 0; padding: 10px; border-left: 3px solid #ccc; background-color: #f9f9f9;">
            <div style="font-size: 12px; color: #666; margin-bottom: 5px;">
                <strong>{segment.index}</strong> | {segment.start_time} → {segment.end_time}
            </div>
            <div style="font-size: 14px; line-height: 1.4;">
                {segment.text}
            </div>
        </div>
        """

def display_enhanced_srt(srt_file_path: str, keywords: List[str]):
    """Display SRT file with enhanced formatting and keyword highlighting"""
    try:
        if not srt_file_path or not os.path.exists(srt_file_path):
            st.error("Archivo SRT no encontrado")
            return
        
        segments = parse_srt_file(srt_file_path)
        
        if not segments:
            st.warning("No se encontraron segmentos en el archivo SRT")
            return
        
        # Check which segments contain keywords
        segments_with_keywords = []
        segments_without_keywords = []
        
        for segment in segments:
            try:
                if check_segment_for_keywords(segment, keywords):
                    segment.contains_keywords = True
                    segments_with_keywords.append(segment)
                else:
                    segments_without_keywords.append(segment)
            except Exception as e:
                # Si hay error procesando un segmento, agregarlo sin keywords
                segments_without_keywords.append(segment)
        
        # Display statistics
        total_segments = len(segments)
        keyword_segments = len(segments_with_keywords)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de segmentos", total_segments)
        with col2:
            st.metric("Con palabras clave", keyword_segments)
        with col3:
            st.metric("Porcentaje", f"{(keyword_segments/total_segments*100):.1f}%" if total_segments > 0 else "0%")
        
        # Display options con key única
        display_option = st.radio(
            "Mostrar:",
            ["Solo segmentos con palabras clave", "Todos los segmentos", "Solo segmentos sin palabras clave"],
            horizontal=True,
            key="display_filter_option"
        )
        
        # Select segments to display
        if display_option == "Solo segmentos con palabras clave":
            segments_to_display = segments_with_keywords
        elif display_option == "Solo segmentos sin palabras clave":
            segments_to_display = segments_without_keywords
        else:
            segments_to_display = segments
        
        if not segments_to_display:
            st.info("No hay segmentos para mostrar con la selección actual.")
            return
        
        # Display segments
        st.markdown("### Transcripción con marcas de tiempo")
        
        # Limitar número de segmentos mostrados para evitar problemas de rendimiento
        max_segments = 50
        if len(segments_to_display) > max_segments:
            st.warning(f"Mostrando los primeros {max_segments} segmentos de {len(segments_to_display)} total.")
            segments_to_display = segments_to_display[:max_segments]
        
        # Display segments one by one para mejor manejo de errores
        for segment in segments_to_display:
            try:
                html_content = format_srt_segment_html(segment, keywords)
                st.markdown(html_content, unsafe_allow_html=True)
            except Exception as e:
                # Si hay error con un segmento específico, mostrar versión simple
                st.write(f"**{segment.index}** | {segment.start_time} → {segment.end_time}")
                st.write(segment.text)
                st.write("---")
                
    except Exception as e:
        st.error(f"Error procesando archivo SRT: {e}")

def highlight_text_simple(text: str, keywords: List[str]) -> Tuple[str, Set[str]]:
    """Simple highlighting for the main text display"""
    if not text or not keywords:
        return text, set()
        
    highlighted_text = text
    found_terms = set()
    
    for keyword in keywords:
        if keyword and keyword.strip() and keyword.lower() in text.lower():
            found_terms.add(keyword)
            # Use case-insensitive replacement
            try:
                highlighted_text = re.sub(
                    re.escape(keyword.strip()), 
                    f'<mark style="background-color: #ffeb3b; color: #d32f2f; font-weight: bold;">{keyword.strip()}</mark>', 
                    highlighted_text, 
                    flags=re.IGNORECASE
                )
            except re.error:
                continue
    
    return highlighted_text, found_terms

if __name__ == "__main__":
    st.title('🎙️ Transcripción de Audio a Texto')
    st.markdown("---")
    
    audio_transcribir = upload_audio()

    if audio_transcribir is not None:
        st.success("✅ Audio cargado exitosamente")

        opciones_elegidas = opciones()
        
        # Guardar keywords en session state
        st.session_state.keywords = opciones_elegidas

        if opciones_elegidas:
            st.info(f"🔍 Términos seleccionados: **{', '.join(opciones_elegidas)}**")
        else:
            st.warning("⚠️ Selecciona al menos una palabra clave para analizar")

        if st.button('🚀 Ejecutar Transcripción', type="primary"):
            if not opciones_elegidas:
                st.error("Por favor selecciona al menos una palabra clave")
            else:
                try:
                    with st.status('Ejecutando transcripción...', expanded=True) as status:
                        start_time = time.time()
                        result = get_transcribe(audio=audio_transcribir)
                        end_time = time.time()
                        status.update(
                            label=f'✅ Transcripción completada en {end_time - start_time:.2f} segundos.', 
                            state='complete', 
                            expanded=False
                        )

                    texto = result.get('text', '')
                    
                    # Save files
                    save_file(result)
                    save_file(result, 'txt')
                    srt_path = save_file(result, 'srt')
                    
                    # Guardar en session state
                    st.session_state.srt_path = srt_path
                    st.session_state.transcription_complete = True
                    
                    # Highlight keywords in main text
                    highlighted_text, found_terms = highlight_text_simple(texto, opciones_elegidas)

                    if found_terms:
                        st.success(f"🎯 Encontradas las palabras: **{', '.join(found_terms)}**")
                        
                        # Main text display
                        st.markdown("### 📝 Texto transcrito")
                        st.markdown(highlighted_text, unsafe_allow_html=True)
                        
                    else:
                        st.error("❌ No se encontraron los términos especificados")
                        st.markdown("### 📝 Texto transcrito completo")
                        st.write(texto)
                        
                        with st.expander("💡 Sugerencias"):
                            st.write("• Verifica que las palabras estén escritas correctamente")
                            st.write("• Intenta con sinónimos o variaciones de las palabras")
                            st.write("• El audio podría no contener los términos buscados")

                except Exception as e:
                    st.error(f"Error durante la transcripción: {e}")
                    st.write("Por favor, intenta de nuevo o verifica que el archivo de audio sea válido.")
                finally:
                    # Clean up
                    try:
                        if audio_transcribir and os.path.exists(audio_transcribir):
                            os.remove(audio_transcribir)
                    except:
                        pass

    # Mostrar análisis SRT solo si la transcripción está completa
    if st.session_state.transcription_complete and st.session_state.srt_path:
        with st.expander("📋 Ver transcripción con marcas de tiempo", expanded=False):
            if st.session_state.keywords:
                display_enhanced_srt(st.session_state.srt_path, st.session_state.keywords)
            else:
                st.warning("No hay palabras clave seleccionadas para el análisis.")

    if not audio_transcribir:
        st.info('📁 Por favor, carga un archivo de audio para comenzar')
        
        # Instructions
        with st.expander("ℹ️ Instrucciones de uso"):
            st.write("""
            1. **Sube un archivo de audio** en formato WAV, MP3 o WAVE
            2. **Selecciona palabras clave** para buscar en la transcripción
            3. **Ejecuta la transcripción** y revisa los resultados
            4. **Explora la transcripción** con marcas de tiempo para ubicar contexto específico
            """)
            
        with st.expander("🔧 Características"):
            st.write("""
            • **Transcripción automática** usando modelo Whisper
            • **Búsqueda de palabras clave** con resaltado visual
            • **Marcas de tiempo precisas** para navegación fácil
            • **Filtrado inteligente** de segmentos relevantes
            • **Estadísticas de resultados** para análisis rápido
            """)
