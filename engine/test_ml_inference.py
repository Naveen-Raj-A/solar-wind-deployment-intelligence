from pathlib import Path

from engine.ml.inference import (
    FEATURE_ORDER,
    MODEL_PATH,
    load_model,
    predict_solar_radiation,
)
from engine.ml.analysis_integration import apply_ml_solar_prediction


def sample_features():
    return {
        "year": 2026.0,
        "month": 8.0,
        "day": 15.0,
        "day_of_year": 227.0,
        "week_number": 33.0,
        "wind_speed_ms": 2.9,
    }


def sample_report():
    return {
        "site_information": {
            "latitude": 13.0827,
            "longitude": 80.2707,
        },
        "datasets": {
            "nasa_power": {
                "source": "NASA POWER",
                "solar_resource": {
                    "solar_radiation_kwh_m2_day": 5.7,
                },
            },
            "wind": {
                "source": "NASA POWER",
                "wind_speed_statistics": {
                    "mean_ms": 2.9,
                },
            },
        },
    }


def main():
    print("=" * 60)
    print("ML INFERENCE VALIDATION")
    print("=" * 60)

    print("\nTEST 1 — MODEL LOADING")
    assert Path(MODEL_PATH).exists()
    first = load_model()
    second = load_model()
    assert first is second
    print(f"Model: {MODEL_PATH}")
    print("Loaded once and cached: PASS")

    print("\nTEST 2 — FEATURE VALIDATION")
    features = sample_features()
    assert tuple(features.keys()) == FEATURE_ORDER
    prediction = predict_solar_radiation(features)
    assert prediction >= 0
    print(f"Prediction: {prediction} kWh/m²/day")
    print("PASS")

    print("\nTEST 3 — INVALID FEATURE SET")
    bad = dict(features)
    del bad["wind_speed_ms"]
    try:
        predict_solar_radiation(bad)
        raise AssertionError("Missing feature was not rejected.")
    except ValueError:
        print("Missing feature rejected: PASS")

    print("\nTEST 4 — ANALYSIS INTEGRATION")
    report = sample_report()
    integrated = apply_ml_solar_prediction(report)

    ml = integrated["ml_prediction"]
    assert ml["used_for_solar_scoring"] is True
    assert "observed_solar_radiation_kwh_m2_day" in (
        integrated["datasets"]["nasa_power"]
    )
    assert (
        integrated["datasets"]["nasa_power"]["solar_resource"]
        ["solar_radiation_kwh_m2_day"]
        == ml["predicted_solar_radiation_kwh_m2_day"]
    )
    print("Prediction inserted into analysis report: PASS")

    print("\n" + "=" * 60)
    print("ALL ML INFERENCE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
