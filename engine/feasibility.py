"""
Technical Feasibility Engine

Hard constraints:
    - Site coordinates
    - Land availability
    - Restricted/protected land
    - Terrain suitability
    - Required resource data
    - Recommended capacity

Soft constraints:
    - Renewable resource quality
    - Terrain quality
    - Infrastructure accessibility
    - Environmental availability
    - Economic suitability

Hard constraint failure blocks deployment.
Soft constraints influence the feasibility score.
"""

from __future__ import annotations

from typing import Any


# ================================================================
# CONFIGURATION
# ================================================================

MIN_REMAINING_LAND_KM2 = 0.01

# Engineering assumption used by the feasibility gate.
MAX_CAPACITY_PER_KM2_MW = 5.0

# Maximum acceptable average slope for deployment.
# This is a configurable project assumption.
MAX_ACCEPTABLE_SLOPE_DEGREES = 15.0


# ================================================================
# GENERIC CONSTRAINT HELPER
# ================================================================

def _constraint(
    name: str,
    status: str,
    message: str,
) -> dict[str, str]:

    return {
        "name": name,
        "status": status,
        "message": message,
    }


# ================================================================
# SITE COORDINATES
# ================================================================

def check_site_inputs(
    latitude: float | None,
    longitude: float | None,
) -> dict[str, str]:

    if latitude is None or longitude is None:
        return _constraint(
            "site_coordinates",
            "FAIL",
            "Latitude and longitude are required.",
        )

    if not -90 <= latitude <= 90:
        return _constraint(
            "site_coordinates",
            "FAIL",
            "Latitude must be between -90 and 90 degrees.",
        )

    if not -180 <= longitude <= 180:
        return _constraint(
            "site_coordinates",
            "FAIL",
            "Longitude must be between -180 and 180 degrees.",
        )

    return _constraint(
        "site_coordinates",
        "PASS",
        "Site coordinates are valid.",
    )


# ================================================================
# LAND AVAILABILITY
# ================================================================

def check_land_constraint(
    available_land_area_km2: float,
    used_land_area_km2: float,
) -> dict[str, Any]:

    if available_land_area_km2 <= 0:
        return _constraint(
            "land_availability",
            "FAIL",
            "Available land area must be greater than 0 km².",
        )

    if used_land_area_km2 < 0:
        return _constraint(
            "land_usage",
            "FAIL",
            "Used land area cannot be negative.",
        )

    if used_land_area_km2 > available_land_area_km2:
        return _constraint(
            "land_usage",
            "FAIL",
            "Used land area exceeds available land area.",
        )

    remaining_land = (
        available_land_area_km2
        - used_land_area_km2
    )

    if remaining_land < MIN_REMAINING_LAND_KM2:
        return _constraint(
            "land_availability",
            "FAIL",
            (
                f"Remaining land area is only "
                f"{remaining_land:.3f} km²."
            ),
        )

    return _constraint(
        "land_availability",
        "PASS",
        (
            f"{remaining_land:.3f} km² of land is available "
            "for deployment."
        ),
    )


# ================================================================
# RESTRICTED / PROTECTED LAND
# ================================================================

def check_restricted_land(
    evaluated_site: dict[str, Any],
) -> dict[str, str]:

    datasets = evaluated_site.get("datasets", {})

    # Look for explicit restricted/protected indicators.
    possible_values = []

    for container in (
        evaluated_site,
        datasets,
        datasets.get("osm", {}),
        datasets.get("sentinel", {}),
        datasets.get("land_use", {}),
    ):
        if not isinstance(container, dict):
            continue

        for key in (
            "restricted_land",
            "protected_land",
            "protected_zone",
            "is_protected",
            "is_restricted",
        ):
            if key in container:
                possible_values.append(container[key])

    # Only reject when the data explicitly says the site is restricted.
    for value in possible_values:
        if value is True:
            return _constraint(
                "restricted_land",
                "FAIL",
                "Site is located in restricted or protected land.",
            )

        if isinstance(value, str):
            if value.strip().lower() in {
                "true",
                "yes",
                "restricted",
                "protected",
            }:
                return _constraint(
                    "restricted_land",
                    "FAIL",
                    "Site is located in restricted or protected land.",
                )

    return _constraint(
        "restricted_land",
        "PASS",
        "No explicit restricted/protected land condition was detected.",
    )


# ================================================================
# TERRAIN HARD CONSTRAINT
# ================================================================

