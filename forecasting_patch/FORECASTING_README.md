# Forecasting milestone patch

Added:
- engine/forecasting/data_loader.py
- engine/forecasting/feature_engineering.py
- engine/forecasting/solar_forecaster.py
- engine/forecasting/wind_forecaster.py
- engine/forecasting/hybrid_forecaster.py
- engine/forecasting/forecasting_service.py
- engine/forecasting/analysis_integration.py
- engine/test_forecasting.py

The loader supports NASA POWER historical data and local CSV data.
The first forecasting model is a transparent seasonal baseline, not an
untrained ML model.

Run:
python -m engine.test_forecasting

For a live forecast:
from engine.forecasting.forecasting_service import forecasting_service
result = forecasting_service.forecast(
    latitude=13.0827,
    longitude=80.2707,
    technology="HYBRID",
    history_days=365,
    horizon_days=7,
)
