import os

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAITextEmbedding,
)
from semantic_kernel.connectors.memory.chroma import ChromaMemoryStore

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(CUR_DIR, "skills")

# 코드와 디렉토리를 정리하면서 database 폴더의 위치를 gen3로 변경했습니다.
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, "database", "chroma-persist")


def init_kernel():
    kernel = sk.Kernel()
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
    skills = {}
    skills["AnswerSkill"] = kernel.import_semantic_skill_from_directory(
        SKILL_DIR, "AnswerSkill"
    )
    skills["IntentSkill"] = kernel.import_semantic_skill_from_directory(
        SKILL_DIR, "IntentSkill"
    )
    skills["SearchSkill"] = kernel.import_semantic_skill_from_directory(
        SKILL_DIR, "SearchSkill"
    )
    skills["NativeSearchSkill"] = kernel.import_native_skill_from_directory(
        os.path.join(SKILL_DIR, "SearchSkill"), "GoogleSearch"
    )

    return kernel, skills
