import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Represents the state of our proactive agent graph.
    """

    messages: Annotated[Sequence[BaseMessage], operator.add]

    intent: str

    context: dict

    current_plan: list[dict] | None

    execution_mode: str

    suggestions: list[str]

    task_history: list[dict]

    retry_count: int
