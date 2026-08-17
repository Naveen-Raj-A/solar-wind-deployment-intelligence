"""Live-data forecasting validation.

This is intentionally separate from test_forecasting.py.

Run:
    python -m engine.test_real_forecasting

This test makes a real network request to NASA POWER. Therefore it is an
integration test, not a unit test.
"""

from engine.forecasting.real_data_loader import (
    load_real_nasa_power_history,
)
from engine.forecasting.real_forecasting_service import (
    forecast_real_site,
)


LATITUDE = 13.0827
LONGITUDE = 80.2707


def main() -> None:
    print("=" * 60)
    print("REAL-DATA FORECASTING VALIDATION")
    print("=" * 60)

    print("\nTEST 1 — NASA POWER HISTORICAL DATA")

    history = load_real_nasa_power_history(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        history_days=365,
    )

    print("Source :", history["source"])
    print("Records:", history["record_count"])
    print("Start  :", history["records"][0]["date"])
    print("End    :", history["records"][-1]["date"])

    assert history["record_count"] >= 60
    assert history["records"][0]["date"] < history["records"][-1]["date"]
    assert history["source"] == "NASA POWER Daily API"

    print("PASS")

    print("\nTEST 2 — REAL SOLAR/WIND FORECAST")

    result = forecast_real_site(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        history_days=365,
        forecast_days=7,
    )

    assert result["status"] == "success"
    assert result["data_type"] == "real_historical_observations"
    assert len(result["forecast"]["solar"]) == 7
    assert len(result["forecast"]["wind"]) == 7
    assert len(result["forecast"]["hybrid"]) == 7

    print("Data source :", result["data_source"])
    print("Solar days  :", len(result["forecast"]["solar"]))
    print("Wind days   :", len(result["forecast"]["wind"]))
    print("Hybrid days :", len(result["forecast"]["hybrid"]))
    print("First solar :", result["forecast"]["solar"][0])
    print("First wind  :", result["forecast"]["wind"][0])

    print("PASS")

    print("\n" + "=" * 60)
    print("ALL REAL-DATA FORECASTING TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
