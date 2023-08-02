import os
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chains import LLMChain, SequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel

load_dotenv()


app = FastAPI()

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
STEP1_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/1_extract_idea.txt")
STEP2_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/2_write_outline.txt")
STEP3_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/3_write_plot.txt")
WRITE_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates/6_write_chapter.txt")


class UserRequest(BaseModel):
    genre: str
    characters: List[Dict[str, str]]
    news_text: str


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


def create_chain(llm, template_path, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=read_prompt_template(template_path),
        ),
        output_key=output_key,
        verbose=True,
    )


@app.post("/writer")
def generate_novel(req: UserRequest) -> Dict[str, str]:
    writer_llm = ChatOpenAI(temperature=0.1, max_tokens=300, model="gpt-3.5-turbo")

    # 아이디어 뽑기 체인 생성
    novel_idea_chain = create_chain(writer_llm, STEP1_PROMPT_TEMPLATE, "novel_idea")

    # 아웃라인 작성 체인 생성
    novel_outline_chain = create_chain(
        writer_llm, STEP2_PROMPT_TEMPLATE, "novel_outline"
    )

    # 플롯 작성 체인 생성
    novel_plot_chain = create_chain(writer_llm, STEP3_PROMPT_TEMPLATE, "novel_plot")

    # 챕터 작성 체인 생성
    novel_chapter_chain = create_chain(writer_llm, WRITE_PROMPT_TEMPLATE, "output")

    preprocess_chain = SequentialChain(
        chains=[
            novel_idea_chain,
            novel_outline_chain,
            novel_plot_chain,
        ],
        input_variables=["genre", "characters", "news_text"],
        output_variables=["novel_idea", "novel_outline", "novel_plot"],
        verbose=True,
    )

    context = req.dict()
    context = preprocess_chain(context)

    context["novel_chapter"] = []
    for chapter_number in range(1, 3):
        context["chapter_number"] = chapter_number
        context = novel_chapter_chain(context)
        context["novel_chapter"].append(context["output"])

    contents = "\n\n".join(context["novel_chapter"])
    return {"results": contents}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
