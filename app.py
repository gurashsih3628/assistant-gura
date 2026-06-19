import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

# Check API key
if not api_key:
    st.error("GROQ_API_KEY not found in .env file")
    st.stop()

# Create Groq client
client = Groq(api_key=api_key)

# Page setup
st.set_page_config(
    page_title="Gura Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Gura Assistant")
st.write("Gura is alive and running!")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
prompt = st.chat_input("Talk to Gura...")

if prompt:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.write(prompt)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.write(reply)

    except Exception as e:
        st.error(f"Error: {e}")