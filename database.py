import sqlite3

DB_NAME = "gura.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT, category TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, message TEXT, session_id TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS fds (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, bank TEXT, amount REAL, interest_rate REAL, start_date TEXT, maturity_date TEXT, status TEXT DEFAULT 'active')")
    conn.commit()
    conn.close()

def save_chat(role, message, session_id="default"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_history (role, message, session_id) VALUES (?, ?, ?)", (role, message, session_id))
    conn.commit()
    conn.close()

def get_chat_history(session_id="default", limit=20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT role, message FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?", (session_id, limit))
    data = cur.fetchall()
    conn.close()
    return data

def save_fd(owner, bank, amount, start_date=None, maturity_date=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO fds (owner, bank, amount, start_date, maturity_date) VALUES (?, ?, ?, ?, ?)", (owner, bank, amount, start_date, maturity_date))
    conn.commit()
    conn.close()

def get_active_fds():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, owner, bank, amount, start_date, maturity_date FROM fds WHERE status = 'active'")
    data = cur.fetchall()
    conn.close()
    return data

def get_fds_by_owner(owner):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, bank, amount, start_date, maturity_date FROM fds WHERE owner = ? AND status = 'active'", (owner,))
    data = cur.fetchall()
    conn.close()
    return data

if __name__ == "__main__":
    init_db()
