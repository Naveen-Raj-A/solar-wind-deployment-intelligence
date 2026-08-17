"""Hybrid solar-wind forecasting."""

from __future__ import annotations

from typing import Any

from .solar_forecaster import SolarForecaster
from .wind_forecaster import WindForecaster


class HybridForecaster:
    """Combines the independently forecast solar and wind resources."""

    def __init__(
        self,
        solar_forecaster: SolarForecaster | None = None,
        wind_forecaster: WindForecaster | None = None,
    ) -> None:
        self.solar_forecaster = solar_forecaster or SolarForecaster()
        self.wind_forecaster = wind_forecaster or WindForecaster()

    def forecast(
        self,
        records: list[dict[str, Any]],
        horizon_days: int = 7,
    ) -> dict[str, Any]:
        solar = self.solar_forecaster.forecast(records, horizon_days)
        wind = self.wind_forecaster.forecast(records, horizon_days)

        combined = []

        for solar_row, wind_row in zip(
            solar["forecast"],
            wind["forecast"],
        ):
            combined.append({
                "date": solar_row["date"],
                "predicted_solar_radiation_kwh_m2_day": (
                    solar_row["predicted_solar_radiation_kwh_m2_day"]
                ),
                "predicted_wind_speed_ms": (
                    wind_row["predicted_wind_speed_ms"]
                ),
            })

        return {
            "technology": "HYBRID",
            "model": "solar_wind_seasonal_baseline_v1",
            "historical_samples": len(records),
            "horizon_days": horizon_days,
            "forecast": combined,
        }
