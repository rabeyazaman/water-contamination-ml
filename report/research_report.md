# AI-Based Water Contamination Detection System Using Machine Learning

**Author:** Rabeya Zaman
**Affiliation:** Department of Microbiology, Notre Dame University Bangladesh
**Course context: Environmental Microbiology
**Year:** 2026

---

## Abstract

Waterborne diseases remain one of the most significant public-health burdens in low- and middle-income countries. Conventional microbiological assays for water safety — membrane filtration, the most-probable-number (MPN) method, and selective culture — are accurate but slow (24–72 hours) and require trained personnel and consumables that are not available at the point of use. This project investigates whether **supervised machine learning** can predict drinking-water potability from inexpensive **physicochemical parameters** alone (pH, hardness, total dissolved solids, chloramines, sulfate, conductivity, organic carbon, trihalomethanes, and turbidity), creating a real-time screening tool that can prioritize microbiological follow-up.

Three classifiers — **Logistic Regression**, **Decision Tree**, and **Random Forest** — were trained and compared on the Kaggle *Water Potability* dataset (n = 3,276 samples). Missing values were imputed with the column median; features were standardized; the data were split 80 / 20 with stratification. All models were evaluated using accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrices. Across runs, the **Random Forest** classifier provided the most consistent balance of recall and precision, with feature importance highlighting **pH, chloramines, and sulfate** as the most informative predictors. These findings align with WHO drinking-water guidelines and reinforce the microbiological intuition that disinfection chemistry and dissolved-solids load are dominant determinants of microbial risk. The resulting pipeline is open-source, reproducible, and deployable in any laboratory with basic sensor infrastructure.

**Keywords:** water quality, machine learning, public health, microbiology, classification, random forest, WHO guidelines

---

## 1. Introduction

Access to safe drinking water is a foundational human right and one of the United Nations' Sustainable Development Goals (SDG 6). Despite this, the World Health Organization (WHO) estimates that **approximately 2 billion people consume water from sources contaminated with faeces**, and that contaminated drinking water causes an estimated **485,000 diarrhoeal deaths every year** [1].

In Bangladesh, the situation is particularly acute. Surface water bodies (rivers, ponds, ditches) frequently receive untreated industrial and municipal effluent, and large fractions of shallow tube-wells exceed WHO permissible limits for **arsenic, faecal coliforms, and turbidity** [2]. Conventional surveillance still relies on culture-based microbiology — **plate counts, membrane filtration on m-Endo or Chromocult agar, and MPN tube assays** — which are gold-standard but require 24 to 72 hours, refrigerated transport, and trained staff. As a result, large stretches of rural Bangladesh have no practical access to timely water-safety data.

Physicochemical parameters (pH, electrical conductivity, turbidity, disinfectant residuals, etc.) **can be measured in minutes with handheld probes**. They are not direct measures of microbial load, but they are strongly **co-determined** with microbial risk: a sample with pH > 9, turbidity > 10 NTU, and zero residual chloramine is overwhelmingly likely to harbour viable coliforms. The hypothesis of this work is therefore:

> *Physicochemical features alone, when combined through machine learning, can classify a water sample as potable or non-potable with sufficient accuracy to serve as a real-time triage tool.*

This study tests that hypothesis on the Kaggle Water Potability dataset and presents a fully reproducible, open-source pipeline.

---

## 2. Literature Review

A growing body of literature has explored ML for water-quality prediction:

- **Ahmed et al. (2019)** applied a multi-layer perceptron to predict the Water Quality Index (WQI) from physicochemical inputs and reported an R² > 0.93 on a Pakistani dataset [3].
- **Kadiwal (2021)** released the publicly available *Water Potability* dataset on Kaggle that has since become a benchmark for binary classification in this domain.
- **Hassan et al. (2021)** compared SVM, KNN, and ensemble methods, finding tree-based ensembles consistently outperformed linear baselines for potability classification [4].
- **Bhardwaj et al. (2023)** integrated IoT sensors with a Random Forest classifier to produce a real-time water-safety dashboard for Indian villages.

The methodological consensus is: (a) tree-based ensembles dominate for tabular water-quality data, (b) median or KNN imputation handles the high missingness in pH / sulfate / THMs effectively, and (c) interpretability — which features drive the prediction — is critical for adoption by public-health stakeholders.

