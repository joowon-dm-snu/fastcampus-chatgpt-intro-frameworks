import os
from typing import Dict, List

import openai
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
STEP1_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/1_extract_idea.txt")
STEP2_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/2_write_outline.txt")
STEP3_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/3_write_plot.txt")
WRITE_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/6_write_chapter.txt")


class UserRequest(BaseModel):
    genre: str
    characters: List[Dict[str, str]]
    news_text: str


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


def request_gpt_api(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    max_token: int = 500,
    temperature: float = 0.8,
) -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_token,
        temperature=temperature,
    )
    return response.choices[0].message.content


@app.post("/writer")
def generate_novel(req: UserRequest) -> Dict[str, str]:
    context = {}

    # 아이디어 뽑기
    novel_idea_prompt_template = read_prompt_template(STEP1_PROMPT_TEMPLATE)
    novel_idea_prompt = novel_idea_prompt_template.format(
        genre=req.genre,
        characters=req.characters,
        news_text=req.news_text,
    )
    context["novel_idea"] = request_gpt_api(novel_idea_prompt)
    print("=============")
    print("Idea:")
    print(context["novel_idea"])

    # 뽑은 아이디어로 아웃라인 작성
    novel_outline_prompt_template = read_prompt_template(STEP2_PROMPT_TEMPLATE)
    novel_outline_prompt = novel_outline_prompt_template.format(
        genre=req.genre,
        characters=req.characters,
        news_text=req.news_text,
        # **context
        novel_idea=context["novel_idea"],
    )
    context["novel_outline"] = request_gpt_api(novel_outline_prompt)
    print("=============")
    print("Outline:")
    print(context["novel_outline"])

    # 아웃라인으로 소설 플롯 작성
    novel_plot_prompt_tempalte = read_prompt_template(STEP3_PROMPT_TEMPLATE)
    novel_plot_prompt = novel_plot_prompt_tempalte.format(
        genre=req.genre,
        characters=req.characters,
        news_text=req.news_text,
        novel_idea=context["novel_idea"],
        novel_outline=context["novel_outline"],
    )
    context["novel_plot"] = request_gpt_api(novel_plot_prompt)
    print("=============")
    print("Plot:")
    print(context["novel_plot"])

    # 플롯으로 소설 챕터 작성
    write_prompt_template = read_prompt_template(WRITE_PROMPT_TEMPLATE)
    context["novel_chapter"] = []
    for chapter_number in range(1, 3):
        write_prompt = write_prompt_template.format(
            genre=req.genre,
            characters=req.characters,
            news_text=req.news_text,
            novel_idea=context["novel_idea"],
            novel_outline=context["novel_outline"],
            novel_plot=context["novel_plot"],
            chapter_number=chapter_number,
        )
        context["novel_chapter"].append(request_gpt_api(write_prompt))
        print("=============")
        print(f"Chapter {chapter_number}:")
        print(context["novel_chapter"][chapter_number - 1])

    contents = "\n\n".join(context["novel_chapter"])
    return {"results": contents}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
