"""
Unified Analysis Pipeline Validation
====================================

Tests the complete Solar-Wind Deployment Intelligence pipeline.

The realtime dataset retrieval stage is mocked so the tests:
    - do not require external APIs
    - do not require Sentinel credentials
    - do not modify real datasets
    - execute the REAL scoring engine
    - execute the REAL optimization engine
    - execute the REAL feasibility engine
    - execute the REAL energy-yield engine
    - execute the REAL financial-analysis engine

Run:
    python test_analysis.py
"""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ==============================================================
# MOCK REALTIME REPORT BUILDER
# ==============================================================

def build_mock_report(
    latitude: float,
    longitude: float,
    solar: float,
    wind: float,
    slope: float,
    *,
    osm_good: bool = True,
):
    """
    Build a mock response in the same structure expected from
    build_realtime_site_report().

    IMPORTANT:
        Only the external/realtime data retrieval is mocked.

    The following remain REAL:
        - scoring
        - optimization
        - feasibility
        - energy yield
        - financial analysis
    """

    # ----------------------------------------------------------
    # OPENSTREETMAP
    # ----------------------------------------------------------

    if osm_good:
        osm = {
            "source": "Mock OpenStreetMap",
            "status": "success",

            "infrastructure_indicators": {
                "nearest_road_distance_km": 0.5,
                "nearest_power_infrastructure_distance_km": 0.5,
                "nearest_substation_distance_km": 0.5,
            },

            "feature_analysis": {
                "building": {
                    "count": 10,
                },
            },
        }

    else:
        osm = {
            "source": "Mock OpenStreetMap",
            "status": "success",

            "infrastructure_indicators": {
                "nearest_road_distance_km": 20.0,
                "nearest_power_infrastructure_distance_km": 20.0,
                "nearest_substation_distance_km": 20.0,
            },

            "feature_analysis": {
                "building": {
                    "count": 500,
                },
            },
        }

    # ----------------------------------------------------------
    # RETURN COMPLETE REALTIME REPORT
    # ----------------------------------------------------------

    return {

        # ======================================================
        # SITE INFORMATION
        # ======================================================

        "site_information": {
            "requested_location": (
                f"{latitude:.6f}, {longitude:.6f}"
            ),

            "latitude": latitude,

            "longitude": longitude,

            "available_land_area_km2": 10.0,

            "used_land_area_km2": 2.0,

            "land_reserve_percent": 80.0,
        },

        # ======================================================
        # DATASETS
        # ======================================================

        "datasets": {

            # --------------------------------------------------
            # NASA POWER
            # --------------------------------------------------

            "nasa_power": {
                "source": "Mock NASA POWER",

                "source_status": "success",

                "status": "success",

                "solar_resource": {
                    "solar_radiation_kwh_m2_day": solar,

                    "solar_resource_class": (
                        "GOOD"
                        if solar >= 4.5
                        else "MODERATE"
                    ),
                },

                "wind_speed_statistics": {
                    "mean_ms": wind,
                },

                "wind_resource_class": (
                    "GOOD"
                    if wind >= 6.0
                    else "MODERATE"
                ),
            },

            # --------------------------------------------------
            # WIND
            # --------------------------------------------------

            "wind": {
                "source": "Mock Global Wind Atlas",

                "source_status": "success",

                "status": "success",

                "wind_speed_statistics": {
                    "mean_ms": wind,
                },

                "wind_measurement_height_m": 150,

                "valid_wind_percentage": 95.0,

                "good_wind_percentage": (
                    80.0
                    if wind >= 6.0
                    else 20.0
                ),

                "excellent_wind_percentage": 0.0,
            },

            # --------------------------------------------------
            # SRTM
            # --------------------------------------------------

            "srtm": {
                "source": "Mock SRTM",

                "source_status": "success",

                "status": "success",

                "elevation_m": 100.0,

                "slope_statistics": {
                    "mean_degrees": slope,
                },

                "terrain_suitability": (
                    "HIGHLY SUITABLE"
                    if slope < 3
                    else "SUITABLE"
                ),

                "favorable_terrain_percentage": (
                    95.0
                    if slope < 3
                    else 80.0
                ),

                "steep_terrain_percentage": (
                    2.0
                    if slope < 3
                    else 20.0
                ),
            },

            # --------------------------------------------------
            # SENTINEL-2
            # --------------------------------------------------

            "sentinel": {
                "source": "Mock Sentinel-2",

                "source_status": "success",

                "status": "success",

                "ndvi_statistics": {
                    "mean": 0.20,
                },

                "ndmi_statistics": {
                    "mean": 0.10,
                },

                "valid_percentage": 95.0,
            },

            # --------------------------------------------------
            # OPENSTREETMAP
            # --------------------------------------------------

            "osm": osm,
        },

        # ======================================================
        # CURRENT CONDITIONS
        # ======================================================

        "current_conditions": {
            "source": "Mock Open-Meteo",

            "current": {
                "wind_speed_10m": wind,
            },
        },

        # ======================================================
        # RUNTIME METADATA
        # ======================================================

        "runtime_metadata": {
            "sentinel_status": "SUCCESS",

            "data_source": "MOCK_REALTIME_PIPELINE",
        },
    }


