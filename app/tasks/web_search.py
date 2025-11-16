from app.tasks.base import Task
from duckduckgo_search import DDGS


def _resolver(query: str) -> str:
    """
    Perform a web search and return relevant results with source links.

    Args:
        query: The search query string

    Returns:
        A formatted string with search results and URLs
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query["text"], max_results=5)

        if not results:
            return "No results found for your query."

        # Format results with title and URL
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            url = result.get('href', '')
            snippet = result.get('body', '')

            formatted_results.append(
                f"{i}. {title}\n"
                f"   URL: {url}\n"
                f"   {snippet[:150]}{'...' if len(snippet) > 150 else ''}"
            )

        return "Here are some relevant links:\n\n" + "\n\n".join(formatted_results)

    except Exception as e:
        return f"Error performing search: {str(e)}"


task = Task(
    name="Web Search",
    description=(
        "Search the web and return a concise set of relevant results and source links. "
        "Designed to extract and surface factual snippets, authoritative references, and "
        "URLs that support user queries. Input: user information request or question. Output: "
        "a ranked list of short snippets with source URLs. Edge cases: ambiguous queries, "
        "requests for personal data or paid content. The resolver should favor high-quality "
        "domains and include snippet context when possible."
    ),
    resolver=_resolver,
)
