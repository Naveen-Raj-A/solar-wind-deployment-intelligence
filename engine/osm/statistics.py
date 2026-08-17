"""
OpenStreetMap Statistics Module

Responsibilities
----------------
• Analyze extracted OSM features
• Count feature occurrences
• Find nearest feature of each type
• Calculate infrastructure indicators

This module operates only on extracted feature objects.
"""

from .config import (
    EXPECTED_FEATURE_TYPES,
    FEATURE_BUILDING,
    FEATURE_ROAD,
    FEATURE_POWER_INFRASTRUCTURE,
    FEATURE_SUBSTATION,
)


# ============================================================
# ANALYZE FEATURES
# ============================================================

def analyze_features(features):
    """
    Analyze extracted OSM features.

    Parameters
    ----------
    features : list

    Returns
    -------
    dict
    """

    analysis = {}

    # Initialize analysis structure
    for feature_type in EXPECTED_FEATURE_TYPES:

        analysis[feature_type] = {

            "count": 0,

            "nearest_distance_km": None,

            "nearest_feature": None,

        }

    # Analyze every extracted feature
    for feature in features:

        feature_type = feature["feature_type"]

        if feature_type not in analysis:

            analysis[feature_type] = {

                "count": 0,

                "nearest_distance_km": None,

                "nearest_feature": None,

            }

        analysis[feature_type]["count"] += 1

        current_distance = analysis[
            feature_type
        ]["nearest_distance_km"]

        if (
            current_distance is None
            or
            feature["distance_km"] < current_distance
        ):

            analysis[
                feature_type
            ]["nearest_distance_km"] = (
                feature["distance_km"]
            )

            analysis[
                feature_type
            ]["nearest_feature"] = {

                "feature_id": feature["feature_id"],

                "osm_id": feature["osm_id"],

                "osm_type": feature["osm_type"],

                "center_latitude":
                    feature["center_latitude"],

                "center_longitude":
                    feature["center_longitude"],

            }

    return analysis


# ============================================================
# INFRASTRUCTURE INDICATORS
# ============================================================

def calculate_infrastructure_indicators(
    feature_analysis,
):
    """
    Calculate infrastructure indicators
    from analyzed features.

    Returns
    -------
    dict
    """

    building_count = feature_analysis[
        FEATURE_BUILDING
    ]["count"]

    road_count = feature_analysis[
        FEATURE_ROAD
    ]["count"]

    power_count = feature_analysis[
        FEATURE_POWER_INFRASTRUCTURE
    ]["count"]

    substation_count = feature_analysis[
        FEATURE_SUBSTATION
    ]["count"]

    infrastructure = {

        "building_presence":
            building_count > 0,

        "road_access_available":
            road_count > 0,

        "power_infrastructure_available":
            power_count > 0,

        "substation_available":
            substation_count > 0,

        "nearest_road_distance_km":
            feature_analysis[
                FEATURE_ROAD
            ]["nearest_distance_km"],

        "nearest_power_infrastructure_distance_km":
            feature_analysis[
                FEATURE_POWER_INFRASTRUCTURE
            ]["nearest_distance_km"],

        "nearest_substation_distance_km":
            feature_analysis[
                FEATURE_SUBSTATION
            ]["nearest_distance_km"],

    }

    return infrastructure


# ============================================================
# FEATURE SUMMARY
# ============================================================

def get_feature_summary(feature_analysis):
    """
    Return a simplified feature summary.

    Useful for dashboards and reports.
    """

    summary = {}

    for feature_type, values in feature_analysis.items():

        summary[feature_type] = {

            "count": values["count"],

            "nearest_distance_km":
                values["nearest_distance_km"],

        }

    return summary