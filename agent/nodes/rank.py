# agent/nodes/rank.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

from agent.state import GraphState
from services.ranker import rank_options



def rank_node(state: GraphState) -> Dict[str, Any]:
    payload = state.get("payload")
    parsed = state.get("parsed_report")
    
    if payload is None or parsed is None:
        return {}  # Early exit if missing required data

    ranked = rank_options(parsed, payload.patient)
    
    # after ranked = rank_options(...)
    debug = state.get("debug", {})
    if payload.debug:
        debug["rank"] = {
            "ranked_drugs": [r.drug for r in ranked],
            "top_score": ranked[0].score if ranked else None,
            "ranker_used": "ml" if (Path("ml/model.joblib").exists()) else "rules"
        }
    
    return {"ranked_options": ranked, "debug": debug}