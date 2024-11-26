import streamlit as st

st.set_page_config(page_title='Inicio',
                   page_icon=':house:',
                   initial_sidebar_state='expanded')

if __name__ == "__main__":
    st.title('Transcripcion de Audio a Texto')
    st.page_link('pages/1_🎙️_Audio_Texto.py', icon='🎙️')
    st.page_link('pages/2_🎙️_Audio_Texto_Extenso.py', icon='🎙️')
    st.page_link('pages/3_✂️_Recortar_Audio.py', icon='✂️')
   



#https://github.com/openai/whisper
#https://nicobytes.com/blog/en/how-to-use-whisper/
#https://pypi.org/project/openai-whisper/