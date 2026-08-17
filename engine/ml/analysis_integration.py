"""Adapter that injects the ML prediction into the existing live analysis.

The trained model predicts solar radiation. Therefore it replaces the
observed solar-resource value used by the existing solar scoring stage,
while preserving the original observed value for transparency.

The existing terrain, wind, Sentinel, OSM and deployment optimization logic
remain unchanged.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from engine.ml.inference import predict_solar_radiation


def _build_features(
    report: dict[str, Any],
) -> dict[str, float]:
    site = report["site_information"]
    wind = report["datasets"]["wind"]["wind_speed_statistics"]

    today = date.today()

    return {
        "year": float(today.year),
        "month": float(today.month),
        "day": float(today.day),
        "day_of_year": float(today.timetuple().tm_yday),
        "week_number": float(today.isocalendar().week),
        "wind_speed_ms": float(wind["mean_ms"]),
    }


def apply_ml_solar_prediction(
    report: dict[str, Any],
) -> dict[str, Any]:
    """Apply the trained model to a live site report.

    Returns a copied report. The original observed NASA POWER solar value is
    retained under observed_solar_radiation_kwh_m2_day.
    """
    if "site_information" not in report:
        raise ValueError("Missing site_information in analysis report.")

    if "datasets" not in report:
        raise ValueError("Missing datasets in analysis report.")

    if "wind" not in report["datasets"]:
        raise ValueError("Missing wind dataset in analysis report.")

    features = _build_features(report)
    prediction = predict_solar_radiation(features)

    result = {
        **report,
        "datasets": {
            **report["datasets"],
            "nasa_power": {
                **report["datasets"]["nasa_power"],
                "observed_solar_radiation_kwh_m2_day": (
                    report["datasets"]["nasa_power"]
                    .get("solar_resource", {})
                    .get("solar_radiation_kwh_m2_day")
                ),
                "solar_resource": {
                    **report["datasets"]["nasa_power"]
                    .get("solar_resource", {}),
                    "solar_radiation_kwh_m2_day": prediction,
                },
            },
        },
        "ml_prediction": {
            "model": "RandomForestRegressor",
            "target": "solar_radiation_kwh_m2_day",
            "predicted_solar_radiation_kwh_m2_day": prediction,
            "feature_values": features,
            "data_source_for_context": "NASA POWER",
            "model_file": "engine/models/best_solar_model.joblib",
            "used_for_solar_scoring": True,
        },
    }

    return result
