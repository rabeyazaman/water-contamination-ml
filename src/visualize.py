"""Matplotlib-only visualizations for the report and portfolio."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .preprocessing import PreparedData, FEATURE_COLS

FIG_DIR = Path("outputs/figures")


def _ensure_dir(p: Path | str = FIG_DIR) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------- Exploratory plots ----------

def plot_class_balance(df: pd.DataFrame, out_dir: Path | str = FIG_DIR) -> Path:
    out_dir = _ensure_dir(out_dir)
    counts = df["Potability"].value_counts().sort_index()
    labels = ["Non-potable (0)", "Potable (1)"]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, counts.values, color=["#c0392b", "#27ae60"])
    ax.set_title("Class Balance — Water Potability")
    ax.set_ylabel("Number of samples")
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width()/2, v, str(v),
                ha="center", va="bottom", fontsize=10)
    fig.tight_layout()
    path = out_dir / "01_class_balance.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_feature_distributions(df: pd.DataFrame, out_dir: Path | str = FIG_DIR) -> Path:
    out_dir = _ensure_dir(out_dir)
    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    for ax, col in zip(axes.flatten(), FEATURE_COLS):
        safe = df.loc[df["Potability"] == 1, col].dropna()
        unsafe = df.loc[df["Potability"] == 0, col].dropna()
        ax.hist(unsafe, bins=30, alpha=0.55, label="Non-potable", color="#c0392b")
        ax.hist(safe,   bins=30, alpha=0.55, label="Potable",     color="#27ae60")
        ax.set_title(col)
        ax.tick_params(labelsize=8)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Feature distributions by Potability", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = out_dir / "02_feature_distributions.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_correlation_heatmap(df: pd.DataFrame, out_dir: Path | str = FIG_DIR) -> Path:
    out_dir = _ensure_dir(out_dir)
    corr = df[FEATURE_COLS + ["Potability"]].corr()

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(corr.columns, fontsize=9)
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            ax.text(j, i, f"{corr.values[i, j]:.2f}",
                    ha="center", va="center", color="black", fontsize=7)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Correlation matrix")
    fig.tight_layout()
    path = out_dir / "03_correlation_heatmap.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ---------- Model performance plots ----------

def plot_confusion_matrix(cm: np.ndarray, name: str,
                          out_dir: Path | str = FIG_DIR) -> Path:
    out_dir = _ensure_dir(out_dir)
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Non-potable", "Potable"])
    ax.set_yticklabels(["Non-potable", "Potable"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix — {name}")
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color=color, fontsize=14, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    safe = name.lower().replace(" ", "_")
    path = out_dir / f"04_confusion_{safe}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_model_comparison(metrics_df: pd.DataFrame,
                          out_dir: Path | str = FIG_DIR) -> Path:
    out_dir = _ensure_dir(out_dir)
    cols = [c for c in ["accuracy", "precision", "recall", "f1", "roc_auc"]
            if c in metrics_df.columns]
    data = metrics_df[cols]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(data.index))
    width = 0.15
    colors = ["#2980b9", "#16a085", "#f39c12", "#8e44ad", "#c0392b"]
    for i, col in enumerate(cols):
        ax.bar(x + i*width, data[col].values, width, label=col, color=colors[i])
    ax.set_xticks(x + width*(len(cols)-1)/2)
    ax.set_xticklabels(data.index)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Model performance comparison")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    path = out_dir / "05_model_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_feature_importance(model, feature_names: list[str], name: str,
                            out_dir: Path | str = FIG_DIR) -> Path | None:
    """Works for tree-based models (feature_importances_) and Logistic Regression (coef_)."""
    out_dir = _ensure_dir(out_dir)
    importances = None
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        x_label = "Importance"
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).ravel()
        x_label = "|Coefficient| (standardized features)"
    else:
        return None

    order = np.argsort(importances)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(np.array(feature_names)[order], importances[order], color="#2c3e50")
    ax.set_xlabel(x_label)
    ax.set_title(f"Feature importance — {name}")
    fig.tight_layout()
    safe = name.lower().replace(" ", "_")
    path = out_dir / f"06_feature_importance_{safe}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
