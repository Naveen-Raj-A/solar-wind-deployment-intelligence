import os
import sqlite3
import time

import requests


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_FILE = os.path.join(
    "datasets",
    "openstreetmap",
    "processed",
    "india_osm_spatial.db",
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# 0.05 degrees around the location.
# Roughly 5–6 km in latitude in each direction.
SEARCH_OFFSET = 0.05


# ============================================================
# GEOCODE LOCATION
# ============================================================

def get_location_coordinates(location_name):

    print("\nSearching location...")

    params = {
        "q": f"{location_name}, India",
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in",
    }

    headers = {
        "User-Agent":
        "solar-wind-deployment-intelligence/1.0"
    }

    try:

        start_time = time.time()

        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        results = response.json()

        geocoding_time = time.time() - start_time


        if not results:

            print("\nERROR: Location not found in India.")

            return None


        location = results[0]

        display_name = location["display_name"]

        latitude = float(location["lat"])

        longitude = float(location["lon"])


        return (
            display_name,
            latitude,
            longitude,
            geocoding_time,
        )


    except requests.RequestException as error:

        print("\nGeocoding failed.")

        print("Error:", error)

        return None


# ============================================================
# QUERY SPATIAL DATABASE
# ============================================================

def query_spatial_database(
    connection,
    south,
    west,
    north,
    east,
):

    cursor = connection.cursor()


    query = """
        SELECT
            f.feature_type,
            COUNT(*)

        FROM osm_features_rtree AS r

        INNER JOIN osm_features AS f

        ON f.feature_id = r.feature_id

        WHERE

            r.max_lon >= ?
            AND r.min_lon <= ?

            AND r.max_lat >= ?
            AND r.min_lat <= ?

        GROUP BY f.feature_type
    """


    start_time = time.time()


    cursor.execute(
        query,
        (
            west,
            east,
            south,
            north,
        ),
    )


    results = cursor.fetchall()


    query_time = time.time() - start_time


    feature_counts = {
        "road": 0,
        "building": 0,
        "substation": 0,
        "power_infrastructure": 0,
    }


    for feature_type, count in results:

        feature_counts[feature_type] = count


    return (
        feature_counts,
        query_time,
    )


# ============================================================
# RUN DYNAMIC LOCATION QUERY
# ============================================================

def run_location_query():

    print(
        "\n===== INDIA OSM SPATIAL DATABASE QUERY ====="
    )


    # ========================================================
    # CHECK DATABASE
    # ========================================================

    if not os.path.exists(DATABASE_FILE):

        print("\nERROR: Spatial database not found.")

        print("Expected File:", DATABASE_FILE)

        return


    # ========================================================
    # GET USER INPUT
    # ========================================================

    location_name = input(
        "\nEnter location in India: "
    ).strip()


    if not location_name:

        print("\nERROR: Location cannot be empty.")

        return


    # ========================================================
    # GEOCODE LOCATION
    # ========================================================

    location_result = get_location_coordinates(
        location_name
    )


    if location_result is None:

        return


    (
        display_name,
        latitude,
        longitude,
        geocoding_time,

    ) = location_result


    # ========================================================
    # DISPLAY LOCATION
    # ========================================================

    print(
        "\n===== LOCATION FOUND ====="
    )

    print(
        "Location:",
        display_name,
    )

    print(
        "Latitude:",
        latitude,
    )

    print(
        "Longitude:",
        longitude,
    )

    print(
        "Geocoding Time:",
        round(geocoding_time, 4),
        "seconds",
    )


    # ========================================================
    # CREATE SEARCH BOUNDS
    # ========================================================

    south = latitude - SEARCH_OFFSET

    north = latitude + SEARCH_OFFSET

    west = longitude - SEARCH_OFFSET

    east = longitude + SEARCH_OFFSET


    print(
        "\n===== SEARCH BOUNDS ====="
    )

    print("South:", south)

    print("North:", north)

    print("West:", west)

    print("East:", east)


    # ========================================================
    # OPEN DATABASE
    # ========================================================

    print(
        "\nOpening India OSM spatial database..."
    )


    connection = sqlite3.connect(
        DATABASE_FILE
    )


    try:

        # ====================================================
        # EXECUTE FAST SPATIAL QUERY
        # ====================================================

        print(
            "Querying nearby OSM features..."
        )


        feature_counts, query_time = (
            query_spatial_database(
                connection,
                south,
                west,
                north,
                east,
            )
        )


        # ====================================================
        # DISPLAY RESULTS
        # ====================================================

        print(
            "\n===== NEARBY OSM FEATURES ====="
        )


        print(
            "Roads:",
            feature_counts["road"],
        )


        print(
            "Buildings:",
            feature_counts["building"],
        )


        print(
            "Substations:",
            feature_counts["substation"],
        )


        print(
            "Other Power Infrastructure:",
            feature_counts[
                "power_infrastructure"
            ],
        )


        # ====================================================
        # PERFORMANCE RESULTS
        # ====================================================

        print(
            "\n===== PERFORMANCE ====="
        )


        print(
            "Database Query Time:",
            round(query_time, 6),
            "seconds",
        )


        total_time = (
            geocoding_time + query_time
        )


        print(
            "Geocoding + Query Time:",
            round(total_time, 6),
            "seconds",
        )


        print(
            "\n===== QUERY COMPLETED SUCCESSFULLY ====="
        )


    except sqlite3.Error as error:

        print(
            "\nDatabase query failed."
        )

        print(
            "Error:",
            error,
        )


    finally:

        connection.close()


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    run_location_query()