import sys
import os
from time import sleep
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import logging
logging.basicConfig(level=logging.INFO)
import streamlit as st
import uuid

from app_core import genAnswer


def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_id = str(uuid.uuid4())

with st.sidebar:
    st.title("LLMs Playground")
    st.button("New Chat", type="primary", use_container_width=True, on_click=reset_chat)

st.title("Chat with AI-tutor")

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = genAnswer(prompt, st.session_state.chat_id)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)