import sqlite3

DB_NAME = "gura.db"


# -------------------------
# CONNECTION
# -------------------------
def get_connection():
    return sqlite3.connect(DB_NAME)


# -------------------------
# INIT DATABASE
# -------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Memories
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT,
        value TEXT,
        category TEXT
    )
    """)

    # Chat History
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        message TEXT,
        session_id TEXT
    )
    """)

    # Fixed Deposits
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT,
        bank TEXT,
        amount REAL,
        interest_rate REAL,
        start_date TEXT,
        maturity_date TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    conn.commit()
    conn.close()


# -------------------------
# CHAT HISTORY
# -------------------------
def save_chat(role, message, session_id="default"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chat_history
        (role, message, session_id)
        VALUES (?, ?, ?)
        """,
        (role, message, session_id)
    )

    conn.commit()
    conn.close()


def get_chat_history(session_id="default", limit=20):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, message
        FROM chat_history
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit)
    )

    data = cur.fetchall()

    conn.close()
    return data


# -------------------------
# MEMORY SYSTEM
# -------------------------
def save_memory(key, value, category="general"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO memories
        (key, value, category)
        VALUES (?, ?, ?)
        """,
        (key, value, category)
    )

    conn.commit()
    conn.close()


def get_memories(limit=20):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT key, value
        FROM memories
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    data = cur.fetchall()

    conn.close()
    return data


# -------------------------
# FIXED DEPOSITS
# -------------------------
def save_fd(
    owner,
    bank,
    amount,
    interest_rate=None,
    start_date=None,
    maturity_date=None
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO fds
        (
            owner,
            bank,
            amount,
            interest_rate,
            start_date,
            maturity_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            owner,
            bank,
            amount,
            interest_rate,
            start_date,
            maturity_date
        )
    )

    conn.commit()
    conn.close()


def get_active_fds():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            owner,
            bank,
            amount,
            interest_rate,
            start_date,
            maturity_date
        FROM fds
        WHERE status='active'
        """
    )

    data = cur.fetchall()

    conn.close()
    return data


def get_fds_by_owner(owner):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            bank,
            amount,
            interest_rate,
            start_date,
            maturity_date
        FROM fds
        WHERE owner=?
        AND status='active'
        """,
        (owner,)
    )

    data = cur.fetchall()

    conn.close()
    return data


# -------------------------
# CLOSE FD
# -------------------------
def close_fd(fd_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE fds
        SET status='closed'
        WHERE id=?
        """,
        (fd_id,)
    )

    conn.commit()
    conn.close()


# -------------------------
# DELETE FD
# -------------------------
def delete_fd(fd_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM fds
        WHERE id=?
        """,
        (fd_id,)
    )

    conn.commit()
    conn.close()


# -------------------------
# TEST
# -------------------------
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
