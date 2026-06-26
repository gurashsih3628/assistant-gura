import re
import streamlit as st
from groq import Groq
from database import (
    init_db, save_chat, get_chat_history, save_memory,
    get_memories, save_fd, get_active_fds, get_fds_by_owner
)

# -------------------------
# CONFIGURATION
# -------------------------
if "PASSWORD" not in st.secrets or "GROQ_API_KEY" not in st.secrets:
    st.error("🔑 Missing secrets in Streamlit dashboard.")
    st.stop()

PASSWORD = st.secrets["PASSWORD"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

init_db()
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# -------------------------
# CORE LOGIC
# -------------------------
def extract_memory(user_message):
    text = user_message.lower()
    dog_match = re.search(r"my dog(?:'s)? name is (.+)", text)
    if dog_match:
        save_memory("dog_name", dog_match.group(1).strip().title(), "personal")
    like_match = re.search(r"i like (.+)", text)
    if like_match:
        save_memory("likes", like_match.group(1).strip(), "preference")

def process_command(user_message):
    msg = user_message.strip().upper()
    if msg.startswith("ADD FD"):
        try:
            owner = re.search(r"Owner:\s*(.*?)\s*Bank:", user_message, re.IGNORECASE).group(1)
            bank = re.search(r"Bank:\s*(.*?)\s*Amount:", user_message, re.IGNORECASE).group(1)
            amount = float(re.search(r"Amount:\s*([\d.]+)", user_message, re.IGNORECASE).group(1))
            start = re.search(r"Start:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)
            maturity = re.search(r"Maturity:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)
            save_fd(owner, bank, amount, start_date=start, maturity_date=maturity)
            return f"✅ FD saved for {owner} at {bank}."
        except Exception as e: return f"❌ Format error: {e}"
    if msg == "ACTIVE FDS":
        fds = get_active_fds()
        if not fds: return "📋 No active FDs found."
        res = "📋 **ACTIVE FDs:**\n\n"
        for f in fds: res += f"- **ID {f[0]}**: {f[1]} (Bank: {f[2]}) | ₹{f[3]:,} | Maturity: {f[6]}\n"
        return res
    if msg.startswith("SHOW FDS"):
        owner = user_message[8:].strip()
        if not owner: return "Please specify an owner (e.g., 'SHOW FDS Mom')"
        fds = get_fds_by_owner(owner)
        if not fds: return f"No active FDs found for {owner}."
        res = f"📋 **FDs for {owner.upper()}:**\n\n"
        for f in fds: res += f"- **ID {f[0]}**: Bank: {f[1]} | ₹{f[2]:,} | Maturity: {f[5]}\n"
        return res
    return None

# -------------------------
# UI INTERFACE
# -------------------------
st.set_page_config(page_title="Gura Assistant", layout="wide")

if not st.session_state["logged_in"]:
    st.title("🤖 Gura Assistant")
    password_input = st.text_input("Enter Password", type="password")
    if st.button("Access"):
        if password_input == PASSWORD:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid password")
else:
    with st.sidebar:
        if st.button("Sign Out"): st.session_state["logged_in"] = False; st.rerun()
        if st.expander("View All FDs"): st.json(get_active_fds())
        if st.expander("View Memories"): st.json(get_memories(10))

    st.title("💬 Gura Personal Assistant")
    
    # Load and display chat
    for chat in reversed(get_chat_history("default", 15)):
        with st.chat_message("user" if chat[0] == "user" else "assistant"):
            st.markdown(chat[1])

    if user_message := st.chat_input("Ask Gura..."):
        with st.chat_message("user"): st.markdown(user_message)
        
        # 1. Process Logic
        extract_memory(user_message)
        reply = process_command(user_message)
        
        # 2. LLM Fallback (if not a command)
        if not reply:
            memories = get_memories(10)
            # Retrieve 9 to avoid duplicating the current message being saved
            history = get_chat_history("default", 9)
            
            memory_text = "\n".join([f"{m[0]}: {m[1]}" for m in memories])
            chat_text = "\n".join([f"{c[0]}: {c[1]}" for c in history])
            
            context = f"""
            LONG TERM MEMORIES:
            {memory_text}

            RECENT CHAT HISTORY:
            {chat_text}

            Rules:
            1. Use memories only when relevant.
            2. Never randomly reveal memories.
            3. Remember previous conversation context.
            4. Act as Gura Assistant.
            """
            
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content
        
        # 3. Save to database after processing
        save_chat("user", user_message, "default")
        save_chat("assistant", reply, "default")
        st.rerun()
