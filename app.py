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
# API KEY
# -------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------
# TITLE
# -------------------------
st.title("🤖 Gura Assistant")
st.caption("Powered by Llama 3.3 70B on Groq")

# -------------------------
# MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Gura, a personal AI assistant. "
                "You help with coding, studies, finance, "
                "productivity, and everyday questions. "
                "Be concise, accurate, and helpful. "
                "Do not invent details about your own model."
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
# USER INPUT
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

    st.header("Gura Controls")

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

    st.info("Model: Llama 3.3 70B Versatile")