# ==============================================================
# RESPONSE DEBUG HELPER
# ==============================================================

def assert_success_response(response, test_name: str):
    """
    Assert HTTP 200.

    If the API returns an error, print the complete response
    before raising the assertion so debugging is easier.
    """

    if response.status_code != 200:

        print()
        print("=" * 70)
        print(f"{test_name} — API ERROR")
        print("=" * 70)

        print("HTTP STATUS:")
        print(response.status_code)

        print()
        print("RESPONSE BODY:")

        try:
            print(response.json())
        except Exception:
            print(response.text)

        print("=" * 70)
        print()

    assert response.status_code == 200


# ==============================================================
# ENERGY EXTRACTION HELPER
# ==============================================================

def extract_annual_energy_mwh(energy_yield):
    """
    Extract annual energy in MWh from the energy-yield response.

    Supports common response formats used by the project.
    """

    if not isinstance(energy_yield, dict):
        return 0.0

    # ----------------------------------------------------------
    # DIRECT MWh VALUES
    # ----------------------------------------------------------

    for key in (
        "annual_energy_yield_mwh",
        "annual_energy_mwh",
        "estimated_annual_energy_mwh",
    ):

        value = energy_yield.get(key)

        if value is not None:
            return float(value)

    # ----------------------------------------------------------
    # DIRECT kWh VALUES
    # ----------------------------------------------------------

    for key in (
        "annual_energy_yield_kwh",
        "annual_energy_kwh",
        "estimated_annual_energy_kwh",
    ):

        value = energy_yield.get(key)

        if value is not None:
            return float(value) / 1000.0

    # ----------------------------------------------------------
    # SOLAR + WIND NESTED VALUES
    # ----------------------------------------------------------

    solar = energy_yield.get("solar", {})

    wind = energy_yield.get("wind", {})

    total_mwh = 0.0

    # ----------------------------------------------------------
    # SOLAR
    # ----------------------------------------------------------

    if isinstance(solar, dict):

        found = False

        for key in (
            "annual_energy_yield_mwh",
            "annual_energy_mwh",
            "estimated_annual_energy_mwh",
        ):

            if solar.get(key) is not None:

                total_mwh += float(solar[key])

                found = True

                break

        if not found:

            for key in (
                "annual_energy_yield_kwh",
                "annual_energy_kwh",
                "estimated_annual_energy_kwh",
            ):

                if solar.get(key) is not None:

                    total_mwh += (
                        float(solar[key]) / 1000.0
                    )

                    break

    # ----------------------------------------------------------
    # WIND
    # ----------------------------------------------------------

    if isinstance(wind, dict):

        found = False

        for key in (
            "annual_energy_yield_mwh",
            "annual_energy_mwh",
            "estimated_annual_energy_mwh",
        ):

            if wind.get(key) is not None:

                total_mwh += float(wind[key])

                found = True

                break

        if not found:

            for key in (
                "annual_energy_yield_kwh",
                "annual_energy_kwh",
                "estimated_annual_energy_kwh",
            ):

                if wind.get(key) is not None:

                    total_mwh += (
                        float(wind[key]) / 1000.0
                    )

                    break

    return total_mwh


