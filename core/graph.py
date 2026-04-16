from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from core.state import AgentState
from agents.chatbot import chatbot_node

def create_graph():
    """
    Creates and compiles the StateGraph for our main agentic flow.
    Currently, it simply connects the user directly to the basic chatbot.
    """
    # 1. Initialize the StateGraph with our custom state schema
    workflow = StateGraph(AgentState)
    
    # 2. Add our nodes (currently just the basic chatbot)
    workflow.add_node("chatbot", chatbot_node)
    
    # 3. Define the edges
    # START is a special node that designates the entry point
    workflow.add_edge(START, "chatbot")
    # From chatbot, we go to END (the execution finishes and returns state to the user)
    workflow.add_edge("chatbot", END)
    
    # 4. Initialize Checkpointer for state persistence / memory
    memory = MemorySaver()
    
    # 5. Compile the graph
    app = workflow.compile(checkpointer=memory)
    
    return app
