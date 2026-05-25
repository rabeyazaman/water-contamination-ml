"""Cleaning, imputation, scaling, and train/test splitting."""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = [
    "ph", "Hardness", "Solids", "Chloramines", "Sulfate",
    "Conductivity", "Organic_carbon", "Trihalomethanes", "Turbidity",
]
TARGET_COL = "Potability"


@dataclass
class PreparedData:
    X_train: np.ndarray
    X_test: np.ndarray
    y_train: pd.Series
    y_test: pd.Series
    feature_names: list[str]
    scaler: StandardScaler
    imputer: SimpleImputer


def prepare_data(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42,
) -> PreparedData:
    """Impute missing values with the column median, then standardize features.

    A stratified split preserves the Potability class ratio in train/test sets.
    """
    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].astype(int)

    # Stratified split BEFORE scaling so the scaler is fit only on training data.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    imputer = SimpleImputer(strategy="median")
    X_train_i = imputer.fit_transform(X_train)
    X_test_i  = imputer.transform(X_test)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train_i)
    X_test_s  = scaler.transform(X_test_i)

    print(f"[preprocessing] Train shape: {X_train_s.shape} | Test shape: {X_test_s.shape}")
    print(f"[preprocessing] Train class balance: {y_train.value_counts().to_dict()}")
    print(f"[preprocessing] Test  class balance: {y_test.value_counts().to_dict()}")

    return PreparedData(
        X_train=X_train_s,
        X_test=X_test_s,
        y_train=y_train,
        y_test=y_test,
        feature_names=FEATURE_COLS,
        scaler=scaler,
        imputer=imputer,
    )
