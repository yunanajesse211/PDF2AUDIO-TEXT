import streamlit as st
import PyPDF2
import tempfile
import os
import time
from docx import Document
from PIL import Image
from gtts import gTTS
from time import sleep

# Setting the logo and title of the web application
img = Image.open('logo.png')
st.set_page_config(
    page_title="PDF2TEXT&AUDIO",
    page_icon=img,
    layout="centered",
    initial_sidebar_state="expanded",
)

######*************** BASIC FUNCTIONS NEEDED FOR BACKEND FUNCTIONALITIES OF THE APP ******####

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_file = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_file.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text
        return text.strip()
    except Exception:
        # Return empty text in case of error, without logging it to the user
        return ""

# Function to convert text to audio using gTTS with retries
def gtts_text_to_audio(text, lang, suffix, p_of_c, p_level):
    retries = 5  # Number of retries in case of failure
    attempt = 0

    while attempt < retries:
        try:
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            
            for i in range(0, 101, 10):  
                time.sleep(0.1) 
                p_of_c.progress(i)  
                p_level.text(f"Converting text to audio. Please be patient... {i}%")  
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_audio.name)

            p_of_c.progress(100)  
            p_level.text("Conversion complete!")

            return temp_audio.name
        except Exception:
            # Retry if gTTS fails, without informing the user
            if attempt < retries - 1:
                attempt += 1
                sleep(2 ** attempt)  # Exponential backoff: wait longer for each retry
            else:
                return None
    return None

# Function to save text as a DOC file
def text_to_doc(text, p_of_c, p_level):
    try:
        temp_doc = tempfile.NamedTemporaryFile(delete=False, suffix=".doc", mode="w", encoding="utf-8")
        with open(temp_doc.name, "w", encoding="utf-8") as file:
            for i in range(0, 101, 10):
                time.sleep(0.1)
                p_of_c.progress(i)
                p_level.text(f"Saving DOC file... {i}%")
            file.write(text)
        return temp_doc.name
    except Exception:
        # Return None silently if there's an error
        return None

# Function to save text as a DOCX file
def text_to_docx(text, p_of_c, p_level):
    try:
        temp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        doc = Document()

        for i in range(0, 101, 10):
            time.sleep(0.1)
            p_of_c.progress(i)
            p_level.text(f"Saving DOCX file... {i}%")

        doc.add_paragraph(text)
        doc.save(temp_docx.name)
        return temp_docx.name
    except Exception:
        # Return None silently if there's an error
        return None

# Function to save text as a TXT file
def text_to_txt(text, p_of_c, p_level):
    try:
        temp_txt = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
        with open(temp_txt.name, "w", encoding="utf-8") as file:
            for i in range(0, 101, 10):
                time.sleep(0.1)
                p_of_c.progress(i)
                p_level.text(f"Saving TXT file... {i}%")
            file.write(text)
        return temp_txt.name
    except Exception:
        return None

#######**************************** MAIN APP INTERFACE ********************########
try:
    st.image("logo.png", use_container_width=True)

    # Dialog box to accept PDF
    uploaded_file = st.file_uploader("**Upload a PDF file**", type=["pdf"])

    # Displaying extracted text
    if uploaded_file is not None:
        # Check if the app has already processed this file to avoid reprocessing
        if 'text' not in st.session_state:
            st.session_state.text = extract_text_from_pdf(uploaded_file)
        
        text = st.session_state.text
        if text:
            st.subheader("Extracted Text")
            st.text_area("Text Preview", text, height=300)

            # Conversion formats for the app
            op_form = st.selectbox(
                "Choose the output format",
                ["MP3", "WAV", "DOC", "DOCX", "TXT"]
            )

            # Show language selection only if audio format is selected
            if op_form in ["MP3", "WAV"]:
                lang_dict = {
                    'English (Australia)': 'en',
                    'English (United Kingdom)': 'en',
                    'English (United States)': 'en',
                    'English (Canada)': 'en',
                    'English (India)': 'en',
                    'English (Ireland)': 'en',
                    'English (South Africa)': 'en',
                    'English (Nigeria)': 'en',
                    'French (Canada)': 'fr',
                    'French (France)': 'fr',
                    'Mandarin (China Mainland)': 'zh-CN',
                    'Mandarin (Taiwan)': 'zh-TW',
                    'Portuguese (Brazil)': 'pt',
                    'Portuguese (Portugal)': 'pt',
                    'Spanish (Mexico)': 'es',
                    'Spanish (Spain)': 'es',
                    'Spanish (United States)': 'es'
                }
                language_choice = st.selectbox("Choose the language for audio conversion", list(lang_dict.keys()))
                lang_abbr = lang_dict[language_choice]  # Get the language abbreviation for gTTS
            else:
                lang_abbr = 'en'  # Default to English if no audio is selected

            if st.button("Convert"):
                p_of_c = st.progress(0)
                p_level = st.empty()

                if op_form in ["MP3", "WAV"]:
                    # Use gTTS for audio conversion
                    output_file_path = gtts_text_to_audio(
                        text, lang=lang_abbr, suffix=f".{op_form.lower()}", p_of_c=p_of_c, p_level=p_level
                    )
                    mime_type = f"audio/{op_form.lower()}"
                    download_label = f"Download {op_form.upper()}"

                elif op_form == "DOC":
                    output_file_path = text_to_doc(text, p_of_c, p_level)
                    mime_type = "application/msword"
                    download_label = "Download DOC"

                elif op_form == "DOCX":
                    output_file_path = text_to_docx(text, p_of_c, p_level)
                    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    download_label = "Download DOCX"

                elif op_form == "TXT":
                    output_file_path = text_to_txt(text, p_of_c, p_level)
                    mime_type = "text/plain"
                    download_label = "Download TXT"

                # Making the file downloadable
                if output_file_path:
                    with open(output_file_path, "rb") as file:
                        file_data = file.read()
                        st.download_button(
                            label=download_label,
                            data=file_data,
                            file_name=f"converted.{output_file_path.split('.')[-1]}",
                            mime=mime_type
                        )

                    # Cleanup temporary file
                    os.unlink(output_file_path)
        else:
            st.error("No text found in the uploaded PDF.")
    else:
        st.info("**Please upload a PDF file to get started.**")

    # Hide Streamlit menu and footer
    hide = """
    <style>
        #MainMenu{visibility:hidden}
        footer{visibility:hidden}
    </style>
    """
    st.markdown(hide, unsafe_allow_html=True)
except Exception:
    # Ensure no errors are shown to the user
    st.warning("An error occurred, but we are handling it gracefully. Please try again.")
