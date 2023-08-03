import os

from dotenv import load_dotenv
from langchain.chains import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate

load_dotenv()


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
BUG_STEP1_PROMPT_TEMPLATE = os.path.join(
    CUR_DIR, "prompt_templates", "bug_say_sorry.txt"
)
BUG_STEP2_PROMPT_TEMPLATE = os.path.join(
    CUR_DIR, "prompt_templates", "bug_request_context.txt"
)
ENHANCE_STEP1_PROMPT_TEMPLATE = os.path.join(
    CUR_DIR, "prompt_templates", "enhancement_say_thanks.txt"
)
INTENT_PROMPT_TEMPLATE = os.path.join(CUR_DIR, "prompt_templates", "parse_intent.txt")


def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


def create_chain(llm, template_path, output_key):
    return LLMChain(
        llm=llm,
        prompt=ChatPromptTemplate.from_template(
            template=read_prompt_template(template_path)
        ),
        output_key=output_key,
        verbose=True,
    )


llm = ChatOpenAI(temperature=0.1, max_tokens=200, model="gpt-3.5-turbo")

bug_step1_chain = create_chain(
    llm=llm,
    template_path=BUG_STEP1_PROMPT_TEMPLATE,
    output_key="bug-step1",
)
bug_step2_chain = create_chain(
    llm=llm,
    template_path=BUG_STEP2_PROMPT_TEMPLATE,
    output_key="bug-step2",
)
enhance_step1_chain = create_chain(
    llm=llm,
    template_path=ENHANCE_STEP1_PROMPT_TEMPLATE,
    output_key="enhance-step1",
)
parse_intent_chain = create_chain(
    llm=llm,
    template_path=INTENT_PROMPT_TEMPLATE,
    output_key="intent",
)
default_chain = ConversationChain(llm=llm, output_key="text")
