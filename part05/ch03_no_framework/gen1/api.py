import os
from typing import Dict, List

import openai
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


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
    prompt_template = read_prompt_template("prompt_template.txt")

    prompt = prompt_template.format(
        genre=req.genre,
        characters=req.characters,
        news_text=req.news_text,
    )

    return {"results": request_gpt_api(prompt)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
