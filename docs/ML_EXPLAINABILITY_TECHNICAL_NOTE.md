# Solar-Wind Deployment Intelligence — ML Explainability Technical Note

## 1. Selected Model

Production model: `RandomForestRegressor`

Serialized model:
`engine/models/best_solar_model.joblib`

The model predicts solar radiation (`solar_radiation_kwh_m2_day`) using:

- year
- month
- day
- day_of_year
- week_number
- wind_speed_ms

The model is loaded from disk and reused; the FastAPI request does not retrain it.

## 2. Evaluation Results

| Model | Validation MAE | Validation RMSE | Validation R² |
|---|---:|---:|---:|
| Decision Tree | 1.4996 | 1.8106 | -5.4228 |
| Random Forest | 1.0031 | 1.1597 | -1.6352 |

Selected model: **Random Forest**

Final held-out test performance:

- MAE: 1.3122
- RMSE: 1.6427
- R²: -1.8726

The Random Forest performed better than the Decision Tree on the validation metrics, although the negative R² indicates that this baseline has limited predictive quality and should not be treated as a highly accurate production forecasting model.

## 3. Feature Importance

Actual `feature_importances_` values extracted from the saved Random Forest:

| Rank | Feature | Importance |
|---:|---|---:|
| 1 | wind_speed_ms | 46.03% |
| 2 | day_of_year | 30.00% |
| 3 | day | 15.27% |
| 4 | week_number | 4.76% |
| 5 | month | 2.80% |
| 6 | year | 1.14% |

## 4. Interpretation

The model relies most heavily on `wind_speed_ms` and time-derived features.

This ranking should not be interpreted as a physical law stating that wind speed is the dominant physical driver of solar radiation. The current baseline contains only six engineered inputs and does not include richer solar-resource variables such as cloud cover, humidity, temperature, direct irradiance, or other atmospheric measurements.

`day_of_year`, `day`, `week_number`, and `month` are related temporal variables, so their importance can overlap because they encode seasonal/time patterns.

## 5. Limitations and Assumptions

1. The baseline dataset is relatively small compared with a production renewable-energy forecasting dataset.
2. The current model has negative validation and test R² values, indicating weak generalization.
3. Feature importance from a Random Forest describes model reliance, not causal physical influence.
4. The model uses temporal features and mean wind speed but lacks richer meteorological predictors.
5. Sentinel-2 environmental data is currently unavailable when CDSE credentials are not configured.
6. The existing deployment recommendation engine remains responsible for SOLAR/WIND/HYBRID technology selection; the ML model currently predicts solar radiation and supplies that prediction to the solar scoring stage.
7. The real environmental data pipeline remains separate from the trained model: observed live data is preserved, while the ML prediction is explicitly identified.

## 6. Explainable Prediction Response

The prediction response now contains:

- predicted value
- complete feature-importance ranking
- top influential features
- concise explanation

Example:

```json
{
  "prediction": 5.772,
  "most_influential_features": [
    {"feature": "wind_speed_ms", "importance_percent": 46.03},
    {"feature": "day_of_year", "importance_percent": 30.0},
    {"feature": "day", "importance_percent": 15.27}
  ]
}
```
