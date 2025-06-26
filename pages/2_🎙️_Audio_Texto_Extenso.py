import streamlit as st
from streamlit_tags import st_tags
import zipfile
import os
import tempfile
import whisper
from whisper.utils import get_writer
import time
import warnings
import re
import shutil
from typing import List, Dict, Tuple
from dataclasses import dataclass
import io

warnings.filterwarnings('ignore')
st.set_page_config(page_title='Speech To Text - Batch ZIP', page_icon=':studio_microphone:', layout="wide")

# Inicializar session state
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = []
if 'current_temp_dir' not in st.session_state:
    st.session_state.current_temp_dir = None

@dataclass
class TranscriptionResult:
    filename: str
    filepath: str
    transcription: str
    duration: float
    processing_time: float
    found_keywords: List[str]
    word_count: int
    srt_path: str = None

@dataclass
class SRTSegment:
    index: int
    start_time: str
    end_time: str
    text: str
    contains_keywords: bool = False
    
@st.cache_resource
def load_whisper_model():
    """Load Whisper model with caching"""
    try:
        return whisper.load_model('base')
    except Exception as e:
        st.error(f"Error cargando modelo Whisper: {e}")
        return None

model = load_whisper_model()

def natural_sort_key(filename: str) -> tuple:
    """
    Genera una clave de ordenamiento natural para archivos con números
    Ejemplos:
    - audio_seg_1.mp3 -> (audio_seg_, 1, .mp3)
    - audio_seg_10.mp3 -> (audio_seg_, 10, .mp3)
    - segment_01.wav -> (segment_, 1, .wav)
    """
    import re
    
    # Dividir el nombre en partes texto-número-texto
    parts = re.split(r'(\d+)', filename.lower())
    
    # Convertir números a enteros para ordenamiento correcto
    result = []
    for part in parts:
        if part.isdigit():
            result.append(int(part))
        else:
            result.append(part)
    
    return tuple(result)

def sort_audio_files(audio_files: List[str]) -> List[str]:
    """
    Ordena archivos de audio de manera inteligente
    Prioriza ordenamiento numérico sobre alfabético
    """
    # Obtener solo los nombres de archivo para ordenar
    files_with_names = [(os.path.basename(f), f) for f in audio_files]
    
    # Ordenar usando la clave natural
    sorted_files = sorted(files_with_names, key=lambda x: natural_sort_key(x[0]))
    
    # Devolver solo las rutas completas
    return [full_path for _, full_path in sorted_files]

def get_audio_files_from_zip(zip_file) -> Tuple[List[str], str]:
    """Extract and validate audio files from ZIP"""
    try:
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        
        # Guardar archivo ZIP
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())
        
        # Extraer ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_dir)
        
        # Buscar archivos de audio (incluyendo en subdirectorios)
        audio_extensions = ('.wav', '.mp3', '.wave', '.m4a', '.flac', '.aac')
        audio_files = []
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith(audio_extensions):
                    full_path = os.path.join(root, file)
                    audio_files.append(full_path)
        
        # Ordenar archivos de manera inteligente
        audio_files = sort_audio_files(audio_files)
        
        return audio_files, temp_dir
        
    except zipfile.BadZipFile:
        st.error("El archivo no es un ZIP válido")
        return [], None
    except Exception as e:
        st.error(f"Error procesando ZIP: {e}")
        return [], None

def validate_audio_file(filepath: str) -> bool:
    """Validate if audio file can be processed"""
    try:
        # Verificar que el archivo existe y tiene tamaño > 0
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return False
        
        # Verificar extensión
        valid_extensions = ('.wav', '.mp3', '.wave', '.m4a', '.flac', '.aac')
        return filepath.lower().endswith(valid_extensions)
    except:
        return False

def get_transcribe_safe(audio_path: str, language: str = 'es') -> Dict:
    """Safe transcription with error handling"""
    try:
        if model is None:
            return {"error": "Modelo Whisper no disponible"}
        
        start_time = time.time()
        result = model.transcribe(audio=audio_path, language=language, verbose=False)
        processing_time = time.time() - start_time
        
        return {
            "text": result.get("text", ""),
            "segments": result.get("segments", []),
            "processing_time": processing_time,
            "error": None
        }
    except Exception as e:
        return {"error": f"Error transcribiendo: {str(e)}"}

def find_keywords_in_text(text: str, keywords: List[str]) -> List[str]:
    """Find which keywords are present in text"""
    found = []
    text_lower = text.lower()
    for keyword in keywords:
        if keyword and keyword.lower().strip() in text_lower:
            found.append(keyword)
    return found

