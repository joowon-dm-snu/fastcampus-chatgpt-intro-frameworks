from pprint import pprint
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel

load_dotenv()

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
def generate_novel(req: UserRequest) -> Dict[str, str]:
    writer_llm = ChatOpenAI(temperature=0.1, max_tokens=500, model="gpt-3.5-turbo")
    writer_prompt_template = ChatPromptTemplate.from_template(
        template=read_prompt_template("prompt_template.txt")
    )
    writer_chain = LLMChain(
        llm=writer_llm, prompt=writer_prompt_template, output_key="output"
    )

    result = writer_chain(req.dict())

    return {"results": result["output"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
