import streamlit as st
import os
import time
from dotenv import load_dotenv

from components.core_logic import get_ai_response, GHADEER_PROFILE
from components.voice_handler import play_audio_button
from components.lang_handler import detect_language
from components.image_processor import perform_ocr 

load_dotenv()

# --- INITIAL SETUP & CONSTANTS ---
AI_NAME = "Rafiq (رفيق)"
USER_NAME = GHADEER_PROFILE.get("name", "Ghadeer")
LOGO_PATH = "assets/rafiq_logo.png"
TEMP_IMAGE_KEY = "temp_uploaded_image.png"

st.set_page_config(page_title=f"{AI_NAME} - Personal Companion", layout="wide")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": f"👋 مرحبًا يا **{USER_NAME}**! أنا رفيقك الشخصي، كيف يمكنني مساعدتك اليوم؟"}
    ]
if "image_uploaded" not in st.session_state:
    st.session_state["image_uploaded"] = False
if "model" not in st.session_state:
    st.session_state["model"] = "openai/gpt-4o-mini"  # Default model


# --- Custom Sidebar ---
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)
    st.title(f"🫂 {AI_NAME}")
    st.subheader("Your Supportive Companion")
    st.markdown("---")

    # --- MODEL SELECTION ---
    st.subheader("⚙️ Choose AI Model")
    model_choice = st.selectbox(
        "Select model to power Rafiq's intelligence:",
        [
            "openai/gpt-4o-mini (Default - Fast)",
            "openai/gpt-4o (Smarter)",
            "mistralai/mistral-7b-instruct-v0.2 (Lightweight)",
            "anthropic/claude-3.5-sonnet (Creative)"
        ],
        index=0
    )

    # Update selected model in session
    if "gpt-4o" in model_choice:
        st.session_state["model"] = "openai/gpt-4o"
    elif "mistral" in model_choice:
        st.session_state["model"] = "mistralai/mistral-7b-instruct-v0.2"
    elif "claude" in model_choice:
        st.session_state["model"] = "anthropic/claude-3.5-sonnet"
    else:
        st.session_state["model"] = "openai/gpt-4o-mini"

    st.markdown("---")

    # --- Text Extraction (OCR) Section ---
    st.subheader("📸 Text Extraction (OCR)")
    uploaded_file = st.file_uploader("Upload Image with Text", type=["png", "jpg", "jpeg"], key="image_uploader")

    if uploaded_file is not None and 'current_image_path' not in st.session_state:
        temp_path = os.path.join("assets", TEMP_IMAGE_KEY)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state['image_uploaded'] = True
        st.session_state['current_image_path'] = temp_path
        st.rerun()

    # --- OCR Analysis Panel ---
    if st.session_state['image_uploaded'] and 'current_image_path' in st.session_state:
        st.markdown("---")
        st.caption("Uploaded Image Preview:")
        st.image(st.session_state['current_image_path'], use_container_width=True)
        st.info("Mode: Text Extraction (OCR)")

        if st.button("Extract Text (OCR)", key="extract_btn"):
            with st.spinner("Extracting text..."):
                extracted_text = perform_ocr(st.session_state['current_image_path'])
                response_content = f"**🔍 Extracted Text (OCR) Result:**\n\n```\n{extracted_text}\n```\n\n"
                
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                
                os.remove(st.session_state['current_image_path'])
                del st.session_state['current_image_path']
                st.session_state['image_uploaded'] = False
                st.rerun()

    st.markdown("---")

    # Clear chat button
    if st.button("🔄 Clear Chat Memory"):
        st.session_state["messages"] = [
            {"role": "assistant", "content": f"👋 مرحبًا يا **{USER_NAME}**! أنا رفيقك الشخصي، كيف يمكنني مساعدتك اليوم؟"}
        ]
        st.rerun()

    st.markdown("---")
    st.caption("🎧 Use 'Play' button for voice response.")


# --- MAIN INTERFACE ---
st.title(f"👋 مرحبًا بك يا **{USER_NAME}**!")
st.subheader(f"Your Personal Companion: {AI_NAME}")
st.markdown("---")


# Display Chat History
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            lang_code, _ = detect_language(message["content"])
            play_audio_button(message["content"], language=lang_code, unique_key=i)


# --- Chat Input & AI Response ---
if prompt := st.chat_input(f"Speak to {AI_NAME} (رفيق) in any language..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{AI_NAME} is thinking..."):
            ai_response = get_ai_response(st.session_state.messages, model=st.session_state["model"])
            st.write(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
