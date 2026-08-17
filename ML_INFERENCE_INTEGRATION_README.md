# First ML Model Integration

This milestone integrates the persisted `best_solar_model.joblib` into the
existing live analysis pipeline.

## Model

RandomForestRegressor

Target:

`solar_radiation_kwh_m2_day`

Features supplied at inference time:

- year
- month
- day
- day_of_year
- week_number
- wind_speed_ms

The feature order is validated exactly.

## Model loading

`engine/ml/inference.py` uses `functools.lru_cache(maxsize=1)`, so the
serialized model is loaded once per Python process and reused.

## Existing pipeline integration

`apply_ml_solar_prediction()` runs before `calculate_deployment_score()`.
The predicted solar value is used by the existing solar scoring stage.

The original observed NASA POWER solar value is preserved as:

`observed_solar_radiation_kwh_m2_day`

This is important for transparency.

## Apply

From project root:

```powershell
python apply_ml_integration.py
```

## Unit/inference test

```powershell
python -m engine.test_ml_inference
```

## End-to-end API test

Start the API:

```powershell
python -m uvicorn main:app --reload
```

Then, in another terminal:

```powershell
python -m engine.test_ml_api_integration
```

The API test sends multiple real site inputs and checks that the final
response contains the ML prediction.

## Important

The current trained model predicts solar radiation; it was NOT trained to
predict the categorical technology (`SOLAR`, `WIND`, `HYBRID`). Therefore this
integration uses the model where its target is applicable: it replaces the
solar-resource input to the existing deployment scoring stage. The existing
technology optimizer remains responsible for SOLAR/WIND/HYBRID selection.
