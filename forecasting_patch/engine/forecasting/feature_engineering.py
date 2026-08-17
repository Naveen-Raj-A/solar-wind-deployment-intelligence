"""Time-based feature extraction for renewable time series."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _parse_date(value: Any) -> datetime:
    text = str(value)
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def add_time_features(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return records enriched with chronological time features."""
    output: list[dict[str, Any]] = []

    for record in records:
        if "date" not in record:
            raise ValueError("Every time-series record must contain 'date'.")

        dt = _parse_date(record["date"])

        enriched = dict(record)
        enriched["year"] = dt.year
        enriched["month"] = dt.month
        enriched["day"] = dt.day
        enriched["day_of_year"] = dt.timetuple().tm_yday
        enriched["week_number"] = dt.isocalendar().week
        output.append(enriched)

    output.sort(key=lambda item: str(item["date"]))
    return output
