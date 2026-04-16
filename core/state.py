import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Represents the state of our graph.
    The `messages` key is a list of messages. The `add_messages` reducer (or `operator.add`) 
    will append new messages to this list.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # We can add other state keys here later, e.g., 'current_intent' or 'context'
