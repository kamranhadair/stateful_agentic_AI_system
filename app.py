import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from langchain_core.messages import HumanMessage
from core.graph import create_graph, create_simple_graph
from core.state import AgentState

st.set_page_config(page_title="Proactive AI Agent", page_icon="🤖", layout="wide")

st.title("🤖 Proactive Stateful Agentic AI")
st.markdown("---")


def init_session():
    defaults = {
        "chat_history": [],
        "tool_history": [],
        "suggestions": [],
        "current_plan": None,
        "thread_id": "default",
        "proactive_mode": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_graph():
    if st.session_state.proactive_mode:
        return create_graph()
    return create_simple_graph()


def display_suggestions():
    if st.session_state.suggestions:
        st.markdown("**💡 Suggestions:**")
        cols = st.columns(len(st.session_state.suggestions))
        for i, (col, suggestion) in enumerate(zip(cols, st.session_state.suggestions)):
            with col:
                if st.button(f"→ {suggestion[:40]}...", key=f"sug_{i}"):
                    st.session_state.chat_history.append(
                        {"role": "user", "content": suggestion}
                    )
                    st.rerun()


def display_plan_progress():
    if st.session_state.current_plan:
        with st.expander("📋 Current Plan Progress", expanded=True):
            for step in st.session_state.current_plan:
                status_emoji = {
                    "pending": "⏳",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                }.get(step.get("status", "pending"), "⚪")
                st.text(f"{status_emoji} Step {step['step_number']}: {step['task']}")


def display_messages():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


init_session()

with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.proactive_mode = st.toggle("🚀 Proactive Mode", value=True)

    st.markdown("---")

    new_thread = st.text_input("Session ID", value=st.session_state.thread_id)
    if new_thread != st.session_state.thread_id:
        st.session_state.thread_id = new_thread
        st.session_state.chat_history = []
        st.session_state.current_plan = None
        st.rerun()

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.current_plan = None
        st.session_state.suggestions = []
        st.rerun()

    st.markdown("---")
    st.markdown("**📊 Activity**")
    st.metric("Messages", len(st.session_state.chat_history))

    mode_status = "Proactive" if st.session_state.proactive_mode else "Reactive"
    st.info(f"Mode: {mode_status}")

    st.markdown("---")
    st.markdown("**🔑 API Status**")
    if os.getenv("GROQ_API_KEY"):
        st.success("✅ Groq Connected")
    else:
        st.error("❌ No API Key")

display_plan_progress()
display_suggestions()
display_messages()

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("🤔 Thinking..."):
        try:
            app = get_graph()
            config = {"configurable": {"thread_id": st.session_state.thread_id}}

            result = app.invoke({"messages": [HumanMessage(content=prompt)]}, config)

            response = result["messages"][-1].content

            if "suggestions" in result and result["suggestions"]:
                st.session_state.suggestions = result["suggestions"]

            if "current_plan" in result and result["current_plan"]:
                st.session_state.current_plan = result["current_plan"]

        except Exception as e:
            response = f"⚠️ Error: {str(e)}"

    st.session_state.chat_history.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

    if st.session_state.suggestions:
        st.rerun()
