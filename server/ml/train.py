# ml/train.py
from __future__ import annotations

import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "ml/model.joblib"

def main():
    df = pd.read_csv("data/processed/susceptibility.csv")

    # ---- normalize ----
    df["organism"] = df["organism"].astype(str).str.strip().str.lower()
    df["drug"] = df["drug"].astype(str).str.strip().str.lower()
    df["sir"] = df["sir"].astype(str).str.strip().str.upper()

    # ---- label: susceptible vs not ----
    df = df[df["sir"].isin(["S", "R", "I"])].copy()
    df["y"] = df["sir"].map({"S": 1, "I": 0, "R": 0}).astype(int)

    X = df[["organism", "drug"]]
    y = df["y"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ---- pipeline ----
    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["organism", "drug"]),
        ],
        remainder="drop",
    )

    clf = LogisticRegression(max_iter=200)

    pipe = Pipeline([("pre", pre), ("clf", clf)])

    pipe.fit(X_train, y_train)

    # ---- eval ----
    probs = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, probs)
    print("ROC-AUC:", auc)

    preds = (probs >= 0.5).astype(int)
    print(classification_report(y_test, preds))

    os.makedirs("ml", exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    print("Saved:", MODEL_PATH)


if __name__ == "__main__":
    main()
