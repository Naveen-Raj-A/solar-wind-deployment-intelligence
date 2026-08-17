"""
Scoring Engine Validation

Validates:
1. Higher renewable resources increase the score.
2. Poor terrain reduces the score.
3. Poor infrastructure reduces the score.
4. Repeated evaluations produce consistent results.
5. Candidate-site ranking changes correctly when scores change.
"""

from engine.scoring import calculate_deployment_score
from engine.site_ranking import rank_candidate_sites


# --------------------------------------------------------------
# TEST REPORT BUILDER
# --------------------------------------------------------------

def build_test_report(
    solar_score,
    wind_score,
    terrain_score,
    sentinel_score,
    osm_score,
):
    """
    Build a realistic test report using the same dataset
    structure expected by calculate_deployment_score().

    The test inputs are expressed as scoring-engine scores
    rather than raw scientific measurements. They are converted
    to representative raw values that exercise the scoring
    thresholds.
    """

    # ----------------------------------------------------------
    # Solar
    #
    # SOLAR_WEIGHT is normally 25.
    #
    # 25 -> EXCELLENT
    # 22.5 -> GOOD
    # 17.5 -> MODERATE
    # 7.5 -> LOW
    # ----------------------------------------------------------

    solar_radiation_map = {
        25: 6.0,
        22.5: 5.0,
        17.5: 4.0,
        7.5: 2.0,
    }

    solar_radiation = solar_radiation_map.get(
        solar_score,
        6.0 if solar_score >= 25 else
        5.0 if solar_score >= 22.5 else
        4.0 if solar_score >= 17.5 else
        2.0,
    )

    # ----------------------------------------------------------
    # Wind
    #
    # WIND_WEIGHT is normally 25.
    # ----------------------------------------------------------

    wind_speed_map = {
        25: 8.0,
        22.5: 7.0,
        17.5: 6.0,
        7.5: 3.0,
    }

    wind_speed = wind_speed_map.get(
        wind_score,
        8.0 if wind_score >= 25 else
        7.0 if wind_score >= 22.5 else
        6.0 if wind_score >= 17.5 else
        3.0,
    )

    # ----------------------------------------------------------
    # Terrain
    #
    # TERRAIN_WEIGHT is normally 20.
    #
    # 20 -> excellent slope
    # 18 -> good slope
    # 14 -> moderate slope
    # 5  -> poor slope
    # ----------------------------------------------------------

    if terrain_score >= 20:
        mean_slope = 2.0
    elif terrain_score >= 18:
        mean_slope = 4.0
    elif terrain_score >= 14:
        mean_slope = 8.0
    else:
        mean_slope = 20.0

    # ----------------------------------------------------------
    # Sentinel
    #
    # SENTINEL_WEIGHT is normally 15.
    #
    # The test uses a representative combination of NDVI,
    # NDMI and valid-pixel percentage.
    # ----------------------------------------------------------

    if sentinel_score >= 15:
        ndvi_mean = 0.80
        ndmi_mean = 0.60
        valid_pixel_percentage = 95.0
    elif sentinel_score >= 13.5:
        ndvi_mean = 0.70
        ndmi_mean = 0.50
        valid_pixel_percentage = 90.0
    elif sentinel_score >= 10.5:
        ndvi_mean = 0.50
        ndmi_mean = 0.30
        valid_pixel_percentage = 75.0
    else:
        ndvi_mean = 0.20
        ndmi_mean = 0.10
        valid_pixel_percentage = 50.0

    # ----------------------------------------------------------
    # OSM
    #
    # OSM_WEIGHT is normally 15.
    #
    # The supplied osm_score is converted into representative
    # infrastructure distances/building density.
    # ----------------------------------------------------------

    if osm_score >= 15:
        road_distance = 0.5
        power_distance = 0.5
        substation_distance = 0.5
        building_count = 10

    elif osm_score >= 11:
        road_distance = 2.0
        power_distance = 2.0
        substation_distance = 2.0
        building_count = 10

    elif osm_score >= 7:
        road_distance = 5.0
        power_distance = 5.0
        substation_distance = 5.0
        building_count = 100

    else:
        road_distance = 20.0
        power_distance = 20.0
        substation_distance = 20.0
        building_count = 500

    return {
        "site_information": {
            "requested_location": "Test Site",
            "latitude": 10.0,
            "longitude": 78.0,
        },

        "datasets": {

            "nasa_power": {
                "solar_resource": {
                    "solar_radiation_kwh_m2_day": solar_radiation,
                },
            },

            "wind": {
                "wind_speed_statistics": {
                    "mean_ms": wind_speed,
                },
            },

            "srtm": {
                "slope_statistics": {
                    "mean_degrees": mean_slope,
                },
            },

            "sentinel": {
                "ndvi_statistics": {
                    "mean": ndvi_mean,
                },
                "ndmi_statistics": {
                    "mean": ndmi_mean,
                },
                "valid_percentage": valid_pixel_percentage,
            },

            "osm": {
                "status": "success",

                "infrastructure_indicators": {
                    "nearest_road_distance_km": road_distance,
                    "nearest_power_infrastructure_distance_km": power_distance,
                    "nearest_substation_distance_km": substation_distance,
                },

                "feature_analysis": {
                    "building": {
                        "count": building_count,
                    },
                },
            },
        },
    }


