import os
from typing import Dict, List

import semantic_kernel as sk
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

load_dotenv()

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()


class UserRequest(BaseModel):
    genre: str
    characters: List[Dict[str, str]]
    news_text: str


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


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
    write_novel_function = writer_skill["WriteNovel"]

    variables = sk.ContextVariables(variables=req.dict())
    variables["characters"] = "\n".join(
        [f"{c['name']}: {c['characteristics']}" for c in variables["characters"]]
    )
    res = await kernel.run_async(write_novel_function, input_vars=variables)
    res = res.result

    return {"results": res}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
