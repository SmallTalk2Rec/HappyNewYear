import os
from dotenv import load_dotenv
import streamlit as st

from agent.builder import graph

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "smalltalk2rec"

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
    st.session_state.messages = [
        {
            "role": "ai",
            "content": "안녕하세요 영화 추천 챗봇입니다. 무엇을 도와드릴까요?",
        }
    ]


st.sidebar.button("Clear Chat History", on_click=clear_chat_history)


# User-provided prompt
if prompt := st.chat_input():  # (disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "ai":
    with st.chat_message("ai"):
        with st.spinner("Thinking..."):
            # response = generate_llama2_response(prompt)
            response = graph.invoke({"messages": st.session_state.messages})["messages"][-1].content

            placeholder = st.empty()
            placeholder.markdown(response)
    message = {"role": "ai", "content": response}
    st.session_state.messages.append(message)
