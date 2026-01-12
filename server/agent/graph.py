# agent/graph.py
from __future__ import annotations

import os
from langgraph.graph import StateGraph, END

from agent.state import GraphState
from agent.nodes.extract import extract_node
from agent.nodes.validate import validate_node
from agent.nodes.rank import rank_node
from agent.nodes.dose import dose_node
from agent.nodes.respond import respond_node
from agent.nodes.explain import explain_node


def _should_end_after_validate(state: GraphState) -> str:
    status = state.get("status")
    return "continue" if status is None else "end"


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("extract", extract_node)
    g.add_node("validate", validate_node)
    g.add_node("rank", rank_node)
    g.add_node("dose", dose_node)
    g.add_node("respond", respond_node)

    # If pytest is running OR OpenAI key missing -> skip explain node
    in_pytest = bool(os.getenv("PYTEST_CURRENT_TEST"))
    has_openai_key = bool(os.getenv("OPENAI_API_KEY"))

    use_explain = (not in_pytest) and has_openai_key

    if use_explain:
        g.add_node("explain", explain_node)

    g.set_entry_point("extract")
    g.add_edge("extract", "validate")

    g.add_conditional_edges(
        "validate",
        _should_end_after_validate,
        {
            "continue": "rank",
            "end": "respond",
        },
    )

    g.add_edge("rank", "dose")

    if use_explain:
        g.add_edge("dose", "explain")
        g.add_edge("explain", "respond")
    else:
        g.add_edge("dose", "respond")

    g.add_edge("respond", END)
    return g.compile()
