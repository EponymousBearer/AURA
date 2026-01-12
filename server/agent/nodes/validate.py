# agent/nodes/validate.py
from __future__ import annotations
from typing import Dict, Any

from agent.state import GraphState
from api.schemas import AnalyzeStatus, RecommendationPackage
from services.dosing import needs_missing_info_for_dosing


def validate_node(state: GraphState) -> Dict[str, Any]:
    payload = state["payload"]
    parsed = state["parsed_report"]

    missing = needs_missing_info_for_dosing(payload.patient)

    # Polymicrobial handling (MVP safe)
    if len(parsed.organisms) > 1:
        rec = RecommendationPackage(
            primary=None,
            alternatives=[],
            rationale=[
                "Multiple organisms detected in blood culture; regimen depends on coverage strategy and clinical context."
            ],
            warnings=["Polymicrobial blood cultures require clinician review."],
            missing_info=missing + ["confirm source control and clinical syndrome"],
        )
        return {
            "missing_info": missing,
            "status": AnalyzeStatus.needs_review,
            "recommendation": rec,
        }

    # Missing info gate (no dosing yet)
    if missing:
        rec = RecommendationPackage(
            primary=None,
            alternatives=[],
            rationale=[
                "Antibiotic options can be ranked from susceptibility, but dosing/route/duration needs missing clinical inputs."
            ],
            warnings=[
                "Do not finalize antibiotic dosing without allergy + renal function + syndrome/source."
            ],
            missing_info=missing,
        )
        return {
            "missing_info": missing,
            "status": AnalyzeStatus.needs_more_info,
            "recommendation": rec,
        }

    # Otherwise proceed
    return {"missing_info": [], "status": None, "recommendation": None}
