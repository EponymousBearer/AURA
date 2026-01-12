# ml/evaluate.py
import joblib
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

MODEL_PATH = "ml/model.joblib"
DATA_PATH = "data/processed/susceptibility.csv"

def main():
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)

    X = df[["organism", "drug"]]
    y = df["sir"].map({"S": 1, "I": 0, "R": 0})

    probs = model.predict_proba(X)[:, 1]
    preds = (probs >= 0.5).astype(int)

    print("ROC-AUC:", roc_auc_score(y, probs))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y, preds))
    print("\nClassification Report:")
    print(classification_report(y, preds))

if __name__ == "__main__":
    main()
