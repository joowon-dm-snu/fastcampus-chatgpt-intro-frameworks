import time

import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000/qna"


def request_chat_api(user_message: str) -> str:
    url = API_BASE_URL

    resp = requests.post(
        url,
        json={
            "user_message": user_message,
        },
    )
    resp = resp.json()
    print(resp)
    return resp["answer"]


def init_streamlit():
    st.title("Simple chat")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def chat_main():
    if message := st.chat_input(""):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": message})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(message)

        # Display assistant response in chat message container
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
    init_streamlit()
    chat_main()
