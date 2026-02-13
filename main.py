# main.py
import sys
from langgraph.graph import StateGraph, END
from state import AgentState

# Import node functions
from graph.nodes_pre import guard_layer, context_retrieval, intent_classifier
from graph.nodes_exec import (
    planner_router, 
    quick_mode_executor, 
    deep_mode_orchestrator,
    gap_analysis_node,
    structured_synthesis_node
)
from graph.nodes_post import format_output

def build_agent():
    """Compiles the Phase 1-4 logic into a LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # --- Phase 1: Pre-Processing ---
    workflow.add_node("guard", guard_layer)
    workflow.add_node("context", context_retrieval)
    workflow.add_node("classify", intent_classifier)

    # --- Phase 2: Planning ---
    workflow.add_node("planner", planner_router)

    # --- Phase 3: Execution (Dual Mode) ---
    workflow.add_node("quick_mode", quick_mode_executor)
    workflow.add_node("deep_research", deep_mode_orchestrator)
    workflow.add_node("gap_analysis", gap_analysis_node)
    workflow.add_node("synthesize", structured_synthesis_node)

    # --- Phase 4: Output ---
    workflow.add_node("formatter", format_output)

    # --- Define Logic Flow (Edges) ---
    workflow.set_entry_point("guard")
    workflow.add_edge("guard", "context")
    workflow.add_edge("context", "classify")

    # Intent Router: If intent is unclear, we end (or ask user). 
    # If clear, proceed to the Planner.
    def intent_route(state):
        if state.get("is_clarified"):
            return "planner"
        return END

    workflow.add_conditional_edges("classify", intent_route)

    # Planner Router: Choose between Quick Mode and Deep Mode
    def mode_route(state):
        return "quick_mode" if state.get("mode") == "quick" else "deep_research"

    workflow.add_conditional_edges("planner", mode_route)

    # Deep Mode Loop: Research -> Analyze -> (Loop or Synthesize)
    workflow.add_edge("deep_research", "gap_analysis")
    
    def gap_route(state):
        confidence = state.get("confidence_score", 0.0)
        iterations = state.get("iterations", 0)
        if confidence < 0.8 and iterations < 3:
            return "deep_research"
        return "synthesize"

    workflow.add_conditional_edges("gap_analysis", gap_route)

    # Close the paths to Formatter
    workflow.add_edge("quick_mode", "formatter")
    workflow.add_edge("synthesize", "formatter")
    workflow.add_edge("formatter", END)

    return workflow.compile()

def main():
    """Main execution loop for the agent."""
    app = build_agent()
    
    from config import Config
    print(f"\n🚀 Developer Research Agent ({Config.MODEL_NAME}) Initialized.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_query = input("🔍 Enter your technical research query: ")
            if user_query.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not user_query.strip():
                continue

            initial_state = {
                "query": user_query,
                "history": [], # In a real app, persistent history
            }

            print("\nProcessing...")
            final_report = ""
            
            # Stream updates
            for output in app.stream(initial_state):
                for key, value in output.items():
                    print(f"✅ Completed Node: [{key}]")
                    if key == "formatter":
                        final_report = value.get("final_report", "")

            print("\n" + "="*60)
            print(final_report)
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()