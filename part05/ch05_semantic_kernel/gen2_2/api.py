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

    # output_key 의 이름이 무조건 'input'으로 고정되기 때문에 프롬프트의 변수명을 {$input}으로 해줘야 합니다.
    # 따라서 gen2_1 에서 실습했던 {$novel_idea}, {$novel_outline}, {$novel_plot}는 활용하기 어렵습니다.
    # 각 스텝에서 이전 결과물들을 한개만 사용하는 경우에 잘 작동 가능합니다.
    # WritePlot 스킬에서 <아이디어> 섹션을 삭제하고 $input으로 바꿔줬습니다.
    res = await kernel.run_async(
        writer_skill["ExtractIdea"],
        writer_skill["WriteOutline"],
        writer_skill["WritePlot"],
        input_vars=variables,
    )
    variables["novel_plot"] = res.result

    return {"results": "해당 파일은 Plot 까지만 생성합니다.\n\n" + variables["novel_plot"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