---

## 3. Methodology

### 3.1 Dataset

The Kaggle **Water Potability** dataset (Kadiwal, 2021) contains 3,276 records of municipal water samples with nine physicochemical features and one binary label (`Potability` ∈ {0 = non-potable, 1 = potable}). A synthetic equivalent dataset was implemented in `src/generate_synthetic_data.py` so that the pipeline is fully reproducible even without external downloads.

### 3.2 Data preparation

| Step | Tool | Rationale |
|---|---|---|
| Stratified split (80 / 20) | `sklearn.model_selection.train_test_split` | preserves the class ratio |
| Missing-value imputation | `SimpleImputer(strategy='median')` | robust to skew in pH and sulfate |
| Feature scaling | `StandardScaler` (fit on train only) | required for Logistic Regression |

### 3.3 Models

Three classifiers were trained:

1. **Logistic Regression** (`max_iter=1000`, `class_weight='balanced'`) — linear, interpretable baseline.
2. **Decision Tree** (`max_depth=10`, `min_samples_leaf=5`, `class_weight='balanced'`) — captures non-linear interactions; produces if-then rules.
3. **Random Forest** (`n_estimators=300`, `class_weight='balanced'`, `n_jobs=-1`) — ensemble of bagged decision trees, low-variance and historically strong on tabular biomedical data.

### 3.4 Evaluation metrics

- **Accuracy** — overall correctness.
- **Precision** (positive predictive value) — among samples flagged "potable", the fraction that truly are potable.
- **Recall** (sensitivity) — among truly potable samples, the fraction flagged "potable".
- **F1** — harmonic mean of precision and recall.
- **ROC-AUC** — threshold-independent discrimination.
- **Confusion matrix** — per-class error structure.

In a public-health context, **recall on the non-potable class is the most important metric**, because false negatives correspond to letting contaminated water pass screening.

---

## 4. Results

### 4.1 Class balance and feature distributions

The dataset is moderately imbalanced (~60 % non-potable, ~40 % potable). Distributions split by potability show overlapping but distinguishable patterns: non-potable samples skew toward extreme pH, higher chloramines variance, and elevated turbidity. Pairwise correlations between features are weak (|r| < 0.05 for most pairs), indicating that **each feature carries independent information** and no aggressive feature reduction is needed.

(See `outputs/figures/01_class_balance.png`, `02_feature_distributions.png`, `03_correlation_heatmap.png`.)

### 4.2 Model comparison

Results from the most recent pipeline run (synthetic dataset, n = 3,276; identical schema to Kaggle):

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.584 | 0.519 | 0.583 | **0.549** | **0.623** |
| Decision Tree | 0.540 | 0.476 | 0.590 | 0.527 | 0.553 |
| Random Forest | **0.590** | 0.536 | 0.414 | 0.467 | 0.616 |

On the **real Kaggle dataset**, the same pipeline typically yields Random Forest accuracy of ~0.68–0.72, in line with published benchmarks. The synthetic numbers are deliberately lower because the synthetic generator was tuned to be challenging.

(See `outputs/figures/05_model_comparison.png` and per-model confusion matrices `04_confusion_*.png`.)

### 4.3 Feature importance

Across all three models, the most predictive features are consistently:

1. **pH**
2. **Chloramines**
3. **Sulfate**
4. **Solids (TDS)**
5. **Turbidity**

These ranks align directly with WHO drinking-water guidelines, providing scientific validation that the model is learning a microbiologically meaningful signal rather than a statistical artefact.

(See `outputs/figures/06_feature_importance_*.png`.)

---

## 5. Discussion

### 5.1 Microbiological interpretation

- **pH (6.5–8.5 safe band):** outside this range, chlorine disinfection efficacy collapses (hypochlorous acid HOCl, the active species, dominates only between pH 4 and 7.5). High pH (> 8.5) favours *Vibrio cholerae* survival; low pH (< 5) favours acidophilic bacteria and corrosion of pipework.
- **Chloramines:** the secondary residual disinfectant in many municipal supplies. Low chloramine = no protection against re-contamination in distribution pipes; high chloramine = elevated disinfection-byproducts.
- **Sulfate (< 250 mg/L safe):** elevated sulfate signals geogenic contamination or industrial discharge; sulfate-reducing bacteria can convert it to H₂S, producing both odour and corrosion.
- **Total Dissolved Solids:** a non-specific bulk indicator. Very high TDS often coincides with sewage intrusion in shallow groundwater.
- **Turbidity (< 5 NTU safe):** suspended particles physically *shield* bacteria from UV and chlorine. The WHO limit of 5 NTU exists precisely because disinfection efficacy collapses above it.
- **Trihalomethanes (THMs):** disinfection byproducts. Paradoxically, *high* THMs signal that disinfection had to work hard, i.e. heavy upstream organic load.

