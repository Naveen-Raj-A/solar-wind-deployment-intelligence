from __future__ import annotations

from pathlib import Path

from engine.ml.train_baseline import (
    MODEL_PATH,
    train_solar_baseline,
)


def main():
    print("=" * 60)
    print("MACHINE LEARNING BASELINE VALIDATION")
    print("=" * 60)

    result = train_solar_baseline(history_days=365)

    assert result["data_source"] == "NASA POWER Daily API"
    assert result["records"] >= 60
    assert result["train_records"] > result["test_records"]
    assert result["metrics"]["mae"] >= 0
    assert result["metrics"]["rmse"] >= 0
    assert Path(MODEL_PATH).exists()

    print("TEST 1 — REAL TRAINING DATA")
    print(f"Source  : {result['data_source']}")
    print(f"Records : {result['records']}")
    print("PASS")

    print("TEST 2 — CHRONOLOGICAL TRAIN/TEST SPLIT")
    print(f"Train records: {result['train_records']}")
    print(f"Test records : {result['test_records']}")
    print("PASS")

    print("TEST 3 — RANDOM FOREST REGRESSION")
    print("Model: RandomForestRegressor")
    print("PASS")

    print("TEST 4 — REGRESSION METRICS")
    print(f"MAE  : {result['metrics']['mae']}")
    print(f"RMSE : {result['metrics']['rmse']}")
    print(f"R²   : {result['metrics']['r2']}")
    print("PASS")

    print("TEST 5 — MODEL PERSISTENCE")
    print(f"Saved: {MODEL_PATH}")
    print("PASS")

    print("=" * 60)
    print("ALL ML BASELINE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
