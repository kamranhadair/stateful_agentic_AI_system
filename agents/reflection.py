from typing import TypedDict
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from core.state import AgentState

MAX_RETRIES = 3


def reflection_node(state: AgentState) -> dict:
    """
    Analyzes the last tool execution result and determines if retry is needed.
    Handles self-correction by refining parameters and retrying failed operations.
    """
    messages = state.get("messages", [])
    retry_count = state.get("retry_count", 0)

    last_message = messages[-1] if messages else None

    needs_retry = False
    if last_message:
        content = getattr(last_message, "content", "")
        if isinstance(content, str):
            error_indicators = ["error", "failed", "exception", "traceback", "timeout"]
            needs_retry = any(err in content.lower() for err in error_indicators)

    if needs_retry and retry_count < MAX_RETRIES:
        return {
            "retry_count": retry_count + 1,
            "suggestions": [f"Attempting retry {retry_count + 1}/{MAX_RETRIES}..."],
        }
    elif retry_count >= MAX_RETRIES:
        return {
            "suggestions": [
                "Max retries reached. Consider simplifying your request or breaking it into smaller steps."
            ]
        }
    else:
        return {"retry_count": 0, "suggestions": generate_suggestions(state)}


def generate_suggestions(state: AgentState) -> list[str]:
    """
    Generate proactive suggestions based on current context.
    """
    suggestions = []
    intent = state.get("intent", "")
    messages = state.get("messages", [])

    if "code" in intent:
        suggestions.append("Would you like me to explain the code I just generated?")
        suggestions.append("Want to modify or extend this code?")
    elif len(messages) > 2:
        suggestions.append("Is there anything else you'd like me to help with?")
        suggestions.append("Would you like to try a different approach?")

    return suggestions[:2]


def should_retry(state: AgentState) -> bool:
    """Determines if the operation should be retried."""
    retry_count = state.get("retry_count", 0)
    messages = state.get("messages", [])

    if retry_count >= MAX_RETRIES:
        return False

    last_message = messages[-1] if messages else None
    if last_message:
        content = getattr(last_message, "content", "")
        if isinstance(content, str):
            error_indicators = ["error", "failed", "exception", "traceback"]
            return any(err in content.lower() for err in error_indicators)

    return False
