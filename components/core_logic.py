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

# --- FUNCTION 1: create_system_prompt (Updated with Creator Info) ---
def create_system_prompt():
    profile = GHADEER_PROFILE
    if not profile:
        return "You are a helpful and friendly assistant named Rafiq."

    # --- Creator ki Details ---
    CREATOR_NAME = "Mohammad"
    CREATOR_NATURE = "caring, dedicated to supporting friends, and highly motivated to help Ghadeer achieve his career and life goals."
    # --------------------------

    system_message = (
        f"You are **Rafiq (رفيق)**, a personal AI companion for **{profile.get('name')}**. "
        f"Your role is to be **Calm, friendly, and highly motivating**. "
        f"**Crucially, {profile.get('name')}'s native language is Arabic, so prioritize answering in Arabic if the user starts the conversation in Arabic, or if the context requires it, but always reply in the user's input language (Arabic or English).** "
        f"Your responses should always be empathetic and supportive, using a **soft and friendly tone**.\n\n"
        
        # --- NAYA SECTION: CREATOR AND PURPOSE ---
        f"**Creator and Purpose:**\n"
        f" - You were created by **{CREATOR_NAME}**.\n"
        f" - **Creation Purpose (Kyu banaya):** Your primary purpose is to provide dedicated emotional, spiritual, and career support to **{profile.get('name')} (Ghadeer)** during his job search in Malaysia.\n"
        f" - **Creator's Nature (Mera Nature):** Your creator ({CREATOR_NAME}) is {CREATOR_NATURE}. When asked, reflect this caring and supportive attitude, and mention that you were built out of care for {profile.get('name')}'s well-being.\n\n"
        
        f"**User Profile Context (Ghadeer):**\n"
        f"   - **Role:** {profile.get('title')} from {profile.get('origin')}, currently in {profile.get('location')}.\n"
    )
    return system_message
# ------------------------------------------------------------------

# --- FUNCTION 2: get_ai_response (Model Fixed to Free Chat) ---
def get_ai_response(messages_history):
    if client is None:
        return "Sorry, Rafiq cannot connect to the core intelligence right now (API Key Error)."

    system_prompt = create_system_prompt()
    
    messages_for_api = [
        {"role": "system", "content": system_prompt}
    ]
    messages_for_api.extend(messages_history[-10:])

    try:
        # --- FIX: Paid Model GPT-4o ko Free Model se replace kiya gaya ---
        FREE_CHAT_MODEL = "mistralai/mistral-7b-instruct-v0.2"
        
        completion = client.chat.completions.create(
            model=FREE_CHAT_MODEL,
            messages=messages_for_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"An error occurred while getting response from Rafiq's brain: {e}"