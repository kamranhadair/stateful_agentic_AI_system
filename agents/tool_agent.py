import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools.code_executor import execute_python_code
from tools.news_fetcher import get_news_tool


def get_tool_agent():
    """
    Creates a Tool-Augmented Agent using LangGraph's prebuilt ReAct agent constructor.
    This agent implicitly knows how to reason about and execute tools.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    # We use a Groq model
    model = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3)

    # Instantiate the list of available tools
    tools = [execute_python_code, get_news_tool()]

    # Create the ReAct agent graph based on the model and tools
    # We will nest this agent inside our overall main state graph later, or use it standalone limits.
    app = create_react_agent(model, tools)

    return app
