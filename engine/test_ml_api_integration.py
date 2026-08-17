"""End-to-end API validation for ML inference.

Run the FastAPI server first:
    python -m uvicorn main:app --reload

Then run:
    python -m engine.test_ml_api_integration
"""

from __future__ import annotations

import requests


URL = "http://127.0.0.1:8000/analysis"

SITES = [
    {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "available_land_area_km2": 5,
        "used_land_area_km2": 0,
    },
    {
        "latitude": 11.0168,
        "longitude": 76.9558,
        "available_land_area_km2": 3,
        "used_land_area_km2": 0,
    },
]


def main():
    print("=" * 60)
    print("ML END-TO-END API VALIDATION")
    print("=" * 60)

    for index, site in enumerate(SITES, start=1):
        payload = {
            **site,
            "nasa_days": 30,
            "osm_radius_m": 5000,
            "sentinel_radius_m": 500,
            "sentinel_days": 30,
            "require_sentinel": False,
        }

        response = requests.post(
            URL,
            json=payload,
            timeout=180,
        )

        print(f"\nTEST {index} — SITE {site['latitude']}, {site['longitude']}")
        print("HTTP status:", response.status_code)

        response.raise_for_status()
        body = response.json()

        assert body.get("status") == "success"
        assert "ml_prediction" in body
        assert (
            body["ml_prediction"]["model"]
            == "RandomForestRegressor"
        )

        predicted = body["ml_prediction"][
            "predicted_solar_radiation_kwh_m2_day"
        ]

        assert predicted >= 0
        assert body["ml_prediction"]["used_for_solar_scoring"] is True

        print("ML prediction:", predicted)
        print("Prediction included in final API response: PASS")

    print("\n" + "=" * 60)
    print("ALL ML API INTEGRATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
