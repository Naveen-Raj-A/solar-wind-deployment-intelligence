"""
OpenStreetMap Summary Module

Responsibilities
----------------
• Create the final analysis summary
• Save summary as JSON
• Validate saved JSON

No geocoding, database, or analysis logic belongs here.
"""

import json

from .config import (
    REQUIRED_JSON_SECTIONS,
)


# ============================================================
# CREATE ANALYSIS SUMMARY
# ============================================================

def create_analysis_summary(
    location_name,
    resolved_location,
    requested_latitude,
    requested_longitude,
    aoi_radius_km,
    aoi_bounds,
    database_path,
    database_size_gb,
    query_time_seconds,
    total_bounding_box_matches,
    exact_radius_matches,
    feature_analysis,
    infrastructure_indicators,
):
    """
    Build the final analysis summary dictionary.
    """

    summary = {

        "location": {

            "requested_location":
                location_name.upper(),

            "resolved_location":
                resolved_location,

            "latitude":
                float(requested_latitude),

            "longitude":
                float(requested_longitude),

        },

        "aoi": {

            "radius_km":
                float(aoi_radius_km),

            "bounds": {

                "west":
                    float(aoi_bounds["west"]),

                "south":
                    float(aoi_bounds["south"]),

                "east":
                    float(aoi_bounds["east"]),

                "north":
                    float(aoi_bounds["north"]),

            },

        },

        "database": {

            "database_file":
                str(database_path),

            "database_size_gb":
                float(database_size_gb),

            "spatial_query_time_seconds":
                float(query_time_seconds),

            "bounding_box_matches":
                int(total_bounding_box_matches),

            "features_inside_radius":
                int(exact_radius_matches),

        },

        "feature_analysis":
            feature_analysis,

        "infrastructure_indicators":
            infrastructure_indicators,

    }

    return summary


# ============================================================
# SAVE SUMMARY
# ============================================================

def save_summary(
    summary,
    output_path,
):
    """
    Save summary JSON to disk.
    """

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False,
            allow_nan=False,
        )


# ============================================================
# LOAD SUMMARY
# ============================================================

def load_summary(
    summary_path,
):
    """
    Load an existing summary JSON.
    """

    with open(
        summary_path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================
# VALIDATE SUMMARY
# ============================================================

def validate_summary(
    summary,
):
    """
    Validate summary dictionary structure.
    """

    for section in REQUIRED_JSON_SECTIONS:

        if section not in summary:

            return False

    return True


# ============================================================
# VALIDATE JSON FILE
# ============================================================

def validate_json_output(
    output_path,
):
    """
    Validate a saved JSON summary.
    """

    if not output_path.exists():
        return False

    if output_path.stat().st_size == 0:
        return False

    try:

        summary = load_summary(
            output_path
        )

        return validate_summary(
            summary
        )

    except (

        json.JSONDecodeError,

        OSError,

    ):

        return False