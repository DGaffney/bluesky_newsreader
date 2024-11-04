import sqlite3

def init_db():
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE,
                        access_token TEXT
                      )''')
    conn.commit()
    conn.close()

def save_user(user_id, access_token):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, access_token) VALUES (?, ?)", (user_id, access_token))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("user_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT access_token FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None