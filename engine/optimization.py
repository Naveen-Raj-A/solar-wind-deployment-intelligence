"""
Deployment Optimization Engine

Determines the most appropriate renewable deployment strategy
for an already evaluated site.

Supported strategies:
    - SOLAR
    - WIND
    - HYBRID

The module uses configurable planning heuristics. These defaults are
intended for software-level site planning and must be replaced with
project-specific engineering constraints when detailed feasibility
data is available.
"""

from __future__ import annotations

from typing import Any, Dict


# ------------------------------------------------------------------
# CONFIGURABLE OPTIMIZATION RULES
# ------------------------------------------------------------------

DEFAULT_CONFIG = {
    # Resource score is normalized to 0-100 before strategy selection.
    "strong_resource_threshold": 70.0,
    "minimum_resource_threshold": 40.0,
    "hybrid_resource_threshold": 65.0,
    "strategy_difference_margin": 10.0,

    # Planning capacity densities.
    # These are configurable software heuristics, not engineering limits.
    "solar_capacity_density_mw_per_km2": 4.0,
    "wind_capacity_density_mw_per_km2": 2.0,
    "hybrid_capacity_density_mw_per_km2": 3.0,

    # Resource multiplier: 50% at zero resource score,
    # 100% at a 100/100 resource score.
    "minimum_resource_capacity_factor": 0.50,

    # Fallback capacity when land area is unavailable.
    "default_max_capacity_mw": 50.0,

    # Expansion rules.
    "expandable_min_reserve_percent": 30.0,
    "limited_expansion_min_reserve_percent": 10.0,

    "expandable_min_infrastructure_score": 60.0,
    "limited_expansion_min_infrastructure_score": 40.0,

    "not_expandable_protected_area_percent": 70.0,
}


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def _merge_config(config: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Merge user configuration with default planning rules.
    """
    merged = DEFAULT_CONFIG.copy()

    if config:
        merged.update(config)

    return merged


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(float(value), maximum))


def _number(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_score(evaluated_site: Dict[str, Any], key: str) -> float:
    """
    Read a score from the evaluated site.

    Supports both:
        evaluated_site["solar_score"]
    and:
        evaluated_site["scores"]["solar_score"]
    """
    if key in evaluated_site:
        return _number(evaluated_site[key])

    scores = evaluated_site.get("scores", {})

    if key in scores:
        return _number(scores[key])

    return 0.0


def _get_category_score(
    evaluated_site: Dict[str, Any],
    category: str,
) -> float:
    """
    Read a category score from:
        category_scores
    or:
        scores.category_scores
    """
    category_scores = evaluated_site.get("category_scores", {})

    if category in category_scores:
        return _number(category_scores[category])

    scores = evaluated_site.get("scores", {})
    category_scores = scores.get("category_scores", {})

    if category in category_scores:
        return _number(category_scores[category])

    return 0.0


def _get_site_value(
    evaluated_site: Dict[str, Any],
    key: str,
    default: float = 0.0,
) -> float:
    """
    Read a site planning value from common locations.
    """

    if key in evaluated_site:
        return _number(evaluated_site[key], default)

    site_information = evaluated_site.get("site_information", {})

    if key in site_information:
        return _number(site_information[key], default)

    return default


# ------------------------------------------------------------------
# TASK 1 — DEPLOYMENT STRATEGY
# ------------------------------------------------------------------

def select_deployment_strategy(
    evaluated_site: Dict[str, Any],
    config: Dict[str, Any] | None = None,
) -> str:
    """
    Select SOLAR, WIND, or HYBRID deployment.

    Strategy logic:
        1. If both resources are strong, prefer HYBRID.
        2. If one resource clearly dominates, select that technology.
        3. If resources are reasonably balanced, select HYBRID.
        4. If neither resource is strong, select the better available
           resource so that the optimizer still produces a deployable
           strategy.

    Returns:
        "SOLAR"
        "WIND"
        "HYBRID"
    """

    cfg = _merge_config(config)

    solar_score = _get_score(evaluated_site, "solar_score")
    wind_score = _get_score(evaluated_site, "wind_score")

    solar_percent = _clamp((solar_score / 25.0) * 100.0)
    wind_percent = _clamp((wind_score / 25.0) * 100.0)

    strong = cfg["strong_resource_threshold"]
    hybrid_threshold = cfg["hybrid_resource_threshold"]
    minimum = cfg["minimum_resource_threshold"]
    margin = cfg["strategy_difference_margin"]

    # Both resources are strong enough for complementary generation.
    if (
        solar_percent >= hybrid_threshold
        and wind_percent >= hybrid_threshold
    ):
        return "HYBRID"

    # Clear solar dominance.
    if (
        solar_percent >= minimum
        and solar_percent >= wind_percent + margin
    ):
        return "SOLAR"

    # Clear wind dominance.
    if (
        wind_percent >= minimum
        and wind_percent >= solar_percent + margin
    ):
        return "WIND"

    # Balanced resources are a natural hybrid case.
    if (
        solar_percent >= minimum
        and wind_percent >= minimum
    ):
        return "HYBRID"

    # If only one resource is usable, choose it.
    if solar_percent >= strong and solar_percent > wind_percent:
        return "SOLAR"

    if wind_percent >= strong and wind_percent > solar_percent:
        return "WIND"

    # Last-resort selection for a low-resource evaluated site.
    return "SOLAR" if solar_percent >= wind_percent else "WIND"


# ------------------------------------------------------------------
# TASK 2 — CAPACITY PLANNING
# ------------------------------------------------------------------

def calculate_recommended_capacity(
    evaluated_site: Dict[str, Any],
    strategy: str,
    config: Dict[str, Any] | None = None,
) -> float:
    """
    Estimate recommended installation capacity in MW.

    Capacity is constrained by:
        - Available land area, when supplied.
        - Selected technology's configurable capacity density.
        - Resource availability.

    The result is a planning estimate, not a detailed electrical
    engineering design.
    """

    cfg = _merge_config(config)

    strategy = strategy.upper()

    density_map = {
        "SOLAR": cfg["solar_capacity_density_mw_per_km2"],
        "WIND": cfg["wind_capacity_density_mw_per_km2"],
        "HYBRID": cfg["hybrid_capacity_density_mw_per_km2"],
    }

    if strategy not in density_map:
        raise ValueError(
            "strategy must be SOLAR, WIND, or HYBRID"
        )

    density = _number(density_map[strategy], 0.0)

    solar_score = _clamp(
        (_get_score(evaluated_site, "solar_score") / 25.0) * 100.0
    )

    wind_score = _clamp(
        (_get_score(evaluated_site, "wind_score") / 25.0) * 100.0
    )

    if strategy == "SOLAR":
        resource_score = solar_score

    elif strategy == "WIND":
        resource_score = wind_score

    else:
        resource_score = (solar_score + wind_score) / 2.0

    resource_factor = (
        cfg["minimum_resource_capacity_factor"]
        + (resource_score / 100.0)
        * (1.0 - cfg["minimum_resource_capacity_factor"])
    )

    land_area = _get_site_value(
        evaluated_site,
        "land_area_km2",
        default=0.0,
    )

    if land_area > 0 and density > 0:
        land_limited_capacity = land_area * density
    else:
        land_limited_capacity = cfg["default_max_capacity_mw"]

    recommended_capacity = (
        land_limited_capacity * resource_factor
    )

    # Existing capacity can be supplied for expansion-aware planning.
    existing_capacity = _get_site_value(
        evaluated_site,
        "existing_capacity_mw",
        default=0.0,
    )

    if existing_capacity > 0:
        recommended_capacity = max(
            recommended_capacity,
            existing_capacity,
        )

    return round(
        max(0.0, recommended_capacity),
        2,
    )


# ------------------------------------------------------------------
# TASK 3 — EXPANSION FEASIBILITY
# ------------------------------------------------------------------

def analyze_expansion_feasibility(
    evaluated_site: Dict[str, Any],
    config: Dict[str, Any] | None = None,
) -> str:
    """
    Determine future expansion feasibility.

    Returns exactly one of:
        "Expandable"
        "Limited Expansion"
        "Not Expandable"

    Main constraints:
        - Land reserve percentage
        - Infrastructure suitability
        - Protected-area percentage
    """

    cfg = _merge_config(config)

    land_area = _get_site_value(
        evaluated_site,
        "land_area_km2",
        default=0.0,
    )

    used_land_area = _get_site_value(
        evaluated_site,
        "used_land_area_km2",
        default=0.0,
    )

    infrastructure_score = _get_category_score(
        evaluated_site,
        "infrastructure",
    )

    protected_area_percent = _get_site_value(
        evaluated_site,
        "protected_area_percent",
        default=0.0,
    )

    # If land area is not available, use the site-level expansion
    # reserve percentage if provided.
    reserve_percent = _get_site_value(
        evaluated_site,
        "land_reserve_percent",
        default=-1.0,
    )

    if reserve_percent < 0:
        if land_area > 0:
            used_land_area = _clamp(
                used_land_area,
                0.0,
                land_area,
            )
            reserve_percent = (
                max(0.0, land_area - used_land_area)
                / land_area
            ) * 100.0
        else:
            reserve_percent = 0.0

    # Protected land above the configured limit prevents expansion.
    if protected_area_percent >= cfg["not_expandable_protected_area_percent"]:
        return "Not Expandable"

    # Insufficient infrastructure is a hard constraint.
    if infrastructure_score < cfg["limited_expansion_min_infrastructure_score"]:
        return "Not Expandable"

    # Adequate land + infrastructure supports expansion.
    if (
        reserve_percent >= cfg["expandable_min_reserve_percent"]
        and infrastructure_score >= cfg["expandable_min_infrastructure_score"]
    ):
        return "Expandable"

    # Some reserve or adequate infrastructure remains, but not enough
    # for a full expansion classification.
    if (
        reserve_percent >= cfg["limited_expansion_min_reserve_percent"]
        or infrastructure_score >= cfg["expandable_min_infrastructure_score"]
    ):
        return "Limited Expansion"

    return "Not Expandable"


# ------------------------------------------------------------------
# TASK 4 — DEPLOYMENT PLAN
# ------------------------------------------------------------------

def generate_deployment_plan(
    evaluated_site: Dict[str, Any],
    strategy: str,
    capacity_mw: float,
    expansion_status: str,
) -> Dict[str, Any]:
    """
    Generate the final deployment plan.
    """

    solar_score = _clamp(
        (_get_score(evaluated_site, "solar_score") / 25.0) * 100.0
    )

    wind_score = _clamp(
        (_get_score(evaluated_site, "wind_score") / 25.0) * 100.0
    )

    infrastructure_score = _get_category_score(
        evaluated_site,
        "infrastructure",
    )

    terrain_score = _get_category_score(
        evaluated_site,
        "terrain",
    )

    overall_score = _number(
        evaluated_site.get(
            "normalized_score",
            evaluated_site.get("overall_score", 0.0),
        )
    )

    if strategy == "SOLAR":
        remarks = (
            f"Solar resource is the dominant renewable resource "
            f"({solar_score:.1f}/100). "
            f"Recommended capacity is constrained by available land "
            f"and solar resource quality."
        )

    elif strategy == "WIND":
        remarks = (
            f"Wind resource is the dominant renewable resource "
            f"({wind_score:.1f}/100). "
            f"Recommended capacity is constrained by available land "
            f"and wind resource quality."
        )

    else:
        remarks = (
            f"Solar and wind resources are sufficiently complementary "
            f"({solar_score:.1f}/100 solar, {wind_score:.1f}/100 wind), "
            f"supporting a hybrid deployment strategy."
        )

    remarks += (
        f" Overall suitability is {overall_score:.1f}/100; "
        f"terrain suitability is {terrain_score:.1f}/100 and "
        f"infrastructure suitability is {infrastructure_score:.1f}/100. "
        f"Expansion assessment: {expansion_status}."
    )

    return {
        "recommended_technology": strategy,
        "recommended_capacity_mw": round(capacity_mw, 2),
        "expansion_status": expansion_status,
        "optimization_remarks": remarks,
    }


# ------------------------------------------------------------------
# COMPLETE OPTIMIZATION PIPELINE
# ------------------------------------------------------------------

def optimize_site(
    evaluated_site: Dict[str, Any],
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Run the complete deployment optimization pipeline.

    Returns:
        Deployment plan containing:
            recommended_technology
            recommended_capacity_mw
            expansion_status
            optimization_remarks
    """

    strategy = select_deployment_strategy(
        evaluated_site,
        config=config,
    )

    capacity = calculate_recommended_capacity(
        evaluated_site,
        strategy,
        config=config,
    )

    expansion_status = analyze_expansion_feasibility(
        evaluated_site,
        config=config,
    )

    plan = generate_deployment_plan(
        evaluated_site,
        strategy,
        capacity,
        expansion_status,
    )

    return plan