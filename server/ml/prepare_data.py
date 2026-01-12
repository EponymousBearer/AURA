# ml/prepare_data.py
from __future__ import annotations

import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/BVBRC_E.coli_Dataset.csv")
OUT_PATH = Path("data/processed/susceptibility.csv")

# Map BV-BRC phenotype strings -> S/I/R
PHENOTYPE_MAP = {
    "SUSCEPTIBLE": "S",
    "RESISTANT": "R",
    "INTERMEDIATE": "I",
    # Conservative mappings for uncommon values
    "NONSUSCEPTIBLE": "R",                 # treat as R for safety
    "SUSCEPTIBLE-DOSE DEPENDENT": "I",     # often SDD ~ closer to I in decisions
}

def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw BV-BRC dataset not found at {RAW_PATH}. "
            f"Put your file there with the exact name: BVBRC_E.coli_Dataset.csv"
        )

    df = pd.read_csv(RAW_PATH, low_memory=False)
    print("Original columns:", df.columns.tolist())

    required = ["Antibiotic", "Resistant Phenotype"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")

    # Keep only required columns + optional MIC components
    cols = ["Antibiotic", "Resistant Phenotype"]
    mic_cols = ["Measurement Sign", "Measurement Value", "Measurement Unit"]
    for c in mic_cols:
        if c in df.columns:
            cols.append(c)

    clean = df[cols].copy()

    # Normalize fields
    clean["drug"] = clean["Antibiotic"].astype(str).str.strip().str.lower()
    clean["phenotype"] = clean["Resistant Phenotype"].astype(str).str.strip().str.upper()

    # Map phenotype -> sir
    clean["sir"] = clean["phenotype"].map(PHENOTYPE_MAP)

    # Drop rows that don't map cleanly
    clean = clean.dropna(subset=["sir", "drug"]).copy()

    # Force organism constant (this dataset is E. coli)
    clean["organism"] = "escherichia coli"

    # Optional MIC string (if the dataset has it)
    if all(c in clean.columns for c in mic_cols):
        def build_mic(row):
            sign = str(row.get("Measurement Sign", "")).strip()
            val = str(row.get("Measurement Value", "")).strip()
            unit = str(row.get("Measurement Unit", "")).strip()

            if val == "" or val.lower() == "nan":
                return ""
            if sign.lower() == "nan":
                sign = ""
            if unit.lower() == "nan":
                unit = ""
            # Example: "> 32 mg/L"
            parts = [p for p in [sign, val] if p]
            mic = " ".join(parts)
            if unit:
                mic = f"{mic} {unit}"
            return mic.strip()

        clean["mic"] = clean.apply(build_mic, axis=1)
    else:
        clean["mic"] = ""

    # Output columns in your standard format
    out = clean[["organism", "drug", "sir", "mic"]].copy()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    print("Saved processed dataset:", OUT_PATH)
    print(out.head(10))
    print("sir value counts:\n", out["sir"].value_counts())

if __name__ == "__main__":
    main()
