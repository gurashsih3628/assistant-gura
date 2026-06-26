import os
import psycopg2

# -------------------------
# CONNECTION
# -------------------------
def get_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set. Please add it to your Render environment variables.")
    # Connect to PostgreSQL (sslmode='require' is often needed for cloud DBs like Render)
    return psycopg2.connect(db_url, sslmode='require')

# -------------------------
# INIT DATABASE
# -------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # MEMORIES (Changed AUTOINCREMENT to SERIAL for PostgreSQL)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id SERIAL PRIMARY KEY,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # CHAT HISTORY
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id SERIAL PRIMARY KEY,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        session_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # FD TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fds (
        id SERIAL PRIMARY KEY,
        owner TEXT NOT NULL,
        bank TEXT NOT NULL,
        amount REAL NOT NULL,
        interest_rate REAL,
        start_date TEXT,
        maturity_date TEXT,
        reminder_days INTEGER DEFAULT 7,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    print("Database initialized successfully")

# -------------------------
# MEMORY FUNCTIONS
# -------------------------
def save_memory(key, value, category="general"):
    conn = get_connection()
    cur = conn.cursor()

    # PostgreSQL uses %s instead of ? for parameterized queries
    cur.execute(
        """
        INSERT INTO memories
        (key, value, category)
        VALUES (%s, %s, %s)
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
        SELECT key, value, category, created_at
        FROM memories
        ORDER BY id DESC
        LIMIT %s
        """,
        (limit,)
    )

    data = cur.fetchall()

    conn.close()

    return data

# -------------------------
# CHAT FUNCTIONS
# -------------------------
def save_chat(role, message, session_id="default"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chat_history
        (role, message, session_id)
        VALUES (%s, %s, %s)
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
        SELECT role, message, created_at
        FROM chat_history
        WHERE session_id = %s
        ORDER BY id DESC
        LIMIT %s
        """,
        (session_id, limit)
    )

    data = cur.fetchall()

    conn.close()

    return data

# -------------------------
# FD FUNCTIONS
# -------------------------
def save_fd(
    owner,
    bank,
    amount,
    interest_rate=None,
    start_date=None,
    maturity_date=None,
    reminder_days=7
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
            maturity_date,
            reminder_days
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            owner,
            bank,
            amount,
            interest_rate,
            start_date,
            maturity_date,
            reminder_days
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
        WHERE status = 'active'
        ORDER BY maturity_date ASC
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
        WHERE owner = %s
        AND status = 'active'
        ORDER BY maturity_date ASC
        """,
        (owner,)
    )

    data = cur.fetchall()

    conn.close()

    return data

def close_fd(fd_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE fds
        SET status = 'closed'
        WHERE id = %s
        """,
        (fd_id,)
    )

    conn.commit()
    conn.close()

def delete_fd(fd_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM fds
        WHERE id = %s
        """,
        (fd_id,)
    )

    conn.commit()
    conn.close()

# -------------------------
# DEBUG TEST
# -------------------------
if __name__ == "__main__":
    # Will fail locally if you don't have DATABASE_URL set in your .env
    init_db()

    print("ACTIVE FDS:")
    print(get_active_fds())
