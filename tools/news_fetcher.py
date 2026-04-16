import os
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


def get_news_tool():
    """
    Returns the AI news fetching tool based on whether the Tavily API key is set.
    """
    if os.getenv("TAVILY_API_KEY"):
        return TavilySearchResults(
            max_results=5,
            description="Search for latest AI news, artificial intelligence updates, and ML breakthroughs.",
            search_depth="basic",
        )
    else:

        @tool
        def ai_news_search(query: str) -> str:
            """Search for latest AI news and artificial intelligence updates."""
            return "Notice: TAVILY_API_KEY is not set. AI news search is disabled."

        return ai_news_search


def get_web_search_tool():
    """
    Returns a general web search tool.
    """
    if os.getenv("TAVILY_API_KEY"):
        return TavilySearchResults(
            max_results=5,
            description="Search the web for any general information, facts, and real-time data.",
            search_depth="basic",
        )
    else:

        @tool
        def web_search(query: str) -> str:
            """Search the web for general information."""
            return "Notice: TAVILY_API_KEY is not set. Web search is disabled."

        return web_search
