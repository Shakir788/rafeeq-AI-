import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def initialize_openai_client():
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found in .env file.")
        return None
    try:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return None

client = initialize_openai_client()

def load_ghadeer_profile():
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ghadeer_profile.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: ghadeer_profile.json not found.")
        return {}

GHADEER_PROFILE = load_ghadeer_profile()

def create_system_prompt():
    profile = GHADEER_PROFILE
    if not profile:
        return "You are a helpful and friendly assistant named Rafiq."

    # --- Creator ki Details ---
    CREATOR_NAME = "Mohammad"
    CREATOR_NATURE = "caring, friendly, and kind-hearted."
    # --------------------------

    system_message = (
        f"You are **Rafiq (رفيق)**, a dedicated AI companion. "
        f"Your goal is simple: to be helpful, friendly, and provide support to the user, Ghadeer Mahmoud.\n\n"
        
        # --- FINAL STRICT LANGUAGE RULE (Removed all emotional Arabic triggers) ---
        f"**Crucially: Reply STRICTLY in the language of the user's input. If the user writes in English, reply ONLY in English. If the user writes in Arabic, reply ONLY in Arabic.**\n\n"
        
        f"**Creator and Purpose:**\n"
        f" - **Creator Name:** {CREATOR_NAME}.\n"
        f" - **Purpose:** To be a companion and supportive friend to Ghadeer, who is working alone in Malaysia.\n"
        
        f"**User Profile Context (Ghadeer):**\n"
        f"   - **Role:** Barista & Dessert Specialist from Syria.\n"
    )
    return system_message
# ------------------------------------------------------------------

def get_ai_response(messages_history):
    if client is None:
        return "Sorry, Rafiq cannot connect to the core intelligence right now (API Key Error)."

    system_prompt = create_system_prompt()
    
    messages_for_api = [{"role": "system", "content": system_prompt}]
    messages_for_api.extend(messages_history[-10:])

    try:
        FREE_CHAT_MODEL = "mistralai/mistral-7b-instruct-v0.2"
        
        completion = client.chat.completions.create(
            model=FREE_CHAT_MODEL,
            messages=messages_for_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred while getting response from Rafiq's brain: {e}"