"""
Reusable ML inference module.

Loads the serialized production model once, validates features,
and performs prediction using the exact training feature order.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "best_solar_model.joblib"
)

FEATURE_ORDER = [
    "year",
    "month",
    "day",
    "day_of_year",
    "week_number",
    "wind_speed_ms",
]


@lru_cache(maxsize=1)
def load_model():
    """
    Load the trained Random Forest model once and reuse it.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def validate_features(features: dict):
    """
    Validate completeness, unexpected fields, exact order,
    numeric values and NaN values.
    """
    if not isinstance(features, dict):
        raise TypeError(
            "Features must be provided as a dictionary."
        )

    received_order = list(features.keys())

    missing = [
        feature
        for feature in FEATURE_ORDER
        if feature not in features
    ]

    if missing:
        raise ValueError(
            f"Missing required features: {missing}"
        )

    unexpected = [
        feature
        for feature in received_order
        if feature not in FEATURE_ORDER
    ]

    if unexpected:
        raise ValueError(
            f"Unexpected features: {unexpected}"
        )

    if received_order != FEATURE_ORDER:
        raise ValueError(
            "Invalid feature order. Expected: "
            f"{FEATURE_ORDER}"
        )

    for feature in FEATURE_ORDER:
        try:
            value = float(features[feature])
        except (TypeError, ValueError):
            raise ValueError(
                f"Feature '{feature}' must be numeric."
            )

        if pd.isna(value):
            raise ValueError(
                f"Feature '{feature}' cannot be NaN."
            )


def predict_solar_radiation(features: dict) -> float:
    """
    Generate solar radiation prediction using the serialized model.
    """
    validate_features(features)

    values = [
        float(features[feature])
        for feature in FEATURE_ORDER
    ]

    dataframe = pd.DataFrame(
        [values],
        columns=FEATURE_ORDER,
    )

    model = load_model()

    prediction = float(
        model.predict(dataframe)[0]
    )

    if pd.isna(prediction):
        raise RuntimeError(
            "Model returned an invalid prediction."
        )

    prediction = max(0.0, prediction)

    return round(prediction, 4)