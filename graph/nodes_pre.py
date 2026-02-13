from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from config import Config
from memory import memory
import uuid

llm = ChatOllama(model=Config.MODEL_NAME)

def guard_layer(state: AgentState):
    """
    Guard Budget and Token and telemetry.
    Initializes the state if needed.
    """
    return {
        "token_usage": 0, 
        "budget_limit": 5000, 
        "research_data": [], 
        "gaps": [], 
        "iterations": 0,
        "history": state.get("history", [])
,
        "query_id": str(uuid.uuid4())  # Generate unique ID for streaming
    }

def context_retrieval(state: AgentState):
    """
    Memory and context retrieval vector DB.
    """
    query = state["query"]
    print(f"DEBUG: Retrieving context for: {query}")
    
    context_docs = memory.get_context(query)
    formatted_context = "\n".join(context_docs) if context_docs else "No prior context found."
    
    return {"context": [formatted_context]}

def intent_classifier(state: AgentState):
    """
    Intent classifier clarification Orchestrator.
    Determines if the query is clear and what the intent is.
    """
    prompt = ChatPromptTemplate.from_template(
        "Classify the following query into one of these categories: "
        "Research, Bug Fix, Architecture, General Question. "
        "Also determine if the query is clear (True/False). "
        "Return the output as 'Category: <category>, Clear: <True/False>'.\n\n"
        "Query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]})
    
    # Track tokens
    tokens_used = 0
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        tokens_used = response.usage_metadata.get('total_tokens', 0)
    
    content = response.content.strip()
    
    # Simple parsing (can be made more robust with structured output)
    intent = "Research"
    is_clarified = True
    
    if "Clear: False" in content:
        is_clarified = False
    
    # Extract intent crudely for now
    if "Bug Fix" in content: intent = "Bug Fix"
    elif "Architecture" in content: intent = "Architecture"
    elif "General Question" in content: intent = "General Question"
    
    return {
        "intent": intent, 
        "is_clarified": is_clarified,
        "token_usage": state.get("token_usage", 0) + tokens_used
    }