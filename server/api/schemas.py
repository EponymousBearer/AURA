from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------
# Enums
# ---------------------------

class SpecimenType(str, Enum):
    blood = "blood"
    urine = "urine"
    sputum = "sputum"
    wound = "wound"
    other = "other"


class SIR(str, Enum):
    susceptible = "S"
    intermediate = "I"
    resistant = "R"
    unknown = "U"


class Severity(str, Enum):
    stable = "stable"
    sepsis = "sepsis"
    septic_shock = "septic_shock"
    unknown = "unknown"


class RenalBucket(str, Enum):
    normal = "normal"
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    unknown = "unknown"


class AnalyzeStatus(str, Enum):
    recommendation_ready = "recommendation_ready"
    needs_more_info = "needs_more_info"
    needs_review = "needs_review"
    no_safe_option = "no_safe_option"


# ---------------------------
# Request Models
# ---------------------------

class PatientInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age_years: int = Field(..., ge=18, description="Adults only")
    sex: Optional[str] = Field(None, description="male/female/other/unknown")

    # Critical prescribing gates
    syndrome: Optional[str] = Field(
        None,
        description="Clinical syndrome/source e.g. gn_bacteremia, mrsa_bacteremia, empiric_sepsis_unknown"
    )
    severity: Severity = Severity.unknown

    # Safety gates
    egfr_ml_min: Optional[float] = Field(None, ge=0, description="eGFR/CrCl if available")
    renal_bucket: RenalBucket = RenalBucket.unknown

    beta_lactam_allergy: Optional[bool] = Field(None, description="True if severe allergy suspected/known")
    other_allergies: Optional[List[str]] = Field(default=None)

    pregnancy: Optional[bool] = Field(None, description="Adults only but still possible")
    hepatic_impairment: Optional[bool] = Field(None)
    interactions: Optional[List[str]] = Field(default=None, description="Known interacting meds if provided")


class CultureReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_text: str = Field(..., min_length=10, description="Paste raw culture report text")
    specimen_hint: Optional[SpecimenType] = None
    patient: PatientInfo

    debug: bool = Field(False, description="Return extra debug info for demo")


# ---------------------------
# Parsed Report Models
# ---------------------------

class ASTResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drug: str
    sir: SIR
    mic: Optional[str] = Field(None, description="Raw MIC string e.g. '0.25', '>32'")
    evidence_line: Optional[str] = Field(None, description="Original line/table cell if available")


class OrganismResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organism: str
    ast: List[ASTResult] = Field(default_factory=list)
    notes: Optional[List[str]] = None  # ESBL/CRE/MRSA flags if present


class ParsedReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    specimen: SpecimenType
    organisms: List[OrganismResult] = Field(default_factory=list)
    overall_notes: Optional[List[str]] = None


# ---------------------------
# Ranking / Recommendation Models
# ---------------------------

class RankedOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drug: str
    score: float = Field(..., ge=0, le=1)
    why: List[str] = Field(default_factory=list)

    sir_summary: Optional[str] = Field(None, description="S/I/R summary for this drug if available")
    mic_summary: Optional[str] = Field(None)

    # Safety flags
    warnings: List[str] = Field(default_factory=list)


class Regimen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drug: str
    route: str = Field(..., description="IV/PO/IM")
    dose: str = Field(..., description="e.g. '2 g'")
    frequency: str = Field(..., description="e.g. 'q24h', 'q8h'")
    duration: str = Field(..., description="e.g. '7–14 days'")

    # Provenance (for your report + demo)
    source: str = Field(..., description="Which guideline/reference row this came from")
    notes: Optional[List[str]] = None


class RecommendationPackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary: Optional[Regimen] = None
    alternatives: List[Regimen] = Field(default_factory=list)

    rationale: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Ask if missing
    missing_info: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    parsed_report: dict
    ranked_options: list
    recommendation: dict
    safety_note: Optional[str] = None
    debug: Optional[dict] = None
