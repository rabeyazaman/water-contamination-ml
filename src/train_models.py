"""Train Logistic Regression, Decision Tree, and Random Forest classifiers."""

from __future__ import annotations

from pathlib import Path
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from .preprocessing import PreparedData


def build_models(random_state: int = 42) -> dict:
    """Return a dict of {name: estimator} with sensible defaults for beginners."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state,
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=random_state,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1,
            random_state=random_state,
        ),
    }


def train_all(data: PreparedData, random_state: int = 42) -> dict:
    """Fit each model on the training data; return {name: fitted_model}."""
    models = build_models(random_state=random_state)
    fitted = {}
    for name, model in models.items():
        print(f"[train_models] Fitting {name} ...")
        model.fit(data.X_train, data.y_train)
        fitted[name] = model
    return fitted


def save_models(models: dict, out_dir: str | Path = "outputs/models") -> dict:
    """Pickle each model to disk and return {name: file_path}."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, model in models.items():
        safe = name.lower().replace(" ", "_")
        p = out_dir / f"{safe}.pkl"
        joblib.dump(model, p)
        paths[name] = p
        print(f"[train_models] Saved {name} -> {p}")
    return paths
