"""
OpenStreetMap Analysis Engine
=============================

Pipeline

    Site Coordinates
          ↓
       AOI Creation
          ↓
     Database Query
          ↓
    Feature Extraction
          ↓
       Statistics
          ↓
    Summary Generation

Coordinate-first design
-----------------------
Latitude and longitude are the authoritative site coordinates.

The analyzer supports two modes:

1. Coordinate mode
   analyze_location(
       latitude=...,
       longitude=...,
       location_name=...
   )

2. Legacy location-name mode
   analyze_location(
       location_name="Krishnagiri"
   )

In coordinate mode, NO second geocoding request is performed.
"""

from __future__ import annotations

import time


from .config import (
    DATABASE_PATH,
    OUTPUT_BASE_DIRECTORY,
    OUTPUT_SUMMARY_FILENAME,
    AOI_RADIUS_KM,
)


from .search import (
    geocode_location,
    calculate_aoi_bounds,
    create_safe_location_name,
)


from .database import (
    database_exists,
    get_database_size_gb,
    connect_database,
    close_database,
    validate_database_structure,
    query_aoi_features,
)


from .extractor import (
    extract_features,
)


from .statistics import (
    analyze_features,
    calculate_infrastructure_indicators,
)


from .summary import (
    create_analysis_summary,
    save_summary,
    validate_json_output,
)


# ============================================================
# OSM ANALYSIS
# ============================================================