# ==============================================================
# TEST 1 — HEALTH
# ==============================================================

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"

    print()
    print("TEST 1 — HEALTH API")
    print("PASS")


# ==============================================================
# TEST 2 — SOLAR SITE
# ==============================================================

def test_complete_analysis_solar_site():

    mock_report = build_mock_report(
        latitude=11.0168,
        longitude=76.9558,
        solar=6.0,
        wind=3.0,
        slope=2.0,
    )

    # ----------------------------------------------------------
    # IMPORTANT:
    #
    # The current AnalysisService calls:
    #
    # build_realtime_site_report()
    #
    # NOT:
    #
    # run_all_datasets()
    # ----------------------------------------------------------

    with patch(
        "engine.analysis_service.build_realtime_site_report",
        return_value=mock_report,
    ):

        response = client.post(
            "/analysis",
            json={
                "latitude": 11.0168,
                "longitude": 76.9558,
                "available_land_area_km2": 10,
                "used_land_area_km2": 2,
            },
        )

    assert_success_response(
        response,
        "TEST 2 — SOLAR SITE",
    )

    data = response.json()

    # ----------------------------------------------------------
    # BASIC RESPONSE
    # ----------------------------------------------------------

    assert data["status"] == "success"

    # ----------------------------------------------------------
    # SITE
    # ----------------------------------------------------------

    assert "site" in data

    assert data["site"]["latitude"] == 11.0168

    assert data["site"]["longitude"] == 76.9558

    # ----------------------------------------------------------
    # DATASETS
    # ----------------------------------------------------------

    assert "datasets" in data

    assert "nasa_power" in data["datasets"]

    assert "wind" in data["datasets"]

    assert "srtm" in data["datasets"]

    assert "osm" in data["datasets"]

    assert "sentinel" in data["datasets"]

    # ----------------------------------------------------------
    # DEPLOYMENT
    # ----------------------------------------------------------

    assert "deployment_assessment" in data

    assert "deployment_recommendation" in data

    # ----------------------------------------------------------
    # TECHNICAL FEASIBILITY
    # ----------------------------------------------------------

    assert "technical_feasibility" in data

    feasibility = data["technical_feasibility"]

    assert "feasibility_status" in feasibility

    assert feasibility["feasibility_status"] == "FEASIBLE"

    # ----------------------------------------------------------
    # ENERGY
    # ----------------------------------------------------------

    assert "energy_yield" in data

    assert data["energy_yield"] is not None

    annual_energy_mwh = extract_annual_energy_mwh(
        data["energy_yield"]
    )

    assert annual_energy_mwh > 0

    # ----------------------------------------------------------
    # OUTPUT
    # ----------------------------------------------------------

    print()
    print("TEST 2 — SOLAR SITE COMPLETE PIPELINE")

    print(
        "Technology:",
        data["deployment_recommendation"].get(
            "recommended_technology"
        ),
    )

    print(
        "Suitability:",
        data["deployment_assessment"].get(
            "normalized_score"
        ),
    )

    print(
        "Feasibility:",
        feasibility.get(
            "feasibility_status"
        ),
    )

    print(
        "Annual Energy:",
        annual_energy_mwh,
        "MWh",
    )

    print("PASS")


# ==============================================================
# TEST 3 — WIND SITE
# ==============================================================

