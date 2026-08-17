# First Machine Learning Baseline

This patch implements the first ML milestone using **real NASA POWER historical data**.

## Target

Solar daily radiation:

`solar_radiation_kwh_m2_day`

## Features

- year
- month
- day
- day_of_year
- week_number
- wind_speed_ms

## Model

`sklearn.ensemble.RandomForestRegressor`

## Evaluation

- MAE
- RMSE
- R²

The split is chronological 80/20 to avoid future-data leakage.

## Run

From the project root:

```powershell
pip install pandas scikit-learn joblib
python -m engine.test_ml_baseline
```

The trained model is saved to:

```text
engine\models\solar_random_forest.joblib
```

Metrics/metadata are saved to:

```text
engine\models\solar_random_forest_metrics.json
```

No predefined solar values are used for training. NASA POWER is queried at runtime.
