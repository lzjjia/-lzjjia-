from langgraph.graph import StateGraph, END
from graph.state import AtlasState
from agents.coordinator import coordinator_node
from agents.planner import planner_node
from agents.notewriter import notewriter_node
from agents.advisor import advisor_node

def route_after_coordinator(state: AtlasState) -> str:
    return state.get("next_agent", "advisor")

def build_atlas_graph():
    graph = StateGraph(AtlasState)
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("planner", planner_node)
    graph.add_node("notewriter", notewriter_node)
    graph.add_node("advisor", advisor_node)

    graph.set_entry_point("coordinator")
    graph.add_conditional_edges("coordinator", route_after_coordinator, {
        "planner": "planner",
        "notewriter": "notewriter",
        "advisor": "advisor"
    })
    graph.add_edge("planner", END)
    graph.add_edge("notewriter", END)
    graph.add_edge("advisor", END)

    return graph.compile()