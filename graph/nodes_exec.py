from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState
from config import Config
import os
from prompts.research_prompts import GAP_ANALYSIS_PROMPT, RESEARCH_SYNTHESIS_PROMPT
from utils.streaming import get_streaming_buffer

llm = ChatOllama(model=Config.MODEL_NAME)

# Custom DDG Tool to bypass langchain-community import issues
from duckduckgo_search import DDGS

class CustomDuckDuckGoSearch:
    def invoke(self, query):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                return str(results)
        except Exception as e:
            return f"Search error: {e}"

# Initialize Search Tools
tavily_api_key = os.getenv("TAVILY_API_KEY")
if tavily_api_key:
    search_tool = TavilySearchResults(max_results=3)
else:
    search_tool = CustomDuckDuckGoSearch()

def planner_router(state: AgentState):
    """
    Planner and router.
    Decides between 'quick' and 'deep' mode.
    """
    # Build conversation history context
    history = state.get("history", [])
    history_text = ""
    if history:
        history_text = "\n\nPrevious conversation:\n" + "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in history[-4:]  # Last 4 messages
        ]) + "\n"
    
    prompt = ChatPromptTemplate.from_template(
        "Analyze the query complexity. "
        "If it requires simple fact checking or code snippet, choose 'quick'. "
        "If it requires extensive research, comparison, or architectural design, choose 'deep'. "
        "Return ONLY the mode: 'quick' or 'deep'.\\n\\n"
        "{history_context}"
        "Current Query: {query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"], "history_context": history_text})
    mode = response.content.strip().lower()
    
    # Track tokens
    tokens_used = 0
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        tokens_used = response.usage_metadata.get('total_tokens', 0)
    
    if "deep" in mode:
        return {"mode": "deep", "token_usage": state.get("token_usage", 0) + tokens_used}
    return {"mode": "quick", "token_usage": state.get("token_usage", 0) + tokens_used}

def quick_mode_executor(state: AgentState):
    """
    Quick mode executor with token-by-token streaming.
    """
    query_id = state.get("query_id", "")
    buffer = get_streaming_buffer(query_id) if query_id else None
    
    full_response = ""
    tokens_used = 0
    
    # Build conversation history for context
    history = state.get("history", [])
    messages = []
    
    # Add conversation history
    for msg in history[-6:]:  # Last 6 messages for context
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        else:
            messages.append(SystemMessage(content=msg['content']))
    
    # Add current query
    messages.append(HumanMessage(content=state["query"]))
    
    # Use streaming with conversation history
    for chunk in llm.stream(messages):
        token = chunk.content
        full_response += token
        
        # Add to streaming buffer for real-time display
        if buffer:
            buffer.add_chunk(token)
    
    # Mark streaming complete
    if buffer:
        buffer.mark_complete()
    
    # Track token metadata (if available)
    # Note: streaming doesn't provide usage_metadata, estimate based on content
    tokens_used = len(full_response.split()) * 2  # Rough estimate
    
    # Return complete state
    return {
        "research_data": [{"content": full_response, "source": "LLM Knowledge"}],
        "final_report": full_response,
        "token_usage": state.get("token_usage", 0) + tokens_used
    }