# --------------------------------------------------------------
# SCORE CALCULATION HELPER
# --------------------------------------------------------------

def calculate_test_score(
    solar_score,
    wind_score,
    terrain_score,
    sentinel_score,
    osm_score,
):
    """
    Calculate the deployment score for test data.
    """

    report = build_test_report(
        solar_score,
        wind_score,
        terrain_score,
        sentinel_score,
        osm_score,
    )

    result = calculate_deployment_score(report)

    return result["normalized_score"]


# --------------------------------------------------------------
# TEST 1 — HIGHER RENEWABLE RESOURCE
# --------------------------------------------------------------

def test_higher_renewable_resource():
    """
    Verify that improving solar and wind scores
    increases the overall score.
    """

    low_resource_score = calculate_test_score(
        solar_score=10,
        wind_score=10,
        terrain_score=20,
        sentinel_score=15,
        osm_score=15,
    )

    high_resource_score = calculate_test_score(
        solar_score=25,
        wind_score=25,
        terrain_score=20,
        sentinel_score=15,
        osm_score=15,
    )

    print("\nTEST 1 — HIGHER RENEWABLE RESOURCE")

    print(
        f"Low renewable score  : "
        f"{low_resource_score:.2f}"
    )

    print(
        f"High renewable score : "
        f"{high_resource_score:.2f}"
    )

    assert high_resource_score > low_resource_score

    print("PASS")


# --------------------------------------------------------------
# TEST 2 — POOR TERRAIN
# --------------------------------------------------------------

def test_poor_terrain():
    """
    Verify that poor terrain reduces the overall score.
    """

    good_terrain_score = calculate_test_score(
        solar_score=25,
        wind_score=25,
        terrain_score=20,
        sentinel_score=15,
        osm_score=15,
    )

    poor_terrain_score = calculate_test_score(
        solar_score=25,
        wind_score=25,
        terrain_score=5,
        sentinel_score=15,
        osm_score=15,
    )

    print("\nTEST 2 — POOR TERRAIN")

    print(
        f"Good terrain score : "
        f"{good_terrain_score:.2f}"
    )

    print(
        f"Poor terrain score : "
        f"{poor_terrain_score:.2f}"
    )

    assert poor_terrain_score < good_terrain_score

    print("PASS")


# --------------------------------------------------------------
# TEST 3 — POOR INFRASTRUCTURE
# --------------------------------------------------------------

def test_poor_infrastructure():
    """
    Verify that poor infrastructure reduces the overall score.
    """

    good_infrastructure_score = calculate_test_score(
        solar_score=25,
        wind_score=25,
        terrain_score=20,
        sentinel_score=15,
        osm_score=15,
    )

    poor_infrastructure_score = calculate_test_score(
        solar_score=25,
        wind_score=25,
        terrain_score=20,
        sentinel_score=15,
        osm_score=2,
    )

    print("\nTEST 3 — POOR INFRASTRUCTURE")

    print(
        f"Good infrastructure score : "
        f"{good_infrastructure_score:.2f}"
    )

    print(
        f"Poor infrastructure score : "
        f"{poor_infrastructure_score:.2f}"
    )

    assert poor_infrastructure_score < good_infrastructure_score

    print("PASS")


# --------------------------------------------------------------
# TEST 4 — CONSISTENCY
# --------------------------------------------------------------

def test_consistency():
    """
    Verify that repeated evaluations with identical
    inputs produce identical scores.
    """

    score_1 = calculate_test_score(
        solar_score=22.5,
        wind_score=22.5,
        terrain_score=20,
        sentinel_score=13.95,
        osm_score=11,
    )

    score_2 = calculate_test_score(
        solar_score=22.5,
        wind_score=22.5,
        terrain_score=20,
        sentinel_score=13.95,
        osm_score=11,
    )

    print("\nTEST 4 — CONSISTENCY")

    print(
        f"First evaluation  : "
        f"{score_1:.2f}"
    )

    print(
        f"Second evaluation : "
        f"{score_2:.2f}"
    )

    assert score_1 == score_2

    print("PASS")


# --------------------------------------------------------------
# TEST 5 — RANKING
# --------------------------------------------------------------

def test_ranking():

    sites = [
        {
            "site_name": "Karur",
            "overall_score": 89.95,
        },
        {
            "site_name": "Krishnagiri",
            "overall_score": 88.95,
        },
        {
            "site_name": "Salem",
            "overall_score": 92.40,
        },
    ]

    ranked = rank_candidate_sites(sites)

    print("\nTEST 5 — SITE RANKING")

    for site in ranked:
        print(
            f"{site['rank']}. "
            f"{site['site_name']} "
            f"-> "
            f"{site['overall_score']:.2f}"
        )

    assert ranked[0]["site_name"] == "Salem"
    assert ranked[1]["site_name"] == "Karur"
    assert ranked[2]["site_name"] == "Krishnagiri"

    print("PASS")


# --------------------------------------------------------------
# RUN ALL TESTS
# --------------------------------------------------------------

def main():

    print()
    print("======================================")
    print("SCORING ENGINE VALIDATION")
    print("======================================")

    test_higher_renewable_resource()

    test_poor_terrain()

    test_poor_infrastructure()

    test_consistency()

    test_ranking()

    print()
    print("======================================")
    print("ALL SCORING TESTS PASSED")
    print("======================================")


if __name__ == "__main__":
    main()