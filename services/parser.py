# services/parser.py
from __future__ import annotations

import re
from typing import List, Optional

from api.schemas import ParsedReport, OrganismResult, ASTResult, SpecimenType, SIR


_SPECIMEN_MAP = [
    (re.compile(r"\bblood\b", re.I), SpecimenType.blood),
    (re.compile(r"\burine\b", re.I), SpecimenType.urine),
    (re.compile(r"\bsputum\b", re.I), SpecimenType.sputum),
    (re.compile(r"\bwound\b", re.I), SpecimenType.wound),
]


def _normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _normalize_drug_name(drug: str) -> str:
    """
    Keep it conservative: remove extra spaces, standardize + and - spacing.
    """
    drug = _normalize_spaces(drug)
    drug = re.sub(r"\s*\+\s*", " + ", drug)
    drug = re.sub(r"\s*-\s*", "-", drug)  # keep hyphens tight (e.g., piperacillin-tazobactam)
    return drug.title()


def _normalize_organism_name(org: str) -> str:
    org = _normalize_spaces(org)
    org = org.replace("E. Coli", "E. coli")
    org = org.replace("Staphylococcus Aureus", "Staphylococcus aureus")
    # Add more normalization rules later as you see more reports
    return org


def _extract_specimen_desc(text: str) -> Optional[str]:
    """
    STRICT SPECIMEN ONLY:
    We only use Specimen Desc line. If it's missing, specimen becomes 'other'.
    """
    # Examples seen:
    # "Specimen Desc. : BLOOD C/S"
    # "Specimen Desc : BLOOD C/S"
    m = re.search(r"Specimen\s*Desc\.?\s*:\s*(.+)", text, re.IGNORECASE)
    if not m:
        return None
    # take the line content only
    line = m.group(1).splitlines()[0].strip()
    return line


def _map_specimen(specimen_desc: Optional[str]) -> SpecimenType:
    if not specimen_desc:
        return SpecimenType.other
    for rx, sp in _SPECIMEN_MAP:
        if rx.search(specimen_desc):
            return sp
    return SpecimenType.other


def _extract_overall_notes(text: str) -> List[str]:
    """
    Pull notable free-text notes commonly present in Result section.
    Keep it simple: capture lines after organism listing until 'ANTIBIOTIC' header,
    and keep non-empty sentences.
    """
    notes: List[str] = []

    # Find block after "Result :" up to "ANTIBIOTIC"
    m = re.search(r"Result\s*:\s*(.+?)\n\s*ANTIBIOTIC", text, re.IGNORECASE | re.DOTALL)
    if not m:
        return notes

    block = m.group(1)

    # Remove organism lines like "1: E. COLI"
    block = re.sub(r"^\s*\d+\s*:\s*.+$", "", block, flags=re.MULTILINE)

    # Split into meaningful lines
    for line in block.splitlines():
        line = _normalize_spaces(line)
        if not line:
            continue
        # avoid obvious headers
        if line.lower() in {"microbiology", "result"}:
            continue
        notes.append(line)

    return notes


def _extract_organisms(text: str) -> List[str]:
    organisms: List[str] = []

    # Match patterns like:
    # "1: E. COLI"
    # "1 : E COLI"
    # "1: ESCHERICHIA COLI"
    rx = re.compile(r"^\s*\d+\s*:\s*([^\n\r]+)\s*$", re.MULTILINE | re.IGNORECASE)

    for m in rx.finditer(text):
        raw = m.group(1).strip()

        # If the line got merged with other sections, cut at known stop tokens
        stop_tokens = [
            "SENSITIVITIES",
            "SINGLE BLOOD CULTURE",
            "ANTIBIOTIC SUSCEPTIBILITY",
            "ANTIBIOTIC",
            "LEGEND",
            "MICROBIOLOGY",
            "REPORT",
        ]
        up = raw.upper()
        for tok in stop_tokens:
            idx = up.find(tok)
            if idx != -1 and idx > 0:
                raw = raw[:idx].strip()
                break

        raw = _normalize_spaces(raw)

        # ✅ Special handling: keep "E. coli" intact (do NOT split on '.')
        # Normalize common E. coli variants.
        # Examples: "E. COLI", "E COLI", "ESCHERICHIA COLI"
        ecoli_rx = re.compile(r"^(E\.?\s*COLI|ESCHERICHIA\s+COLI)\b", re.IGNORECASE)
        if ecoli_rx.search(raw):
            organisms.append("E. coli")
            continue

        # General cleanup: keep the whole line (no dot splitting)
        org = _normalize_organism_name(raw.title())
        if org:
            organisms.append(org)

    # de-dup preserving order
    seen = set()
    out = []
    for o in organisms:
        key = o.lower()
        if key not in seen:
            seen.add(key)
            out.append(o)

    return out