def highlight_keywords(text: str, keywords: List[str]) -> str:
    """Highlight keywords in text"""
    highlighted = text
    for keyword in keywords:
        if keyword and keyword.strip():
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted = pattern.sub(
                lambda m: f'<mark style="background-color: #ffeb3b; color: #d32f2f; font-weight: bold;">{m.group()}</mark>',
                highlighted
            )
    return highlighted

def save_individual_files(result: Dict, filename: str, output_dir: str) -> Dict[str, str]:
    """Save transcription files for individual audio"""
    base_name = os.path.splitext(filename)[0]
    saved_files = {}
    
    try:
        # Guardar TXT
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result.get('text', ''))
        saved_files['txt'] = txt_path
        
        # Guardar SRT si hay segmentos
        if result.get('segments'):
            srt_path = os.path.join(output_dir, f"{base_name}.srt")
            srt_content = []
            for i, segment in enumerate(result['segments'], 1):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                text = segment['text'].strip()
                srt_content.extend([str(i), f"{start} --> {end}", text, ""])
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(srt_content))
            saved_files['srt'] = srt_path
        
    except Exception as e:
        st.warning(f"Error guardando archivos para {filename}: {e}")
    
    return saved_files

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def create_summary_report(results: List[TranscriptionResult], keywords: List[str]) -> str:
    """Create summary report of all transcriptions"""
    total_files = len(results)
    successful = len([r for r in results if r.transcription])
    total_duration = sum(r.duration for r in results)
    total_processing = sum(r.processing_time for r in results)
    total_words = sum(r.word_count for r in results)
    
    files_with_keywords = len([r for r in results if r.found_keywords])
    
    report = f"""# 📊 Reporte de Transcripción Masiva

## 📈 Estadísticas Generales
- **Total de archivos procesados:** {total_files}
- **Transcripciones exitosas:** {successful}
- **Duración total de audio:** {total_duration:.1f} segundos ({total_duration/60:.1f} minutos)
- **Tiempo total de procesamiento:** {total_processing:.1f} segundos
- **Total de palabras transcritas:** {total_words:,}
- **Archivos con palabras clave:** {files_with_keywords}

## 🔍 Palabras Clave Buscadas
{', '.join(keywords) if keywords else 'Ninguna'}

## 📄 Detalle por Archivo
"""
    
    for result in results:
        status = "✅" if result.transcription else "❌"
        keywords_found = ", ".join(result.found_keywords) if result.found_keywords else "Ninguna"
        
        report += f"""
### {status} {result.filename}
- **Duración:** {result.duration:.1f}s
- **Tiempo de procesamiento:** {result.processing_time:.1f}s
- **Palabras:** {result.word_count}
- **Palabras clave encontradas:** {keywords_found}
"""
    
    return report

def opciones():
    """Keyword selection interface"""
    keywords = st_tags(
        label='🏷️ Palabras clave para buscar en todas las transcripciones:',
        text='Presiona Enter o añade más términos',
        value=['emergencia', 'robo', 'drogas'],
        suggestions=['extorsión', 'robos', 'rescate', 'auxilio', 'accidente', 'violencia', 'ayuda'],
        maxtags=15,
        key="batch_keywords"
    )
    return keywords

def cleanup_temp_directory():
    """Clean up temporary directory"""
    if st.session_state.current_temp_dir and os.path.exists(st.session_state.current_temp_dir):
        try:
            shutil.rmtree(st.session_state.current_temp_dir)
            st.session_state.current_temp_dir = None
        except:
            pass

