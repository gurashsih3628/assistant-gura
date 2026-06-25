import re
import streamlit as st
from groq import Groq
# This import will only work if database.py is in the same folder as app.py
from database import (
    init_db, save_chat, get_chat_history, save_memory, 
    get_memories, save_fd, get_active_fds, get_fds_by_owner, 
    close_fd, delete_fd
)

# -------------------------
# CONFIGURATION
# -------------------------
# Ensure secrets are defined in Streamlit Cloud Dashboard (Settings -> Secrets)
if "PASSWORD" not in st.secrets or "GROQ_API_KEY" not in st.secrets:
    st.error("🔑 Missing secrets in Streamlit dashboard settings. Please check your Secrets configuration.")
    st.stop()

PASSWORD = st.secrets["PASSWORD"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Initialize Database and Client
init_db()
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# Session State for Login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# -------------------------
# COMMAND PROCESSOR
# -------------------------
def process_command(user_message):
    msg = user_message.strip().upper()
    
    # ADD FD Command
    if msg.startswith("ADD FD"):
        try:
            owner = re.search(r"Owner:\s*(.*?)\s*Bank:", user_message, re.IGNORECASE).group(1)
            bank = re.search(r"Bank:\s*(.*?)\s*Amount:", user_message, re.IGNORECASE).group(1)
            amount = float(re.search(r"Amount:\s*([\d.]+)", user_message, re.IGNORECASE).group(1))
            start = re.search(r"Start:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)
            maturity = re.search(r"Maturity:\s*([0-9\-]+)", user_message, re.IGNORECASE).group(1)
            save_fd(owner, bank, amount, start_date=start, maturity_date=maturity)
            return f"✅ FD successfully saved for {owner} at {bank}."
        except Exception as e:
            return f"❌ Add FD format error. Use: 'ADD FD Owner: Mom Bank: SBI Amount: 50000 Start: 2026-01-01 Maturity: 2027-01-01'. Error: {e}"

    # ACTIVE FDS Command
    if msg == "ACTIVE FDS":
        fds = get_active_fds()
        if not fds: return "📋 No active FDs found."
        res = "📋 **ACTIVE FDs:**\n\n"
        for f in fds:
            res += f"- **ID {f[0]}**: {f[1]} (Bank: {f[2]}) | ₹{f[3]:,} | Maturity: {f[6]}\n"
        return res

    # SHOW FDS Command
    if msg.startswith("SHOW FDS"):
        owner = user_message[8:].strip()
        if not owner: return "Please specify an owner. Example: 'SHOW FDS Mom'"
        fds = get_fds_by_owner(owner)
        if not fds: return f"No active FDs found for {owner}."
        res = f"📋 **FDs for {owner.upper()}:**\n\n"
        for f in fds:
            res += f"- **ID {f[0]}**: Bank: {f[1]} | ₹{f[2]:,} | Maturity: {f[5]}\n"
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
            st.error("Invalid password.")
else:
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Control Panel")
        if st.button("Sign Out"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.divider()
        st.subheader("📊 Data Explorer")
        if st.expander("View All FDs"):
            st.json(get_active_fds())

    st.title("💬 Gura Personal Assistant")
    
    # Load Chat History
    history = get_chat_history("default", 15)
    for chat in reversed(history):
        with st.chat_message("user" if chat[0] == "user" else "assistant"):
            st.markdown(chat[1])

    # Chat Interaction
    if user_message := st.chat_input("Ask Gura..."):
        with st.chat_message("user"):
            st.markdown(user_message)
        save_chat("user", user_message, "default")
        
        # Priority 1: Check Commands
        reply = process_command(user_message)
        
        # Priority 2: Use LLM
        if not reply:
            response = client.chat.completions.create(
                model=MODEL, 
                messages=[{"role": "user", "content": user_message}]
            )
            reply = response.choices[0].message.content
            
        save_chat("assistant", reply, "default")
        st.rerun()
