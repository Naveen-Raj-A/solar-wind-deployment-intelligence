"""Wind resource forecasting."""

from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import Any


class WindForecaster:
    """Transparent seasonal-baseline wind-speed forecaster."""

    def forecast(
        self,
        records: list[dict[str, Any]],
        horizon_days: int = 7,
    ) -> dict[str, Any]:
        values = [
            r for r in records
            if "wind_speed_ms" in r
        ]

        if len(values) < 7:
            raise ValueError("At least 7 wind observations are required.")

        values = sorted(values, key=lambda r: str(r["date"]))
        recent = [float(r["wind_speed_ms"]) for r in values[-30:]]
        baseline = mean(recent)

        by_month: dict[int, list[float]] = {}
        for record in values:
            by_month.setdefault(int(record["month"]), []).append(
                float(record["wind_speed_ms"])
            )

        last_date = date.fromisoformat(str(values[-1]["date"])[:10])
        predictions = []

        for offset in range(1, horizon_days + 1):
            target = last_date + timedelta(days=offset)
            month_values = by_month.get(target.month, [])
            seasonal = mean(month_values) if month_values else baseline

            prediction = max(
                0.0,
                0.70 * seasonal + 0.30 * baseline,
            )

            predictions.append({
                "date": target.isoformat(),
                "predicted_wind_speed_ms": round(prediction, 3),
            })

        return {
            "technology": "WIND",
            "model": "seasonal_baseline_v1",
            "historical_samples": len(values),
            "horizon_days": horizon_days,
            "forecast": predictions,
        }
