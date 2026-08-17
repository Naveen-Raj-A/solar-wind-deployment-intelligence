"""Reusable, cached inference for the persisted solar Random Forest model."""

from __future__ import annotations

from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Mapping

import joblib
import pandas as pd

FEATURE_ORDER = (
    "year",
    "month",
    "day",
    "day_of_year",
    "week_number",
    "wind_speed_ms",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "engine" / "models" / "best_solar_model.joblib"


@lru_cache(maxsize=1)
def load_model():
    """Load the serialized model once per Python process."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )
    return joblib.load(MODEL_PATH)


def validate_features(features: Mapping[str, float]) -> None:
    """Validate completeness and exact feature order contract."""
    if not isinstance(features, Mapping):
        raise TypeError("features must be a mapping/dictionary.")

    received = tuple(features.keys())
    expected = FEATURE_ORDER

    missing = [name for name in expected if name not in features]
    extra = [name for name in received if name not in expected]

    if missing:
        raise ValueError(
            f"Missing required ML features: {missing}"
        )

    if extra:
        raise ValueError(
            f"Unexpected ML features: {extra}"
        )

    if received != expected:
        raise ValueError(
            "Invalid feature order. Expected exactly: "
            f"{list(expected)}"
        )

    for name in expected:
        try:
            value = float(features[name])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Feature '{name}' must be numeric."
            ) from exc

        if not pd.notna(value):
            raise ValueError(
                f"Feature '{name}' cannot be NaN."
            )


def predict_solar_radiation(
    features: Mapping[str, float],
) -> float:
    """Run one prediction using the cached trained model."""
    validate_features(features)

    row = {
        name: float(features[name])
        for name in FEATURE_ORDER
    }

    frame = pd.DataFrame(
        [[row[name] for name in FEATURE_ORDER]],
        columns=list(FEATURE_ORDER),
    )

    prediction = float(load_model().predict(frame)[0])

    if not pd.notna(prediction):
        raise RuntimeError("Model returned a non-finite prediction.")

    return round(max(0.0, prediction), 4)
