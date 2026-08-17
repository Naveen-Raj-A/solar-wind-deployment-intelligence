"""Solar resource forecasting."""

from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import Any


class SolarForecaster:
    """Deterministic seasonal-baseline solar irradiance forecaster.

    This is intentionally a transparent baseline model for the first
    forecasting milestone. It uses historical day-of-year patterns and
    recent observations rather than claiming an ML model has been trained.
    """

    def forecast(
        self,
        records: list[dict[str, Any]],
        horizon_days: int = 7,
    ) -> dict[str, Any]:
        values = [
            r for r in records
            if "solar_radiation_kwh_m2_day" in r
        ]

        if len(values) < 7:
            raise ValueError("At least 7 solar observations are required.")

        values = sorted(values, key=lambda r: str(r["date"]))
        recent = [float(r["solar_radiation_kwh_m2_day"]) for r in values[-30:]]
        baseline = mean(recent)

        by_month: dict[int, list[float]] = {}
        for record in values:
            by_month.setdefault(int(record["month"]), []).append(
                float(record["solar_radiation_kwh_m2_day"])
            )

        last_date = date.fromisoformat(str(values[-1]["date"])[:10])
        predictions = []

        for offset in range(1, horizon_days + 1):
            target = last_date + timedelta(days=offset)
            month_values = by_month.get(target.month, [])
            seasonal = mean(month_values) if month_values else baseline

            # 70% seasonal pattern + 30% recent level.
            prediction = max(
                0.0,
                0.70 * seasonal + 0.30 * baseline,
            )

            predictions.append({
                "date": target.isoformat(),
                "predicted_solar_radiation_kwh_m2_day": round(prediction, 3),
            })

        return {
            "technology": "SOLAR",
            "model": "seasonal_baseline_v1",
            "historical_samples": len(values),
            "horizon_days": horizon_days,
            "forecast": predictions,
        }
