"""
Generate a realistic synthetic water-quality dataset that mirrors the schema of
the Kaggle "Water Potability" dataset (Aditya Kadiwal).

The distributions and WHO-style thresholds below are chosen so that the resulting
CSV behaves similarly to the real dataset: roughly 60/40 non-potable to potable,
noisy features, and ~10-15% missing values in pH, Sulfate, and Trihalomethanes.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

RNG_SEED = 42
N_SAMPLES = 3276  # same size as Kaggle dataset


def _truncnorm(rng: np.random.Generator, mean: float, std: float,
               low: float, high: float, n: int) -> np.ndarray:
    """Sample from a normal distribution, clipped to [low, high]."""
    x = rng.normal(loc=mean, scale=std, size=n)
    return np.clip(x, low, high)


def generate_dataset(n_samples: int = N_SAMPLES, seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Latent "true safety" score — combines features the way WHO guidelines do.
    # We will create features first, then derive Potability from them.
    ph              = _truncnorm(rng, 7.08, 1.50, 0.0, 14.0, n_samples)
    hardness        = _truncnorm(rng, 196.0, 32.0, 50.0, 350.0, n_samples)
    solids          = _truncnorm(rng, 22014.0, 8770.0, 320.0, 61000.0, n_samples)
    chloramines     = _truncnorm(rng, 7.12, 1.58, 0.5, 13.0, n_samples)
    sulfate         = _truncnorm(rng, 333.0, 41.0, 130.0, 480.0, n_samples)
    conductivity    = _truncnorm(rng, 426.0, 80.0, 180.0, 750.0, n_samples)
    organic_carbon  = _truncnorm(rng, 14.3, 3.30, 2.0, 28.0, n_samples)
    trihalomethanes = _truncnorm(rng, 66.4, 16.2, 0.7, 124.0, n_samples)
    turbidity       = _truncnorm(rng, 3.97, 0.78, 1.5, 6.7, n_samples)

    # Derive potability from a soft scoring rule that mimics WHO thresholds.
    # Each feature contributes a "penalty" the further it is from its safe band.
    def penalty(x, low, high, weight=1.0):
        below = np.maximum(low - x, 0.0) / max(low, 1e-6)
        above = np.maximum(x - high, 0.0) / max(high, 1e-6)
        return weight * (below + above)

    score = (
        penalty(ph,              6.5,   8.5, weight=1.2)
        + penalty(hardness,       0.0, 300.0, weight=0.6)
        + penalty(solids,         0.0, 1000.0 * 30, weight=0.5)  # TDS is huge in raw water
        + penalty(chloramines,    0.0,   4.0, weight=1.0)
        + penalty(sulfate,        0.0, 250.0, weight=0.8)
        + penalty(conductivity,   0.0, 400.0, weight=0.7)
        + penalty(organic_carbon, 0.0,  10.0, weight=0.9)
        + penalty(trihalomethanes,0.0,  80.0, weight=1.0)
        + penalty(turbidity,      0.0,   5.0, weight=1.1)
    )

    # Add Gaussian noise so the model can't trivially recover the rule.
    noise = rng.normal(0.0, 1.5, size=n_samples)
    logits = -1.2 * score + 1.6 + noise   # tuned so positives ~40%
    prob_safe = 1.0 / (1.0 + np.exp(-logits))
    potability = (rng.uniform(0.0, 1.0, size=n_samples) < prob_safe).astype(int)

    df = pd.DataFrame({
        "ph": ph,
        "Hardness": hardness,
        "Solids": solids,
        "Chloramines": chloramines,
        "Sulfate": sulfate,
        "Conductivity": conductivity,
        "Organic_carbon": organic_carbon,
        "Trihalomethanes": trihalomethanes,
        "Turbidity": turbidity,
        "Potability": potability,
    })

    # Inject realistic missing values like the Kaggle dataset does.
    _inject_nans(df, "ph",              frac=0.15, rng=rng)
    _inject_nans(df, "Sulfate",         frac=0.24, rng=rng)
    _inject_nans(df, "Trihalomethanes", frac=0.05, rng=rng)

    return df


def _inject_nans(df: pd.DataFrame, col: str, frac: float, rng: np.random.Generator) -> None:
    n = len(df)
    k = int(n * frac)
    idx = rng.choice(n, size=k, replace=False)
    df.loc[idx, col] = np.nan


def main(out_path: str | Path = "data/water_potability_synthetic.csv") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_dataset()
    df.to_csv(out_path, index=False)
    print(f"[generate_synthetic_data] Wrote {len(df)} samples to {out_path}")
    print(df["Potability"].value_counts(normalize=True).rename("class_balance"))
    return out_path


if __name__ == "__main__":
    main()
