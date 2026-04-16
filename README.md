# Stateful Agentic AI System

A production-ready, stateful AI agent system built with LangGraph and Groq that remembers past interactions, reasons through tasks, and deploys tools to achieve specific user intents.

## Features

- **Basic Chatbot** - Conversational AI with memory persistence using LangGraph's MemorySaver
- **Tool-Augmented Agent** - ReAct-based agent with Python code execution and web search capabilities
- **Code Executor** - Safely execute Python code in an isolated sandbox (30s timeout)
- **AI News Aggregator** - Fetch and summarize latest news via Tavily search API

## Tech Stack

- **Orchestration**: LangGraph
- **LLM Provider**: Groq (llama-3.3-70b-versatile)
- **UI**: Streamlit
- **Search**: Tavily

## Project Structure

```
stateful_agent/
├── agents/             # Agent node definitions
│   ├── chatbot.py      # Basic chatbot agent
│   └── tool_agent.py    # Tool-augmented ReAct agent
├── core/               # Core logic and state
│   ├── graph.py        # LangGraph state graph
│   └── state.py        # State schema definitions
├── tools/              # Custom tools
│   ├── code_executor.py # Python code execution
│   └── news_fetcher.py # Web news search
├── ui/                 # UI components (reserved)
├── app.py              # Main Streamlit application
└── requirements.txt    # Dependencies
```

## Setup

1. **Clone the repository**
```bash
git clone https://github.com/kamranhadair/stateful_agentic_AI_system.git
cd stateful_agentic_AI_system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GROQ_API_KEY="your_groq_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"  # Optional
```

5. **Run the application**
```bash
streamlit run app.py
```

## Usage

### Chatbot Mode
Select "Chatbot" mode in the sidebar for general conversation with memory persistence across sessions.

### Tool Agent Mode
Select "Tool Agent" mode to:
- Execute Python code (ask: "write and run Python code to calculate fibonacci")
- Search for news (ask: "what are the latest AI news?")

### Session Management
- Use Session ID to maintain conversation history across sessions
- Clear Chat button to reset conversation

## API Keys

- **Groq**: Get your API key from [console.groq.com](https://console.groq.com/keys)
- **Tavily**: Get your API key from [tavily.com](https://tavily.com) (optional)

## License

MIT License