def check_terrain_constraint(
    evaluated_site: dict[str, Any],
) -> dict[str, Any]:

    datasets = evaluated_site.get("datasets", {})

    terrain = (
        datasets.get("srtm")
        or datasets.get("terrain")
        or {}
    )

    if not isinstance(terrain, dict):
        return _constraint(
            "terrain_suitability",
            "PASS",
            "Terrain data is not available for a hard rejection.",
        )

    slope_statistics = terrain.get(
        "slope_statistics",
        {},
    )

    if not isinstance(slope_statistics, dict):
        return _constraint(
            "terrain_suitability",
            "PASS",
            "Terrain slope data is unavailable.",
        )

    slope = slope_statistics.get("mean_degrees")

    if slope is None:
        return _constraint(
            "terrain_suitability",
            "PASS",
            "Mean terrain slope is unavailable.",
        )

    try:
        slope = float(slope)
    except (TypeError, ValueError):
        return _constraint(
            "terrain_suitability",
            "FAIL",
            "Terrain slope value is invalid.",
        )

    if slope > MAX_ACCEPTABLE_SLOPE_DEGREES:
        return _constraint(
            "terrain_suitability",
            "FAIL",
            (
                f"Mean terrain slope of {slope:.2f}° exceeds "
                f"the maximum acceptable limit of "
                f"{MAX_ACCEPTABLE_SLOPE_DEGREES:.2f}°."
            ),
        )

    return _constraint(
        "terrain_suitability",
        "PASS",
        (
            f"Mean terrain slope of {slope:.2f}° is within "
            f"the acceptable limit of "
            f"{MAX_ACCEPTABLE_SLOPE_DEGREES:.2f}°."
        ),
    )


# ================================================================
# RESOURCE DATA
# ================================================================

def check_resource_data(
    evaluated_site: dict[str, Any],
) -> dict[str, str]:

    datasets = evaluated_site.get("datasets", {})

    nasa = datasets.get("nasa_power", {})
    wind = datasets.get("wind", {})

    solar = nasa.get("solar_resource", {})
    wind_stats = wind.get("wind_speed_statistics", {})

    solar_value = solar.get(
        "solar_radiation_kwh_m2_day"
    )

    wind_value = wind_stats.get("mean_ms")

    if solar_value is None:
        return _constraint(
            "solar_resource_data",
            "FAIL",
            "Solar resource data is unavailable.",
        )

    if wind_value is None:
        return _constraint(
            "wind_resource_data",
            "FAIL",
            "Wind resource data is unavailable.",
        )

    return _constraint(
        "resource_data",
        "PASS",
        "Required solar and wind resource data is available.",
    )


# ================================================================
# CAPACITY CONSTRAINT
# ================================================================

def check_capacity_constraint(
    available_land_area_km2: float,
    recommended_capacity_mw: float | None,
) -> dict[str, Any]:

    if recommended_capacity_mw is None:
        return _constraint(
            "capacity_limit",
            "FAIL",
            "Recommended deployment capacity is unavailable.",
        )

    if recommended_capacity_mw < 0:
        return _constraint(
            "capacity_limit",
            "FAIL",
            "Recommended capacity cannot be negative.",
        )

    maximum_capacity = (
        available_land_area_km2
        * MAX_CAPACITY_PER_KM2_MW
    )

    if recommended_capacity_mw > maximum_capacity:
        return _constraint(
            "capacity_limit",
            "FAIL",
            (
                f"Recommended capacity "
                f"{recommended_capacity_mw:.2f} MW exceeds "
                f"the estimated site limit of "
                f"{maximum_capacity:.2f} MW."
            ),
        )

    return _constraint(
        "capacity_limit",
        "PASS",
        (
            f"Recommended capacity "
            f"{recommended_capacity_mw:.2f} MW is within "
            f"the estimated site limit of "
            f"{maximum_capacity:.2f} MW."
        ),
    )


# ================================================================
# SOFT CONSTRAINT SCORING
# ================================================================

def calculate_soft_feasibility_score(
    evaluated_site: dict[str, Any],
) -> dict[str, Any]:

    category_scores = evaluated_site.get(
        "category_scores",
        {},
    )

    # Use the existing scoring engine categories.
    renewable = float(
        category_scores.get(
            "renewable_resource",
            0.0,
        )
    )

    terrain = float(
        category_scores.get(
            "terrain",
            0.0,
        )
    )

    infrastructure = float(
        category_scores.get(
            "infrastructure",
            0.0,
        )
    )

    environmental = float(
        category_scores.get(
            "environmental",
            0.0,
        )
    )

    economic = float(
        category_scores.get(
            "economic",
            0.0,
        )
    )

    # Soft feasibility weights.
    weights = {
        "renewable_resource": 0.30,
        "terrain": 0.20,
        "infrastructure": 0.20,
        "environmental": 0.15,
        "economic": 0.15,
    }

    score = (
        renewable * weights["renewable_resource"]
        + terrain * weights["terrain"]
        + infrastructure * weights["infrastructure"]
        + environmental * weights["environmental"]
        + economic * weights["economic"]
    )

    score = round(
        max(0.0, min(100.0, score)),
        2,
    )

    soft_constraints = [
        {
            "name": "renewable_resource",
            "score": round(renewable, 2),
            "weight": 30,
        },
        {
            "name": "terrain",
            "score": round(terrain, 2),
            "weight": 20,
        },
        {
            "name": "infrastructure",
            "score": round(infrastructure, 2),
            "weight": 20,
        },
        {
            "name": "environmental",
            "score": round(environmental, 2),
            "weight": 15,
        },
        {
            "name": "economic",
            "score": round(economic, 2),
            "weight": 15,
        },
    ]

    return {
        "feasibility_score": score,
        "soft_constraints": soft_constraints,
        "soft_constraint_weights": weights,
    }


