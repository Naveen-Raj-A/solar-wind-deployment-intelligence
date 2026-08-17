"""Historical renewable-resource time-series loader.

Supports:
- local CSV files
- NASA POWER Daily API

The loader always returns chronologically sorted records with a common schema.
"""

from __future__ import annotations

import csv
import math
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import requests

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

HEADERS = {
    "User-Agent": "SolarWindDeploymentIntelligence-Forecasting/1.0",
    "Accept": "application/json",
}


def _valid(value: Any) -> bool:
    try:
        x = float(value)
        return math.isfinite(x) and x >= 0 and x != -999
    except (TypeError, ValueError):
        return False


def _record_sort_key(record: dict[str, Any]) -> str:
    return str(record["date"])


class TimeSeriesDataLoader:
    """Reusable loader for historical solar/wind resource observations."""

    def load_csv(self, path: str | Path) -> list[dict[str, Any]]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Historical dataset not found: {path}")

        records: list[dict[str, Any]] = []

        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)

            if not reader.fieldnames or "date" not in reader.fieldnames:
                raise ValueError("CSV must contain a 'date' column.")

            for row in reader:
                raw_date = row.get("date")
                if not raw_date:
                    continue

                record: dict[str, Any] = {"date": raw_date}

                for key in ("solar_radiation_kwh_m2_day", "wind_speed_ms"):
                    value = row.get(key)
                    if _valid(value):
                        record[key] = float(value)

                if len(record) > 1:
                    records.append(record)

        records.sort(key=_record_sort_key)

        if not records:
            raise ValueError("No valid historical observations were found.")

        return records

    def load_nasa_power(
        self,
        latitude: float,
        longitude: float,
        days: int = 365,
    ) -> list[dict[str, Any]]:
        """Load latest-available historical daily NASA POWER resource data."""
        if not -90 <= latitude <= 90:
            raise ValueError("latitude must be between -90 and 90.")
        if not -180 <= longitude <= 180:
            raise ValueError("longitude must be between -180 and 180.")
        if not 1 <= days <= 3650:
            raise ValueError("days must be between 1 and 3650.")

        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=days - 1)

        params = {
            "parameters": "ALLSKY_SFC_SW_DWN,WS10M",
            "community": "RE",
            "longitude": longitude,
            "latitude": latitude,
            "start": start.strftime("%Y%m%d"),
            "end": end.strftime("%Y%m%d"),
            "format": "JSON",
            "time-standard": "UTC",
        }

        response = requests.get(
            NASA_POWER_URL,
            params=params,
            headers=HEADERS,
            timeout=120,
        )
        response.raise_for_status()

        payload = response.json()
        parameters = payload.get("properties", {}).get("parameter", {})

        solar = parameters.get("ALLSKY_SFC_SW_DWN", {})
        wind = parameters.get("WS10M", {})

        records: list[dict[str, Any]] = []

        for day in sorted(set(solar) | set(wind)):
            record: dict[str, Any] = {
                "date": f"{day[:4]}-{day[4:6]}-{day[6:8]}"
            }

            if _valid(solar.get(day)):
                record["solar_radiation_kwh_m2_day"] = float(solar[day])

            if _valid(wind.get(day)):
                record["wind_speed_ms"] = float(wind[day])

            if len(record) > 1:
                records.append(record)

        if not records:
            raise RuntimeError("NASA POWER returned no valid historical records.")

        records.sort(key=_record_sort_key)
        return records

    def load(
        self,
        *,
        latitude: float | None = None,
        longitude: float | None = None,
        days: int = 365,
        csv_path: str | Path | None = None,
    ) -> list[dict[str, Any]]:
        if csv_path is not None:
            return self.load_csv(csv_path)

        if latitude is None or longitude is None:
            raise ValueError(
                "latitude and longitude are required when csv_path is not supplied."
            )

        return self.load_nasa_power(latitude, longitude, days)


time_series_loader = TimeSeriesDataLoader()
