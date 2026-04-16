import os
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

def get_news_tool():
    """
    Returns the appropriate news fetching tool based on whether the Tavily API key is set.
    """
    if os.getenv("TAVILY_API_KEY"):
        return TavilySearchResults(
            max_results=3, 
            description="Search the web for news, latest events, and real-time information."
        )
    else:
        # Fallback dummy tool if no key is provided
        @tool
        def generic_news_search(query: str) -> str:
            """Search the web for news and current events."""
            return "Notice: TAVILY_API_KEY is not set. Real-time news search is disabled."
        return generic_news_search
