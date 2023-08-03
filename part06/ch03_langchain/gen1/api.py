import os
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()


app = FastAPI()


class UserRequest(BaseModel):
    user_message: str


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


@app.post("/qna")
def generate_novel(req: UserRequest) -> Dict[str, str]:
    qna_llm = ChatOpenAI(temperature=0.1, max_tokens=500, model="gpt-3.5-turbo")
    qna_prompt_template = ChatPromptTemplate.from_template(
        template=read_prompt_template(os.path.join(CUR_DIR, "prompt_template.txt"))
    )
    qna_chain = LLMChain(llm=qna_llm, prompt=qna_prompt_template, output_key="output")

    result = qna_chain(req.dict())

    return {"answer": result["output"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
