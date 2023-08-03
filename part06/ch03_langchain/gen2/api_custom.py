"""
Langchain의 기능 중 하나인 LLMRouterChain, MultiPromptChain를 사용하지 않고 동일하게 구현한 예제입니다.
"""
import os
from typing import Dict

from custom_chains import (
    bug_step1_chain,
    bug_step2_chain,
    default_chain,
    enhance_step1_chain,
    parse_intent_chain,
    read_prompt_template,
)
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()


app = FastAPI()


class UserRequest(BaseModel):
    user_message: str


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
INTENT_LIST_TXT = os.path.join(CUR_DIR, "prompt_templates", "intent_list.txt")


@app.post("/qna")
def gernerate_answer(req: UserRequest) -> Dict[str, str]:
    context = req.dict()
    context["input"] = context["user_message"]
    context["intent_list"] = read_prompt_template(INTENT_LIST_TXT)

    # intent = parse_intent_chain(context)["intent"]
    intent = parse_intent_chain.run(context)

    if intent == "bug":
        answer = ""
        for step in [bug_step1_chain, bug_step2_chain]:
            answer += step.run(context)
            answer += "\n\n"
    elif intent == "enhancement":
        answer = enhance_step1_chain.run(context)
    else:
        answer = default_chain.run(context)

    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
