import streamlit as st
import base64
import os
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini AI
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("API key is missing. Set GEMINI_API_KEY in your environment.")
else:
    genai.configure(api_key=API_KEY)

# Function to encode image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Prompt for image analysis
sample_prompt = """
You are a medical practitioner and an expert in analyzing medical-related images for a reputed hospital.
You will be provided with images and must identify anomalies, diseases, or health issues. 
Provide detailed findings, next steps, and recommendations. 
Include a disclaimer: 'Consult with a doctor before making any decisions.' 
If the image is unclear, state 'Unable to determine based on the provided image.'
"""

# Session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'result' not in st.session_state:
    st.session_state.result = None

# Analyze image function
def analyze_image_with_gemini(filename: str):
    base64_image = encode_image(filename)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([
        sample_prompt,
        {"mime_type": "image/jpeg", "data": base64.b64decode(base64_image)}
    ])
    return response.text if response else "Analysis failed."

# Simplified explanation function
def chat_eli(query):
    eli5_prompt = "Explain the following information to a five-year-old:\n" + query
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(eli5_prompt)
    return response.text if response else "Explanation failed."

# ------------------ UI ------------------

# Custom page layout
st.set_page_config(
    page_title="Medical Image Analyzer",
    page_icon="🩺",
    layout="centered"
)

# Main Title
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🩺 Medical Image Analyzer with Gemini AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Upload a medical image to receive AI-powered insights</p>", unsafe_allow_html=True)
st.markdown("---")

# About section
with st.expander("ℹ️ About this App"):
    st.write("""
        This application uses **Google Gemini AI** to analyze medical images like X-rays or scans.
        It simulates a medical expert to identify possible issues, offer recommendations, and provide a simplified explanation if needed.
        **Note:** This tool is for educational/demo purposes only. Always consult a healthcare professional.
    """)

# File Upload Section
st.subheader("📤 Upload Medical Image")
uploaded_file = st.file_uploader("Choose a JPG, JPEG, or PNG image", type=["jpg", "jpeg", "png"])

# Show uploaded image
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state['filename'] = tmp_file.name
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)


# Analyze Button
st.markdown("### 🔍 Run AI Analysis")
if st.button("Analyze Image", use_container_width=True):
    if 'filename' in st.session_state and os.path.exists(st.session_state['filename']):
        with st.spinner("Analyzing image using Gemini AI..."):
            st.session_state['result'] = analyze_image_with_gemini(st.session_state['filename'])
        os.unlink(st.session_state['filename'])  # Delete temp file
        st.success("Analysis Complete ✅")

# Display Result
if st.session_state.get('result'):
    st.markdown("### 📑 Medical Findings")
    st.markdown(st.session_state['result'], unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 Want a simpler explanation for better understanding?")

    if st.radio("ELI5 - Explain Like I'm 5", ("No", "Yes"), horizontal=True) == "Yes":
        with st.spinner("Simplifying explanation..."):
            simplified = chat_eli(st.session_state['result'])
        st.markdown("### 🧸 Simplified Explanation")
        st.markdown(simplified, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; font-size: 12px; color: grey;'>Powered by Google Gemini | Built with ❤️ using Streamlit</p>", unsafe_allow_html=True)
