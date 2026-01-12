# agent/nodes/dose.py
from __future__ import annotations
from typing import Dict, Any

from agent.state import GraphState
from api.schemas import AnalyzeStatus, RecommendationPackage
from services.dosing import build_regimen_package


def dose_node(state: GraphState) -> Dict[str, Any]:
    payload = state["payload"]
    ranked = state.get("ranked_options", [])

    ranked_drugs = [r.drug for r in ranked]
    primary, alternatives = build_regimen_package(ranked_drugs, payload.patient)

    debug = state.get("debug", {})
    if payload.debug:
        debug["dose"] = {
            "primary_found": primary is not None,
            "alternatives_count": len(alternatives),
        }

    if primary is None:
        rec = RecommendationPackage(
            primary=None,
            alternatives=[],
            rationale=[
                "No dosing entry found in dosing_table.csv for ranked options. Add rows for these drugs/indications."
            ],
            warnings=["Expand dosing_table.csv coverage."],
            missing_info=[],
        )
        return {
            "status": AnalyzeStatus.no_safe_option,
            "recommendation": rec,
            "debug": debug,
        }

    rec = RecommendationPackage(
        primary=primary,
        alternatives=alternatives,
        rationale=[
            f"Primary regimen selected from susceptibility-ranked options: {primary.drug}.",
            "Dose/route/duration derived from dosing_table.csv.",
        ],
        warnings=[
            "Clinical decision support only; confirm diagnosis/source and monitor response."
        ],
        missing_info=[],
    )

    return {"status": AnalyzeStatus.recommendation_ready, "recommendation": rec, "debug": debug}
