from pathlib import Path

from engine.ml.model_comparison import (
    BEST_MODEL_PATH,
    COMPARISON_PATH,
    train_compare_and_persist,
)


def main() -> None:
    print("=" * 60)
    print("MODEL COMPARISON VALIDATION")
    print("=" * 60)

    result = train_compare_and_persist(history_days=365)

    print("\nTEST 1 — CHRONOLOGICAL DATASET SPLIT")
    split = result["split"]
    print(f"Training   : {split['training_records']} ({split['training_percent']}%)")
    print(f"Validation : {split['validation_records']} ({split['validation_percent']}%)")
    print(f"Testing    : {split['testing_records']} ({split['testing_percent']}%)")
    assert split["strategy"] == "chronological"
    assert split["training_records"] > split["validation_records"]
    assert split["validation_records"] > 0
    assert split["testing_records"] > 0
    print("PASS")

    print("\nTEST 2 — TWO BASELINE MODELS")
    assert "Decision Tree" in result["models"]
    assert "Random Forest" in result["models"]
    print("Decision Tree  : trained")
    print("Random Forest  : trained")
    print("PASS")

    print("\nTEST 3 — VALIDATION COMPARISON")
    print(
        f"{'Model':<18}"
        f"{'Val MAE':>12}"
        f"{'Val RMSE':>12}"
        f"{'Val R²':>12}"
    )

    for name, item in result["models"].items():
        m = item["metrics"]
        print(
            f"{name:<18}"
            f"{m['validation_mae']:>12.4f}"
            f"{m['validation_rmse']:>12.4f}"
            f"{m['validation_r2']:>12.4f}"
        )

    assert result["best_model"] in result["models"]
    print(f"\nBest model: {result['best_model']}")
    print("PASS")

    print("\nTEST 4 — MODEL BEHAVIOUR")
    for name, item in result["models"].items():
        m = item["metrics"]
        print(
            f"{name}: {item['behavior']} "
            f"(Train R²={m['train_r2']:.4f}, "
            f"Validation R²={m['validation_r2']:.4f}, "
            f"Train RMSE={m['train_rmse']:.4f}, "
            f"Validation RMSE={m['validation_rmse']:.4f})"
        )
        assert item["behavior"] in {
            "Underfitting",
            "Overfitting",
            "Generalizing well",
        }
    print("PASS")

    print("\nTEST 5 — FINAL TEST EVALUATION")
    test = result["test_evaluation"]["metrics"]
    print(f"Model: {result['test_evaluation']['model']}")
    print(f"Test MAE : {test['mae']:.4f}")
    print(f"Test RMSE: {test['rmse']:.4f}")
    print(f"Test R²  : {test['r2']:.4f}")
    print("PASS")

    print("\nTEST 6 — BEST MODEL PERSISTENCE")
    assert Path(BEST_MODEL_PATH).exists()
    assert Path(COMPARISON_PATH).exists()
    print(f"Saved model : {BEST_MODEL_PATH}")
    print(f"Comparison  : {COMPARISON_PATH}")
    print("PASS")

    print("\n" + "=" * 60)
    print("ALL MODEL COMPARISON TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