def test_complete_analysis_wind_site():

    mock_report = build_mock_report(
        latitude=12.9716,
        longitude=77.5946,
        solar=2.0,
        wind=8.0,
        slope=2.0,
    )

    with patch(
        "engine.analysis_service.build_realtime_site_report",
        return_value=mock_report,
    ):

        response = client.post(
            "/analysis",
            json={
                "latitude": 12.9716,
                "longitude": 77.5946,
                "available_land_area_km2": 10,
                "used_land_area_km2": 2,
            },
        )

    assert_success_response(
        response,
        "TEST 3 — WIND SITE",
    )

    data = response.json()

    # ----------------------------------------------------------
    # BASIC RESPONSE
    # ----------------------------------------------------------

    assert data["status"] == "success"

    # ----------------------------------------------------------
    # DEPLOYMENT
    # ----------------------------------------------------------

    assert "deployment_assessment" in data

    assert "deployment_recommendation" in data

    # ----------------------------------------------------------
    # FEASIBILITY
    # ----------------------------------------------------------

    assert "technical_feasibility" in data

    feasibility = data["technical_feasibility"]

    assert (
        feasibility["feasibility_status"]
        == "FEASIBLE"
    )

    # ----------------------------------------------------------
    # ENERGY
    # ----------------------------------------------------------

    assert data["energy_yield"] is not None

    annual_energy_mwh = extract_annual_energy_mwh(
        data["energy_yield"]
    )

    assert annual_energy_mwh > 0

    # ----------------------------------------------------------
    # OUTPUT
    # ----------------------------------------------------------

    print()
    print("TEST 3 — WIND SITE COMPLETE PIPELINE")

    print(
        "Technology:",
        data["deployment_recommendation"].get(
            "recommended_technology"
        ),
    )

    print(
        "Suitability:",
        data["deployment_assessment"].get(
            "normalized_score"
        ),
    )

    print(
        "Feasibility:",
        feasibility.get(
            "feasibility_status"
        ),
    )

    print(
        "Annual Energy:",
        annual_energy_mwh,
        "MWh",
    )

    print("PASS")


# ==============================================================
# TEST 4 — HYBRID SITE
# ==============================================================

def test_complete_analysis_hybrid_site():

    mock_report = build_mock_report(
        latitude=13.0827,
        longitude=80.2707,
        solar=6.0,
        wind=8.0,
        slope=2.0,
    )

    with patch(
        "engine.analysis_service.build_realtime_site_report",
        return_value=mock_report,
    ):

        response = client.post(
            "/analysis",
            json={
                "latitude": 13.0827,
                "longitude": 80.2707,
                "available_land_area_km2": 10,
                "used_land_area_km2": 2,
            },
        )

    assert_success_response(
        response,
        "TEST 4 — HYBRID SITE",
    )

    data = response.json()

    # ----------------------------------------------------------
    # BASIC RESPONSE
    # ----------------------------------------------------------

    assert data["status"] == "success"

    # ----------------------------------------------------------
    # REQUIRED OUTPUT SECTIONS
    # ----------------------------------------------------------

    assert "deployment_assessment" in data

    assert "deployment_recommendation" in data

    assert "technical_feasibility" in data

    assert "energy_yield" in data

    assert "financial_analysis" in data

    assert "pipeline" in data

    # ----------------------------------------------------------
    # FEASIBILITY
    # ----------------------------------------------------------

    feasibility = data["technical_feasibility"]

    assert (
        feasibility["feasibility_status"]
        == "FEASIBLE"
    )

    # ----------------------------------------------------------
    # ENERGY
    # ----------------------------------------------------------

    assert data["energy_yield"] is not None

    annual_energy_mwh = extract_annual_energy_mwh(
        data["energy_yield"]
    )

    assert annual_energy_mwh > 0

    # ----------------------------------------------------------
    # FINANCIAL
    # ----------------------------------------------------------

    assert data["financial_analysis"] is not None

    # ----------------------------------------------------------
    # PIPELINE
    # ----------------------------------------------------------

    assert data["pipeline"]["completed"] is True

    expected_steps = [
        "site_details_received",
        "local_nasa_power_analysis",
        "local_global_wind_atlas_analysis",
        "local_srtm_analysis",
        "local_sentinel_analysis",
        "local_openstreetmap_analysis",
        "deployment_score_calculated",
        "deployment_optimized",
        "technical_feasibility_validated",
        "annual_energy_yield_estimated",
        "financial_analysis_completed",
        "final_response_generated",
    ]

    assert (
        data["pipeline"]["steps"]
        == expected_steps
    )

    # ----------------------------------------------------------
    # OUTPUT
    # ----------------------------------------------------------

    print()
    print("TEST 4 — HYBRID SITE COMPLETE PIPELINE")

    print(
        "Technology:",
        data["deployment_recommendation"].get(
            "recommended_technology"
        ),
    )

    print(
        "Suitability:",
        data["deployment_assessment"].get(
            "normalized_score"
        ),
    )

    print(
        "Feasibility:",
        feasibility.get(
            "feasibility_status"
        ),
    )

    print(
        "Annual Energy:",
        annual_energy_mwh,
        "MWh",
    )

    print(
        "Financial Analysis: PRESENT"
    )

    print(
        "Pipeline: COMPLETE"
    )

    print("PASS")


