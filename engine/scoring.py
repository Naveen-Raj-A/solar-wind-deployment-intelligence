"""
Scoring Engine

Generates renewable energy deployment suitability scores.
"""

from __future__ import annotations
from engine import sentinel
from engine.scoring_rules import (
    SOLAR_WEIGHT,
    WIND_WEIGHT,
    TERRAIN_WEIGHT,
    SENTINEL_WEIGHT,
    OSM_WEIGHT,
    TOTAL_CURRENT_WEIGHT,

    SOLAR_THRESHOLDS,
    WIND_THRESHOLDS,
    TERRAIN_THRESHOLDS,

    SENTINEL_NDVI_THRESHOLDS,
    SENTINEL_NDMI_THRESHOLDS,
    VALID_PIXEL_THRESHOLDS,

    ROAD_DISTANCE_THRESHOLDS,
    POWER_DISTANCE_THRESHOLDS,
    SUBSTATION_DISTANCE_THRESHOLDS,
    BUILDING_COUNT_THRESHOLDS,

    RECOMMENDATION_THRESHOLDS,
)


# ------------------------------------------------------------------
# SOLAR SCORING
# ------------------------------------------------------------------

def calculate_solar_score(solar_radiation: float) -> float:
    """
    Calculate solar suitability score.

    Parameters
    ----------
    solar_radiation : float
        Solar radiation in kWh/m²/day.

    Returns
    -------
    float
        Solar score.
    """

    if solar_radiation >= SOLAR_THRESHOLDS["EXCELLENT"]:
        return round(SOLAR_WEIGHT, 2)

    if solar_radiation >= SOLAR_THRESHOLDS["GOOD"]:
        return round(SOLAR_WEIGHT * 0.90, 2)

    if solar_radiation >= SOLAR_THRESHOLDS["MODERATE"]:
        return round(SOLAR_WEIGHT * 0.70, 2)

    return round(SOLAR_WEIGHT * 0.30, 2)


# ------------------------------------------------------------------
# WIND SCORING
# ------------------------------------------------------------------

def calculate_wind_score(mean_wind_speed: float) -> float:
    """
    Calculate wind suitability score.

    Parameters
    ----------
    mean_wind_speed : float
        Mean wind speed in m/s.

    Returns
    -------
    float
        Wind score.
    """

    if mean_wind_speed >= WIND_THRESHOLDS["EXCELLENT"]:
        return round(WIND_WEIGHT, 2)

    if mean_wind_speed >= WIND_THRESHOLDS["GOOD"]:
        return round(WIND_WEIGHT * 0.90, 2)

    if mean_wind_speed >= WIND_THRESHOLDS["MODERATE"]:
        return round(WIND_WEIGHT * 0.70, 2)

    return round(WIND_WEIGHT * 0.30, 2)


# ------------------------------------------------------------------
# TERRAIN SCORING
# ------------------------------------------------------------------

def calculate_terrain_score(mean_slope: float) -> float:
    """
    Calculate terrain suitability score.

    Parameters
    ----------
    mean_slope : float
        Mean terrain slope in degrees.

    Returns
    -------
    float
        Terrain suitability score.
    """

    if mean_slope < TERRAIN_THRESHOLDS["EXCELLENT"]:
        return round(TERRAIN_WEIGHT, 2)

    if mean_slope < TERRAIN_THRESHOLDS["GOOD"]:
        return round(TERRAIN_WEIGHT * 0.90, 2)

    if mean_slope < TERRAIN_THRESHOLDS["MODERATE"]:
        return round(TERRAIN_WEIGHT * 0.70, 2)

    return round(TERRAIN_WEIGHT * 0.20, 2)


# ------------------------------------------------------------------
# SENTINEL SCORING
# ------------------------------------------------------------------

