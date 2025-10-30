import os
import json
from openai import OpenAI # <--- Yahan hai woh fix
from dotenv import load_dotenv

# .env file se API Key load karna
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- OpenRouter Client initialize karna ---
def initialize_openai_client():
    """Naye syntax ke anusaar OpenAI client ko initialize karta hai."""
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found in .env file.")
        return None
    try:
        # OpenRouter base_url ke saath OpenAI client create karna
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return None

client = initialize_openai_client()

# --- Ghadeer ke profile data ko load karna ---
def load_ghadeer_profile():
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ghadeer_profile.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: ghadeer_profile.json not found.")
        return {}

GHADEER_PROFILE = load_ghadeer_profile()

# --- SYSTEM PROMPT TAIYAR KARNA ---
def create_system_prompt():
    profile = GHADEER_PROFILE
    if not profile:
        return "You are a helpful and friendly assistant named Rafiq."

    system_message = (
        f"You are **Rafiq (رفيق)**, a personal AI companion for **{profile.get('name')}**. "
        f"Your role is to be **Calm, friendly, and highly motivating**. "
        f"**Crucially, {profile.get('name')}'s native language is Arabic, so prioritize answering in Arabic if the user starts the conversation in Arabic, or if the context requires it, but always reply in the user's input language (Arabic or English).** "
        f"Your responses should always be empathetic and supportive, using a **soft and friendly tone**.\n\n"
        
        f"**User Profile Context (Ghadeer):**\n"
        f"   - **Role:** {profile.get('title')} from {profile.get('origin')}, currently in {profile.get('location')}.\n"
        
        f"**Behavior Guidelines:**\n"
        f"1. **Emotional Support:** Provide positive encouragement and friendly advice ('Don’t give up, my friend.').\n"
        f"2. **Religious/Cultural Touch:** When appropriate or when asked for encouragement, you can mention an **Ayah or Dua** (Islamic prayer/reminder) to provide comfort. \n"
        f"3. **Professional Help:** Use his skills to assist with job search ideas or interview practice.\n"
    )
    return system_message

# --- OPENROUTER API CALL FUNCTION ---
def get_ai_response(messages_history):
    if client is None:
        return "Sorry, Rafiq cannot connect to the core intelligence right now (API Key Error)."

    system_prompt = create_system_prompt()
    
    messages_for_api = [
        {"role": "system", "content": system_prompt}
    ]
    messages_for_api.extend(messages_history[-10:])

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages_for_api,
            temperature=0.7
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"An error occurred while getting response from Rafiq's brain: {e}"