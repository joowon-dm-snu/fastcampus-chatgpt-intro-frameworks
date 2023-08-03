import os

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.connectors.memory.chroma import ChromaMemoryStore

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, "chroma-persist")
CHROMA_COLLECTION_NAME = "fastcampus-bot"


async def query_memory(query):
    results = await kernel.memory.search_async(
        collection=CHROMA_COLLECTION_NAME,
        query=query,
        limit=3,
        min_relevance_score=0.7,
    )
    return [result.text for result in results]


QUERY = """
I want to change relevance score threshold

```python
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, "chroma-persist")
CHROMA_COLLECTION_NAME = "fastcampus-bot"


async def query_memory(query):
    results = await kernel.memory.search_async(
        collection=CHROMA_COLLECTION_NAME,
        query=query,
        limit=3,
    )
    return [result.text for result in results]
```
"""
if __name__ == "__main__":
    import asyncio

    from dotenv import load_dotenv

    load_dotenv()

    kernel = sk.Kernel()
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

    result = asyncio.run(query_memory(QUERY))

    print(result[1])
