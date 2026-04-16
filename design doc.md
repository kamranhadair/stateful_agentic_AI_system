# System Design Document: Stateful Agentic AI System

## 1. Introduction
This document outlines the technical design, architectural patterns, and data flow for the **Proactive** Stateful Agentic AI application. The system leverages LangGraph to provide stateful, graph-based routing for various AI functionalities, including proactive planning, autonomous tool execution, and intelligent suggestions. Unlike reactive systems that wait for explicit commands, this system anticipates user needs and takes initiative.

## 2. High-Level Architecture
The system employs a graph-like structure where each node represents an agentic step, planning block, or tool execution. The overarching graph routes user queries intelligently, breaking down complex goals and executing plans autonomously.

### 2.1 Component Flow
```mermaid
graph TD
    User((User Interface)) --> AppEntry[Main App (Streamlit)]
    AppEntry --> IntentDetector[Intent Detection & Context Analysis]
    
    IntentDetector -->|Complex Goal| PlannerNode[Planning Engine]
    IntentDetector -->|Simple Query| ChatbotNode[Proactive Chatbot]
    IntentDetector -->|Direct Action| ToolAgentNode[Tool Agent]
    
    PlannerNode --> PlanReview{Plan Review}
    PlanReview -->|Approved| ExecuteNode[Execute Plan]
    PlanReview -->|Modify| PlannerNode
    ExecuteNode -->|Step 1| ToolAgentNode
    ExecuteNode -->|Step 2| ToolAgentNode
    ExecuteNode -->|Step N| ToolAgentNode
    
    ExecuteNode --> ReflectionNode[Reflection & Refinement]
    ReflectionNode -->|Success| SuggestNode[Proactive Suggestions]
    ReflectionNode -->|Failure| PlannerNode
    
    SuggestNode --> ProgressTracker[Progress Tracker]
    ProgressTracker --> Memory[State Checkpointer]
    Memory --> AppEntry
    
    ToolAgentNode --> PythonREPL[Python Executor]
    ToolAgentNode --> SearchAPI[Tavily News API]
    ToolAgentNode --> SuggestNode
```

## 3. Data Schema & State Management
LangGraph manages conversational state via a state dictionary incrementally passed between nodes.

### 3.1 Enhanced Global State Schema
```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # Conversation messages
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Current user intent (detected or explicit)
    intent: str
    
    # Context for proactive suggestions
    context: dict
    
    # Planning and execution state
    current_plan: list[dict] | None  # [{task, status, result}, ...]
    execution_mode: str  # "reactive" | "proactive"
    
    # Proactive suggestions pending user confirmation
    suggestions: list[str]
    
    # Task history for progress tracking
    task_history: list[dict]
```

## 4. Proactive Sub-Agent Designs

### 4.1 Intent Detection & Context Analysis
- **Objective:** Understand user intent beyond explicit requests.
- **Capabilities:**
  - Detects complex vs simple queries
  - Identifies potential goals from conversation context
  - Triggers proactive suggestion engine when relevant
  - Determines if autonomous execution is appropriate

### 4.2 Planning Engine
- **Objective:** Decompose complex goals into executable tasks.
- **Workflow:**
  1. *Analyze:* Parse user goal into sub-tasks
  2. *Plan:* Create ordered execution sequence
  3. *Review:* Present plan to user for confirmation (optional)
  4. *Execute:* Run tasks with progress updates
  5. *Adapt:* Modify plan if failures occur
- **Safety:** Max 10 steps per plan, requires confirmation for destructive actions

### 4.3 Proactive Chatbot
- **Objective:** Handle standard dialogue with anticipation.
- **Prompting:** Set up with system prompt that includes proactive behavior guidelines.
- **Memory Strategy:** Uses LangGraph's built-in `MemorySaver` checkpointer.
- **Proactive Features:**
  - Offers relevant suggestions based on context
  - Suggests follow-up questions
  - Reminds of incomplete goals

### 4.4 Tool-Augmented Agent (Proactive)
- **Objective:** Plan and execute Python code autonomously.
- **Workflow:**
  1. *Plan:* Break down request into logic steps
  2. *Code:* Generate Python code using Groq LLM
  3. *Execute:* Run code via isolated REPL tool
  4. *Validate:* Check output and errors
  5. *Reflect:* If failed, refine and retry (max 3 attempts)
  6. *Suggest:* Propose improvements or next steps
- **Safety Strategy:** 30s timeout, max 3 retries, sandboxed execution

### 4.5 Proactive News Aggregator
- **Objective:** Fetch and synthesize news with proactive discovery.
- **Capabilities:**
  - Proactively suggests trending topics
  - Offers to set up periodic news updates
  - Summarizes news into digestible formats
- **Workflow:**
  1. LLM extracts search topics from conversation
  2. Agent calls Web Search tool
  3. Synthesizes results into structured summary
  4. Suggests related topics for further exploration

### 4.6 Reflection & Refinement
- **Objective:** Self-correct and improve execution quality.
- **Behavior:**
  - Analyzes success/failure of each step
  - Identifies potential improvements
  - Triggers replan if goals cannot be achieved
  - Generates proactive suggestions for user

### 4.7 Proactive Suggestions Engine
- **Objective:** Anticipate user needs and offer relevant help.
- **Trigger Conditions:**
  - After completing a task (suggest next steps)
  - After detecting a potential goal (offer to help)
  - When conversation suggests relevant tools
  - When news/results suggest user interest
- **User Control:** Users can disable proactive suggestions

## 5. Proactive Behavior Modes

### 5.1 Reactive Mode (Default)
- Waits for explicit user commands
- Executes tools only when asked
- Minimal suggestions

### 5.2 Proactive Mode
- Anticipates user needs
- Breaks down complex goals automatically
- Offers relevant suggestions
- Executes multi-step plans autonomously
- Provides progress updates

## 6. Deployment Architecture
- **Platform:** Hugging Face Spaces (Docker/Python environment)
- **Dependencies:** Managed via `requirements.txt`
- **Secrets Management:** API keys via Hugging Face Space secrets
- **User Interface:** Streamlit with proactive UI elements (progress bars, suggestion cards)

## 7. Implementation Milestones
- **Phase 1:** Environment setup and repository structure. ✅
- **Phase 2:** LangGraph base layout & Chatbot functionality (with memory). ✅
- **Phase 3:** Integration of News Aggregator tools. ✅
- **Phase 4:** Implementation of the Code Execution tool & Tool-Agent logic. ✅
- **Phase 5:** UI integration and Streamlit deployment. ✅
- **Phase 6:** Add Intent Detection & Context Analysis.
- **Phase 7:** Implement Planning Engine with goal decomposition.
- **Phase 8:** Add Reflection & Self-Correction loop.
- **Phase 9:** Integrate Proactive Suggestions Engine.
- **Phase 10:** Final testing and Hugging Face deployment pipeline.
