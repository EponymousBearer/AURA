# services/ranker.py
from __future__ import annotations

from typing import List, Optional
from pathlib import Path
import joblib

from api.schemas import ParsedReport, RankedOption, SIR, PatientInfo

MODEL_PATH = Path(__file__).parent.parent / "ml" / "model.joblib"
_MODEL = None


# ---- old rules fallback ----
BROAD_PENALTY = {
    "meropenem": 0.15,
    "imipenem-cilastatin": 0.15,
    "piperacillin-tazobactam": 0.08,
    "vancomycin": 0.05,
}


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if MODEL_PATH.exists():
        _MODEL = joblib.load(MODEL_PATH)
    else:
        _MODEL = None
    return _MODEL


def _rules_rank(parsed: ParsedReport, patient: PatientInfo) -> List[RankedOption]:
    if not parsed.organisms or not parsed.organisms[0].ast:
        return []

    ast = parsed.organisms[0].ast
    ranked: List[RankedOption] = []

    for r in ast:
        drug_key = r.drug.lower()

        if r.sir == SIR.resistant:
            continue

        base = 0.8 if r.sir == SIR.susceptible else 0.55
        penalty = BROAD_PENALTY.get(drug_key, 0.0)
        score = max(0.0, min(1.0, base - penalty))

        why = []
        if r.sir == SIR.susceptible:
            why.append("Reported susceptible (S) on culture report.")
        elif r.sir == SIR.intermediate:
            why.append("Reported intermediate (I); consider only if limited options.")

        if penalty > 0:
            why.append("Spectrum stewardship penalty applied (broader agent).")

        ranked.append(
            RankedOption(
                drug=r.drug,
                score=score,
                why=why,
                sir_summary=r.sir.value,
                mic_summary=r.mic,
                warnings=[]
            )
        )

    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:5]


def _ml_rank(parsed: ParsedReport, patient: PatientInfo) -> Optional[List[RankedOption]]:
    model = _load_model()
    if model is None:
        return None

    if not parsed.organisms or not parsed.organisms[0].ast:
        return []

    org = parsed.organisms[0].organism.strip().lower()
    ast = parsed.organisms[0].ast

    # Build candidate rows only from drugs in the report
    rows = []
    keep = []
    for r in ast:
        # Never recommend R (hard rule)
        if r.sir == SIR.resistant:
            continue

        rows.append({"organism": org, "drug": r.drug.strip().lower()})
        keep.append(r)

    if not rows:
        return []

    import pandas as pd
    X = pd.DataFrame(rows)

    probs = model.predict_proba(X)[:, 1]  # P(susceptible)

    ranked: List[RankedOption] = []
    for r, p in zip(keep, probs):
        why = [f"ML predicted susceptibility probability: {p:.2f}."]
        # also include actual S/I from report for transparency
        if r.sir == SIR.susceptible:
            why.append("Culture report shows Sensitive (S).")
        elif r.sir == SIR.intermediate:
            why.append("Culture report shows Intermediate (I).")

        ranked.append(
            RankedOption(
                drug=r.drug,
                score=float(max(0.0, min(1.0, p))),
                why=why,
                sir_summary=r.sir.value,
                mic_summary=r.mic,
                warnings=[]
            )
        )

    ranked.sort(key=lambda x: x.score, reverse=True)
    return ranked[:5]


def rank_options(parsed: ParsedReport, patient: PatientInfo) -> List[RankedOption]:
    """
    ML-first ranking:
    - If model exists: rank by P(S)
    - Always enforce: never recommend R
    - Fallback to rules if ML not available
    """
    ml = _ml_rank(parsed, patient)
    if ml is not None:
        return ml
    return _rules_rank(parsed, patient)
