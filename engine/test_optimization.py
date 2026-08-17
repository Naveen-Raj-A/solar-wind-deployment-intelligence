"""
Deployment Optimization Engine Validation

Validates Tasks 1-5:

1. Solar deployment selection.
2. Wind deployment selection.
3. Hybrid deployment selection.
4. Capacity planning responds to site characteristics.
5. Expansion feasibility returns all required states.
6. Deployment plan contains the required output fields.
7. Different site characteristics produce different plans.
"""

from engine.optimization import (
    select_deployment_strategy,
    calculate_recommended_capacity,
    analyze_expansion_feasibility,
    generate_deployment_plan,
    optimize_site,
)


def build_site(
    solar_score,
    wind_score,
    land_area_km2,
    used_land_area_km2,
    infrastructure_score,
    protected_area_percent=0.0,
    normalized_score=80.0,
):
    return {
        "solar_score": solar_score,
        "wind_score": wind_score,

        "category_scores": {
            "infrastructure": infrastructure_score,
            "terrain": 80.0,
            "environmental": 75.0,
            "economic": 100.0,
            "renewable_resource": (
                (solar_score + wind_score) / 50.0
            ) * 100.0,
        },

        "land_area_km2": land_area_km2,
        "used_land_area_km2": used_land_area_km2,
        "protected_area_percent": protected_area_percent,
        "normalized_score": normalized_score,
    }


# --------------------------------------------------------------
# TEST 1 — SOLAR DEPLOYMENT
# --------------------------------------------------------------

def test_solar_deployment():

    site = build_site(
        solar_score=25,
        wind_score=7.5,
        land_area_km2=10,
        used_land_area_km2=3,
        infrastructure_score=80,
    )

    strategy = select_deployment_strategy(site)

    print("\nTEST 1 — SOLAR DEPLOYMENT")
    print(f"Recommended technology : {strategy}")

    assert strategy == "SOLAR"

    print("PASS")


# --------------------------------------------------------------
# TEST 2 — WIND DEPLOYMENT
# --------------------------------------------------------------

def test_wind_deployment():

    site = build_site(
        solar_score=7.5,
        wind_score=25,
        land_area_km2=10,
        used_land_area_km2=3,
        infrastructure_score=80,
    )

    strategy = select_deployment_strategy(site)

    print("\nTEST 2 — WIND DEPLOYMENT")
    print(f"Recommended technology : {strategy}")

    assert strategy == "WIND"

    print("PASS")


# --------------------------------------------------------------
# TEST 3 — HYBRID DEPLOYMENT
# --------------------------------------------------------------

def test_hybrid_deployment():

    site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=10,
        used_land_area_km2=3,
        infrastructure_score=80,
    )

    strategy = select_deployment_strategy(site)

    print("\nTEST 3 — HYBRID DEPLOYMENT")
    print(f"Recommended technology : {strategy}")

    assert strategy == "HYBRID"

    print("PASS")


# --------------------------------------------------------------
# TEST 4 — CAPACITY PLANNING
# --------------------------------------------------------------

def test_capacity_planning():

    small_site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=5,
        used_land_area_km2=2,
        infrastructure_score=80,
    )

    large_site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=20,
        used_land_area_km2=5,
        infrastructure_score=80,
    )

    small_capacity = calculate_recommended_capacity(
        small_site,
        "HYBRID",
    )

    large_capacity = calculate_recommended_capacity(
        large_site,
        "HYBRID",
    )

    print("\nTEST 4 — CAPACITY PLANNING")
    print(f"Small-site capacity : {small_capacity:.2f} MW")
    print(f"Large-site capacity : {large_capacity:.2f} MW")

    assert large_capacity > small_capacity

    print("PASS")


# --------------------------------------------------------------
# TEST 5 — EXPANSION FEASIBILITY
# --------------------------------------------------------------

