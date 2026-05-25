"""Locate and load the water-quality dataset (real or synthetic)."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

EXPECTED_COLUMNS = [
    "ph", "Hardness", "Solids", "Chloramines", "Sulfate",
    "Conductivity", "Organic_carbon", "Trihalomethanes",
    "Turbidity", "Potability",
]


def find_dataset(data_dir: str | Path = "data") -> Path:
    """Return path to a usable dataset, generating a synthetic one if needed."""
    data_dir = Path(data_dir)
    real = data_dir / "water_potability.csv"
    synth = data_dir / "water_potability_synthetic.csv"

    if real.exists():
        return real
    if synth.exists():
        return synth

    # Auto-generate synthetic data.
    from . import generate_synthetic_data
    return generate_synthetic_data.main(synth)


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    """Load and validate the dataset."""
    if path is None:
        path = find_dataset()
    df = pd.read_csv(path)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset {path} is missing expected columns: {missing}. "
            f"Expected: {EXPECTED_COLUMNS}"
        )
    df = df[EXPECTED_COLUMNS].copy()
    print(f"[data_loader] Loaded {len(df)} rows from {path}")
    return df


def quick_summary(df: pd.DataFrame) -> None:
    print("\n=== Dataset summary ===")
    print(f"Shape: {df.shape}")
    print("\nMissing values per column:")
    print(df.isna().sum())
    print("\nClass balance (Potability):")
    print(df["Potability"].value_counts(dropna=False))
    print("\nDescriptive statistics:")
    print(df.describe().round(2))
