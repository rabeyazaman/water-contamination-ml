"""
Water Contamination Detection — end-to-end pipeline.

Usage:
    python main.py

Pipeline:
    1. Locate (or auto-generate) the dataset.
    2. Clean, impute, scale, and split.
    3. Train Logistic Regression, Decision Tree, Random Forest.
    4. Evaluate all models; pick the best by F1.
    5. Save plots to outputs/figures and models to outputs/models.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from src.data_loader import load_dataset, quick_summary
from src.preprocessing import prepare_data
from src.train_models import train_all, save_models
from src.evaluate import (
    evaluate_all, best_model, detailed_report, save_metrics, confusion_matrices,
)
from src.visualize import (
    plot_class_balance, plot_feature_distributions, plot_correlation_heatmap,
    plot_confusion_matrix, plot_model_comparison, plot_feature_importance,
)


def main() -> None:
    print("=" * 70)
    print("  AI-Based Water Contamination Detection System")
    print("  Author: Rabeya Zaman | NDUB Microbiology | 2026")
    print("=" * 70)

    # 1. Load data
    df = load_dataset()
    quick_summary(df)

    # 2. EDA plots
    print("\n[main] Generating exploratory plots ...")
    plot_class_balance(df)
    plot_feature_distributions(df)
    plot_correlation_heatmap(df)

    # 3. Prepare data
    data = prepare_data(df)

    # 4. Train
    print("\n[main] Training models ...")
    models = train_all(data)

    # 5. Evaluate
    metrics = evaluate_all(models, data)
    best = best_model(metrics, metric="f1")
    detailed_report(best, models[best], data)
    save_metrics(metrics, best)

    # 6. Plots: confusion matrices, comparison, feature importance
    print("\n[main] Generating performance plots ...")
    for name, cm in confusion_matrices(models, data).items():
        plot_confusion_matrix(cm, name)
    plot_model_comparison(metrics)
    for name, model in models.items():
        plot_feature_importance(model, data.feature_names, name)

    # 7. Save models + a copy of the best one as best_model.pkl
    paths = save_models(models)
    best_src = paths[best]
    best_dst = Path("outputs/models/best_model.pkl")
    shutil.copyfile(best_src, best_dst)
    print(f"\n[main] Best model also copied to {best_dst}")

    print("\nAll done. Inspect outputs/figures/ and outputs/models/ for results.")


if __name__ == "__main__":
    main()
