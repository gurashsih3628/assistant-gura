import re
import streamlit as st
from groq import Groq
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

# -------------------------
# SECURITY & SECRETS
# -------------------------
if "PASSWORD" not in st.secrets or "GROQ_API_KEY" not in st.secrets:
    st.error("🔑 Missing required secrets! Please add 'PASSWORD' and 'GROQ_API_KEY' in your Streamlit dashboard secrets.")
    st.stop()

PASSWORD = st.secrets["PASSWORD"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

init_db()
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# -------------------------
# COMMAND HANDLERS
# -------------------------
def extract_memory(user_message):
    text = user_message.lower()
    try:
        dog_match = re.search(r"my dog(?:'s)? name is (.+)", text)
        if dog_match:
            save_memory("dog_name", dog_match.group(1).strip().title(), "personal")
        like_match = re.search(r"i like (.+)", text)
        if like_match:
            save_memory("likes", like_match.group(1).strip(), "preference")
    except: pass

def extract_fd(user_message):
    if not user_message.upper().startswith("ADD FD"): return None
    try:
        owner = re.search(r"Owner:\s*(.*?)\s*Bank:", user_message, re.IGNORECASE).group(1)
        bank = re.search(r"Bank:\s*(.*?)\s*Amount:", user_message, re.IGNORECASE).group(1)
        amount = float(re.search(r"Amount:\s*([\d.]+)", user_message, re.IGNORECASE).group(1))
        start = re.search(r"Start:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)
        maturity = re.search(r"Maturity:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)
        save_fd(owner, bank, amount, start_date=start, maturity_date=maturity)
        return f"✅ FD saved for {owner}."
    except Exception as e: return f"❌ Error: {e}"

# -------------------------
# UI LAYOUT
# -------------------------
st.set_page_config(page_title="Gura Assistant", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

if not st.session_state["logged_in"]:
    st.title("🤖 Gura Assistant")
    if st.text_input("Password", type="password") == PASSWORD:
        st.session_state["logged_in"] = True
        st.rerun()
else:
    with st.sidebar:
        st.title("⚙️ Control Panel")
        if st.button("Sign Out"): st.session_state["logged_in"] = False; st.rerun()
        
        st.divider()
        st.subheader("📊 Data Explorer")
        with st.expander("View All Stored FDs"):
            fds = get_active_fds()
            st.json(fds)
        with st.expander("View All Memories"):
            st.json(get_memories(50))
        with st.expander("View Chat Logs"):
            st.json(get_chat_history("default", 20))

    st.title("💬 Gura Personal Assistant")
    
    # Render chat history
    chat_history = get_chat_history("default", 20)
    for chat in reversed(chat_history):
        with st.chat_message("user" if chat[0] == "user" else "assistant"):
            st.markdown(chat[1])

    if user_message := st.chat_input("Ask Gura..."):
        with st.chat_message("user"): st.markdown(user_message)
        save_chat("user", user_message, "default")
        
        # Logic check
        reply = extract_fd(user_message)
        if not reply:
            context = f"Memories: {get_memories(10)}"
            response = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": user_message}])
            reply = response.choices[0].message.content
            
        save_chat("assistant", reply, "default")
        st.rerun()
