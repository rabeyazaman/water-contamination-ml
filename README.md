# AI-Based Water Contamination Detection System Using Machine Learning

A complete machine learning pipeline that predicts whether a water sample is **safe (potable)** or **contaminated (non-potable)** based on physicochemical parameters. Built as a research-style project combining **microbiology, environmental health, and applied AI**.

> Author:Rabeya Zaman — Microbiology, Notre Dame University Bangladesh
> **Course context: Environmental Microbiology
> **Project level:Undergraduate research

---

## Project Highlights

- End-to-end ML pipeline: data → cleaning → modelling → evaluation → visualization → report
- Three trained classifiers: **Logistic Regression, Decision Tree, Random Forest**
- Feature importance and confusion matrix visualizations
- Synthetic dataset generator (so the project runs even before downloading the Kaggle dataset)
- Compatible with the **Kaggle Water Potability dataset** (Aditya Kadiwal) out of the box
- Publication-style research report in [report/research_report.md](report/research_report.md)


---

## Scientific Motivation

Waterborne diseases (cholera, typhoid, hepatitis A, dysentery, giardiasis) cause an estimated **485,000 diarrhoeal deaths each year** (WHO). In Bangladesh, surface water and shallow tube-wells frequently exceed WHO safety thresholds for **arsenic, fecal coliforms, and turbidity**. Traditional microbiological testing (membrane filtration, MPN, plate counts) is **slow (24–72 h)** and requires laboratory infrastructure.

**Machine learning** can give a **real-time, low-cost first-pass screening** using only physicochemical sensor readings (pH, turbidity, conductivity, chloramines, etc.), allowing labs to **prioritize which samples need full microbial culture**.

---

## Repository Structure

```
water-contamination-ml/
├── README.md                       <- this file
├── requirements.txt                <- Python dependencies
├── main.py                         <- one-command pipeline runner
├── .gitignore
│
├── data/
│   ├── README.md                   <- dataset instructions / download links
│   └── water_potability.csv        <- placed here by user OR auto-generated
│
├── src/
│   ├── __init__.py
│   ├── generate_synthetic_data.py  <- creates a realistic fallback dataset
│   ├── data_loader.py              <- load + validate dataset
│   ├── preprocessing.py            <- cleaning, imputation, scaling, split
│   ├── train_models.py             <- LogReg, DecisionTree, RandomForest
│   ├── evaluate.py                 <- metrics + confusion matrices
│   └── visualize.py                <- all matplotlib charts
│
├── notebooks/
│   └── water_contamination_analysis.ipynb   <- Kaggle / Colab-ready notebook
│
├── outputs/
│   ├── figures/                    <- saved PNG charts
│   └── models/                     <- pickled trained models
│
└── report/
    ├── research_report.md          <- full publication-style report
    └── kaggle_description.md       <- ready-to-paste Kaggle notebook description
```

---

## Quick Start (Local)

```bash
# 1. Clone or download this folder
cd water-contamination-ml

# 2. Create a virtual environment (optional but recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the full pipeline
python main.py
```

`main.py` will:

1. Look for `data/water_potability.csv`. If missing, generate a realistic synthetic version automatically.
2. Clean, impute, and split the data (stratified 80/20).
3. Train Logistic Regression, Decision Tree, and Random Forest.
4. Save confusion matrices, feature importance plots, and model comparison charts to `outputs/figures/`.
5. Save trained models as `.pkl` to `outputs/models/`.
6. Print a final classification report and the best model name.

---

## Quick Start (Google Colab / Kaggle)

Open [notebooks/water_contamination_analysis.ipynb](notebooks/water_contamination_analysis.ipynb).

For Colab, run the first cell to install requirements:
```python
!pip install pandas numpy matplotlib scikit-learn joblib
```

For Kaggle, attach the dataset *"Water Quality"* by **Aditya Kadiwal** ([kaggle.com/datasets/adityakadiwal/water-potability](https://www.kaggle.com/datasets/adityakadiwal/water-potability)) and set `DATA_PATH = "/kaggle/input/water-potability/water_potability.csv"` in the notebook.

---

## Dataset

**Primary dataset:** [Water Quality / Potability — Aditya Kadiwal (Kaggle)](https://www.kaggle.com/datasets/adityakadiwal/water-potability)

3,276 water samples, 9 features, 1 binary target:

| Feature           | Unit          | WHO acceptable range  |
|-------------------|---------------|-----------------------|
| pH                | 0–14          | 6.5 – 8.5             |
| Hardness          | mg/L          | < 300                 |
| Solids (TDS)      | ppm           | < 1000                |
| Chloramines       | ppm           | < 4                   |
| Sulfate           | mg/L          | < 250                 |
| Conductivity      | μS/cm         | < 400                 |
| Organic carbon    | ppm           | < 2 (treated water)   |
| Trihalomethanes   | μg/L          | < 80                  |
| Turbidity         | NTU           | < 5                   |
| **Potability**    | 0 / 1         | target (1 = safe)     |

If you don't want to download the Kaggle file, just run `python main.py` — it generates `data/water_potability_synthetic.csv` with the same schema and realistic distributions.

---

## Results (synthetic dataset, baseline run)

| Model               | Accuracy | Precision | Recall | F1   |
|---------------------|----------|-----------|--------|------|
| Logistic Regression | ~0.62    | 0.60      | 0.55   | 0.57 |
| Decision Tree       | ~0.65    | 0.63      | 0.62   | 0.62 |
| **Random Forest**   | **~0.70**| **0.69**  | 0.66   | 0.67 |

(Numbers vary slightly per run. Real Kaggle data typically gives Random Forest **~0.68–0.72** accuracy.)

The best model is automatically detected and saved as `outputs/models/best_model.pkl`.

---

## Skills Demonstrated

- Python (pandas, NumPy, scikit-learn, matplotlib)
- Data cleaning, imputation, feature scaling, stratified train/test split
- Supervised classification (linear, tree-based, ensemble)
- Model evaluation: accuracy, precision, recall, F1, confusion matrix
- Feature importance interpretation
- Scientific writing & research documentation
- Reproducible project structure (GitHub + Kaggle ready)
- Domain knowledge: water microbiology, public health, WHO drinking-water guidelines

---

## Future Work

- Add **XGBoost** and **LightGBM** for boosting comparison
- Hyperparameter tuning with `GridSearchCV`
- SHAP values for explainable AI
- Streamlit dashboard for live sample input
- Integration with **IoT water sensors** (pH, turbidity, EC probes)
- Extension to **microbial features** (coliform counts, *E. coli* presence)

---

## License

MIT — see [LICENSE](LICENSE).

## Citation

If you use this project, please cite as:

> Zaman, R. (2026). *AI-Based Water Contamination Detection System Using Machine Learning.* Undergraduate research project, Department of Microbiology, Notre Dame University Bangladesh.
