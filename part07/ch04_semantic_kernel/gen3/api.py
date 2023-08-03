from typing import Dict

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
CHROMA_COLLECTION_NAME = "fastcampus-bot"


class UserRequest(BaseModel):
    user_message: str


@app.post("/qna")
async def generate_answer(req: UserRequest) -> Dict[str, str]:
    kernel, skills = init_kernel()

    variables = sk.ContextVariables(variables=req.dict())
    variables["intent_list"] = INTENT_LIST
    intent = await kernel.run_async(
        skills["IntentSkill"]["ParseIntent"], input_vars=variables
    )
    intent = intent.result

    if intent == "enhancement":
        answer = await kernel.run_async(
            skills["AnswerSkill"]["EnhanceSayThanks"], input_vars=variables
        )
        answer = answer.result

    else:
        related_materials = await kernel.memory.search_async(
            collection=CHROMA_COLLECTION_NAME,
            query=req.user_message,
            limit=4,
            min_relevance_score=0.7,
        )
        related_materials = [mat.text for mat in related_materials]
        variables["related_materials"] = "\n".join(related_materials)

        print("Related Materials:", len(related_materials))

        if intent == "bug":
            answer = ""
            step1 = await kernel.run_async(
                skills["AnswerSkill"]["BugAnalyze"], input_vars=variables
            )
            variables["bug_analysis"] = step1.result
            answer += step1.result

            step2 = await kernel.run_async(
                skills["AnswerSkill"]["BugSolution"], input_vars=variables
            )
            answer += step2.result
        else:  # Normal Question
            web_search_results = await kernel.run_async(
                skills["NativeSearchSkill"]["GoogleSearch"], input_vars=variables
            )
            variables["web_search_results"] = web_search_results.result

            has_value = await kernel.run_async(
                skills["SearchSkill"]["SearchValueCheck"], input_vars=variables
            )
            print("Web Search Results:")
            print(variables["web_search_results"])
            print(f"Has Value: {has_value}")

            if has_value == "Y":
                compressed_results = await kernel.run_async(
                    skills["SearchSkill"]["SearchCompress"], input_vars=variables
                )
            else:
                compressed_results = ""

            variables["compressed_web_search_results"] = compressed_results

            answer = await kernel.run_async(
                skills["AnswerSkill"]["NormalQuestion"], input_vars=variables
            )
            answer = answer.result

    return {"answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
