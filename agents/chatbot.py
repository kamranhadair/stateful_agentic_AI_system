import os
from langchain_groq import ChatGroq
from core.state import AgentState

# We define a basic chatbot function that will act as a node in our graph.
def chatbot_node(state: AgentState):
    """
    A basic chatbot node that invokes the Groq LLM with the current conversation history.
    """
    # Ensure GROQ_API_KEY is present
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    
    # Initialize the Groq Chat model
    # We use llama3-70b-8192 as a strong default model on Groq.
    model = ChatGroq(
        model_name="llama3-70b-8192", 
        temperature=0.5
    )
    
    # Invoke the model passing the existing conversation history
    response = model.invoke(state["messages"])
    
    # We return a dictionary exactly matching the keys in AgentState we want to update.
    # Because of `operator.add`, this new message will be appended to the state's messages list.
    return {"messages": [response]}
