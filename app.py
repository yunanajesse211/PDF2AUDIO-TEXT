
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
        st.error("Problem reading the PDF file.")
        return ""

# Function to convert text to audio using gTTS with retries
def gtts_text_to_audio(text, lang, suffix, p_of_c, p_level):
    retries = 5  # Number of retries in case of failure
    attempt = 0

    while attempt < retries:
        try:
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            
            # Simulate progress with actual steps for the conversion
            for i in range(0, 101, 10):  # Update progress bar in increments
                time.sleep(0.1)  # Simulate processing time
                p_of_c.progress(i)  # Update progress bar
                p_level.text(f"Converting text to audio... {i}%")  # Update progress text

            # Create TTS and save the file
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_audio.name)

            # Final progress update
            p_of_c.progress(100)  # Set progress bar to 100% once conversion is done
            p_level.text("Conversion complete!")

            return temp_audio.name
        except Exception as e:
            if '429' in str(e):  # Check for Too Many Requests error
                attempt += 1
                sleep(2 ** attempt)  # Exponential backoff: wait longer for each retry
                
            else:
                st.error(f"An error occurred with gTTS: {e}")
                break
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
        st.error("Problem saving the DOC file.")
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
        st.error("Problem saving the DOCX file.")
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
        st.error("Problem saving the TXT file.")
        return None

#######**************************** MAIN APP INTERFACE ********************########
try:
    st.image("logo.png", use_container_width=True)

    # Dialog box to accept PDF
    uploaded_file = st.file_uploader("**Upload a PDF file**", type=["pdf"])

    # Displaying extracted text
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        if text:
            st.subheader("Extracted Text")
            st.text_area("Text Preview", text, height=300)

            # Conversion formats for the app
            op_form = st.selectbox(
                "Choose the output format",
                ["MP3", "WAV", "DOC", "DOCX", "TXT"]
            )

            if st.button("Convert"):
                p_of_c = st.progress(0)
                p_level = st.empty()

                if op_form in ["MP3", "WAV"]:
                    # Use gTTS for audio conversion
                    output_file_path = gtts_text_to_audio(
                        text, lang="en", suffix=f".{op_form.lower()}", p_of_c=p_of_c, p_level=p_level
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
except Exception as e:
    st.error(f"An error occurred within app!")
