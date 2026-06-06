from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, END

class ResearchState(TypedDict):
    query: str
    tasks: List[dict]
    raw_docs: Annotated[List[dict],operator.add]
    top_chunks: List[dict]
    report: str
    eval_scores: dict


def build_graph():
    from agents.planner import planner_node
    from agents.researcher import researcher_node
    from agents.synthesizer import synthesizer_node
    from agents.writer import writer_node

    g= StateGraph(ResearchState)

    g.add_node("planner", planner_node)
    g.add_node("researcher", researcher_node)
    g.add_node("synthesizer", synthesizer_node)
    g.add_node("writer", writer_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "researcher")
    g.add_edge("researcher", "synthesizer")
    g.add_edge("synthesizer", "writer")
    g.add_edge("writer", END)

    return g.compile()