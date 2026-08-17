"""
Five-Location End-to-End API Validation

Tests the REAL /analysis API using five different locations.

Validates:
    - HTTP success
    - Site suitability
    - Recommended deployment
    - Technical feasibility
    - Energy yield
    - Financial metrics
    - Standardized final recommendation
    - Recommendation reason
"""

import requests


API_URL = "http://127.0.0.1:8000/analysis"


LOCATIONS = [
    {
        "name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
    },
    {
        "name": "Salem",
        "latitude": 11.6643,
        "longitude": 78.1460,
    },
    {
        "name": "Coimbatore",
        "latitude": 11.0168,
        "longitude": 76.9558,
    },
    {
        "name": "Karur",
        "latitude": 10.9601,
        "longitude": 78.0766,
    },
    {
        "name": "Krishnagiri",
        "latitude": 12.5186,
        "longitude": 78.2137,
    },
]


def build_payload(location):
    return {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "available_land_area_km2": 5.0,
        "used_land_area_km2": 0.0,

        "nasa_days": 30,
        "osm_radius_m": 5000,
        "sentinel_radius_m": 500,
        "sentinel_days": 30,
        "require_sentinel": False,

        # Energy parameters
        "electricity_tariff_inr_per_kwh": 5.0,
        "cost_per_mw": 5_000_000.0,
        "additional_installation_percent": 0.0,
    }


def validate_response(data):
    required_top_level = [
        "status",
        "site",
        "evaluation",
        "technical_feasibility",
        "deployment_recommendation",
        "energy_yield",
        "financial_analysis",
        "final_recommendation",
        "pipeline",
    ]

    for field in required_top_level:
        assert field in data, (
            f"Missing top-level field: {field}"
        )

    final = data["final_recommendation"]

    required_final_fields = [
        "site_suitability",
        "recommended_deployment",
        "technical_feasibility",
        "energy_yield",
        "financial_metrics",
        "recommendation_reason",
    ]

    for field in required_final_fields:
        assert field in final, (
            f"Missing standardized field: {field}"
        )

    assert data["pipeline"]["completed"] is True

    financial = data["financial_analysis"]

    assert (
        financial["estimated_annual_revenue"] >= 0
    )

    assert (
        financial["estimated_project_cost"] >= 0
    )

    return True


def test_location(location):
    payload = build_payload(location)

    response = requests.post(
        API_URL,
        json=payload,
        timeout=180,
    )

    assert response.status_code == 200, (
        f"{location['name']} returned "
        f"HTTP {response.status_code}: "
        f"{response.text[:1000]}"
    )

    data = response.json()

    assert data["status"] == "success"

    validate_response(data)

    evaluation = data["evaluation"]

    deployment = data[
        "deployment_recommendation"
    ]

    feasibility = data[
        "technical_feasibility"
    ]

    energy = data[
        "energy_yield"
    ]

    financial = data[
        "financial_analysis"
    ]

    print(
        f"\n{location['name']}"
    )

    print(
        "  Suitability Score :",
        evaluation.get(
            "normalized_score"
        ),
    )

    print(
        "  Recommendation     :",
        evaluation.get(
            "recommendation"
        ),
    )

    print(
        "  Technology         :",
        deployment.get(
            "recommended_technology"
        ),
    )

    print(
        "  Capacity           :",
        deployment.get(
            "recommended_capacity_mw"
        ),
        "MW",
    )

    print(
        "  Feasibility        :",
        feasibility.get(
            "feasibility_status"
        ),
    )

    print(
        "  Energy             :",
        energy.get(
            "annual_energy_mwh"
        ),
        "MWh/year"
        if energy
        else "N/A",
    )

    print(
        "  Revenue            : ₹",
        financial.get(
            "estimated_annual_revenue"
        ),
    )

    print(
        "  Project Cost       : ₹",
        financial.get(
            "estimated_project_cost"
        ),
    )

    print(
        "  Payback            :",
        financial.get(
            "payback_period_years"
        ),
        "years",
    )

    print(
        "  ROI                :",
        financial.get(
            "roi_percent"
        ),
        "%",
    )

    print(
        "  Standardized API   : PASS"
    )


def test_invalid_input():

    payload = {
        "latitude": 200,
        "longitude": 80.2707,
        "available_land_area_km2": 5.0,
        "used_land_area_km2": 0.0,
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=30,
    )

    assert response.status_code == 422

    print(
        "\nINVALID LATITUDE"
    )

    print(
        "  Status:",
        response.status_code,
    )

    print(
        "  PASS"
    )


def main():

    print()
    print("======================================")
    print("FIVE-LOCATION END-TO-END VALIDATION")
    print("======================================")

    passed = 0

    for location in LOCATIONS:

        try:
            test_location(location)
            passed += 1

        except Exception as exc:

            print(
                f"\n{location['name']}"
            )

            print(
                "  FAIL:",
                exc,
            )

    print()
    print("--------------------------------------")
    print(
        f"Locations passed: "
        f"{passed}/{len(LOCATIONS)}"
    )
    print("--------------------------------------")

    assert passed == len(LOCATIONS), (
        "One or more location tests failed."
    )

    test_invalid_input()

    print()
    print("======================================")
    print("ALL FIVE-LOCATION TESTS PASSED")
    print("======================================")


if __name__ == "__main__":
    main()