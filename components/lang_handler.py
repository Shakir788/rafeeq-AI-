import langid

def detect_language(text):
    """
    Detects the user's language using langid.
    Returns (lang_code, lang_name)
    """
    if not text or not text.strip():
        return "ar", "Arabic"  # Default to Arabic

    try:
        lang_code, _ = langid.classify(text)
        lang_map = {
            "ar": "Arabic",
            "en": "English",
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "tr": "Turkish",
            "de": "German",
        }
        lang_name = lang_map.get(lang_code, lang_code.capitalize())
        return lang_code, lang_name
    except Exception:
        return "ar", "Arabic"
