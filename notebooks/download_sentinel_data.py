import time

import requests
import planetary_computer
from pystac_client import Client


# ============================================================
# CONFIGURATION
# ============================================================

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

SENTINEL_COLLECTION = "sentinel-2-l2a"

# Search area around the location
SEARCH_OFFSET = 0.05

# Maximum acceptable cloud cover
MAX_CLOUD_COVER = 20

# Search recent imagery
DATE_RANGE = "2025-01-01/2026-12-31"

# Number of scenes to retrieve
MAX_RESULTS = 10


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


        result = results[0]

        display_name = result["display_name"]

        latitude = float(result["lat"])

        longitude = float(result["lon"])


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
# CREATE SEARCH BOUNDING BOX
# ============================================================

def create_search_bounds(latitude, longitude):

    west = longitude - SEARCH_OFFSET

    south = latitude - SEARCH_OFFSET

    east = longitude + SEARCH_OFFSET

    north = latitude + SEARCH_OFFSET


    return [
        west,
        south,
        east,
        north,
    ]


# ============================================================
# SEARCH SENTINEL-2 DATA
# ============================================================

def search_sentinel_data(bounding_box):

    print("\nConnecting to Sentinel-2 STAC catalog...")


    try:

        catalog = Client.open(
            STAC_URL,
            modifier=planetary_computer.sign_inplace,
        )


        print("Connection successful.")

        print("\nSearching Sentinel-2 imagery...")


        start_time = time.time()


        search = catalog.search(

            collections=[
                SENTINEL_COLLECTION
            ],

            bbox=bounding_box,

            datetime=DATE_RANGE,

            query={
                "eo:cloud_cover": {
                    "lt": MAX_CLOUD_COVER
                }
            },

            max_items=MAX_RESULTS,
        )


        items = list(
            search.items()
        )


        search_time = (
            time.time() - start_time
        )


        return (
            items,
            search_time,
        )


    except Exception as error:

        print(
            "\nSentinel search failed."
        )

        print(
            "Error:",
            error,
        )

        return (
            [],
            0,
        )


# ============================================================
# SELECT BEST SENTINEL SCENE
# ============================================================

def select_best_scene(items):

    if not items:

        return None


    sorted_items = sorted(

        items,

        key=lambda item:

        item.properties.get(
            "eo:cloud_cover",
            100,
        ),
    )


    return sorted_items[0]


# ============================================================
# DISPLAY AVAILABLE ASSETS
# ============================================================

def display_assets(item):

    print(
        "\n===== AVAILABLE SENTINEL ASSETS ====="
    )


    for asset_name, asset in item.assets.items():

        print(
            f"{asset_name}: {asset.title}"
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "\n===== SENTINEL-2 DYNAMIC LOCATION SEARCH ====="
    )


    # ========================================================
    # GET LOCATION INPUT
    # ========================================================

    location_name = input(
        "\nEnter location in India: "
    ).strip()


    if not location_name:

        print(
            "\nERROR: Location cannot be empty."
        )

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
    # DISPLAY LOCATION INFORMATION
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
        round(
            geocoding_time,
            4,
        ),
        "seconds",
    )


    # ========================================================
    # CREATE SEARCH BOUNDS
    # ========================================================

    bounding_box = create_search_bounds(
        latitude,
        longitude,
    )


    print(
        "\n===== SENTINEL SEARCH BOUNDS ====="
    )


    print(
        "West:",
        bounding_box[0],
    )


    print(
        "South:",
        bounding_box[1],
    )


    print(
        "East:",
        bounding_box[2],
    )


    print(
        "North:",
        bounding_box[3],
    )


    # ========================================================
    # SEARCH SENTINEL
    # ========================================================

    items, search_time = search_sentinel_data(
        bounding_box
    )


    # ========================================================
    # CHECK RESULTS
    # ========================================================

    print(
        "\n===== SEARCH RESULTS ====="
    )


    print(
        "Scenes Found:",
        len(items),
    )


    print(
        "Search Time:",
        round(
            search_time,
            4,
        ),
        "seconds",
    )


    if not items:

        print(
            "\nNo suitable Sentinel-2 scenes found."
        )

        return


    # ========================================================
    # DISPLAY ALL FOUND SCENES
    # ========================================================

    print(
        "\n===== FOUND SENTINEL SCENES ====="
    )


    for index, item in enumerate(
        items,
        start=1,
    ):

        cloud_cover = (
            item.properties.get(
                "eo:cloud_cover",
                "Unknown",
            )
        )


        print(
            f"\nScene {index}"
        )


        print(
            "Scene ID:",
            item.id,
        )


        print(
            "Date:",
            item.datetime,
        )


        print(
            "Cloud Cover:",
            cloud_cover,
            "%",
        )


    # ========================================================
    # SELECT BEST SCENE
    # ========================================================

    best_scene = select_best_scene(
        items
    )


    print(
        "\n===== BEST SENTINEL SCENE ====="
    )


    print(
        "Scene ID:",
        best_scene.id,
    )


    print(
        "Date:",
        best_scene.datetime,
    )


    print(
        "Cloud Cover:",
        best_scene.properties.get(
            "eo:cloud_cover",
            "Unknown",
        ),
        "%",
    )


    # ========================================================
    # DISPLAY ASSETS
    # ========================================================

    display_assets(
        best_scene
    )


    print(
        "\n===== SENTINEL SEARCH COMPLETED SUCCESSFULLY ====="
    )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()