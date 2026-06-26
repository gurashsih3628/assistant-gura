import os
import re
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    url_for
)
from database import (
    init_db,
    save_chat,
    get_chat_history,
    save_memory,
    get_memories,
    save_fd,
    get_active_fds,
    get_fds_by_owner,
    close_fd,
    delete_fd
)
from groq import Groq
from dotenv import load_dotenv

# -------------------------
# ENVIRONMENT
# -------------------------
load_dotenv()

app = Flask(__name__)

PASSWORD = os.getenv("PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not PASSWORD:
    raise ValueError("PASSWORD not found in .env")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

app.secret_key = PASSWORD

# -------------------------
# DATABASE
# -------------------------
init_db()

# -------------------------
# GROQ
# -------------------------
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# -------------------------
# AUTH
# -------------------------
def is_logged_in():
    return session.get("logged_in", False)

def login_required():
    if not is_logged_in():
        return redirect(url_for("login"))
    return None

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            error = "Invalid password. Please try again."

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gura Assistant | Login</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7f6;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .login-container {{
                background-color: white;
                padding: 40px 30px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                text-align: center;
                width: 100%;
                max-width: 350px;
            }}
            .login-container h2 {{
                margin-top: 0;
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 25px;
            }}
            .input-group {{
                margin-bottom: 20px;
            }}
            input[type="password"] {{
                width: 100%;
                padding: 12px 15px;
                margin: 8px 0;
                display: inline-block;
                border: 1px solid #dce1e6;
                border-radius: 6px;
                box-sizing: border-box;
                font-size: 16px;
                transition: border-color 0.3s;
            }}
            input[type="password"]:focus {{
                border-color: #3498db;
                outline: none;
            }}
            button {{
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
                font-weight: 600;
                transition: background-color 0.3s;
            }}
            button:hover {{
                background-color: #2980b9;
            }}
            .error-message {{
                color: #e74c3c;
                font-size: 14px;
                margin-bottom: 15px;
                background-color: #fadbd8;
                padding: 10px;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Welcome to Gura</h2>
            {'<div class="error-message">' + error + '</div>' if error else ''}
            <form method="POST">
                <div class="input-group">
                    <input type="password" name="password" placeholder="Enter your password" required>
                </div>
                <button type="submit">Access Assistant</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------------------------
# MEMORY EXTRACTION
# -------------------------
def extract_memory(user_message):
    text = user_message.lower()
    
    try:
        dog_match = re.search(r"my dog(?:'s)? name is (.+)", text)
        if dog_match:
            save_memory(
                "dog_name",
                dog_match.group(1).strip().title(),
                "personal"
            )

        like_match = re.search(r"i like (.+)", text)
        if like_match:
            save_memory(
                "likes",
                like_match.group(1).strip(),
                "preference"
            )

    except Exception as e:
        print("MEMORY ERROR:", e)

# -------------------------
# ADD FD
# -------------------------
def extract_fd(user_message):
    if not user_message.upper().startswith("ADD FD"):
        return None

    try:
        owner = re.search(r"Owner:\s*(.*?)\s*Bank:", user_message, re.IGNORECASE).group(1)
        bank = re.search(r"Bank:\s*(.*?)\s*Amount:", user_message, re.IGNORECASE).group(1)
        amount = float(re.search(r"Amount:\s*([\d.]+)", user_message, re.IGNORECASE).group(1))
        start = re.search(r"Start:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)
        maturity = re.search(r"Maturity:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)

        interest_match = re.search(r"Interest:\s*([\d.]+)", user_message, re.IGNORECASE)
        interest = float(interest_match.group(1)) if interest_match else None

        save_fd(
            owner=owner,
            bank=bank,
            amount=amount,
            interest_rate=interest,
            start_date=start,
            maturity_date=maturity
        )

        return f"✅ FD saved for {owner} in {bank}"

    except Exception as e:
        return f"❌ FD save failed: {e}"

# -------------------------
# ACTIVE FDS
# -------------------------
def handle_active_fds(user_message):
    if user_message.strip().upper() != "ACTIVE FDS":
        return None

    fds = get_active_fds()

    if not fds:
        return "No active FDs found."

    result = "📋 ACTIVE FDS\n\n"
    for fd in fds:
        result += (
            f"ID: {fd[0]}\n"
            f"Owner: {fd[1]}\n"
            f"Bank: {fd[2]}\n"
            f"Amount: ₹{fd[3]}\n"
            f"Interest: {fd[4]}\n"
            f"Start: {fd[5]}\n"
            f"Maturity: {fd[6]}\n\n"
        )

    return result

# -------------------------
# SHOW OWNER FDS
# -------------------------
def handle_owner_fds(user_message):
    if not user_message.upper().startswith("SHOW FDS"):
        return None

    owner = user_message[8:].strip()
    fds = get_fds_by_owner(owner)

    if not fds:
        return f"No active FDs found for {owner}"

    result = f"📋 ACTIVE FDS FOR {owner}\n\n"
    for fd in fds:
        result += (
            f"ID: {fd[0]}\n"
            f"Bank: {fd[1]}\n"
            f"Amount: ₹{fd[2]}\n"
            f"Interest: {fd[3]}\n"
            f"Start: {fd[4]}\n"
            f"Maturity: {fd[5]}\n\n"
        )

    return result

# -------------------------
# CLOSE FD
# -------------------------
def handle_close_fd(user_message):
    if not user_message.upper().startswith("CLOSE FD"):
        return None

    try:
        fd_id = int(user_message.split()[-1])
        close_fd(fd_id)
        return f"✅ FD {fd_id} closed successfully."

    except Exception as e:
        return f"❌ Close FD failed: {e}"

# -------------------------
# DELETE FD
# -------------------------
def handle_delete_fd(user_message):
    if not user_message.upper().startswith("DELETE FD"):
        return None

    try:
        fd_id = int(user_message.split()[-1])
        delete_fd(fd_id)
        return f"🗑️ FD {fd_id} deleted successfully."

    except Exception as e:
        return f"❌ Delete FD failed: {e}"

# -------------------------
# CONTEXT
# -------------------------
def build_context(session_id="default"):
    memories = get_memories(20)
    chats = get_chat_history(session_id, 20)

    memory_text = "\n".join([f"{m[0]}: {m[1]}" for m in memories])
    chat_text = "\n".join([f"{c[0]}: {c[1]}" for c in chats])

    return f"""You are Gura Assistant.

LONG TERM MEMORIES:
{memory_text}

RECENT CHAT HISTORY:
{chat_text}

Rules:
1. Use memories ONLY when directly relevant.
2. Never introduce memories on your own.
3. Never mention dog names, preferences, FDs, banks, or personal information unless asked.
4. For greetings like hi, hello, hey, simply respond normally without mentioning memories."""

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    auth = login_required()
    
    if auth:
        return auth

    return render_template("index.html")

# -------------------------
# CHAT
# -------------------------
@app.route("/chat", methods=["POST"])
def chat():
    auth = login_required()
    
    if auth:
        return jsonify({"error": "Login required"}), 401

    try:
        data = request.get_json()
        user_message = data.get("message")
        session_id = data.get("session_id", "default")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        save_chat("user", user_message, session_id)
        extract_memory(user_message)

        # Check for command handlers first
        for handler in [
            handle_active_fds,
            handle_owner_fds,
            handle_close_fd,
            handle_delete_fd,
            extract_fd
        ]:
            result = handler(user_message)
            if result:
                save_chat("assistant", result, session_id)
                return jsonify({"reply": result})

        # Process with LLM if no command matched
        context = build_context(session_id)

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": context
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )

        reply = response.choices[0].message.content
        save_chat("assistant", reply, session_id)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# MEMORY API
# -------------------------
@app.route("/memory", methods=["POST"])
def memory():
    data = request.get_json()
    
    save_memory(
        data["key"],
        data["value"],
        data.get("category", "general")
    )

    return jsonify({"status": "saved"})

# -------------------------
# DEBUG
# -------------------------
@app.route("/debug")
def debug():
    return jsonify({
        "memories": get_memories(50),
        "fds": get_active_fds()
    })

# -------------------------
# HEALTH
# -------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "model": MODEL
    })

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )s
