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

    # 프롬프트 안에서 Function을 실행시키는 방식을 이용하여 코드에서는 최종 함수만 실행하는 예제
    res = await kernel.run_async(
        writer_skill["WritePlot"],
        input_vars=variables,
    )
    variables["novel_plot"] = res.result

    return {"results": "해당 파일은 Plot 까지만 생성합니다.\n\n" + variables["novel_plot"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
