import streamlit as st
from langdetect import detect, lang_detect_exception

# --- Language Detection Function ---
def detect_language(text):
    """
    Detects the language of the input text using langdetect.
    Returns the language code (e.g., 'ar', 'en') and the full name.
    """
    if not text or not text.strip():
        return 'ar', 'Arabic' # Default to Arabic if text is empty
        
    try:
        # Detect function sirf code deta hai (e.g., 'en', 'ar')
        lang_code = detect(text)
        lang_name = ""
        
        # Simple name mapping
        if lang_code == 'ar':
            lang_name = "Arabic"
        elif lang_code == 'en':
            lang_name = "English"
        else:
            lang_name = lang_code.capitalize()
            
        return lang_code, lang_name
        
    except lang_detect_exception.LangDetectException:
        # st.warning("Language detection failed: Text might be too short or complex. Defaulting to Arabic.")
        return 'ar', 'Arabic' # Error aane par Ghadeer ki native bhasha (Arabic) ko default set karein।
    except Exception as e:
        # st.error(f"Unknown detection error: {e}")
        return 'ar', 'Arabic'