from __future__ import annotations

import json
from pathlib import Path

import joblib

from engine.ml.evaluate_model import evaluate_regression
from engine.ml.random_forest_baseline import FEATURE_COLUMNS, create_model
from engine.ml.training_dataset import (
    build_training_dataset,
    fetch_nasa_power_history,
)

DEFAULT_LATITUDE = 13.0827
DEFAULT_LONGITUDE = 80.2707

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "engine" / "models"
MODEL_PATH = MODEL_DIR / "solar_random_forest.joblib"
METRICS_PATH = MODEL_DIR / "solar_random_forest_metrics.json"


def train_solar_baseline(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    history_days: int = 365,
) -> dict:
    """Train and persist a real-data solar radiation Random Forest baseline."""
    history = fetch_nasa_power_history(
        latitude=latitude,
        longitude=longitude,
        days=history_days,
    )

    X, y = build_training_dataset(history)

    # Chronological split: first 80% train, final 20% test.
    split_index = int(len(X) * 0.80)
    if split_index <= 0 or split_index >= len(X):
        raise RuntimeError("Invalid chronological train/test split.")

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = create_model()
    model.fit(X_train, y_train)

    metrics = evaluate_regression(model, X_test, y_test)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    metadata = {
        "model": "RandomForestRegressor",
        "target": "solar_radiation_kwh_m2_day",
        "features": FEATURE_COLUMNS,
        "latitude": latitude,
        "longitude": longitude,
        "records": len(X),
        "train_records": len(X_train),
        "test_records": len(X_test),
        "history_start": str(history["date"].min().date()),
        "history_end": str(history["date"].max().date()),
        "split": "chronological_80_20",
        "data_source": "NASA POWER Daily API",
        "metrics": metrics,
        "model_path": str(MODEL_PATH),
    }

    METRICS_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    print("=" * 60)
    print("REAL-DATA RANDOM FOREST BASELINE")
    print("=" * 60)

    result = train_solar_baseline()

    print(f"Data source : {result['data_source']}")
    print(f"Records     : {result['records']}")
    print(f"Train       : {result['train_records']}")
    print(f"Test        : {result['test_records']}")
    print(f"MAE         : {result['metrics']['mae']}")
    print(f"RMSE        : {result['metrics']['rmse']}")
    print(f"R²          : {result['metrics']['r2']}")
    print(f"Model saved : {result['model_path']}")
    print("=" * 60)
