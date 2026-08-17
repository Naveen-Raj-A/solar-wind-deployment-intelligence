import json
import math
import sqlite3
import time
from pathlib import Path

from geopy.geocoders import Nominatim


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATABASE_PATH = Path(
    "datasets/openstreetmap/processed/"
    "india_osm_spatial.db"
)

OUTPUT_BASE_DIRECTORY = Path(
    "datasets/openstreetmap/processed"
)

OUTPUT_SUMMARY_FILE_NAME = (
    "osm_analysis_summary.json"
)

GEOCODER_USER_AGENT = (
    "solar_wind_deployment_intelligence"
)

GEOCODER_TIMEOUT_SECONDS = 20

# AOI radius around requested location.
AOI_RADIUS_KM = 5.0

EXPECTED_FEATURE_TYPES = [
    "building",
    "road",
    "power_infrastructure",
    "substation",
]


# --------------------------------------------------
# CREATE SAFE LOCATION NAME
# --------------------------------------------------

def create_safe_location_name(location_name):

    safe_name = (
        location_name
        .strip()
        .lower()
    )

    safe_name = "".join(
        character
        if character.isalnum()
        else "_"
        for character in safe_name
    )

    while "__" in safe_name:

        safe_name = safe_name.replace(
            "__",
            "_",
        )

    return safe_name.strip("_")


# --------------------------------------------------
# GEOCODE LOCATION
# --------------------------------------------------

def geocode_location(location_name):

    geolocator = Nominatim(
        user_agent=GEOCODER_USER_AGENT,
        timeout=GEOCODER_TIMEOUT_SECONDS,
    )

    search_query = (
        f"{location_name}, India"
    )

    location = geolocator.geocode(
        search_query
    )

    if location is None:

        return None

    return {
        "resolved_location": (
            location.address
        ),
        "latitude": float(
            location.latitude
        ),
        "longitude": float(
            location.longitude
        ),
    }


# --------------------------------------------------
# CALCULATE HAVERSINE DISTANCE
# --------------------------------------------------

def calculate_haversine_distance(
    latitude_1,
    longitude_1,
    latitude_2,
    longitude_2,
):

    earth_radius_km = 6371.0088

    latitude_1_radians = math.radians(
        latitude_1
    )

    latitude_2_radians = math.radians(
        latitude_2
    )

    latitude_difference = math.radians(
        latitude_2 - latitude_1
    )

    longitude_difference = math.radians(
        longitude_2 - longitude_1
    )

    haversine_value = (
        math.sin(
            latitude_difference / 2.0
        ) ** 2
        +
        math.cos(
            latitude_1_radians
        )
        *
        math.cos(
            latitude_2_radians
        )
        *
        math.sin(
            longitude_difference / 2.0
        ) ** 2
    )

    angular_distance = (
        2.0
        *
        math.atan2(
            math.sqrt(
                haversine_value
            ),
            math.sqrt(
                1.0 - haversine_value
            ),
        )
    )

    return (
        earth_radius_km
        * angular_distance
    )


# --------------------------------------------------
# CALCULATE AOI BOUNDS
# --------------------------------------------------

def calculate_aoi_bounds(
    latitude,
    longitude,
    radius_km,
):

    latitude_delta = (
        radius_km / 111.32
    )

    latitude_radians = math.radians(
        latitude
    )

    longitude_scale = (
        111.32
        *
        math.cos(
            latitude_radians
        )
    )

    if abs(longitude_scale) < 0.000001:

        raise ValueError(
            "Unable to calculate longitude bounds."
        )

    longitude_delta = (
        radius_km
        / longitude_scale
    )

    west = (
        longitude
        - longitude_delta
    )

    east = (
        longitude
        + longitude_delta
    )

    south = (
        latitude
        - latitude_delta
    )

    north = (
        latitude
        + latitude_delta
    )

    return {
        "west": float(west),
        "south": float(south),
        "east": float(east),
        "north": float(north),
    }


# --------------------------------------------------
# CHECK DATABASE STRUCTURE
# --------------------------------------------------

