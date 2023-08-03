import os
from typing import List, Tuple

from semantic_kernel import ContextVariables, Kernel, SKFunctionBase
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAITextEmbedding,
)
from semantic_kernel.connectors.memory.chroma import ChromaMemoryStore

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(CUR_DIR, "skills")
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, "database", "chroma-persist")

SKILL_LIST = [
    ("AnswerSkill", "AnswerSkill", True),
    ("IntentSkill", "IntentSkill", True),
    ("SearchSkill", "SearchSkill", True),
    ("NativeSearchSkill", "NativeGoogleSearch", False),
]


def init_kernel():
    kernel = Kernel()
    kernel.add_chat_service(
        "gpt-3.5-turbo",
        OpenAIChatCompletion(
            "gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
    )
    kernel.add_text_embedding_generation_service(
        "ada",
        OpenAITextEmbedding(
            "text-embedding-ada-002",
            os.getenv("OPENAI_API_KEY"),
        ),
    )
    kernel.register_memory_store(
        memory_store=ChromaMemoryStore(persist_directory=CHROMA_PERSIST_DIR)
    )

    return kernel


def import_skills(kernel: Kernel, skill_list: List[Tuple[str, str, bool]] = None):
    skill_list = skill_list or SKILL_LIST

    skills = {}
    for skill_name, skill_dir, is_semantic in skill_list:
        if is_semantic:
            skills[skill_name] = kernel.import_semantic_skill_from_directory(
                SKILL_DIR, skill_dir
            )
        else:
            skills[skill_name] = kernel.import_native_skill_from_directory(
                SKILL_DIR, skill_dir
            )

    return skills


async def run_function(function: SKFunctionBase, variables: ContextVariables) -> str:
    result = await function.invoke_async(variables=variables)
    return result.result
