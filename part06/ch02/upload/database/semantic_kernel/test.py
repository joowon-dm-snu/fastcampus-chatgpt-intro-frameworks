import os

from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.connectors.memory.chroma import ChromaMemoryStore

load_dotenv()

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, "chroma-persist")
CHROMA_COLLECTION_NAME = "fastcampus-bot"


async def search_async(kernel, query):
    return await kernel.memory.search_async(
        collection=CHROMA_COLLECTION_NAME,
        query=query,
        limit=3,
        min_relevance_score=0,
    )


if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    kernel = Kernel()
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

    docs = asyncio.run(search_async(kernel, "i want to know about planner"))
    pprint([doc.text for doc in docs])
