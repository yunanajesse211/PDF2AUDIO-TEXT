# basic libraries needed for app development
import streamlit as st
import PyPDF2
import pyttsx3
import tempfile
import os
import time
from docx import Document
from PIL import Image



# Setting the logo and title of the web application
img = Image.open('logo.png')
st.set_page_config(
    page_title="PDF2TEXT&AUDIO",
    page_icon=img,
    layout="centered",
    initial_sidebar_state="expanded",   
)



######***************BASIC FUNCTIONS NEEDED FOR BACKEND FUNCTIONALITIES OF THE APP******####

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_file = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_file.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error("problem with PDF uploaded.")

# Function to convert text to audio format
def text_to_audio(text, op_form, v_type, v_rate, p_of_c, p_level):
    try:
        engine = pyttsx3.init()
        if v_rate == "Slow":
            engine.setProperty('rate', 100)
        elif v_rate == "Fast":
            engine.setProperty('rate', 240)
        else: 
            engine.setProperty('rate', 150)
        
        # gender voice type
        voices = engine.getProperty('voices')
        if v_type == "Male":
            for voice in voices:
                if "David" in voice.name: 
                    engine.setProperty('voice', voice.id)
                    break
        elif v_type == "Female":
            for voice in voices:
                if "Zira" in voice.name: 
                    engine.setProperty('voice', voice.id)
                    break
        
        # saving file upon conversion
        suffix = f".{op_form.lower()}"
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_audio.close()
        p_of_c.progress(0) 
        p_level.text(f"Converting text to {op_form.upper()} audio... 0%")
        for i in range(1, 101, 10): 
            time.sleep(0.5) 
            p_of_c.progress(i)
            p_level.text(f"Converting text to {op_form.upper()} audio... {i}%")
        engine.save_to_file(text, temp_audio.name)
        engine.runAndWait()
        p_of_c.progress(100) 
        p_level.text(f"Converting text to {op_form.upper()} audio... 100%")
        return temp_audio.name
    except Exception as e:
        st.error("problem with PDF uploaded.")





# Function to save text as a DOC file with progress bar
def text_to_doc(text, p_of_c, p_level):
    try:
        temp_doc = tempfile.NamedTemporaryFile(delete=False, suffix=".doc", mode='w', encoding='utf-8')
        with open(temp_doc.name, 'w', encoding='utf-8') as file:
            for i in range(0, 101, 10): 
                time.sleep(0.1)
                p_of_c.progress(i)
                p_level.text(f"Saving DOC file... {i}%")
            file.write(text)
        return temp_doc.name
    except Exception as e:
        st.error("problem with PDF uploaded.")



#cleaning text to remove unwanted chars or bytes
def clean_text(input_text):
    try:
        #Remove null bytes and control characters from the input text.
        return ''.join(c for c in input_text if c.isprintable() or c in '\n\t ')
    except Exception as e:
        st.error("problem with PDF uploaded.")



# Function to save text as a DOCX file with progress bar
def text_to_docx(text, p_of_c, p_level):
    try:
        temp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        doc = Document()

        sanitized_text = clean_text(text)  # Sanitize the input text

        for i in range(0, 101, 10):  
            time.sleep(0.1)
            p_of_c.progress(i)
            p_level.text(f"Saving DOCX file... {i}%")

        doc.add_paragraph(sanitized_text)  # Add sanitized text to the paragraph
        doc.save(temp_docx.name)
        return temp_docx.name
    except Exception as e:
        st.error("problem with PDF uploaded.")
        



# Function to save text as a TXT file with progress bar
def text_to_txt(text, p_of_c, p_level):
    try:
        temp_txt = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
        with open(temp_txt.name, 'w', encoding='utf-8') as file:
            for i in range(0, 101, 10):  
                time.sleep(0.1)
                p_of_c.progress(i)
                p_level.text(f"Saving TXT file... {i}%")
            file.write(text)
        return temp_txt.name
    except Exception as e:
        st.error("problem with PDF uploaded.")
        st.error(e)




#######****************************MAIN APP INTERFACE********************########
try:
    st.image("logo.png", use_container_width=True)

    # dialog box to accept pdf
    uploaded_file = st.file_uploader("**Upload a PDF file**", type=["pdf"])


    # Displaying extracted text
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        if text.strip():
            st.subheader("Extracted Text")
            st.text_area("Text Preview", text, height=300, max_chars=None)
            
            # conversion formats for the app
            op_form = st.selectbox(
                "Choose the output format",
                ["MP3", "WAV", "DOC", "DOCX", "TXT"]
            )
            
            if op_form in ["MP3", "WAV"]:
                # more audio chocies for users
                v_type = st.selectbox("Choose Voice Type", ["Male", "Female"])
                v_rate = st.selectbox("Choose Speech voice speed", ["Slow", "Normal", "Fast"])
            
            if st.button("Convert"):
                p_of_c = st.progress(0)
                p_level = st.empty()
                if op_form in ["MP3", "WAV"]:
                    output_file_path = text_to_audio(text, op_form, v_type, v_rate, p_of_c, p_level)
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
                p_level.empty()
                
                
                
                # making the file downloadable 
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
        
        
        

    # Removing stremlit menu side bar for app
    hide = """
    <style>
        #MainMenu{visibility:hidden}
        footer{visibility:hidden}
    </style>
    """
    st.markdown(hide, unsafe_allow_html=True)
except Exception as e:
    st.error("Sorry an error occured app can't Load some files....")
    st.error(e)
