from typing import Dict, List

import semantic_kernel as sk
from dotenv import load_dotenv
from fastapi import FastAPI
from init_kernel import init_kernel
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

INTENT_LIST = """
    bug: Related to a bug, vulnerability, unexpected error with an existing feature
    documentation: Changes to documentation and examples, like .md, .rst, .ipynb files. Changes to the docs/ folder
    enhancement: A large net-new component, integration, or chain. Use sparingly. The largest features
    improvement: Medium size change to existing code to handle new use-cases
    nit: Small modifications/deletions, fixes, deps or improvements to existing code or docs
    question: A specific question about the codebase, product, project, or how to use a feature
    refactor: A large refactor of a feature(s) or restructuring of many files
"""


class UserRequest(BaseModel):
    user_message: str


@app.post("/qna")
async def generate_novel(req: UserRequest) -> Dict[str, str]:
    kernel, skills = init_kernel()

    variables = sk.ContextVariables(variables=req.dict())
    variables["intent_list"] = INTENT_LIST
    intent = await kernel.run_async(
        skills["IntentSkill"]["ParseIntent"], input_vars=variables
    )
    intent = intent.result

    answer = ""
    if intent == "bug":
        step1 = await kernel.run_async(
            skills["AnswerSkill"]["BugSaySorry"], input_vars=variables
        )
        answer += step1.result

        step2 = await kernel.run_async(
            skills["AnswerSkill"]["BugRequestContext"], input_vars=variables
        )
        answer += step2.result

    elif intent == "enhancement":
        step1 = await kernel.run_async(
            skills["AnswerSkill"]["EnhanceSayThanks"], input_vars=variables
        )
        answer += step1.result

    else:
        answer = "hi"

    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
