import os
from dotenv import load_dotenv
import streamlit as st
import requests
import json
import uuid

load_dotenv()

# API Configuration
API_URL = "http://fastapi:8080/callback/test"
API_HEADERS = {
    "Content-Type": "application/json",
}

# Initialize thread_id in session state if it doesn't exist
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Streamlit App UI
st.set_page_config(page_title="SmallTalk2Rec")

# Replicate Credentials
with st.sidebar:
    st.title("대화형 영화 추천")
    
    # selectbox 레이블 공백 제거
    st.markdown(
        """
        <style>
        .stSelectbox label {  /* This targets the label element for selectbox */
            display: none;  /* Hides the label element */
        }
        .stSelectbox div[role='combobox'] {
            margin-top: -20px; /* Adjusts the margin if needed */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("영화어때???")
st.subheader("영화 추천해드릴게요! 🎬")
st.write("")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "ai",
            "content": "안녕하세요 영화 추천 챗봇입니다. 무엇을 도와드릴까요?",
        }
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    # Generate new thread_id when clearing chat
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = [
        {
            "role": "ai",
            "content": "안녕하세요 영화 추천 챗봇입니다. 무엇을 도와드릴까요?",
        }
    ]

st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "ai":
    with st.chat_message("ai"):
        with st.spinner("Thinking..."):
            try:
                # Prepare the request payload
                payload = {
                    "user_id": st.session_state.thread_id,
                    "message": st.session_state.messages[-1]["content"],
                }
                
                # Make the API request
                response = requests.post(
                    API_URL,
                    headers=API_HEADERS,
                    json=payload,
                    timeout=60
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse the response
                response_data = response.json()
                ai_message = response_data["template"]["outputs"][0]["simpleText"]["text"]
                
                # Display the response
                placeholder = st.empty()
                placeholder.markdown(ai_message)
                
                # Add the response to session state
                message = {"role": "ai", "content": ai_message}
                st.session_state.messages.append(message)
                
            except requests.exceptions.RequestException as e:
                error_message = f"Error communicating with the API: {str(e)}"
                st.error(error_message)
                message = {"role": "ai", "content": "죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해 주세요."}
                st.session_state.messages.append(message)