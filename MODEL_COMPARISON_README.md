# Train and Evaluate the First Baseline Models

This milestone uses the real NASA POWER historical dataset already used by
the project.

## Task 1: Split

A chronological 70/15/15 split is used:

- 70% training
- 15% validation
- 15% testing

Because this is time-series data, chronological splitting avoids future-data
leakage.

## Task 2: Two models

1. DecisionTreeRegressor
2. RandomForestRegressor

## Task 3: Comparison

Both models are evaluated on the validation set using:

- MAE
- RMSE
- R²

The model with the lower validation RMSE is selected.

## Task 4: Behaviour

Training and validation metrics are compared:

- Large train/validation gap -> possible overfitting
- Weak train and validation performance -> possible underfitting
- Similar and strong train/validation performance -> generalizing well

The classification is a diagnostic, not a statistical proof.

## Task 5: Persistence

The best model is saved as:

engine/models/best_solar_model.joblib

The complete comparison and metrics are saved as:

engine/models/model_comparison.json

## Run

```powershell
python -m engine.test_ml_model_comparison
```