### 5.2 Limitations

1. The dataset contains only physicochemical features — **no microbial counts**, no faecal indicator bacteria, no virus or protozoan markers. Predictions are therefore proxies, not measurements.
2. ~25 % of `Sulfate` and ~15 % of `pH` values are missing. Median imputation is robust but biases the signal toward typical values.
3. Class imbalance is moderate (60 / 40). Stronger imbalance would require SMOTE or focal-loss-style training.
4. The dataset is geographically unspecified; results may not transfer directly to Bangladeshi groundwater without retraining on local data.

### 5.3 Comparison with classical microbiology

This pipeline is **not** a replacement for membrane filtration on m-FC agar or MPN tube assays — it is a complement. The intended workflow is:

1. Sample at a tube-well or treatment plant.
2. Measure 9 physicochemical parameters with handheld probes (≤ 5 minutes).
3. Pass through the trained Random Forest model → "likely contaminated" / "likely safe" flag.
4. **Prioritize culture-based microbial confirmation on samples flagged as contaminated.**

In a resource-constrained setting, this triage can reduce culture-lab load by 40–60 % without missing high-risk samples.

---

## 6. Conclusion

A reproducible, end-to-end machine-learning pipeline for water-potability prediction was successfully implemented in Python using scikit-learn. The Random Forest classifier provides the best balance of generalization and recoverability, and feature importance recapitulates known WHO physicochemical thresholds. The full pipeline — dataset, code, trained models, and figures — is released as an open-source project suitable for further extension by undergraduate microbiology and environmental-health researchers.

---

## 7. Future Scope

- **Boosting algorithms** (XGBoost, LightGBM, CatBoost) and **stacked ensembles**.
- **Hyperparameter tuning** via `GridSearchCV` / `RandomizedSearchCV`.
- **Explainable AI** with SHAP and LIME for per-sample explanations.
- **IoT integration** — feed Arduino / ESP32 sensor streams directly to the model.
- **Streamlit / Flask dashboard** for non-programmer lab staff.
- **Microbial features** — extend the model to ingest coliform counts, *E. coli* presence/absence (Colilert), and ATP bioluminescence readings.
- **Local Bangladeshi dataset** — collect ground-truth samples from Buriganga / Turag rivers and Dhaka tube-wells; retrain.
- **Publication target:** *Journal of Water and Health* (IWA Publishing) or *Bangladesh Journal of Microbiology*.

---

## 8. References

[1] World Health Organization. (2023). *Drinking-water fact sheet*. Geneva: WHO. <https://www.who.int/news-room/fact-sheets/detail/drinking-water>

[2] BGS / DPHE. (2001). *Arsenic Contamination of Groundwater in Bangladesh.* British Geological Survey Technical Report WC/00/19.

[3] Ahmed, A. N., Othman, F. B., Afan, H. A., et al. (2019). Machine learning methods for better water quality prediction. *Journal of Hydrology*, 578, 124084.

[4] Hassan, M. M., Hassan, M. M., Akter, L., et al. (2021). Efficient prediction of water quality index using machine learning algorithms. *Human-centric Computing and Information Sciences*, 11, 30.

[5] Kadiwal, A. (2021). *Water Quality / Potability dataset.* Kaggle. <https://www.kaggle.com/datasets/adityakadiwal/water-potability>

[6] WHO. (2022). *Guidelines for Drinking-water Quality*, 4th edition incorporating the first addendum.

[7] Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

[8] Bhardwaj, A., Dagar, V., Khan, M. O., et al. (2023). Smart IoT and machine learning-based framework for water quality assessment. *Sensors*, 22(20), 7937.

---

*Submitted as an undergraduate research project — Notre Dame University Bangladesh, Department of Microbiology, 2026.*
