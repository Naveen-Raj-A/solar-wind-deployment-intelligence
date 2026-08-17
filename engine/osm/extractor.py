"""
OpenStreetMap Feature Extractor

Responsibilities
----------------
• Convert SQLite records into structured feature objects
• Calculate feature center coordinates
• Preserve raw feature metadata

No statistics or scoring logic belongs here.
"""

from .search import calculate_haversine_distance


# ============================================================
# FEATURE CENTER
# ============================================================

def calculate_feature_center(
    min_lon: float,
    max_lon: float,
    min_lat: float,
    max_lat: float,
):
    """
    Calculate the center point of a feature's
    bounding box.
    """

    center_longitude = (
        min_lon + max_lon
    ) / 2.0

    center_latitude = (
        min_lat + max_lat
    ) / 2.0

    return (
        float(center_latitude),
        float(center_longitude),
    )


# ============================================================
# EXTRACT FEATURES
# ============================================================

def extract_features(
    records,
    requested_latitude,
    requested_longitude,
    radius_km,
):
    """
    Convert raw SQLite rows into structured
    feature dictionaries.

    Returns
    -------
    tuple
        (
            extracted_features,
            total_bounding_box_matches,
            exact_radius_matches,
        )
    """

    extracted_features = []

    total_bounding_box_matches = len(records)

    exact_radius_matches = 0

    for record in records:

        (
            feature_id,
            osm_id,
            osm_type,
            feature_type,
            min_lon,
            max_lon,
            min_lat,
            max_lat,
        ) = record

        (
            center_latitude,
            center_longitude,
        ) = calculate_feature_center(
            min_lon=min_lon,
            max_lon=max_lon,
            min_lat=min_lat,
            max_lat=max_lat,
        )

        distance_km = (
            calculate_haversine_distance(
                requested_latitude,
                requested_longitude,
                center_latitude,
                center_longitude,
            )
        )

        # Keep only features whose center lies
        # within the requested AOI radius.

        if distance_km > radius_km:
            continue

        exact_radius_matches += 1

        extracted_features.append(

            {

                "feature_id": int(feature_id),

                "osm_id": int(osm_id),

                "osm_type": str(osm_type),

                "feature_type": str(feature_type),

                "center_latitude": float(
                    center_latitude
                ),

                "center_longitude": float(
                    center_longitude
                ),

                "distance_km": float(
                    distance_km
                ),

                "bounding_box": {

                    "min_lon": float(min_lon),

                    "max_lon": float(max_lon),

                    "min_lat": float(min_lat),

                    "max_lat": float(max_lat),

                },

            }

        )

    return (

        extracted_features,

        total_bounding_box_matches,

        exact_radius_matches,
    )