import os

from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

load_dotenv()

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, "chroma-persist")
CHROMA_COLLECTION_NAME = "fastcampus-bot"


if __name__ == "__main__":
    from pprint import pprint

    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=OpenAIEmbeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
    )

    docs = db.similarity_search("i want to know about planner")

    # pprint(docs)

    retriever = db.as_retriever()
    retriever.get_relevant_documents("i want to know about planner")

    pprint(docs)
