import streamlit as st
import os
from dotenv import load_dotenv
import time # Temporary file naming ke liye
import builtins # Pylance "reportUndefinedVariable" warnings ko fix karne ke liye

# Components files se functions aur data import karna
from components.core_logic import get_ai_response, GHADEER_PROFILE
from components.voice_handler import play_audio_button
from components.lang_handler import detect_language
from components.image_processor import perform_ocr, analyze_image_with_vision

# --- Memory Handler Import ---
# Assuming you have created this file as discussed
from components.memory_handler import load_memory, save_memory, init_db 

# Load environment variables (API Key)
load_dotenv()
init_db() # Database initialization - First time table banata hai

# --- Initial Setup ---
AI_NAME = "Rafiq (رفيق)"
USER_ID = "GHADEER_MAHMOUD_ID" # <--- IMPORTANT: This should be dynamic for multi-user apps
USER_NAME = GHADEER_PROFILE.get("name", "Ghadeer")
LOGO_PATH = "assets/rafiq_logo.png"

# Streamlit Page Configuration
st.set_page_config(page_title=f"{AI_NAME} - Personal Companion", layout="wide")

# Initialize Session State
if "messages" not in st.session_state:
    # 1. Long-term memory se messages load karna
    persisted_messages = load_memory(USER_ID)
    
    if persisted_messages:
        st.session_state["messages"] = persisted_messages
    else:
        # 2. Agar koi memory nahi mili, toh default message se start karna
        st.session_state["messages"] = [
            {"role": "assistant", "content": f"مرحبًا يا {USER_NAME}! أنا رفيقك الشخصي، كيف يمكنني مساعدتك اليوم؟"}
        ]

if 'image_mode' not in st.session_state:
    st.session_state['image_mode'] = 'description'

# --- Custom Sidebar ---
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)
    st.title(f"🫂 {AI_NAME}")
    st.subheader("Your Supportive Companion")
    st.markdown("---")
    
    # --- Image Upload Section ---
    st.subheader("🖼️ Image Analysis")
    uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="image_uploader")

    if uploaded_file is not None:
        file_name = f"temp_{int(time.time())}_{uploaded_file.name}"
        temp_path = os.path.join("assets", file_name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True) 
        
        st.session_state['image_mode'] = st.radio(
            "Select Analysis Mode:",
            ('Description & Analysis (Vision)', 'Text Extraction (OCR)'),
            index=0,
            key='mode_radio'
        )
        
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                if st.session_state['image_mode'] == 'Text Extraction (OCR)':
                    extracted_text = perform_ocr(temp_path)
                    response_content = f"**🔍 Extracted Text (OCR):**\n\n```\n{extracted_text}\n```\n\n"
                    
                else:
                    vision_question = st.text_input("Rafiq, is image ke baare mein kya bataun?", value="Describe this photo and tell me what you think, keep the tone friendly.", key="vision_q")
                    response_content = analyze_image_with_vision(temp_path, vision_question)
                
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                
                os.remove(temp_path)
                
                # Update memory after AI response
                save_memory(USER_ID, st.session_state.messages) # <--- Memory Save
                st.rerun()
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("Clear Chat Memory"):
        # Memory clear karne se pehle, database mein bhi clear karna chahiye
        # Temporary: Database mein empty list save karna
        save_memory(USER_ID, []) 
        
        st.session_state["messages"] = [
            {"role": "assistant", "content": f"مرحبًا يا {USER_NAME}! أنا رفيقك الشخصي، كيف يمكنني مساعدتك اليوم؟"}
        ]
        st.rerun()

    st.markdown("---")
    st.caption("Now using manual 'Play' button for voice response.")

st.title(f"👋 مرحبا بك يا {USER_NAME}!")
st.subheader(f"Your Personal Companion: {AI_NAME}")
st.markdown("---")


# Display Chat History
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # --- Voice Button ---
        if message["role"] == "assistant":
            # AI response ki language detect karna
            lang_code, _ = detect_language(message["content"])
            
            # Play button dikhana
            play_audio_button(message["content"], language=lang_code, unique_key=i)


# --- Main Chat Input and Response Logic ---
if prompt := st.chat_input(f"Speak to {AI_NAME} in Arabic or English..."):
    # 1. User Message Add karna
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. AI Response generate karna
    with st.chat_message("assistant"):
        with st.spinner(f"{AI_NAME} is thinking..."):
            
            ai_response = get_ai_response(st.session_state.messages)
            
            st.write(ai_response)
            
            # Response history mein save karna
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

            # 3. Long-term memory mein save karna
            save_memory(USER_ID, st.session_state.messages) # <--- Memory Save

            # Auto-rerun for the play button to appear correctly
            st.rerun()