def deep_mode_orchestrator(state: AgentState):
    """
    Deep mode executor: Orchestrator -> Agent Research
    Performs search and evidence gathering.
    """
    query = state["query"]
    iteration = state.get("iterations", 0)
    gaps = state.get("gaps", [])
    history = state.get("history", [])
    
    # Build context-aware query from history
    search_query = query
    if history:
        # Get last user message for context
        last_messages = [msg['content'] for msg in history[-2:] if msg['role'] == 'user']
        if last_messages:
            context_hint = " (in context of: " + ", ".join(last_messages) + ")"
            search_query = query + context_hint
    
    # If we have gaps, refine the search query
    if gaps:
        search_query = f"{search_query} focusing on {', '.join(gaps)}"
        
    print(f"DEBUG: Executing Search for: {search_query} (Iter: {iteration})")
    
    try:
        if isinstance(search_tool, TavilySearchResults):
            # Tavily returns list of dicts
            results = search_tool.invoke({"query": search_query})
            # Format Tavily results to extract content
            if isinstance(results, list):
                formatted_content = []
                for r in results:
                    if isinstance(r, dict):
                        title = r.get('title', r.get('url', 'Untitled'))
                        content_text = r.get('content', r.get('snippet', ''))
                        url = r.get('url', '')
                        formatted_content.append(f"**{title}**\n{content_text}\nSource: {url}\n")
                content = "\n---\n".join(formatted_content) if formatted_content else str(results)
            else:
                content = str(results)
        else:
            # Custom duckduckgo returns formatted string via custom invoke
            content = search_tool.invoke(search_query)

    except Exception as e:
        content = f"Search failed: {e}"

    return {
        "research_data": state.get("research_data", []) + [{"content": content, "source": "Web Search"}],
        "iterations": iteration + 1
    }

def gap_analysis_node(state: AgentState):
    """
    Cross references and Gap analysis.
    Checks if enough information is gathered.
    """
    data = state.get("research_data", [])
    combined_content = "\\n".join([d["content"] for d in data])
    history = state.get("history", [])
    
    # Build history context
    history_text = ""
    if history:
        history_text = "\nConversation history: " + "; ".join([
            f"{msg['role']}: {msg['content'][:100]}" for msg in history[-3:]
        ])
    
    prompt = GAP_ANALYSIS_PROMPT
    
    chain = prompt | llm
    response = chain.invoke({
        "query": state["query"] + history_text, 
        "research_data": combined_content[:5000]  # Context limit
    })
    
    # Track tokens
    tokens_used = 0
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        tokens_used = response.usage_metadata.get('total_tokens', 0)
    
    # Simple parsing
    try:
        # Looking for "Confidence: 0.X"
        import re
        score_match = re.search(r"Confidence:\\s*([0-9.]+)", response.content)
        score = float(score_match.group(1)) if score_match else 0.5
        
        gaps = []
        if "Gaps:" in response.content:
            gaps_str = response.content.split("Gaps:")[1].strip()
            gaps = [g.strip() for g in gaps_str.split(",")]
            
    except:
        score = 0.5
        gaps = ["Could not parse analysis"]

    return {
        "confidence_score": score, 
        "gaps": gaps,
        "token_usage": state.get("token_usage", 0) + tokens_used
    }

def structured_synthesis_node(state: AgentState):
    """
    Structure reasoning and synthesis with streaming.
    """
    query_id = state.get("query_id", "")
    buffer = get_streaming_buffer(query_id) if query_id else None
    
    data = state.get("research_data", [])
    combined_content = "\\n".join([d["content"] for d in data])
    history = state.get("history", [])
    
    # Build conversation context
    history_context = ""
    if history:
        history_context = "\\n\\nConversation context:\\n" + "\\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in history[-4:]
        ]) + "\\n"
    
    prompt = RESEARCH_SYNTHESIS_PROMPT
    
    full_response = ""
    tokens_used = 0
    
    # Stream the synthesis with conversation context
    chain = prompt | llm
    query_with_context = state["query"] + history_context
    
    for chunk in chain.stream({"query": query_with_context, "context": combined_content[:8000]}):
        token = chunk.content
        full_response += token
        
        # Add to streaming buffer
        if buffer:
            buffer.add_chunk(token)
    
    # Mark complete
    if buffer:
        buffer.mark_complete()
    
    cleaned_report = full_response.replace("```markdown", "").replace("```", "").strip()
    tokens_used = len(cleaned_report.split()) * 2  # Estimate
    
    return {
        "final_report": cleaned_report,
        "token_usage": state.get("token_usage", 0) + tokens_used
    }