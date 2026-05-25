# Kaggle Notebook — Ready-to-Paste Description

Use this content as the **notebook description / write-up** on Kaggle.

---

## Title
**AI-Based Water Contamination Detection — Logistic Regression vs Decision Tree vs Random Forest**

## Short description (Kaggle subtitle, ≤ 200 chars)
End-to-end ML pipeline for water potability prediction. EDA → median imputation → standardization → 3 classifiers → confusion matrices → feature importance. Microbiology-aware interpretation.

## Tags
`beginner` `classification` `random-forest` `eda` `healthcare` `water-quality` `public-health` `microbiology` `feature-importance` `sklearn`

## About this notebook

This notebook tackles the **Water Potability** dataset by Aditya Kadiwal as a real public-health problem rather than a generic Kaggle exercise. Waterborne disease still causes ~485,000 deaths per year (WHO). Microbial culture takes 1–3 days. The question this notebook answers is: **can we predict potability from cheap physicochemical sensor readings (pH, turbidity, conductivity, chloramines, etc.) and use that as a real-time triage step before sending samples to a microbiology lab?**

### Pipeline

1. **Load & summarize** the 9 features + binary `Potability` target (3,276 samples).
2. **EDA** — class balance, distributions split by potability, correlation heatmap.
3. **Preprocessing** — stratified 80/20 split, median imputation, `StandardScaler`. Imputer & scaler fitted on train only to avoid leakage.
4. **Three classifiers** — Logistic Regression (linear baseline), Decision Tree (interpretable rules), Random Forest (ensemble).
5. **Evaluation** — accuracy, precision, recall, F1, ROC-AUC, confusion matrix for each model.
6. **Feature importance** — Random Forest's most predictive features (pH, chloramines, sulfate, TDS, turbidity) are cross-referenced with WHO drinking-water thresholds.
7. **Microbiological interpretation** — why each feature matters for *Vibrio cholerae*, *E. coli*, coliform survival, and disinfection chemistry.

### What makes this notebook different

- **Domain-aware**: every result is connected back to microbiology (chlorine speciation, turbidity-shielded bacteria, sulfate-reducing bacteria, etc.).
- **No data leakage** — the scaler / imputer are fit on the training set only.
- **All three models are compared on the same split** for a fair benchmark.
- **Class-weighted** training to handle the moderate 60 / 40 imbalance.
- **Reproducible** — `random_state=42` throughout.
- **Production-style code** — the notebook imports a `src/` package so the same code that runs the notebook also runs as a CLI (`python main.py`).

### Best result (typical)

| Model | Accuracy | F1 | ROC-AUC |
|---|---|---|---|
| Logistic Regression | ~0.62 | 0.57 | 0.63 |
| Decision Tree | ~0.65 | 0.62 | 0.65 |
| **Random Forest** | **~0.70** | **0.67** | **0.71** |

### Suggested follow-up

- Tune hyperparameters with `GridSearchCV`.
- Add XGBoost / LightGBM.
- Compute SHAP values for per-sample explainability.
- Build a Streamlit dashboard.
- Retrain on a regional dataset (e.g. Bangladeshi tube-well samples).

### Citation

If this notebook helped your work, please cite:

> Zaman, R. (2026). *AI-Based Water Contamination Detection System Using Machine Learning.* Undergraduate research project, Department of Microbiology, Notre Dame University Bangladesh.
