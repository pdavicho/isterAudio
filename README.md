# 🎙️ Speech To Text Toolkit

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io)
[![OpenAI Whisper](https://img.shields.io/badge/OpenAI-Whisper-green.svg)](https://github.com/openai/whisper)
[![Deploy](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B.svg)](https://isteraudio.streamlit.app/)


## 🏛️ **Instituto Universitario Rumiñahui**  
**Departamento de Investigación**

Sistema de herramientas de inteligencia artificial para procesamiento, análisis y transcripción de contenido de audio, desarrollada para facilitar el análisis de datos de audio de forma eficiente y profesional.

## ✨ Características Principales

- 🤖 **IA Avanzada**: Tecnología OpenAI Whisper de última generación
- 📦 **Procesamiento por lotes**: Manejo eficiente de múltiples archivos
- 🔍 **Análisis inteligente**: Detección y resaltado de palabras clave
- ⏱️ **Marcas de tiempo**: Sincronización precisa de texto y audio
- 🎨 **Interfaz moderna**: Diseño optimizado 
- 🛡️ **Procesamiento Streamlit Cloud**: Datos seguros y privados

## 🛠️ Herramientas Disponibles

### 1. 🎙️ Transcripción Individual
Convierte archivos de audio individuales a texto con análisis avanzado.

**Características:**
- Transcripción con modelo Whisper optimizado
- Búsqueda y resaltado de palabras clave
- Visualización con marcas de tiempo
- Filtrado inteligente de segmentos

### 2. 📦 Procesamiento Masivo (ZIP)
Procesa múltiples archivos de audio desde un archivo ZIP.

**Características:**
- Procesamiento por lotes desde ZIP
- Ordenamiento automático inteligente
- Análisis estadístico completo
- Descarga organizada de resultados
- Reportes detallados con métricas

### 3. ✂️ División Inteligente de Audio
Divide archivos de audio largos en segmentos optimizados.

**Características:**
- Detección inteligente de silencios
- Control de calidad y formato de salida
- Numeración automática ordenada
- Metadata completa incluida

## 🌐 Acceso Directo

**🚀 [Usar la aplicación en línea](https://isteraudio.streamlit.app/)**

*No requiere instalación - Acceso inmediato desde cualquier navegador*

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 
- pip (gestor de paquetes de Python)

### Instalación paso a paso

1. **Clona el repositorio:**
```bash
git clone [https://github.com/tu-usuario/audio-processing-toolkit.git](https://github.com/pdavicho/isterAudio.git)
```

2. **Crea un entorno virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecuta la aplicación:**
```bash
streamlit run Inicio.py
```

## 📦 Dependencias Principales

```txt
streamlit>=1.28.0
openai-whisper>=20231117
streamlit-tags>=1.2.8
pydub>=0.25.1
numpy>=1.21.0
torch>=2.0.0
torchaudio>=2.0.0
```

## 📁 Estructura del Proyecto

```
isterAudio/
├── 📄 README.md
├── 📄 requirements.txt
├── 📄 Inicio.py                          # Página principal
├── 📁 pages/
│   ├── 1_🎙️_Audio_Texto.py          # Transcripción individual
│   ├── 2_🎙️_Audio_Texto_Extenso.py  # Procesamiento masivo
│   └── 3_✂️_Recortar_Audio.py        # División de audio
└── 📄 packages.txt
```

## 🎯 Uso Rápido

### Para Transcripción Individual:
1. Navega a "🎙️ Transcripción Individual"
2. Sube tu archivo de audio (MP3, WAV, M4A, etc.)
3. Define palabras clave a buscar
4. Ejecuta la transcripción
5. Analiza resultados con marcas de tiempo

### Para Procesamiento Masivo:
1. Prepara un ZIP con múltiples archivos de audio
2. Navega a "📦 Procesamiento Masivo"
3. Sube el archivo ZIP
4. Configura palabras clave
5. Procesa todos los archivos automáticamente
6. Descarga resultados organizados

### Para División de Audio:
1. Navega a "✂️ División de Audio"
2. Sube archivo de audio largo
3. Configura duración de segmentos
4. Ajusta detección de silencios
5. Descarga segmentos numerados

## 🔧 Configuración Avanzada

### Modelos de Whisper Disponibles:
- `tiny`: Más rápido, menor precisión
- `base`: Equilibrio velocidad/precisión (por defecto)
- `small`: Mayor precisión, más lento
- `medium`: Alta precisión
- `large`: Máxima precisión

### Formatos de Audio Soportados:
- **Entrada**: MP3, WAV, M4A, FLAC, AAC, OGG
- **Salida**: MP3, WAV, M4A
- **Transcripción**: TXT, SRT, VTT, JSON

### Variables de Entorno (Opcional):
```bash
# Configurar modelo por defecto
export WHISPER_MODEL=base

# Configurar directorio temporal
export TEMP_DIR=/tmp/audio_processing
```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, sigue estos pasos:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías para Contribuir:
- Sigue el estilo de código existente
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación según sea necesario
- Respeta las convenciones de commit

## 🐛 Reportar Problemas

Si encuentras un bug o tienes una sugerencia:

1. Revisa que no esté ya reportado en [Issues](../../issues)
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Sistema operativo y versión de Python
   - Logs de error (si aplica)

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo de Desarrollo

**Instituto Universitario Rumiñahui**  
**Departamento de Investigación**

- **Desarrollado por**: Pablo David Minango Negrete
- **Supervisión Académica**: Departamento de Investigación
- **Soporte Técnico**: [pablo.minango@ister.edu.ec]

## 🙏 Agradecimientos

- [OpenAI](https://openai.com/) por el modelo Whisper
- [Streamlit](https://streamlit.io/) por el framework de aplicaciones web
- Comunidad académica del Instituto Rumiñahui

## 📞 Contacto y Soporte

- **Email**: [pablo.minango@ister.edu.ec]
- **Sitio Web**: [(https://ister.edu.ec/)]

## 📊 Estadísticas del Proyecto

![GitHub stars](https://img.shields.io/github/stars/pdavicho/audio-processing-toolkit?style=social)
![GitHub forks](https://img.shields.io/github/forks/pdavicho/audio-processing-toolkit?style=social)
![GitHub issues](https://img.shields.io/github/issues/pdavicho/audio-processing-toolkit)
![GitHub last commit](https://img.shields.io/github/last-commit/pdavicho/audio-processing-toolkit)

---

<div align="center">
  <p>🏛️ Instituto Universitario Rumiñahui | 🔬 Departamento de Investigación</p>
</div>
