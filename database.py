import sqlite3

DB_NAME = "gura.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()

def add_memory(category, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO memories (category, content) VALUES (?, ?)",
        (category, content)
    )

    conn.commit()
    conn.close()

def get_memories():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, category, content FROM memories"
    )

    data = cursor.fetchall()

    conn.close()

    return data
