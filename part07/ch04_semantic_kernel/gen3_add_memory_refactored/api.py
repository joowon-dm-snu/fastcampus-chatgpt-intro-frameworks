import os
from typing import Dict

from database import query_db
from dotenv import load_dotenv
from fastapi import FastAPI
from kernel import import_skills, init_kernel, run_function
from memory import (
    get_chat_history,
    load_conversation_history,
    log_bot_message,
    log_user_message,
    save_conversation_history,
)
from pydantic import BaseModel
from semantic_kernel import ContextVariables
from web_search import query_web_search

load_dotenv()

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
INTENT_LIST_TXT = os.path.join(CUR_DIR, "configs", "intent_list.txt")


app = FastAPI()


class UserRequest(BaseModel):
    user_message: str


@app.post("/qna/{conversation_id}")
async def generate_answer(req: UserRequest, conversation_id: str) -> Dict[str, str]:
    kernel = init_kernel()
    skills = import_skills(kernel)

    variables = ContextVariables(variables=req.dict())
    variables["intent_list"] = open(INTENT_LIST_TXT).read().strip()
    variables["chat_history"] = get_chat_history(conversation_id)

    intent = await run_function(skills["IntentSkill"]["ParseIntent"], variables)

    if intent == "bug":
        variables["related_documents"] = await query_db(kernel, req.user_message)

        answer = ""
        for step in [
            skills["AnswerSkill"]["BugAnalyze"],
            skills["AnswerSkill"]["BugSolution"],
        ]:
            answer += await run_function(step, variables)
            answer += "\n\n"

    elif intent == "enhancement":
        answer = await run_function(
            skills["AnswerSkill"]["EnhanceSayThanks"], variables
        )

    else:
        variables["related_documents"] = await query_db(kernel, req.user_message)
        variables["compressed_web_search_results"] = await query_web_search(
            req.user_message,
            web_search_func=skills["NativeSearchSkill"]["GoogleSearch"],
            value_check_func=skills["SearchSkill"]["SearchValueCheck"],
            compression_func=skills["SearchSkill"]["SearchCompress"],
            variables=variables,
        )
        answer = await run_function(skills["AnswerSkill"]["NormalQuestion"], variables)

    history = load_conversation_history(conversation_id)
    log_user_message(history, req.user_message)
    log_bot_message(history, answer)
    save_conversation_history(conversation_id, history)

    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
