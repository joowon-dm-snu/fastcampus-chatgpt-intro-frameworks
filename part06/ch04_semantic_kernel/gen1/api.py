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
    user_message: str


@app.post("/qna")
async def generate_novel(req: UserRequest) -> Dict[str, str]:
    kernel = sk.Kernel()
    kernel.add_chat_service(
        "gpt-3.5-turbo",
        OpenAIChatCompletion(
            "gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
    )
    answer_skill = kernel.import_semantic_skill_from_directory(CUR_DIR, "AnswerSkill")
    qna_function = answer_skill["QuestionAnswer"]

    variables = sk.ContextVariables(variables=req.dict())
    res = await kernel.run_async(qna_function, input_vars=variables)
    res = res.result

    return {"answer": res}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