# ==============================================================
# TEST 5 — INVALID LAND INPUT
# ==============================================================

def test_invalid_land_area():

    response = client.post(
        "/analysis",
        json={
            "latitude": 13.0827,
            "longitude": 80.2707,
            "available_land_area_km2": 5,
            "used_land_area_km2": 6,
        },
    )

    # ----------------------------------------------------------
    # The API should reject this before running analysis.
    # ----------------------------------------------------------

    assert response.status_code == 422

    print()
    print("TEST 5 — INVALID LAND INPUT")

    print(
        "Status:",
        response.status_code,
    )

    print("PASS")


# ==============================================================
# TEST 6 — TECHNICAL FEASIBILITY FAILURE
# ==============================================================

def test_feasibility_failure_is_reported():

    # ----------------------------------------------------------
    # Deliberately create unacceptable terrain.
    #
    # Slope = 20 degrees.
    # ----------------------------------------------------------

    mock_report = build_mock_report(
        latitude=13.0827,
        longitude=80.2707,
        solar=6.0,
        wind=8.0,
        slope=20.0,
    )

    with patch(
        "engine.analysis_service.build_realtime_site_report",
        return_value=mock_report,
    ):

        response = client.post(
            "/analysis",
            json={
                "latitude": 13.0827,
                "longitude": 80.2707,
                "available_land_area_km2": 10,
                "used_land_area_km2": 2,
            },
        )

    assert_success_response(
        response,
        "TEST 6 — FEASIBILITY FAILURE",
    )

    data = response.json()

    assert data["status"] == "success"

    # ----------------------------------------------------------
    # FEASIBILITY
    # ----------------------------------------------------------

    feasibility = data["technical_feasibility"]

    assert (
        feasibility["feasibility_status"]
        == "NOT_FEASIBLE"
    )

    # At least one hard constraint must fail.
    assert feasibility["failed_constraints"]

    # ----------------------------------------------------------
    # OUTPUT
    # ----------------------------------------------------------

    print()
    print(
        "TEST 6 — FEASIBILITY FAILURE REPORTING"
    )

    print(
        "Status:",
        feasibility[
            "feasibility_status"
        ],
    )

    print(
        "Passed:",
        feasibility.get(
            "passed_constraints"
        ),
    )

    print(
        "Failed:",
        feasibility.get(
            "failed_constraints"
        ),
    )

    print("PASS")


# ==============================================================
# MAIN
# ==============================================================

def main():

    print()

    print(
        "======================================"
    )

    print(
        "UNIFIED ANALYSIS PIPELINE VALIDATION"
    )

    print(
        "======================================"
    )

    # ----------------------------------------------------------
    # TEST 1
    # ----------------------------------------------------------

    test_health()

    # ----------------------------------------------------------
    # TEST 2
    # ----------------------------------------------------------

    test_complete_analysis_solar_site()

    # ----------------------------------------------------------
    # TEST 3
    # ----------------------------------------------------------

    test_complete_analysis_wind_site()

    # ----------------------------------------------------------
    # TEST 4
    # ----------------------------------------------------------

    test_complete_analysis_hybrid_site()

    # ----------------------------------------------------------
    # TEST 5
    # ----------------------------------------------------------

    test_invalid_land_area()

    # ----------------------------------------------------------
    # TEST 6
    # ----------------------------------------------------------

    test_feasibility_failure_is_reported()

    # ----------------------------------------------------------
    # FINAL
    # ----------------------------------------------------------

    print()

    print(
        "======================================"
    )

    print(
        "ALL ANALYSIS PIPELINE TESTS PASSED"
    )

    print(
        "======================================"
    )


# ==============================================================
# ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    main()