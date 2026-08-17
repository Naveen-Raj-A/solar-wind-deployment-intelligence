"""
Integrated Financial Analysis Validation

Validates that changes in:
    - Installed capacity
    - Electricity tariff
    - Project cost

produce the expected changes in the final /analysis response.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from test_analysis import build_mock_report


client = TestClient(app)


def create_mock_report():
    return build_mock_report(
        13.0827,
        80.2707,
        6.0,
        8.0,
        2.0,
    )


def run_analysis(
    *,
    installed_capacity_mw=None,
    electricity_tariff_inr_per_kwh=5.0,
    cost_per_mw=5_000_000.0,
):
    payload = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "available_land_area_km2": 10,
        "used_land_area_km2": 2,
        "installed_capacity_mw": installed_capacity_mw,
        "electricity_tariff_inr_per_kwh": (
            electricity_tariff_inr_per_kwh
        ),
        "cost_per_mw": cost_per_mw,
    }

    report = create_mock_report()

    with patch(
        "engine.analysis_service.build_realtime_site_report",
        return_value=report,
    ):
        response = client.post(
            "/analysis",
            json=payload,
        )

    assert response.status_code == 200

    return response.json()


def test_capacity_change():

    small = run_analysis(
        installed_capacity_mw=10,
    )

    large = run_analysis(
        installed_capacity_mw=20,
    )

    small_financial = small["financial_analysis"]
    large_financial = large["financial_analysis"]

    assert (
        large_financial["estimated_project_cost"]
        > small_financial["estimated_project_cost"]
    )

    assert (
        large_financial["annual_energy_yield_kwh"]
        > small_financial["annual_energy_yield_kwh"]
    )

    print(
        "PASS: test_capacity_change"
    )


def test_tariff_change():

    low = run_analysis(
        installed_capacity_mw=10,
        electricity_tariff_inr_per_kwh=4.0,
    )

    high = run_analysis(
        installed_capacity_mw=10,
        electricity_tariff_inr_per_kwh=8.0,
    )

    low_financial = low["financial_analysis"]
    high_financial = high["financial_analysis"]

    assert (
        high_financial["estimated_annual_revenue"]
        > low_financial["estimated_annual_revenue"]
    )

    assert (
        high_financial["payback_period_years"]
        < low_financial["payback_period_years"]
    )

    assert (
        high_financial["roi_percent"]
        > low_financial["roi_percent"]
    )

    print(
        "PASS: test_tariff_change"
    )


def test_project_cost_change():

    low_cost = run_analysis(
        installed_capacity_mw=10,
        cost_per_mw=4_000_000,
    )

    high_cost = run_analysis(
        installed_capacity_mw=10,
        cost_per_mw=8_000_000,
    )

    low_financial = low_cost["financial_analysis"]
    high_financial = high_cost["financial_analysis"]

    assert (
        high_financial["estimated_project_cost"]
        > low_financial["estimated_project_cost"]
    )

    assert (
        high_financial["payback_period_years"]
        > low_financial["payback_period_years"]
    )

    assert (
        high_financial["roi_percent"]
        < low_financial["roi_percent"]
    )

    print(
        "PASS: test_project_cost_change"
    )


def test_final_response_consistency():

    data = run_analysis(
        installed_capacity_mw=10,
        electricity_tariff_inr_per_kwh=5.0,
        cost_per_mw=5_000_000,
    )

    assert data["status"] == "success"

    assert "energy_yield" in data

    assert "financial_analysis" in data

    financial = data["financial_analysis"]

    required_fields = [
        "annual_energy_yield_kwh",
        "installed_capacity_mw",
        "electricity_tariff_inr_per_kwh",
        "cost_per_mw",
        "estimated_annual_revenue",
        "estimated_project_cost",
        "payback_period_years",
        "roi_percent",
    ]

    for field in required_fields:
        assert field in financial

    assert financial[
        "annual_energy_yield_kwh"
    ] > 0

    assert financial[
        "estimated_annual_revenue"
    ] > 0

    assert financial[
        "estimated_project_cost"
    ] > 0

    print(
        "PASS: test_final_response_consistency"
    )


def main():

    print()
    print("======================================")
    print("INTEGRATED FINANCIAL SCENARIO VALIDATION")
    print("======================================")
    print()

    test_capacity_change()
    test_tariff_change()
    test_project_cost_change()
    test_final_response_consistency()

    print()
    print("======================================")
    print("ALL FINANCIAL INTEGRATION TESTS PASSED")
    print("======================================")


if __name__ == "__main__":
    main()