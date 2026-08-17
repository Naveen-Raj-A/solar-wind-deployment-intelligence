"""Small integration adapter for the existing analysis pipeline.

This module deliberately does not replace scoring.py, optimization.py, or
analysis_service.py. It adds a real-data forecasting stage that can consume
the same latitude/longitude supplied to the existing analysis endpoint.
"""

from __future__ import annotations

from typing import Any

from .real_forecasting_service import forecast_real_site


def add_real_forecast_to_analysis(
    analysis_result: dict[str, Any],
    *,
    latitude: float,
    longitude: float,
    history_days: int = 1095,
    forecast_days: int = 7,
) -> dict[str, Any]:
    """Return the existing analysis result with a real-data forecast section."""
    forecast = forecast_real_site(
        latitude=latitude,
        longitude=longitude,
        history_days=history_days,
        forecast_days=forecast_days,
    )

    result = dict(analysis_result)
    result["forecasting"] = forecast
    return result
