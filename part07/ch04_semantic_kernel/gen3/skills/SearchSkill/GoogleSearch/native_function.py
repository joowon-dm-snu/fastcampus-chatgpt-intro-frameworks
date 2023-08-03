import os
from typing import Any, List

from dotenv import load_dotenv
from semantic_kernel.orchestration.sk_context import SKContext
from semantic_kernel.skill_definition import sk_function

load_dotenv()


def _google_search_results(engine, search_term: str, **kwargs: Any) -> List[dict]:
    cse = engine.cse()
    res = cse.list(q=search_term, cx=os.environ["GOOGLE_CSE_ID"], **kwargs).execute()
    return res.get("items", [])


class GoogleSearchSkill:
    @sk_function(
        description="",
        name="GoogleSearch",
        input_description="",
    )
    async def search_google_get_texts(self, context: SKContext) -> str:
        from googleapiclient.discovery import build

        engine = build("customsearch", "v1", developerKey=os.environ["GOOGLE_API_KEY"])
        query = " ".join([context["chat_history"], context["user_message"]]).replace(
            '"', ""
        )
        print(query)
        num_results = 4

        snippets = []
        results = _google_search_results(engine, query, num=num_results)
        if len(results) == 0:
            return "No good Google Search Result was found"
        for result in results:
            if "snippet" in result:
                snippets.append(result["snippet"])

        return "\n\n".join(snippets)
