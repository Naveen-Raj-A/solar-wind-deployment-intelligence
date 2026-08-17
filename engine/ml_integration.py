"""
Machine Learning Integration Layer

Runs the trained solar model for prediction and explainability while
preserving an available measured/historical solar resource value for
engineering scoring.

If measured/historical solar is available, it remains the engineering
scoring value. The ML prediction is still returned for prediction and
explainability. If measured/historical solar is unavailable, ML is used
as a fallback.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from engine.ml_inference import predict_solar_radiation
from engine.explainability import predict_solar_with_explanation


FEATURE_ORDER = [
    "year",
    "month",
    "day",
    "day_of_year",
    "week_number",
    "wind_speed_ms",
]


def _extract_wind_speed(report: dict[str, Any]) -> float:
    datasets = report.get("datasets", {})
    value = (
        datasets.get("wind", {})
        .get("wind_speed_statistics", {})
        .get("mean_ms")
    )

    if value is None:
        value = (
            datasets.get("nasa_power", {})
            .get("wind_speed_statistics", {})
            .get("mean_ms")
        )

    if value is None:
        raise ValueError("Wind speed mean_ms is unavailable for ML prediction.")

    return float(value)


def _extract_solar_resource(report: dict[str, Any]) -> float | None:
    value = (
        report.get("datasets", {})
        .get("nasa_power", {})
        .get("solar_resource", {})
        .get("solar_radiation_kwh_m2_day")
    )

    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    return value if value >= 0 else None


def _build_features(report: dict[str, Any]) -> dict[str, float]:
    now = datetime.now(timezone.utc)

    features = {
        "year": float(now.year),
        "month": float(now.month),
        "day": float(now.day),
        "day_of_year": float(now.timetuple().tm_yday),
        "week_number": float(now.isocalendar().week),
        "wind_speed_ms": _extract_wind_speed(report),
    }

    if list(features.keys()) != FEATURE_ORDER:
        raise ValueError(
            f"Invalid ML feature order. Expected: {FEATURE_ORDER}"
        )

    return features


def apply_ml_prediction(report: dict[str, Any]) -> dict[str, Any]:
    """
    Attach ML prediction and explainability without overwriting a valid
    measured/historical solar resource used by engineering scoring.
    """
    if not isinstance(report, dict):
        raise TypeError("report must be a dictionary.")

    features = _build_features(report)

    prediction = float(predict_solar_radiation(features))
    explanation = predict_solar_with_explanation(features)

    actual_solar = _extract_solar_resource(report)

    if actual_solar is not None:
        used_for_solar_scoring = False
        scoring_value = actual_solar
        scoring_source = "measured_or_historical_resource"
    else:
        used_for_solar_scoring = True
        scoring_value = prediction
        scoring_source = "machine_learning_fallback"

        datasets = report.setdefault("datasets", {})
        nasa = datasets.setdefault("nasa_power", {})
        solar = nasa.setdefault("solar_resource", {})
        solar["solar_radiation_kwh_m2_day"] = round(prediction, 3)
        solar["source"] = "RandomForestRegressor fallback"

    report["ml_prediction"] = {
        "status": "success",
        "model": "RandomForestRegressor",
        "target": "solar_radiation_kwh_m2_day",
        "predicted_value": round(prediction, 3),
        "feature_values": features,
        "used_for_solar_scoring": used_for_solar_scoring,
        "scoring_value": round(scoring_value, 3),
        "scoring_source": scoring_source,
        "model_file": "engine/models/best_solar_model.joblib",
    }

    report["ml_explainability"] = explanation

    return report