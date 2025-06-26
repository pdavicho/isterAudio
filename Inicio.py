import streamlit as st
from datetime import datetime
import base64

st.set_page_config(
    page_title='Herramientas de Audio IA - Instituto Rumiñahui',
    page_icon='🎙️',
    layout='wide',
    initial_sidebar_state='expanded'
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        margin: 2rem 0;
        padding: 1rem;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    .logo-placeholder {
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        color: #667eea;
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    .stats-container {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .tool-link {
        text-decoration: none;
        display: block;
        width: 100%;
    }
    
    .footer-info {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 2rem;
        text-align: center;
        border-top: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def create_tool_card(title, description, icon, page_link, features):
    """Crear tarjeta de herramienta mejorada"""
    with st.container():
        st.markdown(f"""
        <div class="feature-card">
            <h3>{icon} {title}</h3>
            <p style="color: #666; margin-bottom: 1rem;">{description}</p>
            <div style="margin-bottom: 1rem;">
                <strong>Características principales:</strong>
                <ul style="margin: 0.5rem 0;">
                    {''.join([f'<li>{feature}</li>' for feature in features])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.page_link(page_link, label=f"🚀 Acceder a {title}", icon=icon, use_container_width=True)
        st.markdown("---")

if __name__ == "__main__":
    # Header principal con logo único
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ Herramientas de Inteligencia Artificial para Audio</h1>
        <h3>Instituto Universitario Rumiñahui | Departamento de Investigación</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sección de logo centrado usando columnas de Streamlit
    st.markdown('<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">', unsafe_allow_html=True)
    
    # Logo centrado
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:  # Columna central
        try:
            st.image("universitarioRU.png", width=150)
        except FileNotFoundError:
            st.markdown("""
            <div style="width: 150px; height: 150px; background: rgba(255,255,255,0.9); 
                        border-radius: 15px; display: flex; align-items: center; 
                        justify-content: center; font-size: 60px; color: #667eea; 
                        border: 3px solid rgba(255,255,255,0.3); margin: 0 auto;">
                🏛️
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; color: white; padding: 1rem;">
            <h2 style="margin: 0.5rem 0; color: white;">Instituto Universitario Rumiñahui</h2>
            <h4 style="margin: 0.5rem 0; color: white; opacity: 0.9;">Departamento de Investigación</h4>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">Excelencia Académica e Innovación Tecnológica</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Descripción del proyecto
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🚀 Bienvenido al Centro de Herramientas de Audio IA
        
        Esta plataforma integra tecnologías de inteligencia artificial de vanguardia para el procesamiento 
        y análisis de contenido de audio. Desarrollada por el **Departamento de Investigación** del 
        **Instituto Universitario Rumiñahui**, estas herramientas están diseñadas para facilitar la 
        transcripción, análisis y procesamiento de audio de manera eficiente y profesional.
        
        ### 🎯 Objetivos del Proyecto:
        - **Democratizar el acceso** a tecnologías de IA para audio
        - **Facilitar la investigación** académica y científica  
        - **Optimizar procesos** de transcripción y análisis
        - **Promover la innovación** en el procesamiento de audio
        """)
    
    with col2:
        st.markdown("""
        <div class="stats-container">
            <h3>📊 Estadísticas del Sistema</h3>
            <div style="display: flex; justify-content: space-around; margin: 1rem 0;">
                <div>
                    <h2 style="margin: 0;">3</h2>
                    <p style="margin: 0;">Herramientas</p>
                </div>
                <div>
                    <h2 style="margin: 0;">99%</h2>
                    <p style="margin: 0;">Precisión</p>
                </div>
                <div>
                    <h2 style="margin: 0;">24/7</h2>
                    <p style="margin: 0;">Disponible</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("""
        💡 **Nota Importante:**
        
        Todas las herramientas utilizan modelos de IA de última generación 
        y están optimizadas para el entorno académico y de investigación.
        """)
    
    st.markdown("---")
    
    # Herramientas disponibles
    st.markdown("## 🛠️ Herramientas Disponibles")
    
    # Herramienta 1: Audio a Texto Individual
    create_tool_card(
        title="Transcripción Individual",
        description="Convierte archivos de audio individuales a texto con análisis de palabras clave y marcas de tiempo precisas.",
        icon="🎙️",
        page_link="pages/1_🎙️_Audio_Texto.py",
        features=[
            "Transcripción con modelo Whisper optimizado",
            "Búsqueda y resaltado de palabras clave", 
            "Visualización con marcas de tiempo",
            "Filtrado inteligente de segmentos",
            "Exportación en múltiples formatos"
        ]
    )
    
    # Herramienta 2: Procesamiento Masivo
    create_tool_card(
        title="Transcripción Masiva (ZIP)",
        description="Procesa múltiples archivos de audio desde un ZIP, ideal para análisis de grandes volúmenes de contenido.",
        icon="🎙️",
        page_link="pages/2_🎙️_Audio_Texto_Extenso.py",
        features=[
            "Procesamiento por lotes desde ZIP",
            "Ordenamiento automático inteligente",
            "Análisis estadístico completo",
            "Descarga organizada de resultados",
            "Reporte detallado con métricas"
        ]
    )
    
    # Herramienta 3: División de Audio
    create_tool_card(
        title="División Inteligente de Audio",
        description="Divide archivos de audio largos en segmentos optimizados con detección automática de silencios.",
        icon="✂️",
        page_link="pages/3_✂️_Recortar_Audio.py",
        features=[
            "Detección inteligente de silencios",
            "Control de calidad y formato de salida",
            "Efectos profesionales (fade in/out)",
            "Numeración automática ordenada",
            "Metadata completa incluida"
        ]
    )
    
    # Sección de tecnologías y metodología
    st.markdown("## 🔬 Tecnologías y Metodología")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 Inteligencia Artificial
        - **OpenAI Whisper**: Modelo de transcripción de última generación
        - **Procesamiento en tiempo real**: Optimizado para eficiencia
        - **Múltiples idiomas**: Soporte especializado para español
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Análisis de Datos
        - **Detección de patrones**: Identificación automática de contenido relevante
        - **Estadísticas avanzadas**: Métricas detalladas de procesamiento
        - **Visualización interactiva**: Interfaces intuitivas y profesionales
        """)
    
    with col3:
        st.markdown("""
        ### 🛡️ Calidad y Seguridad
        - **Procesamiento local**: Datos seguros y privados
        - **Validación robusta**: Control de errores y recuperación
        - **Estándares académicos**: Calidad de investigación
        """)
    
    # Casos de uso
    st.markdown("## 📋 Casos de Uso Académicos")
    
    use_cases = [
        {
            "title": "📚 Investigación Cualitativa",
            "description": "Transcripción de entrevistas, grupos focales y sesiones de investigación",
            "icon": "🎓"
        },
        {
            "title": "📺 Análisis de Medios",
            "description": "Procesamiento de contenido audiovisual para estudios de comunicación",
            "icon": "📡"
        },
        {
            "title": "🏛️ Archivo Histórico",
            "description": "Digitalización y transcripción de grabaciones históricas y testimonios",
            "icon": "📜"
        },
        {
            "title": "📖 Educación Digital",
            "description": "Creación de contenido accesible y material educativo transcrito",
            "icon": "💻"
        }
    ]
    
    cols = st.columns(2)
    for i, use_case in enumerate(use_cases):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="feature-card">
                <h4>{use_case['icon']} {use_case['title']}</h4>
                <p style="color: #666; margin: 0;">{use_case['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer con información institucional
    st.markdown(f"""
    <div class="footer-info">
        <h4>📍 Instituto Universitario Rumiñahui</h4>
        <p><strong>Departamento de Investigación</strong> | Ciencia, Tecnología e Innovación</p>
        <p>🌐 Comprometidos con la excelencia académica y el desarrollo tecnológico</p>
        <p style="color: #666; font-size: 0.9em; margin-top: 1rem;">
            Última actualización: {datetime.now().strftime("%d/%m/%Y")} | 
            Versión del sistema: 2.0 | 
            Desarrollado con ❤️ para la comunidad académica
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Nota sobre las imágenes (puedes reemplazar con las reales)
    with st.expander("ℹ️ Instrucciones para agregar logos institucionales"):
        st.markdown("""
        ### 📸 Para agregar los logos reales:
        
        1. **Guarda las imágenes** en una carpeta `assets/` en tu proyecto:
           - `assets/logo_ruminhahui.png`
           - `assets/logo_investigacion.png`
        
        2. **Reemplaza los placeholders** 🏛️ y 🔬 con:
        ```python
        # En lugar de <div class="logo-placeholder">🏛️</div>
        st.image("assets/logo_ruminhahui.png", width=120)
        
        # En lugar de <div class="logo-placeholder">🔬</div>
        st.image("assets/logo_investigacion.png", width=120)
        ```
        
        3. **Formatos recomendados**: PNG con fondo transparente, 120x120px para mejor visualización
        
        ### 🎨 Personalización adicional:
        - Modifica los colores en el CSS para usar los colores institucionales
        - Ajusta los textos según las especificaciones del instituto
        - Agrega información de contacto específica si es necesario
        """)
