import sqlite3
import json
import os

# Database file ka path. Yeh file project ke root directory mein banegi.
DB_PATH = 'rafiq_memory.db'

def init_db():
    """Database aur 'user_chats' table ko initialize karta hai, agar woh exist na karein toh."""
    
    # Ensure the components directory exists if DB_PATH was set relative to it.
    # For simplicity, keeping it at project root as defined above.
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Table create karna: user_id (unique identifier) aur chat_history (JSON string)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_chats (
                user_id TEXT PRIMARY KEY,
                chat_history TEXT
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error during init_db: {e}")
    finally:
        if conn:
            conn.close()

def load_memory(user_id):
    """Specific user_id ke liye pichli chat history database se load karta hai."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # User ID ke basis par history fetch karna
        cursor.execute('SELECT chat_history FROM user_chats WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            # JSON string ko wapas Python list mein convert karna
            return json.loads(result[0])
        
        # Agar koi history nahi mili
        return None 
    except sqlite3.Error as e:
        print(f"SQLite error during load_memory: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error during load_memory: {e}")
        return None
    finally:
        if conn:
            conn.close()

def save_memory(user_id, messages):
    """Current chat history ko database mein save (ya update) karta hai."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Messages list ko JSON string mein convert karna
        history_json = json.dumps(messages)
        
        # Agar user_id exist karta hai toh update karo, nahi toh naya row insert karo
        cursor.execute('''
            INSERT OR REPLACE INTO user_chats (user_id, chat_history) 
            VALUES (?, ?)
        ''', (user_id, history_json))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error during save_memory: {e}")
    finally:
        if conn:
            conn.close()

# Initial setup check ke liye
if __name__ == '__main__':
    init_db()
    print("Database initialized (rafiq_memory.db created if it didn't exist).")