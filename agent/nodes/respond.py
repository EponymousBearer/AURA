# agent/nodes/respond.py
from __future__ import annotations
from typing import Dict, Any

from agent.state import GraphState
from api.schemas import AnalyzeStatus


def respond_node(state: GraphState) -> Dict[str, Any]:
    """
    If earlier nodes already set status+recommendation (needs_more_info/needs_review/no_safe_option),
    keep them. Otherwise ensure defaults are set.
    """
    status = state.get("status")
    recommendation = state.get("recommendation")

    if status is None:
        status = AnalyzeStatus.recommendation_ready  # usually dose_node sets it
    if recommendation is None:
        # This shouldn't happen, but keep safe default
        from api.schemas import RecommendationPackage
        recommendation = RecommendationPackage(
            primary=None,
            alternatives=[],
            rationale=["No recommendation generated."],
            warnings=["Pipeline ended without recommendation."],
            missing_info=[],
        )

    return {"status": status, "recommendation": recommendation}
