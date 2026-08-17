from __future__ import annotations

from sklearn.ensemble import RandomForestRegressor


FEATURE_COLUMNS = [
    "year",
    "month",
    "day",
    "day_of_year",
    "week_number",
    "wind_speed_ms",
]


def create_model() -> RandomForestRegressor:
    """Create the first deterministic Random Forest regression baseline."""
    return RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
