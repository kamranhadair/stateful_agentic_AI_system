import os
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from typing import Literal

from core.state import AgentState
from agents.chatbot import chatbot_node
from agents.intent_detector import intent_detector_node, route_based_on_intent
from agents.planner import planner_node, should_continue_planning
from agents.reflection import reflection_node
from agents.tool_agent import get_tool_agent


def tool_executor_node(state: AgentState) -> dict:
    """
    Executes tools using the tool agent.
    """
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None

    user_request = ""
    if last_message:
        user_request = getattr(last_message, "content", str(last_message))

    try:
        agent = get_tool_agent()
        response = agent.invoke({"messages": [last_message]})

        tool_messages = []
        for msg in response.get("messages", []):
            msg_type = getattr(msg, "type", "")
            if msg_type in ["tool", "ai"]:
                tool_messages.append(msg)

        return {"messages": tool_messages}
    except Exception as e:
        return {"messages": []}


def route_for_execution(state: AgentState) -> Literal["tool_executor", "chatbot"]:
    """
    Routes to tool executor or chatbot based on intent.
    """
    intent = state.get("intent", "simple_chat")

    if (
        "code" in intent
        or "complex" in intent
        or "news" in intent
        or "information" in intent
        or "research" in intent
    ):
        return "tool_executor"
    else:
        return "chatbot"


def create_graph():
    """
    Creates and compiles the proactive StateGraph.
    Includes intent detection, tool execution, and self-correction.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_detector", intent_detector_node)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tool_executor", tool_executor_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("reflection", reflection_node)

    workflow.add_edge(START, "intent_detector")

    workflow.add_conditional_edges(
        "intent_detector",
        route_for_execution,
        {"tool_executor": "tool_executor", "chatbot": "chatbot"},
    )

    workflow.add_edge("chatbot", "reflection")
    workflow.add_edge("tool_executor", "reflection")

    workflow.add_edge("reflection", END)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


def create_simple_graph():
    """
    Creates a simple reactive graph (original behavior).
    """
    workflow = StateGraph(AgentState)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_edge(START, "chatbot")
    workflow.add_edge("chatbot", END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
