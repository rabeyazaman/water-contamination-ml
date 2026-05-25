# Roadmap — from this baseline to a publishable / scholarship-grade project

This file lists concrete next-step upgrades, ranked by how much value they add for your CV, scholarship applications, and a possible publication. Each upgrade is small enough to finish in a weekend.

---

## Tier 1 — Polish (do these next, ~1 week total)

### 1.1 Download the real Kaggle dataset
- Get `water_potability.csv` from <https://www.kaggle.com/datasets/adityakadiwal/water-potability>
- Place it in `data/`.
- Re-run `python main.py`. Random Forest accuracy should rise to ~0.68–0.72.
- Update the numbers in `report/research_report.md` § 4.2.

### 1.2 Hyperparameter tuning
- Add a `src/tune.py` script using `sklearn.model_selection.GridSearchCV`.
- Search over `n_estimators`, `max_depth`, `min_samples_leaf` for Random Forest.
- Save the best params to `outputs/best_params.json`.

### 1.3 Cross-validation
- Replace the single train/test split with `StratifiedKFold(n_splits=5)`.
- Report mean ± std for each metric. Reviewers expect this.

---

## Tier 2 — Advanced ML (~2 weeks)

### 2.1 XGBoost & LightGBM
```bash
pip install xgboost lightgbm
```
Add them to `src/train_models.py`. They typically beat Random Forest by 1–3 % on this dataset.

### 2.2 Class-imbalance handling
- Try `imbalanced-learn`'s SMOTE on the training set only.
- Compare F1 of the minority (potable) class with and without SMOTE.

### 2.3 SHAP for explainability
```bash
pip install shap
```
- Generate a SHAP summary plot and a SHAP force plot for one positive and one negative sample.
- This is *the* feature reviewers love for biomedical ML.

---

## Tier 3 — Productization (~2 weeks)

### 3.1 Streamlit dashboard
Create `app.py`:
```python
import streamlit as st, joblib, pandas as pd
model = joblib.load("outputs/models/best_model.pkl")
st.title("Water Potability Predictor")
# 9 number inputs → DataFrame → model.predict_proba → traffic-light output
```
Deploy free on **Streamlit Community Cloud**.

### 3.2 IoT integration prototype
- Wire an **ESP32** to a pH probe (Atlas Scientific or DFRobot), turbidity sensor (SEN0189), and TDS sensor (SEN0244).
- Stream readings over MQTT to a Python listener that calls `model.predict_proba`.
- Even a *mocked* version with simulated sensor data is impressive in a poster.

### 3.3 Docker
Add a `Dockerfile` so the entire pipeline runs in a single container — common university IT requirement.

---

## Tier 4 — Research-grade extensions (~1 month)

### 4.1 Collect a Bangladeshi dataset
- 50–100 water samples from Dhaka tube-wells, Buriganga, Turag, NDUB campus.
- Measure 9 physicochemical features + perform membrane-filtration coliform count.
- Public-health partner: ICDDR,B microbiology lab, or NDUB Microbiology Department.

### 4.2 Multi-label / regression extension
- Predict CFU/100 mL of total coliforms (regression) instead of binary potability.
- Use the same features.

### 4.3 Write a paper
- Target journals (open access, no APC required for students):
  - *Bangladesh Journal of Microbiology* (BSM)
  - *Heliyon* (Elsevier, ~$1000 APC waivers available)
  - *Journal of Water Sanitation and Hygiene for Development* (IWA)
- Target conferences:
  - **IEEE ICCIT** (held annually in Bangladesh)
  - **ICBSLP**
  - **ICASERT**

---

## Tier 5 — Scholarship / Portfolio positioning

### For undergraduate scholarships (DAAD, MEXT, Fulbright, Erasmus):
- Push this repo to your GitHub: `github.com/<yourhandle>/water-contamination-ml`
- Pin it as a featured repo.
- In your CV: "Built and open-sourced an end-to-end ML pipeline for water contamination detection; benchmarked 3 models; cross-referenced with WHO guidelines; report and reproducible code published on GitHub and Kaggle."
- Print one A0 poster for any NDUB science fair or research symposium.

### For Master's / PhD applications:
- Cite this project under **"Independent research"** in your SOP.
- Reach out to professors working in *environmental microbiology* or *bioinformatics* with this repo link as evidence of self-direction.

### Possible advanced extensions to mention in your SOP
- "I plan to extend this work into **metagenomic prediction** — predicting microbial community composition from physicochemical inputs using deep learning."
- "I would like to combine this with **antimicrobial-resistance gene detection** in drinking water (qPCR / 16S amplicon sequencing) to study the human-health risk of waterborne ARGs."

---

## Quick reference — files you should edit next

| You want to ... | Edit this file |
|---|---|
| Use the real Kaggle data | drop `water_potability.csv` into `data/` — no code change needed |
| Try a new model | `src/train_models.py` (`build_models` function) |
| Add a new metric | `src/evaluate.py` (`evaluate_model` function) |
| Add a new plot | `src/visualize.py` |
| Change train/test split | `src/preprocessing.py` (`prepare_data` function) |
| Update the report | `report/research_report.md` |