def _extract_antibiogram(text: str) -> List[ASTResult]:
    ast: List[ASTResult] = []

    # Pattern A: "1    AMIKACIN    S"
    row_rx_a = re.compile(
        r"^\s*(\d{1,3})\s+([A-Z][A-Z0-9\s\+\-\/\.\(\)]{2,}?)\s+([SRI])\s*$",
        re.MULTILINE
    )

    # Pattern B: "AMIKACIN S" (no index)
    row_rx_b = re.compile(
        r"^\s*([A-Z][A-Z0-9\s\+\-\/\.\(\)]{2,}?)\s+([SRI])\s*$",
        re.MULTILINE
    )

    def add_row(drug_raw: str, sir_raw: str, evidence: str):
        drug = _normalize_drug_name(drug_raw)
        sir_raw = sir_raw.upper()
        sir = SIR.susceptible if sir_raw == "S" else SIR.resistant if sir_raw == "R" else SIR.intermediate
        ast.append(ASTResult(drug=drug, sir=sir, mic=None, evidence_line=evidence))

    # Try A first
    for m in row_rx_a.finditer(text):
        add_row(m.group(2), m.group(3), m.group(0).strip())

    # If nothing found, try B
    if not ast:
        for m in row_rx_b.finditer(text):
            # Avoid matching headers accidentally
            drug_candidate = m.group(1).strip().upper()
            if drug_candidate in {"RESULT", "LEGEND", "MICROBIOLOGY", "ANTIBIOTIC", "S.#"}:
                continue
            add_row(m.group(1), m.group(2), m.group(0).strip())

    # De-dup by drug
    seen = set()
    deduped = []
    for item in ast:
        key = item.drug.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped


def parse_report(report_text: str) -> ParsedReport:
    """
    Main parser: returns ParsedReport per your API schema.
    STRICT SPECIMEN ONLY: relies on Specimen Desc line.
    """
    text = report_text

    # If the input contains literal "\n" sequences (common when pasted into JSON),
    # convert them into real newlines so MULTILINE regex works.
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")

    # Also normalize actual CRLF if present
    text = text.replace("\r\n", "\n").replace("\r", "\n")


    specimen_desc = _extract_specimen_desc(text)
    specimen = _map_specimen(specimen_desc)

    organisms = _extract_organisms(text)
    overall_notes = _extract_overall_notes(text)

    antibiogram = _extract_antibiogram(text)

    organism_results: List[OrganismResult] = []
    if organisms:
        # Apply same antibiogram to each organism by default (common in basic reports).
        # Later, if you see organism-specific tables, you can split by sections.
        for org in organisms:
            organism_results.append(
                OrganismResult(
                    organism=org,
                    ast=antibiogram,
                    notes=None
                )
            )
    else:
        # No organism parsed → still return table if available
        organism_results.append(
            OrganismResult(
                organism="Unknown",
                ast=antibiogram,
                notes=["Organism not detected by parser"]
            )
        )

    parsed = ParsedReport(
        specimen=specimen,
        organisms=organism_results,
        overall_notes=overall_notes if overall_notes else None
    )
    return parsed