def validate_database_structure(
    connection,
):

    required_tables = {
        "osm_features",
        "osm_features_rtree",
    }

    table_records = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()

    available_tables = {
        record[0]
        for record in table_records
    }

    missing_tables = (
        required_tables
        - available_tables
    )

    if missing_tables:

        return (
            False,
            sorted(
                missing_tables
            ),
        )

    feature_columns = connection.execute(
        """
        PRAGMA table_info(osm_features)
        """
    ).fetchall()

    feature_column_names = {
        record[1]
        for record in feature_columns
    }

    required_feature_columns = {
        "feature_id",
        "osm_id",
        "osm_type",
        "feature_type",
    }

    missing_feature_columns = (
        required_feature_columns
        - feature_column_names
    )

    if missing_feature_columns:

        return (
            False,
            sorted(
                missing_feature_columns
            ),
        )

    rtree_columns = connection.execute(
        """
        PRAGMA table_info(osm_features_rtree)
        """
    ).fetchall()

    rtree_column_names = {
        record[1]
        for record in rtree_columns
    }

    required_rtree_columns = {
        "feature_id",
        "min_lon",
        "max_lon",
        "min_lat",
        "max_lat",
    }

    missing_rtree_columns = (
        required_rtree_columns
        - rtree_column_names
    )

    if missing_rtree_columns:

        return (
            False,
            sorted(
                missing_rtree_columns
            ),
        )

    return (
        True,
        [],
    )


# --------------------------------------------------
# QUERY AOI FEATURES
# --------------------------------------------------

def query_aoi_features(
    connection,
    bounds,
):

    query = """
        SELECT
            f.feature_id,
            f.osm_id,
            f.osm_type,
            f.feature_type,
            r.min_lon,
            r.max_lon,
            r.min_lat,
            r.max_lat

        FROM osm_features_rtree AS r

        JOIN osm_features AS f
            ON f.feature_id = r.feature_id

        WHERE
            r.max_lon >= ?
            AND r.min_lon <= ?
            AND r.max_lat >= ?
            AND r.min_lat <= ?
    """

    records = connection.execute(
        query,
        (
            bounds["west"],
            bounds["east"],
            bounds["south"],
            bounds["north"],
        ),
    ).fetchall()

    return records


# --------------------------------------------------
# CALCULATE FEATURE CENTER
# --------------------------------------------------

def calculate_feature_center(
    min_lon,
    max_lon,
    min_lat,
    max_lat,
):

    center_longitude = (
        min_lon
        + max_lon
    ) / 2.0

    center_latitude = (
        min_lat
        + max_lat
    ) / 2.0

    return (
        float(center_latitude),
        float(center_longitude),
    )


# --------------------------------------------------
# ANALYZE FEATURES
# --------------------------------------------------

def analyze_features(
    records,
    requested_latitude,
    requested_longitude,
    radius_km,
):

    analysis = {}

    for feature_type in (
        EXPECTED_FEATURE_TYPES
    ):

        analysis[
            feature_type
        ] = {
            "count": 0,
            "nearest_distance_km": None,
            "nearest_feature": None,
        }

    total_bounding_box_matches = (
        len(records)
    )

    exact_radius_records = 0

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

        # Bounding-box query is only the fast
        # candidate selection stage.
        #
        # This check keeps only features whose
        # bounding-box center is inside the exact
        # requested radius.

        if distance_km > radius_km:

            continue

        exact_radius_records += 1

        if feature_type not in analysis:

            analysis[
                feature_type
            ] = {
                "count": 0,
                "nearest_distance_km": None,
                "nearest_feature": None,
            }

        analysis[
            feature_type
        ][
            "count"
        ] += 1

        current_nearest_distance = (
            analysis[
                feature_type
            ][
                "nearest_distance_km"
            ]
        )

        if (
            current_nearest_distance is None
            or
            distance_km
            <
            current_nearest_distance
        ):

            analysis[
                feature_type
            ][
                "nearest_distance_km"
            ] = float(
                distance_km
            )

            analysis[
                feature_type
            ][
                "nearest_feature"
            ] = {
                "feature_id": int(
                    feature_id
                ),
                "osm_id": int(
                    osm_id
                ),
                "osm_type": str(
                    osm_type
                ),
                "center_latitude": float(
                    center_latitude
                ),
                "center_longitude": float(
                    center_longitude
                ),
            }

    return (
        analysis,
        total_bounding_box_matches,
        exact_radius_records,
    )


# --------------------------------------------------
# CALCULATE INFRASTRUCTURE INDICATORS
# --------------------------------------------------

