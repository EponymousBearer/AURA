# agent/state.py
from __future__ import annotations
from typing import TypedDict, Optional, List, Dict, Any

from api.schemas import (
    CultureReportRequest,
    ParsedReport,
    RankedOption,
    RecommendationPackage,
    AnalyzeStatus,
)

class GraphState(TypedDict, total=False):
    # Input
    payload: CultureReportRequest

    # Outputs from nodes
    parsed_report: ParsedReport
    ranked_options: List[RankedOption]
    missing_info: List[str]

    status: AnalyzeStatus
    recommendation: RecommendationPackage

    # Optional debug
    debug: Dict[str, Any]
