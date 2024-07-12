import os
import streamlit as st
import fitz
import pytesseract
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as gen_ai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)
gemini_model = gen_ai.GenerativeModel('gemini-pro')

def extract_text_from_pdf(file):
    text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_image(file):
    text = ""
    try:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    except Exception as e:
        st.error(f"Error extracting text from image: {e}")
    return text

def analyze_text(text):
    try:
        gemini_prompt = f"Analyze the following medical report:\n{text}"
        gemini_response = gemini_model.generate_content(gemini_prompt)
        analysis = gemini_response.parts[0].text
    except Exception as e:
        st.error(f"Error analyzing text with Gemini: {e}")
        analysis = ""
    return analysis

st.title("Medical Report Analyzer")

uploaded_file = st.file_uploader("Upload your medical report", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    st.write(f"Uploaded file type: {file_type}")

    text = ""
    if file_type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif file_type in ["image/png", "image/jpeg"]:
        st.image(uploaded_file, caption="Uploaded File", use_column_width=True)
        text = extract_text_from_image(uploaded_file)

    if text:
        st.success("Now click 'Analyse' to get the report analysis.")
        
        analyze = st.button('Analyse')
        if analyze:
            with st.spinner("Analysing"):
                analysis = analyze_text(text)
            if analysis:
                st.write("Analysis:")
                st.write(analysis)
            else:
                st.error("Failed to analyze the text.")
    else:
        st.error("No text extracted from the uploaded file.")