def calculate_infrastructure_indicators(
    feature_analysis,
):

    building_count = (
        feature_analysis[
            "building"
        ][
            "count"
        ]
    )

    road_count = (
        feature_analysis[
            "road"
        ][
            "count"
        ]
    )

    power_infrastructure_count = (
        feature_analysis[
            "power_infrastructure"
        ][
            "count"
        ]
    )

    substation_count = (
        feature_analysis[
            "substation"
        ][
            "count"
        ]
    )

    nearest_road_distance = (
        feature_analysis[
            "road"
        ][
            "nearest_distance_km"
        ]
    )

    nearest_power_distance = (
        feature_analysis[
            "power_infrastructure"
        ][
            "nearest_distance_km"
        ]
    )

    nearest_substation_distance = (
        feature_analysis[
            "substation"
        ][
            "nearest_distance_km"
        ]
    )

    infrastructure_indicators = {
        "building_presence": (
            building_count > 0
        ),
        "road_access_available": (
            road_count > 0
        ),
        "power_infrastructure_available": (
            power_infrastructure_count > 0
        ),
        "substation_available": (
            substation_count > 0
        ),
        "nearest_road_distance_km": (
            nearest_road_distance
        ),
        "nearest_power_infrastructure_distance_km": (
            nearest_power_distance
        ),
        "nearest_substation_distance_km": (
            nearest_substation_distance
        ),
    }

    return infrastructure_indicators


# --------------------------------------------------
# VALIDATE JSON OUTPUT
# --------------------------------------------------

