from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
from sklearn.tree import DecisionTreeRegressor

from engine.ml.evaluate_model import evaluate_regression
from engine.ml.random_forest_baseline import create_model
from engine.ml.training_dataset import (
    build_training_dataset,
    fetch_nasa_power_history,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "engine" / "models"
BEST_MODEL_PATH = MODEL_DIR / "best_solar_model.joblib"
COMPARISON_PATH = MODEL_DIR / "model_comparison.json"

DEFAULT_LATITUDE = 13.0827
DEFAULT_LONGITUDE = 80.2707


def _metrics_with_train_and_validation(
    model,
    X_train,
    y_train,
    X_validation,
    y_validation,
) -> dict[str, float]:
    train_metrics = evaluate_regression(model, X_train, y_train)
    validation_metrics = evaluate_regression(
        model,
        X_validation,
        y_validation,
    )

    return {
        "train_mae": train_metrics["mae"],
        "train_rmse": train_metrics["rmse"],
        "train_r2": train_metrics["r2"],
        "validation_mae": validation_metrics["mae"],
        "validation_rmse": validation_metrics["rmse"],
        "validation_r2": validation_metrics["r2"],
    }


def classify_model_behavior(metrics: dict[str, float]) -> str:
    """Classify behavior from observed train vs validation performance.

    This is deliberately a simple diagnostic, not a claim of statistical proof.
    """
    train_r2 = metrics["train_r2"]
    validation_r2 = metrics["validation_r2"]
    train_rmse = metrics["train_rmse"]
    validation_rmse = metrics["validation_rmse"]

    r2_gap = train_r2 - validation_r2
    rmse_ratio = (
        validation_rmse / train_rmse
        if train_rmse > 0
        else float("inf")
    )

    if train_r2 < 0.20 and validation_r2 < 0.20:
        return "Underfitting"

    if r2_gap >= 0.25 and rmse_ratio >= 1.25:
        return "Overfitting"

    return "Generalizing well"


def train_compare_and_persist(
    latitude: float = DEFAULT_LATITUDE,
    longitude: float = DEFAULT_LONGITUDE,
    history_days: int = 365,
) -> dict[str, Any]:
    """Train Decision Tree and Random Forest using real NASA POWER data.

    Split:
        70% training
        15% validation
        15% testing

    The split is chronological to avoid future-data leakage.
    The validation set selects the best model. The untouched test set is
    evaluated only after model selection.
    """
    history = fetch_nasa_power_history(
        latitude=latitude,
        longitude=longitude,
        days=history_days,
    )
    X, y = build_training_dataset(history)

    n = len(X)
    train_end = int(n * 0.70)
    validation_end = int(n * 0.85)

    if train_end < 30 or validation_end <= train_end or validation_end >= n:
        raise RuntimeError("Insufficient records for 70/15/15 split.")

    X_train = X.iloc[:train_end]
    y_train = y.iloc[:train_end]

    X_validation = X.iloc[train_end:validation_end]
    y_validation = y.iloc[train_end:validation_end]

    X_test = X.iloc[validation_end:]
    y_test = y.iloc[validation_end:]

    models = {
        "Decision Tree": DecisionTreeRegressor(
            max_depth=8,
            min_samples_leaf=3,
            random_state=42,
        ),
        "Random Forest": create_model(),
    }

    results: dict[str, dict[str, Any]] = {}

    for name, model in models.items():
        model.fit(X_train, y_train)

        metrics = _metrics_with_train_and_validation(
            model,
            X_train,
            y_train,
            X_validation,
            y_validation,
        )

        results[name] = {
            "model": model,
            "metrics": metrics,
            "behavior": classify_model_behavior(metrics),
        }

    # Model selection is based ONLY on validation RMSE.
    best_name = min(
        results,
        key=lambda name: results[name]["metrics"]["validation_rmse"],
    )
    best_model = results[best_name]["model"]

    # Final test evaluation happens only after selection.
    test_metrics = evaluate_regression(
        best_model,
        X_test,
        y_test,
    )
    results[best_name]["test_metrics"] = test_metrics

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, BEST_MODEL_PATH)

    serializable_results = {}
    for name, item in results.items():
        serializable_results[name] = {
            "metrics": item["metrics"],
            "behavior": item["behavior"],
            "test_metrics": item.get("test_metrics"),
        }

    output = {
        "data_source": "NASA POWER Daily API",
        "target": "solar_radiation_kwh_m2_day",
        "features": list(X.columns),
        "latitude": latitude,
        "longitude": longitude,
        "total_records": n,
        "split": {
            "training_percent": 70,
            "validation_percent": 15,
            "testing_percent": 15,
            "strategy": "chronological",
            "reason": (
                "The data is time-series data, so chronological splitting "
                "prevents future observations from leaking into training."
            ),
            "training_records": len(X_train),
            "validation_records": len(X_validation),
            "testing_records": len(X_test),
        },
        "models": serializable_results,
        "best_model": best_name,
        "selection_metric": "validation_rmse",
        "best_model_path": str(BEST_MODEL_PATH),
        "test_evaluation": {
            "model": best_name,
            "metrics": test_metrics,
        },
    }

    COMPARISON_PATH.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    return output
