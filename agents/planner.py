from typing import TypedDict
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from core.state import AgentState

PLANNER_PROMPT = """You are a planning engine. Break down the user's request into clear, actionable steps.

For each step, provide:
- task: Description of what to do
- tool: Which tool to use (code_executor, news_fetcher, chatbot)

Format your response as a JSON array of steps. Example:
[
  {{"task": "Research the topic", "tool": "news_fetcher"}},
  {{"task": "Write code to analyze data", "tool": "code_executor"}}
]

Only provide the JSON array, nothing else."""


def planner_node(state: AgentState) -> dict:
    """
    Decomposes complex user goals into ordered sub-tasks.
    """
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None

    user_request = ""
    if last_message:
        user_request = getattr(last_message, "content", str(last_message))

    model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

    try:
        response = model.invoke(
            [HumanMessage(content=f"{PLANNER_PROMPT}\n\nUser request: {user_request}")]
        )

        import json

        plan_text = response.content.strip()

        if plan_text.startswith("```"):
            plan_text = plan_text.split("```")[1]
            if plan_text.startswith("json"):
                plan_text = plan_text[4:]

        plan = json.loads(plan_text)

        for i, step in enumerate(plan):
            step["status"] = "pending"
            step["result"] = None
            step["step_number"] = i + 1

        return {
            "current_plan": plan,
            "task_history": [],
            "suggestions": [f"Created plan with {len(plan)} steps. Ready to execute?"],
        }
    except Exception as e:
        return {
            "current_plan": None,
            "suggestions": [f"Could not create plan: {str(e)}"],
        }


def plan_executor_node(state: AgentState) -> dict:
    """
    Executes the next pending step in the current plan.
    """
    plan = state.get("current_plan", [])
    task_history = state.get("task_history", [])

    if not plan:
        return {"suggestions": ["No active plan to execute."]}

    pending_steps = [s for s in plan if s.get("status") == "pending"]

    if not pending_steps:
        return {
            "suggestions": ["Plan completed! Any follow-up questions?"],
            "task_history": task_history,
        }

    current_step = pending_steps[0]
    current_step["status"] = "in_progress"

    return {
        "current_plan": plan,
        "suggestions": [
            f"Executing step {current_step['step_number']}: {current_step['task']}"
        ],
    }


def should_continue_planning(state: AgentState) -> bool:
    """Returns True if there are more steps to execute."""
    plan = state.get("current_plan", [])
    if not plan:
        return False
    return any(s.get("status") == "pending" for s in plan)
