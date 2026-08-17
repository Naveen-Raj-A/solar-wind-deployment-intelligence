"""
Scoring Rules

Defines scoring weights and classification thresholds for
renewable energy deployment suitability.
"""

SOLAR_WEIGHT = 25
WIND_WEIGHT = 25
TERRAIN_WEIGHT = 20
SENTINEL_WEIGHT = 15
OSM_WEIGHT = 15

TOTAL_CURRENT_WEIGHT = (
    SOLAR_WEIGHT
    + WIND_WEIGHT
    + TERRAIN_WEIGHT
    + SENTINEL_WEIGHT
    + OSM_WEIGHT
)

SOLAR_THRESHOLDS = {
    "EXCELLENT": 5.75,
    "GOOD": 5.25,
    "MODERATE": 4.75,
    "POOR": 0.0,
}

WIND_THRESHOLDS = {
    "EXCELLENT": 8.0,
    "GOOD": 6.0,
    "MODERATE": 4.0,
    "POOR": 0.0,
}

TERRAIN_THRESHOLDS = {
    "EXCELLENT": 3.0,
    "GOOD": 8.0,
    "MODERATE": 15.0,
}

# ------------------------------------------------------------------
# SENTINEL SCORING
# ------------------------------------------------------------------

SENTINEL_NDVI_THRESHOLDS = {
    "EXCELLENT": 0.20,
    "GOOD": 0.35,
    "MODERATE": 0.50,
}

SENTINEL_NDMI_THRESHOLDS = {
    "EXCELLENT": 0.10,
    "GOOD": 0.25,
    "MODERATE": 0.40,
}

VALID_PIXEL_THRESHOLDS = {
    "EXCELLENT": 95.0,
    "GOOD": 90.0,
    "MODERATE": 80.0,
}

RECOMMENDATION_THRESHOLDS = {
    "HIGHLY_SUITABLE": 85,
    "SUITABLE": 70,
    "MODERATELY_SUITABLE": 50,
    "NOT_SUITABLE": 0,
}

# ------------------------------------------------------------------
# OPENSTREETMAP SCORING
# ------------------------------------------------------------------

ROAD_DISTANCE_THRESHOLDS = {
    "EXCELLENT": 0.5,
    "GOOD": 1.0,
    "MODERATE": 2.0,
    "POOR": 5.0,
}

POWER_DISTANCE_THRESHOLDS = {
    "EXCELLENT": 1.0,
    "GOOD": 2.0,
    "MODERATE": 5.0,
    "POOR": 10.0,
}

SUBSTATION_DISTANCE_THRESHOLDS = {
    "EXCELLENT": 1.0,
    "GOOD": 3.0,
    "MODERATE": 5.0,
    "POOR": 10.0,
}

BUILDING_COUNT_THRESHOLDS = {
    "LOW": 500,
    "MODERATE": 1500,
}