def calculate_sentinel_score(
    ndvi_mean: float,
    ndmi_mean: float,
    valid_pixel_percentage: float,
) -> float:
    """
    Calculate Sentinel suitability score.

    Parameters
    ----------
    ndvi_mean : float
        Mean NDVI.

    ndmi_mean : float
        Mean NDMI.

    valid_pixel_percentage : float
        Percentage of valid pixels.

    Returns
    -------
    float
        Sentinel suitability score.
    """

    score = 0.0

    # -----------------------------
    # NDVI (40%)
    # -----------------------------

    ndvi_weight = SENTINEL_WEIGHT * 0.40

    if ndvi_mean <= SENTINEL_NDVI_THRESHOLDS["EXCELLENT"]:
        score += ndvi_weight

    elif ndvi_mean <= SENTINEL_NDVI_THRESHOLDS["GOOD"]:
        score += ndvi_weight * 0.90

    elif ndvi_mean <= SENTINEL_NDVI_THRESHOLDS["MODERATE"]:
        score += ndvi_weight * 0.70

    else:
        score += ndvi_weight * 0.30

    # -----------------------------
    # NDMI (30%)
    # -----------------------------

    ndmi_weight = SENTINEL_WEIGHT * 0.30

    if ndmi_mean <= SENTINEL_NDMI_THRESHOLDS["EXCELLENT"]:
        score += ndmi_weight

    elif ndmi_mean <= SENTINEL_NDMI_THRESHOLDS["GOOD"]:
        score += ndmi_weight * 0.90

    elif ndmi_mean <= SENTINEL_NDMI_THRESHOLDS["MODERATE"]:
        score += ndmi_weight * 0.70

    else:
        score += ndmi_weight * 0.30

    # -----------------------------
    # Valid Pixels (30%)
    # -----------------------------

    valid_weight = SENTINEL_WEIGHT * 0.30

    if valid_pixel_percentage >= VALID_PIXEL_THRESHOLDS["EXCELLENT"]:
        score += valid_weight

    elif valid_pixel_percentage >= VALID_PIXEL_THRESHOLDS["GOOD"]:
        score += valid_weight * 0.90

    elif valid_pixel_percentage >= VALID_PIXEL_THRESHOLDS["MODERATE"]:
        score += valid_weight * 0.70

    else:
        score += valid_weight * 0.30

    return round(score, 2)


# ------------------------------------------------------------------
# OPENSTREETMAP SCORING
# ------------------------------------------------------------------

def calculate_osm_score(
    road_distance: float,
    power_distance: float,
    substation_distance: float,
    building_count: int,
) -> float:
    score = 0.0

    # ----------------------------------------------------------
    # Road Accessibility (5)
    # ----------------------------------------------------------

    road_weight = 5

    if road_distance is not None:

        if road_distance <= ROAD_DISTANCE_THRESHOLDS["EXCELLENT"]:
            score += road_weight

        elif road_distance <= ROAD_DISTANCE_THRESHOLDS["GOOD"]:
            score += road_weight * 0.80

        elif road_distance <= ROAD_DISTANCE_THRESHOLDS["MODERATE"]:
            score += road_weight * 0.60

        elif road_distance <= ROAD_DISTANCE_THRESHOLDS["POOR"]:
            score += road_weight * 0.40

    # ----------------------------------------------------------
    # Power Infrastructure (4)
    # ----------------------------------------------------------

    power_weight = 4

    if power_distance is not None:

        if power_distance <= POWER_DISTANCE_THRESHOLDS["EXCELLENT"]:
            score += power_weight

        elif power_distance <= POWER_DISTANCE_THRESHOLDS["GOOD"]:
            score += power_weight * 0.75

        elif power_distance <= POWER_DISTANCE_THRESHOLDS["MODERATE"]:
            score += power_weight * 0.50

        elif power_distance <= POWER_DISTANCE_THRESHOLDS["POOR"]:
            score += power_weight * 0.25

    # ----------------------------------------------------------
    # Substation (4)
    # ----------------------------------------------------------

    substation_weight = 4

    if substation_distance is not None:

        if substation_distance <= SUBSTATION_DISTANCE_THRESHOLDS["EXCELLENT"]:
            score += substation_weight

        elif substation_distance <= SUBSTATION_DISTANCE_THRESHOLDS["GOOD"]:
            score += substation_weight * 0.75

        elif substation_distance <= SUBSTATION_DISTANCE_THRESHOLDS["MODERATE"]:
            score += substation_weight * 0.50

        elif substation_distance <= SUBSTATION_DISTANCE_THRESHOLDS["POOR"]:
            score += substation_weight * 0.25

    # ----------------------------------------------------------
    # Building Density (2)
    # ----------------------------------------------------------

    building_weight = 2

    if building_count < BUILDING_COUNT_THRESHOLDS["LOW"]:
        score += building_weight

    elif building_count < BUILDING_COUNT_THRESHOLDS["MODERATE"]:
        score += building_weight * 0.50

    return round(score, 2)


