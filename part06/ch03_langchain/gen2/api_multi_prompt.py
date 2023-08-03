"""
Langchain의 기능 중 하나인 LLMRouterChain, MultiPromptChain을 사용하여 API를 만들어보는 예제입니다.
"""

from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from multi_prompt_chains import multi_prompt_chain
from pydantic import BaseModel

load_dotenv()


app = FastAPI()


class UserRequest(BaseModel):
    user_message: str


@app.post("/qna")
def gernerate_answer(req: UserRequest) -> Dict[str, str]:
    context = req.dict()
    context["input"] = context["user_message"]
    answer = multi_prompt_chain.run(context)

    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
