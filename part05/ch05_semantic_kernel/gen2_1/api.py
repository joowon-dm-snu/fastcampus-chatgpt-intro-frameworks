import json
import os
from typing import Dict, List

import semantic_kernel as sk
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

load_dotenv()

app = FastAPI()

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


class UserRequest(BaseModel):
    genre: str
    characters: List[Dict[str, str]]
    news_text: str


@app.post("/writer")
async def generate_novel(req: UserRequest) -> Dict[str, str]:
    kernel = sk.Kernel()
    kernel.add_chat_service(
        "gpt-3.5-turbo",
        OpenAIChatCompletion(
            "gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
    )
    writer_skill = kernel.import_semantic_skill_from_directory(CUR_DIR, "WriterSkill")

    variables = sk.ContextVariables(variables=req.dict())
    variables["characters"] = json.dumps(variables["characters"], indent=4)

    # 아이디어 뽑기
    res = await kernel.run_async(writer_skill["ExtractIdea"], input_vars=variables)
    variables["novel_idea"] = res.result

    # 아웃라인 작성
    res = await kernel.run_async(writer_skill["WriteOutline"], input_vars=variables)
    variables["novel_outline"] = res.result

    # 플롯 작성
    res = await kernel.run_async(writer_skill["WritePlot"], input_vars=variables)
    variables["novel_plot"] = res.result

    # 플롯으로 소설 챕터 작성
    chapters = []
    for chapter_number in range(1, 3):
        variables["chapter_number"] = chapter_number
        res = await kernel.run_async(writer_skill["WriteChapter"], input_vars=variables)
        chapters.append(res.result)

    contents = "\n\n".join(chapters)
    return {"results": contents}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