def test_expansion_feasibility():

    expandable_site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=20,
        used_land_area_km2=5,
        infrastructure_score=80,
    )

    limited_site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=20,
        used_land_area_km2=18,
        infrastructure_score=60,
    )

    not_expandable_site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=20,
        used_land_area_km2=19,
        infrastructure_score=30,
    )

    expandable = analyze_expansion_feasibility(
        expandable_site
    )

    limited = analyze_expansion_feasibility(
        limited_site
    )

    not_expandable = analyze_expansion_feasibility(
        not_expandable_site
    )

    print("\nTEST 5 — EXPANSION FEASIBILITY")
    print(f"Expandable site       : {expandable}")
    print(f"Limited site          : {limited}")
    print(f"Not expandable site   : {not_expandable}")

    assert expandable == "Expandable"
    assert limited == "Limited Expansion"
    assert not_expandable == "Not Expandable"

    print("PASS")


# --------------------------------------------------------------
# TEST 6 — DEPLOYMENT PLAN OUTPUT
# --------------------------------------------------------------

def test_deployment_plan_output():

    site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=10,
        used_land_area_km2=3,
        infrastructure_score=80,
        normalized_score=92.5,
    )

    plan = optimize_site(site)

    print("\nTEST 6 — DEPLOYMENT PLAN")

    print(
        f"Recommended Technology : "
        f"{plan['recommended_technology']}"
    )

    print(
        f"Recommended Capacity   : "
        f"{plan['recommended_capacity_mw']:.2f} MW"
    )

    print(
        f"Expansion Status       : "
        f"{plan['expansion_status']}"
    )

    print(
        f"Optimization Remarks   : "
        f"{plan['optimization_remarks']}"
    )

    assert "recommended_technology" in plan
    assert "recommended_capacity_mw" in plan
    assert "expansion_status" in plan
    assert "optimization_remarks" in plan

    assert plan["recommended_technology"] in {
        "SOLAR",
        "WIND",
        "HYBRID",
    }

    assert plan["recommended_capacity_mw"] > 0

    assert plan["expansion_status"] in {
        "Expandable",
        "Limited Expansion",
        "Not Expandable",
    }

    print("PASS")


# --------------------------------------------------------------
# TEST 7 — DIFFERENT SITES PRODUCE DIFFERENT PLANS
# --------------------------------------------------------------

def test_different_sites_produce_different_plans():

    solar_site = build_site(
        solar_score=25,
        wind_score=7.5,
        land_area_km2=10,
        used_land_area_km2=3,
        infrastructure_score=80,
    )

    wind_site = build_site(
        solar_score=7.5,
        wind_score=25,
        land_area_km2=10,
        used_land_area_km2=3,
        infrastructure_score=80,
    )

    hybrid_site = build_site(
        solar_score=25,
        wind_score=25,
        land_area_km2=10,
        used_land_area_km2=3,
        infrastructure_score=80,
    )

    solar_plan = optimize_site(solar_site)
    wind_plan = optimize_site(wind_site)
    hybrid_plan = optimize_site(hybrid_site)

    print("\nTEST 7 — DIFFERENT SITE CHARACTERISTICS")

    print(
        f"Solar site  -> "
        f"{solar_plan['recommended_technology']}, "
        f"{solar_plan['recommended_capacity_mw']:.2f} MW"
    )

    print(
        f"Wind site   -> "
        f"{wind_plan['recommended_technology']}, "
        f"{wind_plan['recommended_capacity_mw']:.2f} MW"
    )

    print(
        f"Hybrid site -> "
        f"{hybrid_plan['recommended_technology']}, "
        f"{hybrid_plan['recommended_capacity_mw']:.2f} MW"
    )

    assert solar_plan["recommended_technology"] == "SOLAR"
    assert wind_plan["recommended_technology"] == "WIND"
    assert hybrid_plan["recommended_technology"] == "HYBRID"

    assert len({
        solar_plan["recommended_technology"],
        wind_plan["recommended_technology"],
        hybrid_plan["recommended_technology"],
    }) == 3

    print("PASS")


# --------------------------------------------------------------
# RUN ALL TESTS
# --------------------------------------------------------------

def main():

    print()
    print("======================================")
    print("DEPLOYMENT OPTIMIZATION VALIDATION")
    print("======================================")

    test_solar_deployment()
    test_wind_deployment()
    test_hybrid_deployment()
    test_capacity_planning()
    test_expansion_feasibility()
    test_deployment_plan_output()
    test_different_sites_produce_different_plans()

    print()
    print("======================================")
    print("ALL OPTIMIZATION TESTS PASSED")
    print("======================================")


if __name__ == "__main__":
    main()