def validate_json_output(
    output_path,
):

    if not output_path.exists():

        return False

    if output_path.stat().st_size == 0:

        return False

    try:

        with open(
            output_path,
            "r",
            encoding="utf-8",
        ) as file:

            summary_data = json.load(
                file
            )

        required_sections = [
            "location",
            "aoi",
            "database",
            "feature_analysis",
            "infrastructure_indicators",
        ]

        for section in required_sections:

            if section not in summary_data:

                return False

        return True

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return False


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print(
        "\n===== OPENSTREETMAP INFRASTRUCTURE ANALYSIS ====="
    )


    # --------------------------------------------------
    # GET LOCATION
    # --------------------------------------------------

    location_name = input(
        "\nEnter location in India: "
    ).strip()

    if not location_name:

        print(
            "\nError: Location cannot be empty."
        )

        return


    # --------------------------------------------------
    # CHECK DATABASE
    # --------------------------------------------------

    print(
        "\n===== CHECKING OSM DATABASE ====="
    )

    if not DATABASE_PATH.exists():

        print(
            "OSM Database: NOT FOUND"
        )

        print(
            "Expected File:",
            DATABASE_PATH,
        )

        return

    database_size_gb = (
        DATABASE_PATH.stat().st_size
        /
        (1024 ** 3)
    )

    print(
        "OSM Database: FOUND"
    )

    print(
        "Database File:",
        DATABASE_PATH,
    )

    print(
        "Database Size:",
        round(
            database_size_gb,
            4,
        ),
        "GB",
    )

    processing_start_time = (
        time.time()
    )


    # --------------------------------------------------
    # GEOCODE LOCATION
    # --------------------------------------------------

    print(
        "\n===== GEOCODING LOCATION ====="
    )

    print(
        "Searching location..."
    )

    try:

        location_information = (
            geocode_location(
                location_name
            )
        )

    except Exception as error:

        print(
            "Geocoding Error:",
            error,
        )

        return

    if location_information is None:

        print(
            "Location could not be found."
        )

        return

    resolved_location = (
        location_information[
            "resolved_location"
        ]
    )

    requested_latitude = float(
        location_information[
            "latitude"
        ]
    )

    requested_longitude = float(
        location_information[
            "longitude"
        ]
    )

    print(
        "\n===== LOCATION FOUND ====="
    )

    print(
        "Requested Location:",
        location_name.upper(),
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


    # --------------------------------------------------
    # CREATE AOI
    # --------------------------------------------------

    print(
        "\n===== CREATING OSM AOI ====="
    )

    try:

        aoi_bounds = (
            calculate_aoi_bounds(
                latitude=(
                    requested_latitude
                ),
                longitude=(
                    requested_longitude
                ),
                radius_km=(
                    AOI_RADIUS_KM
                ),
            )
        )

    except ValueError as error:

        print(
            "AOI Error:",
            error,
        )

        return

    print(
        "AOI Radius:",
        AOI_RADIUS_KM,
        "km",
    )

    print(
        "West:",
        aoi_bounds[
            "west"
        ],
    )

    print(
        "South:",
        aoi_bounds[
            "south"
        ],
    )

    print(
        "East:",
        aoi_bounds[
            "east"
        ],
    )

    print(
        "North:",
        aoi_bounds[
            "north"
        ],
    )


    # --------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------

    safe_location_name = (
        create_safe_location_name(
            location_name
        )
    )

    output_directory = (
        OUTPUT_BASE_DIRECTORY
        /
        safe_location_name
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_summary_path = (
        output_directory
        /
        OUTPUT_SUMMARY_FILE_NAME
    )

    print(
        "\nOutput Directory:",
        output_directory,
    )


    # --------------------------------------------------
    # CONNECT TO DATABASE
    # --------------------------------------------------

    print(
        "\n===== CONNECTING TO OSM DATABASE ====="
    )

    try:

        connection = sqlite3.connect(
            DATABASE_PATH
        )

    except sqlite3.Error as error:

        print(
            "Database Connection Error:",
            error,
        )

        return

    print(
        "Database Connection: SUCCESSFUL"
    )


    # --------------------------------------------------
    # VALIDATE DATABASE STRUCTURE
    # --------------------------------------------------

    print(
        "\n===== VALIDATING DATABASE STRUCTURE ====="
    )

    try:

        (
            database_valid,
            missing_database_items,
        ) = validate_database_structure(
            connection
        )

    except sqlite3.Error as error:

        print(
            "Database Validation Error:",
            error,
        )

        connection.close()

        return

    if not database_valid:

        print(
            "Database Structure: INVALID"
        )

        print(
            "Missing Items:",
            missing_database_items,
        )

        connection.close()

        return

    print(
        "Database Structure: VALID"
    )


    # --------------------------------------------------
    # QUERY SPATIAL INDEX
    # --------------------------------------------------

    print(
        "\n===== QUERYING OSM SPATIAL INDEX ====="
    )

    query_start_time = (
        time.time()
    )

    try:

        records = query_aoi_features(
            connection=connection,
            bounds=aoi_bounds,
        )

    except sqlite3.Error as error:

        print(
            "Spatial Query Error:",
            error,
        )

        connection.close()

        return

    query_time = (
        time.time()
        -
        query_start_time
    )

    print(
        "Bounding Box Matches:",
        len(records),
    )

    print(
        "Spatial Query Time:",
        round(
            query_time,
            4,
        ),
        "seconds",
    )


    # --------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------

    connection.close()

    print(
        "Database Connection: CLOSED"
    )


    # --------------------------------------------------
    # ANALYZE FEATURES
    # --------------------------------------------------

    print(
        "\n===== ANALYZING OSM FEATURES ====="
    )

    (
        feature_analysis,
        total_bounding_box_matches,
        exact_radius_records,
    ) = analyze_features(
        records=records,
        requested_latitude=(
            requested_latitude
        ),
        requested_longitude=(
            requested_longitude
        ),
        radius_km=(
            AOI_RADIUS_KM
        ),
    )

    print(
        "Bounding Box Candidates:",
        total_bounding_box_matches,
    )

    print(
        "Features Inside AOI Radius:",
        exact_radius_records,
    )

    print(
        "Feature Analysis: COMPLETED"
    )


    # --------------------------------------------------
    # DISPLAY FEATURE STATISTICS
    # --------------------------------------------------

    print(
        "\n===== OSM FEATURE STATISTICS ====="
    )

    for feature_type in (
        EXPECTED_FEATURE_TYPES
    ):

        feature_information = (
            feature_analysis[
                feature_type
            ]
        )

        print(
            "\nFeature Type:",
            feature_type
        )

        print(
            "Count:",
            feature_information[
                "count"
            ],
        )

        nearest_distance = (
            feature_information[
                "nearest_distance_km"
            ]
        )

        if nearest_distance is None:

            print(
                "Nearest Distance: NOT AVAILABLE"
            )

        else:

            print(
                "Nearest Distance:",
                round(
                    nearest_distance,
                    4,
                ),
                "km",
            )


    # --------------------------------------------------
    # CALCULATE INFRASTRUCTURE INDICATORS
    # --------------------------------------------------

    print(
        "\n===== CALCULATING INFRASTRUCTURE INDICATORS ====="
    )

    infrastructure_indicators = (
        calculate_infrastructure_indicators(
            feature_analysis
        )
    )

    print(
        "Road Access Available:",
        infrastructure_indicators[
            "road_access_available"
        ],
    )

    print(
        "Power Infrastructure Available:",
        infrastructure_indicators[
            "power_infrastructure_available"
        ],
    )

    print(
        "Substation Available:",
        infrastructure_indicators[
            "substation_available"
        ],
    )

    print(
        "Infrastructure Analysis: COMPLETED"
    )


    # --------------------------------------------------
    # CREATE ANALYSIS SUMMARY
    # --------------------------------------------------

    analysis_summary = {

        "location": {

            "requested_location": (
                location_name.upper()
            ),

            "resolved_location": (
                resolved_location
            ),

            "latitude": float(
                requested_latitude
            ),

            "longitude": float(
                requested_longitude
            ),
        },


        "aoi": {

            "radius_km": float(
                AOI_RADIUS_KM
            ),

            "bounds": {

                "west": float(
                    aoi_bounds[
                        "west"
                    ]
                ),

                "south": float(
                    aoi_bounds[
                        "south"
                    ]
                ),

                "east": float(
                    aoi_bounds[
                        "east"
                    ]
                ),

                "north": float(
                    aoi_bounds[
                        "north"
                    ]
                ),
            },
        },


        "database": {

            "database_file": str(
                DATABASE_PATH
            ),

            "database_size_gb": float(
                database_size_gb
            ),

            "spatial_query_time_seconds": float(
                query_time
            ),

            "bounding_box_matches": int(
                total_bounding_box_matches
            ),

            "features_inside_radius": int(
                exact_radius_records
            ),
        },


        "feature_analysis": (
            feature_analysis
        ),


        "infrastructure_indicators": (
            infrastructure_indicators
        ),
    }


    # --------------------------------------------------
    # SAVE JSON OUTPUT
    # --------------------------------------------------

    print(
        "\n===== SAVING PROCESSED OUTPUT ====="
    )

    try:

        with open(
            output_summary_path,
            "w",
            encoding="utf-8",
        ) as summary_file:

            json.dump(
                analysis_summary,
                summary_file,
                indent=4,
                ensure_ascii=False,
                allow_nan=False,
            )

    except (
        OSError,
        TypeError,
        ValueError,
    ) as error:

        print(
            "Output Saving Error:",
            error,
        )

        return

    print(
        "Saved:",
        output_summary_path,
    )


    # --------------------------------------------------
    # VALIDATE OUTPUT
    # --------------------------------------------------

    print(
        "\n===== OUTPUT VALIDATION ====="
    )

    output_valid = (
        validate_json_output(
            output_summary_path
        )
    )

    print(
        OUTPUT_SUMMARY_FILE_NAME,
        ":",
        (
            "VALID"
            if output_valid
            else "INVALID"
        ),
    )


    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    processing_time = (
        time.time()
        -
        processing_start_time
    )

    print(
        "\n===== OSM ANALYSIS SUMMARY ====="
    )

    print(
        "Requested Location:",
        location_name.upper(),
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
        "AOI Radius:",
        AOI_RADIUS_KM,
        "km",
    )

    print(
        "Buildings:",
        feature_analysis[
            "building"
        ][
            "count"
        ],
    )

    print(
        "Roads:",
        feature_analysis[
            "road"
        ][
            "count"
        ],
    )

    print(
        "Power Infrastructure:",
        feature_analysis[
            "power_infrastructure"
        ][
            "count"
        ],
    )

    print(
        "Substations:",
        feature_analysis[
            "substation"
        ][
            "count"
        ],
    )

    print(
        "Output File:",
        output_summary_path,
    )

    print(
        "Output Validation:",
        (
            "PASSED"
            if output_valid
            else "FAILED"
        ),
    )

    print(
        "Total Processing Time:",
        round(
            processing_time,
            2,
        ),
        "seconds",
    )


    # --------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------

    if output_valid:

        print(
            "\n===== OSM ANALYSIS "
            "COMPLETED SUCCESSFULLY ====="
        )

    else:

        print(
            "\n===== OSM ANALYSIS FAILED ====="
        )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()