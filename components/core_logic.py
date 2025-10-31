import os
import json
import langid
from openai import OpenAI
from dotenv import load_dotenv
from components.lang_handler import detect_language

# --- Load environment variables ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Initialize OpenAI Client (via OpenRouter) ---
def initialize_openai_client():
    if not OPENROUTER_API_KEY:
        print("❌ Error: OPENROUTER_API_KEY not found in .env file.")
        return None
    try:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
    except Exception as e:
        print(f"⚠️ Error initializing OpenAI client: {e}")
        return None


client = initialize_openai_client()

# --- Load Ghadeer Profile ---
def load_ghadeer_profile():
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ghadeer_profile.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ Error: ghadeer_profile.json not found.")
        return {}

GHADEER_PROFILE = load_ghadeer_profile()

# --- Smart Language Detector ---
def get_language_name(code):
    mapping = {
        "en": "English",
        "ar": "Arabic",
        "es": "Spanish",
        "fr": "French",
        "hi": "Hindi"
    }
    return mapping.get(code, code.capitalize())


# --- Build System Prompt ---
def create_system_prompt(input_language="en"):
    creator = "Mohammad"
    user = "Ghadeer Mahmoud"
    language_name = get_language_name(input_language)

    system_message = (
        f"You are **Rafiq (رفيق)** — a friendly and emotionally intelligent AI assistant created by {creator} "
        f"for {user}. You must always reply **in the same language** as the user's message "
        f"(detected: {language_name}).\n\n"
        f"✨ Rules:\n"
        f"- Reply strictly in the user's input language.\n"
        f"- Never translate or mix languages.\n"
        f"- Be warm, natural, and human-like.\n"
        f"- Keep responses short, meaningful, and emotionally engaging.\n"
        f"- If user greets or chats casually, respond like a close supportive friend.\n"
        f"- If user asks questions, answer with helpful clarity.\n"
    )

    return system_message


# --- Generate AI Response ---
def get_ai_response(messages_history, model=None):
    if client is None:
        return "❌ Connection to OpenRouter failed. Please check your API key."

    # Detect language of last message
    try:
        last_user_msg = messages_history[-1]["content"]
        lang_code = langid.classify(last_user_msg)[0]
    except Exception:
        lang_code = "en"

    system_prompt = create_system_prompt(lang_code)
    selected_model = model or "openai/gpt-4o-mini"

    # Prepare messages for API
    messages_for_api = [{"role": "system", "content": system_prompt}]
    messages_for_api.extend(messages_history[-10:])

    try:
        completion = client.chat.completions.create(
            model=selected_model,
            messages=messages_for_api,
            temperature=0.7
        )

        response_text = completion.choices[0].message.content.strip()
        return response_text

    except Exception as e:
        return f"⚠️ Error while thinking: {str(e)}"
