"""Forecasting integration helper for the existing AnalysisService.

This adapter deliberately does not run forecasting during the existing
/analysis request by default. That keeps the validated analysis pipeline
stable while providing a clean, explicit forecasting entry point.
"""

from __future__ import annotations

from typing import Any

from engine.forecasting.forecasting_service import forecasting_service


def forecast_from_site(
    *,
    latitude: float,
    longitude: float,
    technology: str,
    horizon_days: int = 7,
    history_days: int = 365,
) -> dict[str, Any]:
    """Use the same site coordinates produced by analysis as forecast input."""
    return forecasting_service.forecast(
        latitude=latitude,
        longitude=longitude,
        technology=technology,
        horizon_days=horizon_days,
        history_days=history_days,
    )