# ================================================================
# MAIN FEASIBILITY ENGINE
# ================================================================

def evaluate_hard_constraints(
    evaluated_site: dict[str, Any],
    recommended_capacity_mw: float | None = None,
) -> dict[str, Any]:

    site = evaluated_site.get(
        "site_information",
        {},
    )

    latitude = site.get("latitude")
    longitude = site.get("longitude")

    available_land = site.get(
        "available_land_area_km2"
    )

    used_land = site.get(
        "used_land_area_km2",
        0.0,
    )

    constraints: list[dict[str, str]] = []

    # ------------------------------------------------------------
    # HARD CONSTRAINT 1 — COORDINATES
    # ------------------------------------------------------------

    constraints.append(
        check_site_inputs(
            latitude,
            longitude,
        )
    )

    # ------------------------------------------------------------
    # HARD CONSTRAINT 2 — LAND
    # ------------------------------------------------------------

    if available_land is None:
        constraints.append(
            _constraint(
                "land_availability",
                "FAIL",
                "Available land area is missing.",
            )
        )
    else:
        constraints.append(
            check_land_constraint(
                float(available_land),
                float(used_land),
            )
        )

    # ------------------------------------------------------------
    # HARD CONSTRAINT 3 — RESTRICTED LAND
    # ------------------------------------------------------------

    constraints.append(
        check_restricted_land(
            evaluated_site
        )
    )

    # ------------------------------------------------------------
    # HARD CONSTRAINT 4 — TERRAIN
    # ------------------------------------------------------------

    constraints.append(
        check_terrain_constraint(
            evaluated_site
        )
    )

    # ------------------------------------------------------------
    # HARD CONSTRAINT 5 — RESOURCE DATA
    # ------------------------------------------------------------

    constraints.append(
        check_resource_data(
            evaluated_site
        )
    )

    # ------------------------------------------------------------
    # HARD CONSTRAINT 6 — CAPACITY
    # ------------------------------------------------------------

    if (
        available_land is not None
        and recommended_capacity_mw is not None
    ):
        constraints.append(
            check_capacity_constraint(
                float(available_land),
                recommended_capacity_mw,
            )
        )

    # ------------------------------------------------------------
    # PASS / FAIL
    # ------------------------------------------------------------

    failed_constraints = [
        item
        for item in constraints
        if item["status"] == "FAIL"
    ]

    passed_constraints = [
        item
        for item in constraints
        if item["status"] == "PASS"
    ]

    feasible = len(failed_constraints) == 0

    # ------------------------------------------------------------
    # SOFT FEASIBILITY
    # ------------------------------------------------------------

    soft_result = calculate_soft_feasibility_score(
        evaluated_site
    )

    # ------------------------------------------------------------
    # CONSTRAINT SUMMARY
    # ------------------------------------------------------------

    if not feasible:
        constraint_summary = (
            f"Site is NOT technically feasible. "
            f"{len(failed_constraints)} hard constraint(s) failed."
        )
    elif soft_result["feasibility_score"] >= 80:
        constraint_summary = (
            "Site satisfies all hard constraints and "
            "has high soft-constraint feasibility."
        )
    elif soft_result["feasibility_score"] >= 60:
        constraint_summary = (
            "Site satisfies all hard constraints and "
            "has moderate soft-constraint feasibility."
        )
    else:
        constraint_summary = (
            "Site satisfies all hard constraints but "
            "has low soft-constraint feasibility."
        )

    return {
        "feasibility_status": (
            "FEASIBLE"
            if feasible
            else "NOT_FEASIBLE"
        ),

        "feasibility_score": (
            soft_result["feasibility_score"]
            if feasible
            else 0.0
        ),

        "hard_constraints_passed": len(
            passed_constraints
        ),

        "hard_constraints_failed": len(
            failed_constraints
        ),

        "hard_constraints": constraints,

        "failed_constraints": failed_constraints,

        "passed_constraints": passed_constraints,

        "soft_constraints": soft_result[
            "soft_constraints"
        ],

        "soft_constraint_weights": soft_result[
            "soft_constraint_weights"
        ],

        "constraint_summary": constraint_summary,
    }


# ================================================================
# SIMPLE FEASIBILITY GATE
# ================================================================

def is_site_feasible(
    evaluated_site: dict[str, Any],
    recommended_capacity_mw: float | None = None,
) -> bool:

    result = evaluate_hard_constraints(
        evaluated_site,
        recommended_capacity_mw,
    )

    return (
        result["feasibility_status"]
        == "FEASIBLE"
    )