# ------------------------------------------------------------------
# CATEGORY-WISE SCORING
# ------------------------------------------------------------------


def calculate_renewable_resource_category_score(
    solar_score: float,
    wind_score: float,
) -> float:
    """
    Calculate Renewable Resource Score.

    Solar and wind are equally weighted.

    Input:
        solar_score: score from 0-25
        wind_score: score from 0-25

    Output:
        category score from 0-100
    """

    renewable_weight = SOLAR_WEIGHT + WIND_WEIGHT

    if renewable_weight <= 0:
        return 0.0

    score = (
        solar_score + wind_score
    ) / renewable_weight * 100

    return round(score, 2)


def calculate_elevation_suitability_score(elevation_m: float | None) -> float:
    """Convert the real DEM elevation into a 0-100 suitability score.

    The elevation value itself comes from the live Open-Meteo/Copernicus
    DEM response. These thresholds are configurable engineering rules,
    not invented site values.
    """
    if elevation_m is None:
        return 0.0
    elevation_m = float(elevation_m)
    if elevation_m <= 500:
        return 100.0
    if elevation_m <= 1000:
        return 90.0
    if elevation_m <= 1500:
        return 75.0
    if elevation_m <= 2000:
        return 55.0
    if elevation_m <= 2500:
        return 35.0
    return 15.0


def calculate_terrain_category_score(
    terrain_score: float,
    elevation_score: float | None = None,
) -> float:
    """Calculate terrain suitability from real slope + DEM elevation.

    Terrain composition:
        70% slope
        30% elevation

    ``None`` preserves backward compatibility for unit tests; the live
    pipeline always supplies the DEM-derived elevation score.
    """
    if elevation_score is None:
        elevation_score = 100.0

    terrain_score_normalized = (
        terrain_score / TERRAIN_WEIGHT
    ) * 100

    score = (
        terrain_score_normalized * 0.70
        + elevation_score * 0.30
    )

    return round(
        max(0.0, min(score, 100.0)),
        2,
    )


def calculate_infrastructure_category_score(
    osm_score: float,
) -> float:
    """
    Calculate Infrastructure Category Score.

    The current OSM score contains:
        Road accessibility
        Power infrastructure
        Substation accessibility
        Building density

    OSM currently has a maximum weight of 15.
    """

    if OSM_WEIGHT <= 0:
        return 0.0

    score = (
        osm_score / OSM_WEIGHT
    ) * 100

    return round(
        max(0.0, min(score, 100.0)),
        2,
    )


def calculate_environmental_category_score(
    sentinel_score: float,
) -> float:
    """
    Convert the existing Sentinel score into a
    0-100 Environmental Score.

    Sentinel currently represents:
        NDVI
        NDMI
        Valid pixel percentage
    """

    if SENTINEL_WEIGHT <= 0:
        return 0.0

    score = (
        sentinel_score / SENTINEL_WEIGHT
    ) * 100

    return round(
        max(0.0, min(score, 100.0)),
        2,
    )


def calculate_economic_category_score(
    land_reserve_percent: float | None = None,
    road_distance_km: float | None = None,
    power_distance_km: float | None = None,
    substation_distance_km: float | None = None,
) -> float:
    """Calculate an evidence-based economic/development proxy score.

    No land-price dataset is available in this project, so the engine does
    NOT fabricate a rupee land price. Instead it uses real site constraints
    returned by the pipeline: remaining land and distances to road/power/
    substation. The result is explicitly a development-cost proxy.
    """
    def bounded(v: float) -> float:
        return max(0.0, min(100.0, v))

    if land_reserve_percent is None:
        land_score = 0.0
    else:
        land_score = bounded(float(land_reserve_percent))

    def distance_score(value: float | None, excellent: float, good: float, moderate: float, poor: float) -> float:
        if value is None:
            return 0.0
        value = float(value)
        if value <= excellent:
            return 100.0
        if value <= good:
            return 85.0
        if value <= moderate:
            return 65.0
        if value <= poor:
            return 40.0
        return 15.0

    road_score = distance_score(road_distance_km, 0.10, 0.50, 1.00, 2.00)
    power_score = distance_score(power_distance_km, 0.25, 1.00, 3.00, 5.00)
    substation_score = distance_score(substation_distance_km, 0.50, 2.00, 5.00, 10.00)
    accessibility_score = (road_score * 0.40 + power_score * 0.30 + substation_score * 0.30)

    return round(
        max(0.0, min(100.0, land_score * 0.40 + accessibility_score * 0.60)),
        2,
    )

    return round(
        max(0.0, min(score, 100.0)),
        2,
    )


