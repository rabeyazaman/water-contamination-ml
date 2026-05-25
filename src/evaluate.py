"""Evaluation: accuracy, precision, recall, F1, ROC-AUC, confusion matrices."""

from __future__ import annotations

from pathlib import Path
import json
import pandas as pd
import numpy as np

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix,
)

from .preprocessing import PreparedData


def evaluate_model(name: str, model, data: PreparedData) -> dict:
    y_pred = model.predict(data.X_test)

    # ROC-AUC needs probabilities; fall back gracefully if unavailable.
    try:
        y_proba = model.predict_proba(data.X_test)[:, 1]
        auc = float(roc_auc_score(data.y_test, y_proba))
    except Exception:
        auc = float("nan")

    metrics = {
        "model": name,
        "accuracy":  float(accuracy_score(data.y_test, y_pred)),
        "precision": float(precision_score(data.y_test, y_pred, zero_division=0)),
        "recall":    float(recall_score(data.y_test, y_pred, zero_division=0)),
        "f1":        float(f1_score(data.y_test, y_pred, zero_division=0)),
        "roc_auc":   auc,
    }
    return metrics


def evaluate_all(models: dict, data: PreparedData) -> pd.DataFrame:
    rows = [evaluate_model(n, m, data) for n, m in models.items()]
    df = pd.DataFrame(rows).set_index("model").round(4)
    print("\n=== Model comparison ===")
    print(df)
    return df


def best_model(metrics_df: pd.DataFrame, metric: str = "f1") -> str:
    name = metrics_df[metric].idxmax()
    print(f"\n[evaluate] Best model by {metric}: {name}")
    return name


def detailed_report(name: str, model, data: PreparedData) -> str:
    y_pred = model.predict(data.X_test)
    text = classification_report(
        data.y_test, y_pred,
        target_names=["Non-potable (0)", "Potable (1)"],
        digits=3,
    )
    print(f"\n=== Classification report — {name} ===\n{text}")
    return text


def save_metrics(metrics_df: pd.DataFrame, best_name: str,
                 out_dir: str | Path = "outputs") -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(out_dir / "metrics.csv")
    payload = {
        "best_model": best_name,
        "metrics": metrics_df.reset_index().to_dict(orient="records"),
    }
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=2))
    print(f"[evaluate] Saved metrics -> {out_dir/'metrics.csv'} and metrics.json")


def confusion_matrices(models: dict, data: PreparedData) -> dict[str, np.ndarray]:
    return {n: confusion_matrix(data.y_test, m.predict(data.X_test))
            for n, m in models.items()}
