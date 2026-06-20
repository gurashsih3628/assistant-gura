import streamlit as st
from groq import Groq

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Gura Assistant",
    page_icon="🤖",
    layout="centered"
)

# -------------------------
# CUSTOM CSS
# -------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

.main-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: bold;
}

.login-box {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #333;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# LOGIN SYSTEM
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.markdown(
        "<div class='main-title'>🔒 Gura Assistant</div>",
        unsafe_allow_html=True
    )

    st.markdown("### Private Access Required")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login", use_container_width=True):

        if password == st.secrets["PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect Password")

    st.stop()

# -------------------------
# LOAD API KEY
# -------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------
# HEADER
# -------------------------
st.title("🤖 Gura Assistant")
st.caption("Powered by Llama 3.3 70B Versatile")

# -------------------------
# CHAT MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Gura, a personal AI assistant. "
                "You help with coding, studies, finance, "
                "productivity, and everyday questions. "
                "Be concise, accurate, and helpful."
            )
        }
    ]

# -------------------------
# DISPLAY CHAT
# -------------------------
for message in st.session_state.messages:

    if message["role"] != "system":

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# -------------------------
# CHAT INPUT
# -------------------------
prompt = st.chat_input("Talk to Gura...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.7,
            max_tokens=1024
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        with st.chat_message("assistant"):
            st.markdown(reply)

    except Exception as e:
        st.error(f"Error: {str(e)}")

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:

    st.header("⚙️ Gura Controls")

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "You are Gura, a personal AI assistant. "
                    "You help with coding, studies, finance, "
                    "productivity, and everyday questions."
                )
            }
        ]

        st.rerun()

    if st.button("🚪 Logout"):

        st.session_state.authenticated = False
        st.rerun()

    st.info("Model: Llama 3.3 70B Versatile")
