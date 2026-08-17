"""Application-facing forecasting service."""

from __future__ import annotations

from typing import Any

from .data_loader import TimeSeriesDataLoader, time_series_loader
from .feature_engineering import add_time_features
from .hybrid_forecaster import HybridForecaster
from .solar_forecaster import SolarForecaster
from .wind_forecaster import WindForecaster


class ForecastingService:
    """Coordinates loading, temporal features and resource forecasting."""

    def __init__(
        self,
        loader: TimeSeriesDataLoader | None = None,
    ) -> None:
        self.loader = loader or time_series_loader
        self.solar = SolarForecaster()
        self.wind = WindForecaster()
        self.hybrid = HybridForecaster(
            self.solar,
            self.wind,
        )

    def forecast(
        self,
        *,
        latitude: float,
        longitude: float,
        horizon_days: int = 7,
        history_days: int = 365,
        technology: str = "HYBRID",
        csv_path: str | None = None,
    ) -> dict[str, Any]:
        if not 1 <= horizon_days <= 90:
            raise ValueError("horizon_days must be between 1 and 90.")

        records = self.loader.load(
            latitude=latitude,
            longitude=longitude,
            days=history_days,
            csv_path=csv_path,
        )

        featured = add_time_features(records)

        technology = technology.upper()

        if technology == "SOLAR":
            result = self.solar.forecast(
                featured,
                horizon_days,
            )
        elif technology == "WIND":
            result = self.wind.forecast(
                featured,
                horizon_days,
            )
        elif technology == "HYBRID":
            result = self.hybrid.forecast(
                featured,
                horizon_days,
            )
        else:
            raise ValueError(
                "technology must be SOLAR, WIND, or HYBRID."
            )

        return {
            **result,
            "data_source": (
                "local_csv" if csv_path else "NASA_POWER"
            ),
            "time_features": [
                "year",
                "month",
                "day",
                "day_of_year",
                "week_number",
            ],
        }


forecasting_service = ForecastingService()