def analyze_location(
    location_name=None,
    latitude=None,
    longitude=None,
    resolved_location=None,
):
    """
    Run complete OpenStreetMap analysis.

    Parameters
    ----------
    location_name : str, optional
        Original location name.

    latitude : float, optional
        Exact site latitude.

    longitude : float, optional
        Exact site longitude.

    resolved_location : str, optional
        Human-readable resolved location.

    Returns
    -------
    dict
        Complete OSM analysis summary.

    Notes
    -----
    If latitude and longitude are supplied, they are treated
    as authoritative and geocoding is skipped.

    If coordinates are not supplied, the function falls back
    to the existing location-name geocoding workflow.
    """

    overall_start_time = time.time()

    # ========================================================
    # START
    # ========================================================

    print(
        "\n===== OPENSTREETMAP ANALYSIS ====="
    )

    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    coordinate_mode = (
        latitude is not None
        and longitude is not None
    )

    # ========================================================
    # DATABASE CHECK
    # ========================================================

    if not database_exists():

        raise FileNotFoundError(
            f"Database not found:\n{DATABASE_PATH}"
        )

    database_size_gb = (
        get_database_size_gb()
    )

    # ========================================================
    # LOCATION RESOLUTION
    # ========================================================

    if coordinate_mode:

        # ----------------------------------------------------
        # COORDINATE MODE
        # ----------------------------------------------------

        requested_latitude = float(
            latitude
        )

        requested_longitude = float(
            longitude
        )

        if not resolved_location:

            resolved_location = (
                location_name
                if location_name
                else (
                    f"{requested_latitude}, "
                    f"{requested_longitude}"
                )
            )

        if not location_name:

            location_name = (
                resolved_location
            )

        print(
            "\n===== COORDINATE LOCATION ====="
        )

        print(
            "Location:",
            location_name,
        )

        print(
            "Resolved Location:",
            resolved_location,
        )

        print(
            "Latitude:",
            requested_latitude,
        )

        print(
            "Longitude:",
            requested_longitude,
        )

        print(
            "Geocoding: SKIPPED"
        )

    else:

        # ----------------------------------------------------
        # LEGACY LOCATION-NAME MODE
        # ----------------------------------------------------

        if not location_name:

            raise ValueError(
                "Either location_name or "
                "latitude/longitude must be provided."
            )

        print(
            "\n===== GEOCODING LOCATION ====="
        )

        print(
            "Location:",
            location_name,
        )

        location = geocode_location(
            location_name
        )

        if location is None:

            raise ValueError(
                "Location not found."
            )

        requested_latitude = float(
            location["latitude"]
        )

        requested_longitude = float(
            location["longitude"]
        )

        resolved_location = (
            location["resolved_location"]
        )

        print(
            "Resolved Location:",
            resolved_location,
        )

        print(
            "Latitude:",
            requested_latitude,
        )

        print(
            "Longitude:",
            requested_longitude,
        )

    # ========================================================
    # AOI CREATION
    # ========================================================

    print(
        "\n===== CREATING OSM AOI ====="
    )

    bounds = calculate_aoi_bounds(
        latitude=requested_latitude,
        longitude=requested_longitude,
        radius_km=AOI_RADIUS_KM,
    )

    print(
        "AOI Radius:",
        AOI_RADIUS_KM,
        "km",
    )

    print(
        "South:",
        bounds["south"],
    )

    print(
        "North:",
        bounds["north"],
    )

    print(
        "West:",
        bounds["west"],
    )

    print(
        "East:",
        bounds["east"],
    )

    # ========================================================
    # OUTPUT DIRECTORY
    # ========================================================

    safe_name = create_safe_location_name(
        location_name
    )

    output_directory = (
        OUTPUT_BASE_DIRECTORY
        / safe_name
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_directory
        / OUTPUT_SUMMARY_FILENAME
    )

    # ========================================================
    # OPEN DATABASE
    # ========================================================

    print(
        "\n===== OPENING OSM DATABASE ====="
    )

    connection = connect_database()

    try:

        # ----------------------------------------------------
        # VALIDATE DATABASE
        # ----------------------------------------------------

        valid, missing = (
            validate_database_structure(
                connection
            )
        )

        if not valid:

            raise RuntimeError(
                f"Invalid database: {missing}"
            )

        print(
            "Database Validation: PASSED"
        )

        # ----------------------------------------------------
        # QUERY AOI
        # ----------------------------------------------------

        print(
            "\n===== QUERYING OSM FEATURES ====="
        )

        query_start = time.time()

        records = query_aoi_features(
            connection,
            bounds,
        )

        query_time = (
            time.time()
            - query_start
        )

        print(
            "Database Query: COMPLETED"
        )

        print(
            "Query Time:",
            round(
                query_time,
                4,
            ),
            "seconds",
        )

        print(
            "Bounding Box Matches:",
            len(records),
        )

    finally:

        close_database(
            connection
        )

    # ========================================================
    # EXTRACT FEATURES
    # ========================================================

    print(
        "\n===== EXTRACTING OSM FEATURES ====="
    )

    (
        extracted_features,
        total_matches,
        radius_matches,
    ) = extract_features(
        records,
        requested_latitude,
        requested_longitude,
        AOI_RADIUS_KM,
    )

    print(
        "Total Bounding Box Matches:",
        total_matches,
    )

    print(
        "Exact Radius Matches:",
        radius_matches,
    )

    print(
        "Feature Extraction: COMPLETED"
    )

    # ========================================================
    # FEATURE STATISTICS
    # ========================================================

    print(
        "\n===== ANALYSING OSM FEATURES ====="
    )

    feature_analysis = (
        analyze_features(
            extracted_features
        )
    )

    print(
        "Feature Statistics: COMPLETED"
    )

    # ========================================================
    # INFRASTRUCTURE INDICATORS
    # ========================================================

    print(
        "\n===== CALCULATING INFRASTRUCTURE INDICATORS ====="
    )

    infrastructure = (
        calculate_infrastructure_indicators(
            feature_analysis
        )
    )

    print(
        "Infrastructure Indicators: COMPLETED"
    )

    # ========================================================
    # DISPLAY INFRASTRUCTURE RESULTS
    # ========================================================

    print(
        "\n===== INFRASTRUCTURE SUMMARY ====="
    )

    print(
        "Building Presence:",
        infrastructure[
            "building_presence"
        ],
    )

    print(
        "Road Access:",
        infrastructure[
            "road_access_available"
        ],
    )

    print(
        "Power Infrastructure:",
        infrastructure[
            "power_infrastructure_available"
        ],
    )

    print(
        "Substation Available:",
        infrastructure[
            "substation_available"
        ],
    )

    print(
        "Nearest Road:",
        infrastructure[
            "nearest_road_distance_km"
        ],
        "km",
    )

    print(
        "Nearest Power Infrastructure:",
        infrastructure[
            "nearest_power_infrastructure_distance_km"
        ],
        "km",
    )

    print(
        "Nearest Substation:",
        infrastructure[
            "nearest_substation_distance_km"
        ],
        "km",
    )

    # ========================================================
    # CREATE SUMMARY
    # ========================================================

    print(
        "\n===== GENERATING OSM SUMMARY ====="
    )

    summary = create_analysis_summary(
        location_name=location_name,
        resolved_location=resolved_location,
        requested_latitude=requested_latitude,
        requested_longitude=requested_longitude,
        aoi_radius_km=AOI_RADIUS_KM,
        aoi_bounds=bounds,
        database_path=DATABASE_PATH,
        database_size_gb=database_size_gb,
        query_time_seconds=query_time,
        total_bounding_box_matches=total_matches,
        exact_radius_matches=radius_matches,
        feature_analysis=feature_analysis,
        infrastructure_indicators=infrastructure,
    )

    # ========================================================
    # SAVE SUMMARY
    # ========================================================

    print(
        "\n===== SAVING OSM SUMMARY ====="
    )

    save_summary(
        summary,
        output_file,
    )

    print(
        "Saved:",
        output_file,
    )

    # ========================================================
    # VALIDATE OUTPUT
    # ========================================================

    output_valid = (
        validate_json_output(
            output_file
        )
    )

    print(
        "Output Validation:",
        "PASSED"
        if output_valid
        else "FAILED",
    )

    # ========================================================
    # OUTPUT INFORMATION
    # ========================================================

    summary["output"] = {
        "directory": str(
            output_directory
        ),
        "file": str(
            output_file
        ),
        "validated": output_valid,
    }

    # ========================================================
    # PROCESSING INFORMATION
    # ========================================================

    summary["processing"] = {
        "processing_time_seconds":
            round(
                time.time()
                - overall_start_time,
                4,
            )
    }

    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n===== OPENSTREETMAP ANALYSIS COMPLETED SUCCESSFULLY ====="
    )

    return summary