from engine.feasibility import evaluate_hard_constraints


def build_site(
    available_land=10.0,
    used_land=2.0,
    solar=6.0,
    wind=8.0,
    slope=5.0,
    category_scores=None,
):
    """
    Build a reusable hypothetical site for feasibility testing.
    """

    if category_scores is None:
        category_scores = {
            "renewable_resource": 90.0,
            "terrain": 90.0,
            "infrastructure": 90.0,
            "environmental": 90.0,
            "economic": 90.0,
        }

    return {
        "site_information": {
            "latitude": 13.0827,
            "longitude": 80.2707,
            "available_land_area_km2": available_land,
            "used_land_area_km2": used_land,
        },

        "datasets": {
            "nasa_power": {
                "solar_resource": {
                    "solar_radiation_kwh_m2_day": solar
                }
            },

            "wind": {
                "wind_speed_statistics": {
                    "mean_ms": wind
                }
            },

            "srtm": {
                "elevation_m": 20.0,
                "slope_statistics": {
                    "mean_degrees": slope
                }
            },
        },

        "category_scores": category_scores,
    }


# ================================================================
# TEST 1 — VALID SITE
# ================================================================

def test_valid_site():

    site = build_site()

    result = evaluate_hard_constraints(
        site,
        recommended_capacity_mw=30.0,
    )

    assert result["feasibility_status"] == "FEASIBLE"
    assert result["hard_constraints_failed"] == 0

    print("TEST 1 — VALID SITE")
    print("Status:", result["feasibility_status"])
    print("Feasibility Score:", result["feasibility_score"])
    print("PASS")


# ================================================================
# TEST 2 — INVALID LAND
# ================================================================

def test_invalid_land():

    site = build_site(
        available_land=0.0,
    )

    result = evaluate_hard_constraints(
        site,
        recommended_capacity_mw=10.0,
    )

    assert result["feasibility_status"] == "NOT_FEASIBLE"

    print("TEST 2 — INVALID LAND")
    print("Status:", result["feasibility_status"])
    print("PASS")


# ================================================================
# TEST 3 — EXCESS LAND USAGE
# ================================================================

def test_excess_land_usage():

    site = build_site(
        available_land=5.0,
        used_land=6.0,
    )

    result = evaluate_hard_constraints(
        site,
        recommended_capacity_mw=10.0,
    )

    assert result["feasibility_status"] == "NOT_FEASIBLE"

    print("TEST 3 — EXCESS LAND USAGE")
    print("Status:", result["feasibility_status"])
    print("PASS")


# ================================================================
# TEST 4 — MISSING RESOURCE DATA
# ================================================================

def test_missing_resource_data():

    site = build_site(
        solar=None,
    )

    result = evaluate_hard_constraints(
        site,
        recommended_capacity_mw=10.0,
    )

    assert result["feasibility_status"] == "NOT_FEASIBLE"

    print("TEST 4 — MISSING RESOURCE DATA")
    print("Status:", result["feasibility_status"])
    print("PASS")


# ================================================================
# TEST 5 — CAPACITY VIOLATION
# ================================================================

def test_capacity_violation():

    site = build_site(
        available_land=2.0,
    )

    # Engineering assumption:
    # 2 km² × 5 MW/km² = 10 MW maximum capacity.

    result = evaluate_hard_constraints(
        site,
        recommended_capacity_mw=20.0,
    )

    assert result["feasibility_status"] == "NOT_FEASIBLE"

    print("TEST 5 — CAPACITY VIOLATION")
    print("Status:", result["feasibility_status"])
    print("PASS")


# ================================================================
# TEST 6 — UNACCEPTABLE TERRAIN
# ================================================================

def test_terrain_violation():

    site = build_site(
        slope=20.0,
    )

    result = evaluate_hard_constraints(
        site,
        recommended_capacity_mw=10.0,
    )

    assert result["feasibility_status"] == "NOT_FEASIBLE"

    print("TEST 6 — UNACCEPTABLE TERRAIN")
    print("Status:", result["feasibility_status"])
    print("PASS")


# ================================================================
# TEST 7 — RESTRICTED / PROTECTED LAND
# ================================================================

def test_restricted_land():

    site = build_site()

    # Explicitly mark the site as a protected zone.
    site["datasets"]["osm"] = {
        "protected_zone": True
    }

    result = evaluate_hard_constraints(
        site,
        recommended_capacity_mw=10.0,
    )

    assert result["feasibility_status"] == "NOT_FEASIBLE"

    print("TEST 7 — RESTRICTED LAND")
    print("Status:", result["feasibility_status"])
    print("PASS")


# ================================================================
# TEST 8 — SOFT CONSTRAINT SCORING
# ================================================================

def test_soft_constraints():

    # ------------------------------------------------------------
    # GOOD SITE
    # ------------------------------------------------------------

    good_site = build_site(
        category_scores={
            "renewable_resource": 95.0,
            "terrain": 95.0,
            "infrastructure": 95.0,
            "environmental": 95.0,
            "economic": 95.0,
        }
    )

    # ------------------------------------------------------------
    # POOR SITE
    # ------------------------------------------------------------

    poor_site = build_site(
        category_scores={
            "renewable_resource": 60.0,
            "terrain": 50.0,
            "infrastructure": 40.0,
            "environmental": 50.0,
            "economic": 50.0,
        }
    )

    good_result = evaluate_hard_constraints(
        good_site,
        recommended_capacity_mw=20.0,
    )

    poor_result = evaluate_hard_constraints(
        poor_site,
        recommended_capacity_mw=20.0,
    )

    # Both sites satisfy hard constraints.
    assert (
        good_result["feasibility_status"]
        == "FEASIBLE"
    )

    assert (
        poor_result["feasibility_status"]
        == "FEASIBLE"
    )

    # Good soft conditions must produce a higher score.
    assert (
        good_result["feasibility_score"]
        > poor_result["feasibility_score"]
    )

    print("TEST 8 — SOFT CONSTRAINT SCORING")
    print(
        "Good site score :",
        good_result["feasibility_score"],
    )
    print(
        "Poor site score :",
        poor_result["feasibility_score"],
    )
    print("PASS")


# ================================================================
# MAIN TEST RUNNER
# ================================================================

def main():

    print()
    print("======================================")
    print("TECHNICAL FEASIBILITY VALIDATION")
    print("======================================")
    print()

    test_valid_site()
    print()

    test_invalid_land()
    print()

    test_excess_land_usage()
    print()

    test_missing_resource_data()
    print()

    test_capacity_violation()
    print()

    test_terrain_violation()
    print()

    test_restricted_land()
    print()

    test_soft_constraints()
    print()

    print("======================================")
    print("ALL FEASIBILITY TESTS PASSED")
    print("======================================")


if __name__ == "__main__":
    main()