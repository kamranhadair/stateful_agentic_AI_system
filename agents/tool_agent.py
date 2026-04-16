import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools.code_executor import execute_python_code
from tools.news_fetcher import get_news_tool, get_web_search_tool


def get_tool_agent():
    """
    Creates a Tool-Augmented Agent using LangGraph's prebuilt ReAct agent constructor.
    This agent has access to code execution, AI news, and general web search.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    model = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3)

    tools = [execute_python_code, get_news_tool(), get_web_search_tool()]

    app = create_react_agent(model, tools)

    return app
