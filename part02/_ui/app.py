import time

import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000/chat"


def request_chat_api(
    message: str,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 500,
    temperature: float = 0.9,
) -> str:
    resp = requests.post(
        API_BASE_URL,
        json={
            "message": message,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )
    resp = resp.json()
    return resp["message"]


def init_session_state():
    st.title("Simple chat")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def chat_main():
    init_session_state()

    if message := st.chat_input(""):
        st.session_state.messages.append({"role": "user", "content": message})
        with st.chat_message("user"):
            st.markdown(message)

        assistant_response = request_chat_api(message)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for lines in assistant_response.split("\n"):
                for chunk in lines.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response)
                full_response += "\n"
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    chat_main()
