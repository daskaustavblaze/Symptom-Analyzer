import streamlit as st
import base64
import os
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai
 
# Load environment variables
load_dotenv()
 
# Configure Gemini AI with API Key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("API key is missing. Set GEMINI_API_KEY in your environment.")
else:
    genai.configure(api_key=API_KEY)
 
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
 
sample_prompt = """You are a medical practitioner and an expert in analyzing medical-related images for a reputed hospital.
You will be provided with images and must identify anomalies, diseases, or health issues. Provide detailed findings, next steps, and recommendations.
You must also include a disclaimer: 'Consult with a doctor before making any decisions.'
If the image is unclear, state 'Unable to determine based on the provided image.'"""
 
# Initialize session state variables
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'result' not in st.session_state:
    st.session_state.result = None
 
def analyze_image_with_gemini(filename: str):
    base64_image = encode_image(filename)
   
    model = genai.GenerativeModel("gemini-1.5-flash")  # Updated model
    response = model.generate_content([
        sample_prompt,
        {"mime_type": "image/jpeg", "data": base64.b64decode(base64_image)}
    ])
   
    return response.text if response else "Analysis failed."
 
def chat_eli(query):
    eli5_prompt = "Explain the following information to a five-year-old: \n" + query
    model = genai.GenerativeModel("gemini-1.5-flash")  # Updated model
    response = model.generate_content(eli5_prompt)
    return response.text if response else "Explanation failed."
 
st.title("Medical Help using Gemini AI")
 
with st.expander("About this App"):
    st.write("Upload an image to get a medical analysis using Gemini AI.")
 
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
 
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state['filename'] = tmp_file.name
   
    st.image(uploaded_file, caption='Uploaded Image')
 
if st.button('Analyze Image'):
    if 'filename' in st.session_state and os.path.exists(st.session_state['filename']):
        st.session_state['result'] = analyze_image_with_gemini(st.session_state['filename'])
        st.markdown(st.session_state['result'], unsafe_allow_html=True)
        os.unlink(st.session_state['filename'])  # Delete temp file
 
if 'result' in st.session_state and st.session_state['result']:
    st.info("Optionally, get a simplified explanation.")
    if st.radio("ELI5 - Explain Like I'm 5", ('No', 'Yes')) == 'Yes':
        simplified_explanation = chat_eli(st.session_state['result'])
        st.markdown(simplified_explanation, unsafe_allow_html=True)