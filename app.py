import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from core.state import AgentState
from core.graph import create_graph
from tools.code_executor import execute_python_code
from tools.news_fetcher import get_news_tool

st.set_page_config(page_title="Stateful Agentic AI", page_icon="🤖", layout="wide")

st.title("🤖 Stateful Agentic AI System")
st.markdown("---")


def init_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "tool_history" not in st.session_state:
        st.session_state.tool_history = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = "default"


def get_llm(temperature=0.5):
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=temperature)


def get_tool_agent():
    model = get_llm(temperature=0.3)
    tools = [execute_python_code, get_news_tool()]
    return create_react_agent(model, tools)


def get_chatbot():
    return create_graph()


def display_messages():
    for msg in st.session_state.chat_history:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")

        with st.chat_message(role):
            if isinstance(content, str):
                st.markdown(content)
            else:
                st.json(content)


def display_tool_history():
    if st.session_state.tool_history:
        with st.expander("🔧 Tool Executions", expanded=True):
            for i, tool in enumerate(st.session_state.tool_history, 1):
                st.text(f"{i}. {tool['name']}")
                st.code(
                    tool["input"][:200] + "..."
                    if len(tool["input"]) > 200
                    else tool["input"],
                    language="python",
                )
                if tool.get("output"):
                    st.text(f"Output: {tool['output'][:300]}...")
                st.markdown("---")


init_session()

with st.sidebar:
    st.header("⚙️ Settings")

    mode = st.selectbox("Select Mode", ["💬 Chatbot", "🔧 Tool Agent"], index=0)

    st.markdown("---")

    new_thread = st.text_input("Session ID", value=st.session_state.thread_id)
    if new_thread != st.session_state.thread_id:
        st.session_state.thread_id = new_thread
        st.session_state.chat_history = []
        st.session_state.tool_history = []
        st.rerun()

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.tool_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("**API Status**")
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        st.success(f"✅ Groq: Connected")
    else:
        st.error("❌ Groq: No API Key")

    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        st.success(f"✅ Tavily: Connected")
    else:
        st.warning("⚠️ Tavily: Not configured")

col_main, col_tools = st.columns([3, 1])

with col_main:
    display_messages()

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("🤔 Thinking..."):
            try:
                if mode == "💬 Chatbot":
                    app = get_chatbot()
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    response = app.invoke(
                        {"messages": [HumanMessage(content=prompt)]}, config
                    )
                    response_text = response["messages"][-1].content
                else:
                    app = get_tool_agent()
                    response = app.invoke({"messages": [HumanMessage(content=prompt)]})
                    response_text = response["messages"][-1].content

                    for msg in response["messages"]:
                        if hasattr(msg, "type") and msg.type == "tool":
                            st.session_state.tool_history.append(
                                {
                                    "name": "tool",
                                    "input": str(msg.content),
                                    "output": "",
                                }
                            )

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response_text}
                )

                with st.chat_message("assistant"):
                    st.markdown(response_text)

            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": error_msg}
                )
                st.error(error_msg)

with col_tools:
    st.header("📊 Activity")
    st.metric("Messages", len(st.session_state.chat_history))
    st.metric("Tools Used", len(st.session_state.tool_history))

    if st.session_state.tool_history:
        with st.expander("🔧 Tool History", expanded=False):
            for i, tool in enumerate(st.session_state.tool_history, 1):
                st.text(f"{i}. {tool['name']}")
