import streamlit as st
from PIL import Image
import pytesseract
import os
import base64
from openai import OpenAI # <--- Yahan bhi fix
from dotenv import load_dotenv

# API Key load karna
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter Client initialize karna
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
except Exception as e:
    # st.error(f"Error initializing OpenAI client: {e}") # Streamlit error se bachne ke liye print use karein
    client = None

# --- Helper Function: Image ko Base64 mein Encode karna ---
def encode_image_to_base64(image_path):
    """Image file path ko Base64 string mein badalta hai."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        # st.error(f"Error encoding image: {e}")
        return None

# --- 1. OCR (Text Extraction) Function ---
def perform_ocr(image_file):
    st.info("Performing OCR (Optical Character Recognition)...")
    try:
        img = Image.open(image_file)
        extracted_text = pytesseract.image_to_string(img, lang='ara+eng')
        
        if extracted_text.strip():
            return extracted_text.strip()
        else:
            return "OCR failed to extract clear text. The image might be blurry or handwritten."
            
    except pytesseract.TesseractNotFoundError:
        st.error("Tesseract not found. Please ensure Tesseract is installed on your system and added to PATH.")
        return None
    except Exception as e:
        st.error(f"An error occurred during OCR: {e}")
        return None

# --- 2. Vision API (Description & Analysis) Function ---
def analyze_image_with_vision(image_path, question):
    if client is None:
        return "Vision API is unavailable due to an API client error."
        
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return "Could not process image for Vision API."
        
    st.info("Analyzing image with Rafiq's Vision System...")
    
    vision_prompt = (
        "Analyze this image based on the user's question. Provide a supportive, friendly, and detailed response. "
        f"User's Question: {question}"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"An error occurred during Vision Analysis: {e}"