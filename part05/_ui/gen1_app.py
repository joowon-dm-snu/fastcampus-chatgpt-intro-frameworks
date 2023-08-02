from typing import Dict, List

import requests
import streamlit as st

API_URL = "http://localhost:8000/writer"

DEFAULT_GENRE = "Thriller"
DEFAULT_CHACRACTERS = [
    {"name": "James", "characteristics": "야망에 찬 사업가"},
    {"name": "Kong", "characteristics": "생물학 연구소에서 일하는 유명한 박사, James 와 연인관계"},
    {"name": "Bab", "characteristics": "질투 많은 경쟁사 사장"},
]
DEFAULT_NEWS_TEXT = """기름값 하락 계속…휘발유 6.6원·경유 5.9원↓ 이번 주에도 국내 주유소 휘발유와 경유 판매 가격이 동반 하락했습니다.
한국석유공사 유가정보시스템 오피넷에 따르면 6월 셋째주 전국 주유소 휘발유 평균 판매 가격은 전주보다 6.6원 하락한 리터당 1,575.8원을 기록했습니다.
경유 판매 가격 역시 8.7원 내린 1,387.6원으로 집계됐습니다.
휘발유 가격은 8주째, 경유 가격은 9주 연속 내림세입니다.
대한석유협회 관계자는 "다음 주에도 휘발유·경유 가격은 하향 안정세를 보이겠지만, 그 다음 주부터는 특히 경유 가격이 반등할 가능성이 있다"고 전망했습니다."""


def request_writer_api(
    genre: str,
    characters: List[Dict[str, str]],
    news_text: str,
) -> str:
    resp = requests.post(
        API_URL,
        json={
            "genre": genre,
            "characters": characters,
            "news_text": news_text,
        },
    )
    resp = resp.json()
    return resp["results"]


def init_session_state():
    if "genre" not in st.session_state:
        st.session_state.genre = DEFAULT_GENRE
    if "characters" not in st.session_state:
        st.session_state.characters = DEFAULT_CHACRACTERS
    if "news_text" not in st.session_state:
        st.session_state.news_text = DEFAULT_NEWS_TEXT
    if "result" not in st.session_state:
        st.session_state.result = ""


def input_step1_ui():
    # Step 1: Select genre
    st.subheader("Step 1: Select Genre")
    genres = [
        "Thriller",
        "Fantasy",
        "Sci-Fi",
        "Mystery",
        "Romance",
    ]
    st.session_state.genre = st.selectbox("Select a genre:", genres)


def input_step2_ui():
    # Step 2: Add Characters
    st.subheader("Step 2: Add Characters")

    character_name = st.text_input("Name")
    character_characteristics = st.text_input("Characteristics")

    if st.button("Add Character"):
        st.session_state.characters.append(
            {
                "name": character_name,
                "characteristics": character_characteristics,
            }
        )


def input_step3_ui():
    # Step 3: Add News Article
    st.subheader("Step 3: Add News Article")
    news_text = st.text_area(
        "Paste the news article here", value=st.session_state.news_text
    )
    st.session_state.news_text = news_text

    if st.button("Begin!"):
        st.session_state.result = request_writer_api(
            genre=st.session_state.genre,
            characters=st.session_state.characters,
            news_text=st.session_state.news_text,
        )


def characters_ui():
    st.subheader("Added Characters")

    placeholder = st.empty()
    character_list = []
    for character in st.session_state.characters:
        name, characteristics = character.values()
        character_list.append(f"[{name}]\n{characteristics}")
    placeholder.text("\n".join(character_list))

    # Add a 'Reset' button to reset the characters
    if st.button("Reset"):
        placeholder.empty()
        st.session_state.characters = []
        st.success("Characters have been reset.")


def result_ui():
    st.subheader("Result")
    st.text_area("Your Novel", st.session_state.result, height=600)


def main():
    st.title("[Part 06] Writer GPT")

    init_session_state()

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        input_step1_ui()
    with col2:
        input_step2_ui()
    with col3:
        input_step3_ui()

    st.markdown("---")
    characters_ui()

    st.markdown("---")
    result_ui()


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    main()
