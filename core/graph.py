from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal

from core.state import AgentState
from agents.chatbot import chatbot_node
from agents.intent_detector import intent_detector_node, route_based_on_intent
from agents.planner import planner_node, plan_executor_node, should_continue_planning
from agents.reflection import reflection_node, should_retry


def create_graph():
    """
    Creates and compiles the proactive StateGraph.
    Includes intent detection, planning, and self-correction.
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_detector", intent_detector_node)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("plan_executor", plan_executor_node)
    workflow.add_node("reflection", reflection_node)

    workflow.add_edge(START, "intent_detector")

    workflow.add_conditional_edges(
        "intent_detector",
        route_based_on_intent,
        {"chatbot": "chatbot", "tool_agent": "planner", "news_agent": "chatbot"},
    )

    workflow.add_edge("chatbot", "reflection")
    workflow.add_edge("planner", "plan_executor")

    workflow.add_conditional_edges(
        "plan_executor",
        lambda state: (
            "reflection" if not should_continue_planning(state) else "plan_executor"
        ),
    )

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
