"""Validation tests for the forecasting milestone."""

from __future__ import annotations

import csv
import tempfile
from datetime import date, timedelta
from pathlib import Path

from engine.forecasting.data_loader import TimeSeriesDataLoader
from engine.forecasting.feature_engineering import add_time_features
from engine.forecasting.solar_forecaster import SolarForecaster
from engine.forecasting.wind_forecaster import WindForecaster
from engine.forecasting.hybrid_forecaster import HybridForecaster


def build_sample_csv(path: Path, days: int = 60) -> None:
    start = date(2026, 1, 1)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "date",
                "solar_radiation_kwh_m2_day",
                "wind_speed_ms",
            ],
        )
        writer.writeheader()

        # Deliberately write reverse chronological order to test sorting.
        for index in reversed(range(days)):
            day = start + timedelta(days=index)
            writer.writerow({
                "date": day.isoformat(),
                "solar_radiation_kwh_m2_day": 4.0 + (index % 10) * 0.1,
                "wind_speed_ms": 4.0 + (index % 7) * 0.2,
            })


def main() -> None:
    print("=" * 38)
    print("FORECASTING ENGINE VALIDATION")
    print("=" * 38)

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "historical.csv"
        build_sample_csv(csv_path)

        loader = TimeSeriesDataLoader()
        records = loader.load_csv(csv_path)

        assert records[0]["date"] < records[-1]["date"]
        print("TEST 1 — CHRONOLOGICAL DATA LOADER")
        print(f"Records loaded: {len(records)}")
        print("PASS")

        featured = add_time_features(records)
        required = {
            "year",
            "month",
            "day",
            "day_of_year",
            "week_number",
        }
        assert required.issubset(featured[0])
        print("TEST 2 — TIME-BASED FEATURES")
        print(
            "Features: year, month, day, day_of_year, week_number"
        )
        print("PASS")

        solar = SolarForecaster().forecast(
            featured,
            horizon_days=7,
        )
        assert len(solar["forecast"]) == 7
        assert all(
            row["predicted_solar_radiation_kwh_m2_day"] >= 0
            for row in solar["forecast"]
        )
        print("TEST 3 — SOLAR FORECAST")
        print(f"Forecast days: {len(solar['forecast'])}")
        print("PASS")

        wind = WindForecaster().forecast(
            featured,
            horizon_days=7,
        )
        assert len(wind["forecast"]) == 7
        assert all(
            row["predicted_wind_speed_ms"] >= 0
            for row in wind["forecast"]
        )
        print("TEST 4 — WIND FORECAST")
        print(f"Forecast days: {len(wind['forecast'])}")
        print("PASS")

        hybrid = HybridForecaster().forecast(
            featured,
            horizon_days=7,
        )
        assert len(hybrid["forecast"]) == 7
        assert all(
            "predicted_solar_radiation_kwh_m2_day" in row
            and "predicted_wind_speed_ms" in row
            for row in hybrid["forecast"]
        )
        print("TEST 5 — HYBRID FORECAST")
        print(f"Forecast days: {len(hybrid['forecast'])}")
        print("PASS")

    print("=" * 38)
    print("ALL FORECASTING TESTS PASSED")
    print("=" * 38)


if __name__ == "__main__":
    main()
