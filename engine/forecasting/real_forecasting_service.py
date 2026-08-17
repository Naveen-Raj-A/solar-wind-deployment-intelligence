"""Forecasting from real NASA POWER historical observations.

The forecast is intentionally transparent: it uses historical seasonal
profiles from the real downloaded observations rather than invented sample
values or a pretend pre-trained ML model.

Method:
- For each forecast day, use observations from the same day-of-year window
  across prior years when available.
- Blend those seasonal observations with a recent weighted mean.
- Solar and wind are forecast independently.
- Hybrid is derived from the two renewable forecasts.
"""

from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import Any

from .real_data_loader import load_real_nasa_power_history


def _day_of_year(d: date) -> int:
    return d.timetuple().tm_yday


def _seasonal_values(
    records: list[dict[str, Any]],
    target_date: date,
    field: str,
    window: int = 3,
) -> list[float]:
    target_doy = _day_of_year(target_date)
    values: list[float] = []

    for row in records:
        row_date = date.fromisoformat(row["date"])
        row_doy = _day_of_year(row_date)

        distance = abs(row_doy - target_doy)
        distance = min(distance, 366 - distance)

        if distance <= window:
            values.append(float(row[field]))

    return values


def _recent_values(
    records: list[dict[str, Any]],
    field: str,
    count: int = 30,
) -> list[float]:
    return [
        float(row[field])
        for row in records[-count:]
    ]


def _forecast_series(
    records: list[dict[str, Any]],
    field: str,
    forecast_days: int,
) -> list[dict[str, Any]]:
    last_date = date.fromisoformat(records[-1]["date"])
    recent = _recent_values(records, field, 30)

    result: list[dict[str, Any]] = []

    for offset in range(1, forecast_days + 1):
        target = last_date + timedelta(days=offset)

        seasonal = _seasonal_values(
            records,
            target,
            field,
            window=3,
        )

        if seasonal:
            seasonal_mean = mean(seasonal)
            recent_mean = mean(recent)
            predicted = (seasonal_mean * 0.80) + (recent_mean * 0.20)
            method = "historical_seasonal_profile"
        else:
            predicted = mean(recent)
            method = "recent_historical_mean"

        predicted = max(0.0, predicted)

        result.append(
            {
                "date": target.isoformat(),
                "predicted_value": round(predicted, 3),
                "method": method,
            }
        )

    return result


def forecast_real_site(
    latitude: float,
    longitude: float,
    history_days: int = 1095,
    forecast_days: int = 7,
) -> dict[str, Any]:
    """Fetch real NASA POWER history and produce solar/wind/hybrid forecasts."""
    if forecast_days < 1 or forecast_days > 30:
        raise ValueError("forecast_days must be between 1 and 30.")

    history = load_real_nasa_power_history(
        latitude=latitude,
        longitude=longitude,
        history_days=history_days,
    )

    records = history["records"]

    solar = _forecast_series(
        records,
        "solar_radiation_kwh_m2_day",
        forecast_days,
    )

    wind = _forecast_series(
        records,
        "wind_speed_ms",
        forecast_days,
    )

    hybrid = []
    for solar_row, wind_row in zip(solar, wind):
        # Keep the hybrid result as a transparent combined renewable index.
        # This is NOT a generated physical power value.
        solar_norm = min(solar_row["predicted_value"] / 7.0, 1.0)
        wind_norm = min(wind_row["predicted_value"] / 12.0, 1.0)
        hybrid_index = ((solar_norm + wind_norm) / 2.0) * 100.0

        hybrid.append(
            {
                "date": solar_row["date"],
                "renewable_complementarity_index": round(
                    hybrid_index,
                    2,
                ),
            }
        )

    return {
        "status": "success",
        "data_source": history["source"],
        "data_type": "real_historical_observations",
        "latitude": latitude,
        "longitude": longitude,
        "history": {
            "requested_days": history_days,
            "records_used": len(records),
            "start": records[0]["date"],
            "end": records[-1]["date"],
        },
        "forecast": {
            "forecast_days": forecast_days,
            "solar": solar,
            "wind": wind,
            "hybrid": hybrid,
        },
    }
