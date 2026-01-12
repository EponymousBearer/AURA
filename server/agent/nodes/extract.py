# agent/nodes/extract.py
from __future__ import annotations
from typing import Dict, Any

from agent.state import GraphState
from services.parser import parse_report


def extract_node(state: GraphState) -> Dict[str, Any]:
    payload = state.get("payload")
    if not payload:
        return {"parsed_report": None, "debug": {}}
    
    print("\n[EXTRACT NODE] first 300 chars:\n", repr(payload.report_text[:300]))

    debug = state.get("debug", {})
    if payload.debug:
        debug["extract"] = {"first_200_chars": payload.report_text[:200]}

    parsed = parse_report(payload.report_text)

    if payload.debug:
        debug["extract"] = {
            "specimen": parsed.specimen,
            "organism_count": len(parsed.organisms),
            "overall_notes_count": len(parsed.overall_notes or []),
        }

    return {"parsed_report": parsed, "debug": debug}
