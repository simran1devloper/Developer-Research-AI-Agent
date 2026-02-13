# tools/search_tools.py
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document

# 1. Tavily is the "Gold Standard" for LLM Research Agents
# Note: Requires TAVILY_API_KEY in your .env
def get_tavily_search():
    return TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_raw_content=False, # We want clean snippets for Gemma's context window
        include_answer=True
    )

# 2. DuckDuckGo as a zero-cost fallback
def get_ddg_search():
    return DuckDuckGoSearchRun()

def web_search_tool(query: str, mode: str = "quick"):
    """
    Orchestrates the search based on the execution mode.
    """
    try:
        if mode == "deep" and os.getenv("TAVILY_API_KEY"):
            search = get_tavily_search()
            results = search.invoke({"query": query})
            # Format results into a single string for the LLM
            return "\n\n".join([f"Source: {r['url']}\nContent: {r['content']}" for r in results])
        else:
            search = get_ddg_search()
            return search.invoke(query)
    except Exception as e:
        return f"Search failed: {str(e)}"