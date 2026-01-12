# services/dosing.py
from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional, Dict

from api.schemas import Regimen, PatientInfo


import re

# -------------------------------------------------
# CSV CONFIG
# -------------------------------------------------

CSV_PATH = Path(__file__).parent.parent / "knowledge" / "dosing_table.csv"

# Cache rows so we don't reload on every request
_DOSING_ROWS: List[Dict[str, str]] = []
DEBUG_MATCH = True

# -------------------------------------------------
# CSV LOADER
# -------------------------------------------------

def _load_dosing_table() -> None:
    global _DOSING_ROWS
    if _DOSING_ROWS:
        return

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"dosing_table.csv not found at {CSV_PATH}")

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # normalize keys & values
            normalized = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
            _DOSING_ROWS.append(normalized)


# -------------------------------------------------
# SAFETY GATING
# -------------------------------------------------

def needs_missing_info_for_dosing(patient: PatientInfo) -> List[str]:
    """
    Minimal gating for adult blood culture dosing.
    """
    missing = []

    if not patient.syndrome:
        missing.append("syndrome (clinical source/category for bacteremia)")

    if patient.beta_lactam_allergy is None:
        missing.append("beta_lactam_allergy (true/false)")

    if patient.egfr_ml_min is None and patient.renal_bucket.value == "unknown":
        missing.append("egfr_ml_min or renal_bucket")

    return missing


# -------------------------------------------------
# MATCHING LOGIC
# -------------------------------------------------

def _canon(s: str) -> str:
    """
    Canonicalize strings so minor formatting differences don't break matching.
    - lowercase
    - convert '+' and '/' to spaces
    - remove punctuation except letters/numbers
    - collapse spaces
    """
    s = (s or "").lower().strip()
    s = s.replace("+", " ")
    s = s.replace("/", " ")
    s = s.replace("-", " ")
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _match_rows_for_drug(drug: str, syndrome: str) -> List[Dict[str, str]]:
    drug_key = _canon(drug)
    syndrome_key = _canon(syndrome)

    exact_matches = []
    generic_matches = []

    for row in _DOSING_ROWS:
        row_drug = _canon(row.get("drug", ""))
        if row_drug != drug_key:
            continue

        indication = _canon(row.get("indication", ""))

        # flexible indication match
        if indication == syndrome_key or syndrome_key in indication or indication in syndrome_key:
            exact_matches.append(row)
        elif not indication:
            generic_matches.append(row)

    return exact_matches or generic_matches


def _select_best_row(rows: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    MVP logic: first matching row wins.
    (You can later add severity / renal bucket scoring.)
    """
    if not rows:
        return None
    return rows[0]


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def pick_regimen(drug: str, patient: PatientInfo) -> Optional[Regimen]:
    """
    Return a Regimen from dosing_table.csv for a single drug.
    """
    _load_dosing_table()

    if not patient.syndrome:
        return None

    rows = _match_rows_for_drug(drug, patient.syndrome)
    chosen = _select_best_row(rows)

    # if not chosen:
    #     return None
    if not chosen:
        if DEBUG_MATCH:
            print("\n[DOSING DEBUG] No match for drug:", drug, "| syndrome:", patient.syndrome)
            print("[DOSING DEBUG] Available drugs in dosing table sample:", [r.get("drug","") for r in _DOSING_ROWS[:10]])
        return None


    return Regimen(
        drug=chosen["drug"],
        route=chosen["route"],
        dose=chosen["standard_dose"],
        frequency=chosen["frequency"],
        duration=chosen["typical_duration"],
        source=chosen["source"],
        notes=[chosen["notes"]] if chosen.get("notes") else [],
    )


def build_regimen_package(
    drugs_ranked: List[str],
    patient: PatientInfo
):
    """
    Primary = first ranked drug with dosing
    Alternatives = next 2 with dosing
    """
    _load_dosing_table()

    primary: Optional[Regimen] = None
    alternatives: List[Regimen] = []

    for drug in drugs_ranked:
        regimen = pick_regimen(drug, patient)
        if not regimen:
            continue

        if primary is None:
            primary = regimen
        elif len(alternatives) < 2:
            alternatives.append(regimen)

    return primary, alternatives
