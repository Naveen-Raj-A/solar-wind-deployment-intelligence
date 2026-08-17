"""Real historical renewable-data loader using NASA POWER Daily API.

No sample/test values are used by this loader. It retrieves the requested
historical time series from NASA POWER for the supplied latitude/longitude.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
import requests

NASA_POWER_DAILY_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
)

SOLAR_PARAMETER = "ALLSKY_SFC_SW_DWN"
WIND_PARAMETER = "WS10M"


def _validate_coordinates(latitude: float, longitude: float) -> None:
    if not -90 <= latitude <= 90:
        raise ValueError("latitude must be between -90 and 90.")
    if not -180 <= longitude <= 180:
        raise ValueError("longitude must be between -180 and 180.")


def load_real_nasa_power_history(
    latitude: float,
    longitude: float,
    history_days: int = 1095,
    end_date: date | None = None,
    timeout: int = 45,
) -> dict[str, Any]:
    """Fetch real daily solar and wind history from NASA POWER.

    The POWER Daily API provides analysis-ready daily solar/meteorological
    time series. The returned records are sorted chronologically and contain
    no fabricated values.
    """
    _validate_coordinates(latitude, longitude)

    if history_days < 60:
        raise ValueError("history_days must be at least 60.")
    if history_days > 3650:
        raise ValueError("history_days cannot exceed 3650.")

    if end_date is None:
        end_date = date.today()

    start_date = end_date - timedelta(days=history_days - 1)

    params = {
        "parameters": f"{SOLAR_PARAMETER},{WIND_PARAMETER}",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON",
        "time-standard": "UTC",
    }

    response = requests.get(
        NASA_POWER_DAILY_URL,
        params=params,
        timeout=timeout,
    )
    response.raise_for_status()

    payload = response.json()
    properties = payload.get("properties", {})
    parameter_data = properties.get("parameter", {})

    solar = parameter_data.get(SOLAR_PARAMETER, {})
    wind = parameter_data.get(WIND_PARAMETER, {})

    if not solar or not wind:
        raise RuntimeError(
            "NASA POWER returned no solar/wind historical series."
        )

    records: list[dict[str, Any]] = []

    for date_key in sorted(set(solar) & set(wind)):
        solar_value = solar[date_key]
        wind_value = wind[date_key]

        # NASA POWER can use -999 as missing-data sentinel.
        if solar_value == -999 or wind_value == -999:
            continue

        records.append(
            {
                "date": date(
                    int(date_key[0:4]),
                    int(date_key[4:6]),
                    int(date_key[6:8]),
                ).isoformat(),
                "solar_radiation_kwh_m2_day": float(solar_value),
                "wind_speed_ms": float(wind_value),
            }
        )

    if len(records) < 60:
        raise RuntimeError(
            f"NASA POWER returned only {len(records)} valid paired records; "
            "at least 60 are required for forecasting."
        )

    return {
        "source": "NASA POWER Daily API",
        "source_url": NASA_POWER_DAILY_URL,
        "latitude": latitude,
        "longitude": longitude,
        "requested_start": start_date.isoformat(),
        "requested_end": end_date.isoformat(),
        "records": records,
        "record_count": len(records),
    }
