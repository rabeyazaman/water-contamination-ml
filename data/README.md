# Data

This folder stores the dataset used by the project.

## Option A — Use the real Kaggle dataset (recommended for final results)

1. Download: <https://www.kaggle.com/datasets/adityakadiwal/water-potability>
2. Place the file **`water_potability.csv`** directly in this `data/` folder.

The columns must be (in any order):

```
ph, Hardness, Solids, Chloramines, Sulfate, Conductivity,
Organic_carbon, Trihalomethanes, Turbidity, Potability
```

## Option B — Use the auto-generated synthetic dataset

If you don't place a real CSV here, running `python main.py` will automatically
generate a realistic synthetic dataset at `data/water_potability_synthetic.csv`
using `src/generate_synthetic_data.py`. The schema is identical, so all
downstream code works without modification.

The synthetic dataset is good enough to **demonstrate the pipeline**,
but final results in the report should be based on the real Kaggle dataset.
