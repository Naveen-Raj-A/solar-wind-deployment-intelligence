from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd
import requests

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def fetch_nasa_power_history(
    latitude: float,
    longitude: float,
    days: int = 365,
    timeout: int = 90,
) -> pd.DataFrame:
    """Fetch real historical NASA POWER daily solar/wind observations."""
    if days < 60:
        raise ValueError("days must be at least 60 for a useful baseline.")

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,WS10M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON",
        "time-standard": "UTC",
    }

    response = requests.get(NASA_POWER_URL, params=params, timeout=timeout)
    response.raise_for_status()
    payload: dict[str, Any] = response.json()

    parameters = payload.get("properties", {}).get("parameter", {})
    solar = parameters.get("ALLSKY_SFC_SW_DWN", {})
    wind = parameters.get("WS10M", {})

    rows = []
    for raw_date in sorted(set(solar) | set(wind)):
        try:
            solar_value = float(solar.get(raw_date))
            wind_value = float(wind.get(raw_date))
        except (TypeError, ValueError):
            continue

        if solar_value < 0 or wind_value < 0:
            continue

        rows.append(
            {
                "date": pd.to_datetime(raw_date, format="%Y%m%d"),
                "solar_radiation_kwh_m2_day": solar_value,
                "wind_speed_ms": wind_value,
            }
        )

    if not rows:
        raise RuntimeError("NASA POWER returned no valid historical observations.")

    frame = pd.DataFrame(rows).sort_values("date").drop_duplicates("date")
    frame = frame.reset_index(drop=True)

    if len(frame) < 60:
        raise RuntimeError(
            f"Only {len(frame)} valid NASA POWER records were returned; "
            "at least 60 are required."
        )

    return frame


def build_training_dataset(history: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Create the ML feature matrix X and solar target y from real observations."""
    required = {
        "date",
        "solar_radiation_kwh_m2_day",
        "wind_speed_ms",
    }
    missing = required - set(history.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = history.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    # Time-based features are generated programmatically from the date.
    iso = df["date"].dt.isocalendar()
    df["year"] = df["date"].dt.year.astype(int)
    df["month"] = df["date"].dt.month.astype(int)
    df["day"] = df["date"].dt.day.astype(int)
    df["day_of_year"] = df["date"].dt.dayofyear.astype(int)
    df["week_number"] = iso.week.astype(int)

    feature_columns = [
        "year",
        "month",
        "day",
        "day_of_year",
        "week_number",
        "wind_speed_ms",
    ]

    df = df.dropna(subset=feature_columns + ["solar_radiation_kwh_m2_day"])

    X = df[feature_columns].astype(float)
    y = df["solar_radiation_kwh_m2_day"].astype(float)

    if len(X) < 60:
        raise RuntimeError("Training dataset has fewer than 60 usable records.")

    return X, y
