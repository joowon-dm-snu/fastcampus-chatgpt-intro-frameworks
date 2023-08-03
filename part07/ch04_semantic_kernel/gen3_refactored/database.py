from semantic_kernel import Kernel

CHROMA_COLLECTION_NAME = "fastcampus-bot"


async def query_db(
    kernel: Kernel,
    query: str,
    collection: str = CHROMA_COLLECTION_NAME,
    limit: int = 3,
    min_relevance_score: float = 0.7,
    doc_len_limit: int = 500,
) -> str:
    related_docs = await kernel.memory.search_async(
        collection=collection,
        query=query,
        limit=limit,
        min_relevance_score=min_relevance_score,
    )
    related_docs = [doc.text[:doc_len_limit] for doc in related_docs]

    return "\n".join(related_docs)