# ------------------------------------------------------------------
# DEPLOYMENT SCORING
# ------------------------------------------------------------------

def safe_get(data, *keys, default=None):
    """
    Safely retrieve nested dictionary values.
    Returns default if any key is missing.
    """
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default


def calculate_deployment_score(report: dict) -> dict:

    # --------------------------------------------------------------
    # Extract Dataset Values
    # --------------------------------------------------------------

    solar_radiation = safe_get(
        report,
        "datasets",
        "nasa_power",
        "solar_resource",
        "solar_radiation_kwh_m2_day",
        default=None,
    )

    mean_wind_speed = safe_get(
        report,
        "datasets",
        "wind",
        "wind_speed_statistics",
        "mean_ms",
        default=None,
    )

    mean_slope = safe_get(
        report,
        "datasets",
        "srtm",
        "slope_statistics",
        "mean_degrees",
        default=None,
    )

    elevation_m = safe_get(
        report,
        "datasets",
        "srtm",
        "elevation_m",
        default=None,
    )

    # --------------------------------------------------------------
    # Individual Scores
    # --------------------------------------------------------------

    solar_score = (
        calculate_solar_score(solar_radiation)
        if solar_radiation is not None
        else 0.0
    )

    wind_score = (
        calculate_wind_score(mean_wind_speed)
        if mean_wind_speed is not None
        else 0.0
    )

    terrain_score = (
        calculate_terrain_score(mean_slope)
        if mean_slope is not None
        else 0.0
    )

    # --------------------------------------------------------------
    # Sentinel Metrics
    # --------------------------------------------------------------

    sentinel = safe_get(
        report,
        "datasets",
        "sentinel",
        default=None,
    )

    if sentinel:

        ndvi_mean = safe_get(
            sentinel,
            "ndvi_statistics",
            "mean",
            default=None,
        )

        ndmi_mean = safe_get(
            sentinel,
            "ndmi_statistics",
            "mean",
            default=None,
        )

        valid_pixel_percentage = safe_get(
            sentinel,
            "valid_percentage",
            default=None,
        )

        if (
            ndvi_mean is not None
            and ndmi_mean is not None
            and valid_pixel_percentage is not None
        ):
            sentinel_score = calculate_sentinel_score(
                ndvi_mean,
                ndmi_mean,
                valid_pixel_percentage,
            )
        else:
            sentinel_score = 0.0

    else:
        sentinel_score = 0.0

    # --------------------------------------------------------------
    # OSM Metrics
    # --------------------------------------------------------------

    osm = safe_get(
        report,
        "datasets",
        "osm",
        default=None,
    )

    if (
        not osm
        or osm.get("status") == "failed"
    ):

        osm_score = 0.0

    else:

        infrastructure_indicators = safe_get(
            osm,
            "infrastructure_indicators",
            default=None,
        )

        feature_analysis = safe_get(
            osm,
            "feature_analysis",
            default=None,
        )

        if (
            not infrastructure_indicators
            or not feature_analysis
        ):

            osm_score = 0.0

        else:

            road_distance = safe_get(
                infrastructure_indicators,
                "nearest_road_distance_km",
                default=None,
            )

            power_distance = safe_get(
                infrastructure_indicators,
                "nearest_power_infrastructure_distance_km",
                default=None,
            )

            substation_distance = safe_get(
                infrastructure_indicators,
                "nearest_substation_distance_km",
                default=None,
            )

            building_count = safe_get(
                feature_analysis,
                "building",
                "count",
                default=None,
            )

            if (
                road_distance is None
                or power_distance is None
                or substation_distance is None
                or building_count is None
            ):

                osm_score = 0.0

            else:

                osm_score = calculate_osm_score(
                    road_distance,
                    power_distance,
                    substation_distance,
                    building_count,
                )

    # --------------------------------------------------------------
    # Overall Score
    # --------------------------------------------------------------

    overall_score = (
        solar_score
        + wind_score
        + terrain_score
        + sentinel_score
        + osm_score
    )

    normalized_score = (
        overall_score / TOTAL_CURRENT_WEIGHT
    ) * 100

    normalized_score = round(normalized_score, 2)

    # --------------------------------------------------------------
    # CATEGORY-WISE SCORES
    # --------------------------------------------------------------

    renewable_resource_score = (
        calculate_renewable_resource_category_score(
            solar_score,
            wind_score,
        )
    )

    elevation_score = calculate_elevation_suitability_score(elevation_m)

    terrain_category_score = (
        calculate_terrain_category_score(
            terrain_score,
            elevation_score,
        )
    )

    infrastructure_score = (
        calculate_infrastructure_category_score(
            osm_score,
        )
    )

    environmental_score = (
        calculate_environmental_category_score(
            sentinel_score,
        )
    )

    road_distance = safe_get(
        report, "datasets", "osm", "infrastructure_indicators",
        "nearest_road_distance_km", default=None
    )
    power_distance = safe_get(
        report, "datasets", "osm", "infrastructure_indicators",
        "nearest_power_infrastructure_distance_km", default=None
    )
    substation_distance = safe_get(
        report, "datasets", "osm", "infrastructure_indicators",
        "nearest_substation_distance_km", default=None
    )
    land_reserve_percent = safe_get(
        report, "site_information", "land_reserve_percent", default=None
    )

    economic_score = calculate_economic_category_score(
        land_reserve_percent=land_reserve_percent,
        road_distance_km=road_distance,
        power_distance_km=power_distance,
        substation_distance_km=substation_distance,
    )

    # --------------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------------

    if normalized_score >= RECOMMENDATION_THRESHOLDS["HIGHLY_SUITABLE"]:
        recommendation = "HIGHLY SUITABLE"

    elif normalized_score >= RECOMMENDATION_THRESHOLDS["SUITABLE"]:
        recommendation = "SUITABLE"

    elif normalized_score >= RECOMMENDATION_THRESHOLDS["MODERATELY_SUITABLE"]:
        recommendation = "MODERATELY SUITABLE"

    else:
        recommendation = "NOT SUITABLE"

    # --------------------------------------------------------------
    # Return Results
    # --------------------------------------------------------------

    return {

        "solar_score": solar_score,
        "wind_score": wind_score,
        "terrain_score": terrain_score,
        "sentinel_score": sentinel_score,
        "osm_score": osm_score,

        "category_scores": {
            "renewable_resource": renewable_resource_score,
            "terrain": terrain_category_score,
            "infrastructure": infrastructure_score,
            "environmental": environmental_score,
            "economic": economic_score,
        },

        "weights": {
            "solar": SOLAR_WEIGHT,
            "wind": WIND_WEIGHT,
            "terrain": TERRAIN_WEIGHT,
            "sentinel": SENTINEL_WEIGHT,
            "osm": OSM_WEIGHT,
        },

        "overall_score": round(overall_score, 2),
        "normalized_score": normalized_score,
        "recommendation": recommendation,

        "dataset_status": {

            "solar": {
                "status": "SUCCESS" if solar_radiation is not None else "FAILED",
                "score": solar_score,
                "weight": SOLAR_WEIGHT,
            },

            "wind": {
                "status": "SUCCESS" if mean_wind_speed is not None else "FAILED",
                "score": wind_score,
                "weight": WIND_WEIGHT,
            },

            "terrain": {
                "status": "SUCCESS" if mean_slope is not None else "FAILED",
                "score": terrain_score,
                "weight": TERRAIN_WEIGHT,
            },

            "sentinel": {
                "status": (
                    "SUCCESS"
                    if sentinel and sentinel.get("status", "success") == "success"
                    and "ndvi_statistics" in sentinel
                    else "UNAVAILABLE"
                ),
                "score": sentinel_score,
                "weight": SENTINEL_WEIGHT,
            },

            "osm": {
                "status": "SUCCESS" if osm is not None else "FAILED",
                "score": osm_score,
                "weight": OSM_WEIGHT,
            }

        }

    }