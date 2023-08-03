import json
import os
from typing import Dict, List

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(CUR_DIR, "chat_histories")


def load_conversation_history(conversation_id: str):
    file_path = os.path.join(HISTORY_DIR, f"{conversation_id}.json")

    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("[]")

    with open(file_path, "r") as file:
        history = json.loads(file.read())

    return history


def save_conversation_history(conversation_id: str, history: List[Dict[str, str]]):
    file_path = os.path.join(HISTORY_DIR, f"{conversation_id}.json")

    with open(file_path, "w") as file:
        file.write(json.dumps(history))


def log_user_message(history: List[Dict[str, str]], user_message: str):
    history.append({"role": "user", "message": user_message})


def log_bot_message(history: List[Dict[str, str]], bot_message: str):
    history.append({"role": "bot", "message": bot_message})


def get_chat_history(conversation_id: str, limit: int = 10):
    history = load_conversation_history(conversation_id)

    chat_history_str = ""
    for message in history[: limit * -1]:
        if message["role"] == "user":
            chat_history_str += f"User: {message['message']}\n"
        else:
            chat_history_str += f"Bot: {message['message']}\n"

    return chat_history_str
