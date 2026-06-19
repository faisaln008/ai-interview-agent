from langchain_core.tools import tool

@tool
def search_tool(query: str) -> str:
    """Search for information about a query."""
    return f"Search results for: {query}"