import os
from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from core.state import AgentState

INTENT_PROMPT = """You are an intent detection system. Analyze the user's message and determine:

1. **simple_chat** - General conversation, greetings, casual questions
2. **code_request** - User wants to write, run, or execute code
3. **news_request** - User wants news, information, or research
4. **complex_goal** - Multi-step task that needs planning

Be concise. Return only the intent type."""


@tool
def detect_intent(message: str) -> str:
    """Detect the user's intent from their message."""
    model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    response = model.invoke(
        [HumanMessage(content=f"{INTENT_PROMPT}\n\nUser message: {message}")]
    )
    return response.content.strip().lower()


def intent_detector_node(state: AgentState) -> dict:
    """
    Analyzes user message and determines routing intent.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    last_message = state["messages"][-1]
    if hasattr(last_message, "content"):
        user_message = last_message.content
    else:
        user_message = str(last_message)

    intent = detect_intent.invoke(user_message)

    return {
        "intent": intent,
        "context": {"original_message": user_message},
        "execution_mode": "proactive" if intent == "complex_goal" else "reactive",
    }


def route_based_on_intent(
    state: AgentState,
) -> Literal["chatbot", "planner"]:
    """
    Routes to the appropriate agent based on detected intent.
    News/code/complex requests go to planner -> tool_agent.
    Simple chat goes to chatbot.
    """
    intent = state.get("intent", "simple_chat")

    if (
        "code" in intent
        or "complex" in intent
        or "news" in intent
        or "information" in intent
        or "research" in intent
    ):
        return "planner"
    else:
        return "chatbot"
