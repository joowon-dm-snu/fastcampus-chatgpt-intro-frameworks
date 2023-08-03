from kernel import run_function
from semantic_kernel import ContextVariables, SKFunctionBase


async def query_web_search(
    user_message: str,
    web_search_func: SKFunctionBase,
    value_check_func: SKFunctionBase,
    compression_func: SKFunctionBase,
    variables: ContextVariables,
):
    variables["user_message"] = user_message
    variables["web_search_results"] = await run_function(web_search_func, variables)

    has_value = await run_function(value_check_func, variables)

    if has_value == "Y":
        return await run_function(compression_func, variables)
    else:
        return ""