def parse_srt_file(srt_file_path: str) -> List[SRTSegment]:
    """Parse SRT file into structured segments"""
    segments = []
    
    try:
        if not os.path.exists(srt_file_path):
            return segments
            
        with open(srt_file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
    except Exception as e:
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

def create_safe_key(filename: str, suffix: str = "") -> str:
    """Create a safe key for Streamlit widgets"""
    import hashlib
    
    # Limpiar el nombre del archivo de caracteres especiales
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', filename)
    safe_name = safe_name[:30]  # Limitar longitud
    
    # Crear hash más corto y seguro
    hash_object = hashlib.md5(filename.encode())
    short_hash = hash_object.hexdigest()[:8]
    
    return f"{safe_name}_{short_hash}_{suffix}" if suffix else f"{safe_name}_{short_hash}"

def display_enhanced_srt_for_file(srt_file_path: str, keywords: List[str], filename: str):
    """Display SRT file with enhanced formatting and keyword highlighting"""
    try:
        if not srt_file_path or not os.path.exists(srt_file_path):
            st.warning(f"Archivo SRT no encontrado para {filename}")
            return
        
        segments = parse_srt_file(srt_file_path)
        
        if not segments:
            st.warning(f"No se encontraron segmentos en el archivo SRT de {filename}")
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
        
        # Usar un enfoque más seguro para el filtrado
        safe_key = create_safe_key(filename, "filter")
        
        # Inicializar en session state si no existe
        if safe_key not in st.session_state:
            st.session_state[safe_key] = "Solo segmentos con palabras clave" if keyword_segments > 0 else "Todos los segmentos"
        
        # Display options con mejor manejo de estado
        filter_options = ["Solo segmentos con palabras clave", "Todos los segmentos", "Solo segmentos sin palabras clave"]
        
        # Usar selectbox en lugar de radio para evitar conflictos
        display_option = st.selectbox(
            "Filtrar segmentos:",
            filter_options,
            index=filter_options.index(st.session_state[safe_key]),
            key=f"{safe_key}_select"
        )
        
        # Actualizar session state
        st.session_state[safe_key] = display_option
        
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
        st.markdown("#### 📋 Transcripción con marcas de tiempo")
        
        # Limitar número de segmentos mostrados para evitar problemas de rendimiento
        max_segments = 30  # Reducir para mejor rendimiento
        if len(segments_to_display) > max_segments:
            st.warning(f"Mostrando los primeros {max_segments} segmentos de {len(segments_to_display)} total.")
            segments_to_display = segments_to_display[:max_segments]
        
        # Mostrar segmentos usando container para mejor rendimiento
        segments_container = st.container()
        with segments_container:
            for i, segment in enumerate(segments_to_display):
                try:
                    html_content = format_srt_segment_html(segment, keywords)
                    st.markdown(html_content, unsafe_allow_html=True)
                except Exception as e:
                    # Si hay error con un segmento específico, mostrar versión simple
                    st.write(f"**{segment.index}** | {segment.start_time} → {segment.end_time}")
                    st.write(segment.text)
                    st.divider()
                
                # Evitar sobrecarga procesando en lotes
                if i > 0 and i % 10 == 0:
                    time.sleep(0.01)  # Pequeña pausa para evitar bloqueo
                
    except Exception as e:
        st.error(f"Error procesando archivo SRT para {filename}: {e}")
        st.info("Intenta recargar la página o procesar menos archivos a la vez.")

def highlight_keywords_in_text(text: str, keywords: List[str]) -> Tuple[str, List[str]]:
    """Highlight keywords in text and return found terms"""
    if not text or not keywords:
        return text, []
        
    highlighted_text = text
    found_terms = []
    
    for keyword in keywords:
        if keyword and keyword.strip():  # Verificar que el keyword no esté vacío
            # Create a case-insensitive pattern that preserves original case
            try:
                pattern = re.compile(re.escape(keyword.strip()), re.IGNORECASE)
                if pattern.search(text):
                    found_terms.append(keyword.strip())
                    # Reemplazar de manera más segura
                    highlighted_text = pattern.sub(
                        lambda m: f'<mark style="background-color: #ffeb3b; color: #d32f2f; font-weight: bold;">{m.group()}</mark>',
                        highlighted_text
                    )
            except re.error:
                # Si hay error en regex, continuar con el siguiente keyword
                continue
    
    return highlighted_text, found_terms

def create_download_zip(results: List[TranscriptionResult], keywords: List[str]) -> bytes:
    """Create ZIP file with all transcription results"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Agregar reporte resumen
        report = create_summary_report(results, keywords)
        zip_file.writestr("REPORTE_TRANSCRIPCION.md", report.encode('utf-8'))
        
        # Agregar archivos individuales
        for result in results:
            if result.transcription:
                base_name = os.path.splitext(result.filename)[0]
                
                # Archivo TXT
                zip_file.writestr(f"transcripciones/{base_name}.txt", result.transcription.encode('utf-8'))
                
                # Archivo SRT con marcas de tiempo
                if result.srt_path and os.path.exists(result.srt_path):
                    with open(result.srt_path, 'r', encoding='utf-8') as srt_file:
                        srt_content = srt_file.read()
                    zip_file.writestr(f"transcripciones_srt/{base_name}.srt", srt_content.encode('utf-8'))
                
                # Archivo con keywords resaltadas
                highlighted = highlight_keywords(result.transcription, keywords)
                zip_file.writestr(f"resaltados/{base_name}_resaltado.html", 
                                f"<html><body><pre>{highlighted}</pre></body></html>".encode('utf-8'))
    
    zip_buffer.seek(0)
    return zip_buffer.read()

# Interfaz principal
def main():
    st.title('🎙️ Transcripción Masiva desde ZIP')
    st.markdown("*Procesa múltiples archivos de audio desde un archivo ZIP*")
    st.markdown("---")
    
    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Información")
        st.write("**Formatos soportados:**")
        st.write("• WAV, MP3, WAVE")
        st.write("• M4A, FLAC, AAC")
        st.write("")
        st.write("**Características:**")
        st.write("• Procesamiento por lotes")
        st.write("• **Ordenamiento automático**")
        st.write("• Búsqueda de palabras clave")
        st.write("• **Marcas de tiempo precisas**")
        st.write("• **Filtrado inteligente SRT**")
        st.write("• Reporte detallado")
        st.write("• Descarga de resultados")
        st.write("")
        st.write("**🔢 Orden de procesamiento:**")
        st.write("Los archivos se procesan automáticamente en orden numérico:")
        st.code("audio_seg_1 → audio_seg_2 → audio_seg_10")
        
        if st.button("🗑️ Limpiar archivos temporales"):
            cleanup_temp_directory()
            st.session_state.processing_results = []
            st.success("Archivos limpiados")
    
    # Upload ZIP file
    zip_file = st.file_uploader(
        '📁 Sube un archivo ZIP con audios',
        type=['zip'],
        help="El ZIP puede contener archivos en subdirectorios"
    )
    
    if zip_file is not None:
        with st.spinner("Analizando archivo ZIP..."):
            audio_files, temp_dir = get_audio_files_from_zip(zip_file)
            st.session_state.current_temp_dir = temp_dir
        
        if not audio_files:
            st.error("❌ No se encontraron archivos de audio válidos en el ZIP")
            return
        
        st.success(f"✅ {len(audio_files)} archivos de audio encontrados y ordenados automáticamente")
        
        # Mostrar lista de archivos encontrados (ahora ordenados)
        with st.expander("📋 Archivos encontrados (en orden de procesamiento)", expanded=False):
            for i, audio_file in enumerate(audio_files, 1):
                filename = os.path.basename(audio_file)
                file_size = os.path.getsize(audio_file) / (1024 * 1024)  # MB
                is_valid = validate_audio_file(audio_file)
                status = "✅" if is_valid else "❌"
                st.write(f"**{i}.** {status} **{filename}** ({file_size:.2f} MB)")
        
        # Filtrar archivos válidos manteniendo el orden
        valid_files = [f for f in audio_files if validate_audio_file(f)]
        
        if not valid_files:
            st.error("❌ No hay archivos de audio válidos para procesar")
            return
        
        # Configuración de procesamiento
        col1, col2 = st.columns([2, 1])
        
        with col1:
            keywords = opciones()
            if keywords:
                st.info(f"🔍 Buscando: **{', '.join(keywords)}**")
        
        with col2:
            st.metric("Archivos válidos", len(valid_files))
            st.metric("Archivos inválidos", len(audio_files) - len(valid_files))
        
        # Procesamiento
        if st.button('🚀 Procesar todos los archivos', type="primary"):
            if not keywords:
                st.warning("⚠️ Agrega al menos una palabra clave para continuar")
                return
            
            results = []
            output_dir = tempfile.mkdtemp()
            
            # Progress bars
            overall_progress = st.progress(0)
            status_text = st.empty()
            
            # Contenedor para resultados
            results_container = st.container()
            
            start_total = time.time()
            
            for i, audio_file in enumerate(valid_files):
                filename = os.path.basename(audio_file)
                
                # Actualizar progreso
                progress = (i + 1) / len(valid_files)
                overall_progress.progress(progress)
                status_text.text(f"🎵 Procesando archivo {i+1}/{len(valid_files)}: {filename}")
                
                # Transcribir archivo
                transcription_result = get_transcribe_safe(audio_file)
                
                if transcription_result.get("error"):
                    st.error(f"❌ Error en archivo {i+1} ({filename}): {transcription_result['error']}")
                    continue
                
                # Procesar resultados
                text = transcription_result.get("text", "")
                found_keywords = find_keywords_in_text(text, keywords)
                word_count = len(text.split()) if text else 0
                
                # Guardar archivos individuales
                saved_files = save_individual_files(transcription_result, filename, output_dir)
                
                # Crear objeto resultado
                result = TranscriptionResult(
                    filename=filename,
                    filepath=audio_file,
                    transcription=text,
                    duration=len(transcription_result.get("segments", [])) * 1.0,  # Aproximado
                    processing_time=transcription_result.get("processing_time", 0),
                    found_keywords=found_keywords,
                    word_count=word_count,
                    srt_path=saved_files.get('srt')
                )
                
                results.append(result)
                
                # Mostrar resultado inmediato
                with results_container:
                    with st.expander(f"{'🎯' if found_keywords else '📄'} {filename}", expanded=bool(found_keywords)):
                        if found_keywords:
                            st.success(f"Palabras encontradas: **{', '.join(found_keywords)}**")
                            
                            # Usar tabs en lugar de expanders anidados
                            tab1, tab2 = st.tabs(["📝 Texto resaltado", "⏱️ Marcas de tiempo"])
                            
                            with tab1:
                                highlighted_text = highlight_keywords(text, keywords)
                                st.markdown(highlighted_text, unsafe_allow_html=True)
                            
                            with tab2:
                                if saved_files.get('srt'):
                                    display_enhanced_srt_for_file(saved_files['srt'], keywords, filename)
                                else:
                                    st.info("No hay archivo SRT disponible")
                        else:
                            st.write("No se encontraron palabras clave")
                            
                            # Usar tabs también para archivos sin keywords
                            tab1, tab2 = st.tabs(["📝 Texto completo", "⏱️ Marcas de tiempo"])
                            
                            with tab1:
                                st.write(text[:300] + "..." if len(text) > 300 else text)
                            
                            with tab2:
                                if saved_files.get('srt'):
                                    display_enhanced_srt_for_file(saved_files['srt'], keywords, filename)
                                else:
                                    st.info("No hay archivo SRT disponible")
            
            # Finalizar procesamiento
            total_time = time.time() - start_total
            st.session_state.processing_results = results
            
            overall_progress.progress(1.0)
            status_text.text(f"✅ Procesamiento completado en {total_time:.2f} segundos")
            
            # Mostrar resumen
            st.markdown("---")
            st.markdown("## 📊 Resumen del Procesamiento")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Archivos procesados", len(results))
            with col2:
                st.metric("Con palabras clave", len([r for r in results if r.found_keywords]))
            with col3:
                st.metric("Total palabras", sum(r.word_count for r in results))
            with col4:
                st.metric("Tiempo total", f"{total_time:.1f}s")
            
            # Botón de descarga
            if results:
                zip_data = create_download_zip(results, keywords)
                st.download_button(
                    label="📥 Descargar todos los resultados (ZIP)",
                    data=zip_data,
                    file_name=f"transcripciones_{int(time.time())}.zip",
                    mime="application/zip"
                )
    
    else:
        st.info('📁 Sube un archivo ZIP con audios para comenzar')
        
        # Instrucciones
        with st.expander("📖 Instrucciones de uso"):
            st.markdown("""
            ### 🚀 Cómo usar esta herramienta:
            
            1. **Prepara tu ZIP**: Coloca todos los archivos de audio en un ZIP
            2. **Sube el archivo**: Usa el botón de arriba para subir tu ZIP
            3. **Configura palabras clave**: Selecciona los términos que quieres encontrar
            4. **Procesa**: Inicia el procesamiento masivo (**se procesarán en orden numérico**)
            5. **Descarga**: Obtén todos los resultados en un ZIP organizado
            
            ### 📝 Formatos soportados:
            - **Audio**: WAV, MP3, WAVE, M4A, FLAC, AAC
            - **Estructura**: El ZIP puede tener subdirectorios
            
            ### 🔢 Ordenamiento inteligente:
            Los archivos se procesan en orden numérico automáticamente:
            - ✅ `audio_seg_1.mp3` → `audio_seg_2.mp3` → `audio_seg_10.mp3`
            - ✅ `segment_01.wav` → `segment_02.wav` → `segment_03.wav`
            - ✅ `parte1.mp3` → `parte2.mp3` → `parte11.mp3`
            - ✅ También funciona con: `audio1`, `seg_001`, `recording_5`, etc.
            
            ### 📊 Resultados incluyen:
            - Transcripciones completas en TXT
            - **Archivos SRT con marcas de tiempo precisas**
            - **Visualización interactiva** con filtrado de segmentos
            - Archivos con palabras clave resaltadas
            - Reporte detallado con estadísticas
            - Análisis por archivo individual
            
            ### ⏱️ Funcionalidades de marcas de tiempo:
            - **Navegación por segmentos** temporales
            - **Filtrado inteligente** (solo con keywords, todos, sin keywords)
            - **Estadísticas por archivo** (segmentos totales vs. relevantes)
            - **Resaltado visual** de segmentos importantes
            - **Descarga de archivos SRT** para usar en editores de video
            """)

if __name__ == "__main__":
    main()
