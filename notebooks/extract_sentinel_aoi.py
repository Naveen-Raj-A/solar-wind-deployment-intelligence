import os
import time

import planetary_computer
import rasterio
import requests
from pystac_client import Client
from rasterio.mask import mask
from rasterio.warp import transform_geom
from shapely.geometry import box, mapping


# ============================================================
# CONFIGURATION
# ============================================================

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

SENTINEL_COLLECTION = "sentinel-2-l2a"

OUTPUT_DIRECTORY = os.path.join(
    "datasets",
    "sentinel",
    "aoi",
)

SEARCH_OFFSET = 0.05

MAX_CLOUD_COVER = 20

DATE_RANGE = "2025-01-01/2026-12-31"

MAX_RESULTS = 20

REQUIRED_ASSETS = [
    "B04",
    "B08",
    "B11",
    "SCL",
]


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIRECTORY,
    exist_ok=True,
)


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

        geocoding_time = (
            time.time() - start_time
        )

        if not results:

            print(
                "\nERROR: Location not found in India."
            )

            return None

        result = results[0]

        return (
            result["display_name"],
            float(result["lat"]),
            float(result["lon"]),
            geocoding_time,
        )

    except requests.RequestException as error:

        print("\nGeocoding failed.")

        print("Error:", error)

        return None


# ============================================================
# CREATE SEARCH BOUNDS
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
# SEARCH SENTINEL SCENES
# ============================================================

def search_sentinel_scenes(bounding_box):

    print(
        "\nConnecting to Sentinel-2 STAC catalog..."
    )

    catalog = Client.open(
        STAC_URL,
        modifier=planetary_computer.sign_inplace,
    )

    print("Connection successful.")

    print(
        "\nSearching Sentinel-2 imagery..."
    )

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

    items = list(search.items())

    search_time = (
        time.time() - start_time
    )

    return items, search_time


# ============================================================
# SELECT BEST SCENE
# ============================================================

def select_best_scene(items):

    if not items:

        return None

    return min(
        items,
        key=lambda item:
        item.properties.get(
            "eo:cloud_cover",
            100,
        ),
    )


# ============================================================
# CREATE SAFE LOCATION NAME
# ============================================================

def create_safe_location_name(location_name):

    safe_name = ""

    for character in location_name.lower():

        if character.isalnum():

            safe_name += character

        elif character in (" ", "-", "_"):

            safe_name += "_"

    return safe_name.strip("_")


# ============================================================
# EXTRACT ONE SENTINEL ASSET
# ============================================================

def extract_asset(
    item,
    asset_name,
    bounding_box,
    location_directory,
):

    print(
        f"\nProcessing asset: {asset_name}"
    )

    if asset_name not in item.assets:

        print(
            f"ERROR: {asset_name} "
            f"not available in selected scene."
        )

        return False

    # Sign the asset URL
    signed_asset = planetary_computer.sign(
        item.assets[asset_name]
    )

    asset_url = signed_asset.href

    output_path = os.path.join(
        location_directory,
        f"{asset_name}.tif",
    )

    try:

        start_time = time.time()

        # Open remote Cloud Optimized GeoTIFF
        with rasterio.open(asset_url) as source:

            print(
                "Source CRS:",
                source.crs,
            )

            print(
                "Source Resolution:",
                source.res,
            )

            # AOI geometry starts in WGS84
            west, south, east, north = bounding_box

            aoi_geometry = mapping(
                box(
                    west,
                    south,
                    east,
                    north,
                )
            )

            # Transform AOI into raster CRS
            transformed_geometry = transform_geom(
                "EPSG:4326",
                source.crs,
                aoi_geometry,
            )

            # Read only the AOI
            output_data, output_transform = mask(
                source,
                [transformed_geometry],
                crop=True,
            )

            output_metadata = source.meta.copy()

            output_metadata.update(
                {
                    "driver": "GTiff",
                    "height": output_data.shape[1],
                    "width": output_data.shape[2],
                    "transform": output_transform,
                    "compress": "deflate",
                }
            )

            with rasterio.open(
                output_path,
                "w",
                **output_metadata,
            ) as destination:

                destination.write(
                    output_data
                )

        elapsed_time = (
            time.time() - start_time
        )

        file_size_mb = (
            os.path.getsize(output_path)
            / (1024 * 1024)
        )

        print(
            "Status: Extraction successful."
        )

        print(
            "Output File:",
            output_path,
        )

        print(
            "File Size:",
            round(file_size_mb, 2),
            "MB",
        )

        print(
            "Processing Time:",
            round(elapsed_time, 2),
            "seconds",
        )

        return True

    except Exception as error:

        print(
            f"ERROR processing {asset_name}:"
        )

        print(error)

        return False


# ============================================================
# VALIDATE OUTPUT FILE
# ============================================================

def validate_output(file_path):

    try:

        with rasterio.open(file_path) as dataset:

            if dataset.count < 1:

                return False

            if dataset.width <= 0:

                return False

            if dataset.height <= 0:

                return False

        return True

    except rasterio.errors.RasterioIOError:

        return False


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "\n===== SENTINEL-2 AOI EXTRACTION ====="
    )

    # --------------------------------------------------------
    # LOCATION INPUT
    # --------------------------------------------------------

    location_name = input(
        "\nEnter location in India: "
    ).strip()

    if not location_name:

        print(
            "\nERROR: Location cannot be empty."
        )

        return

    # --------------------------------------------------------
    # GEOCODING
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SEARCH BOUNDS
    # --------------------------------------------------------

    bounding_box = create_search_bounds(
        latitude,
        longitude,
    )

    print(
        "\n===== SEARCH BOUNDS ====="
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

    # --------------------------------------------------------
    # SENTINEL SEARCH
    # --------------------------------------------------------

    try:

        items, search_time = search_sentinel_scenes(
            bounding_box
        )

    except Exception as error:

        print(
            "\nSentinel search failed."
        )

        print(
            "Error:",
            error,
        )

        return

    print(
        "\n===== SEARCH RESULTS ====="
    )

    print(
        "Scenes Found:",
        len(items),
    )

    print(
        "Search Time:",
        round(search_time, 4),
        "seconds",
    )

    if not items:

        print(
            "\nNo suitable scenes found."
        )

        return

    # --------------------------------------------------------
    # BEST SCENE
    # --------------------------------------------------------

    best_scene = select_best_scene(
        items
    )

    print(
        "\n===== SELECTED SENTINEL SCENE ====="
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

    # --------------------------------------------------------
    # LOCATION OUTPUT DIRECTORY
    # --------------------------------------------------------

    safe_location_name = (
        create_safe_location_name(
            location_name
        )
    )

    location_directory = os.path.join(
        OUTPUT_DIRECTORY,
        safe_location_name,
    )

    os.makedirs(
        location_directory,
        exist_ok=True,
    )

    print(
        "\nOutput Directory:",
        location_directory,
    )

    # --------------------------------------------------------
    # EXTRACT REQUIRED ASSETS
    # --------------------------------------------------------

    successful_assets = 0

    failed_assets = 0

    total_start_time = time.time()

    print(
        "\n===== STARTING AOI EXTRACTION ====="
    )

    for asset_name in REQUIRED_ASSETS:

        success = extract_asset(
            best_scene,
            asset_name,
            bounding_box,
            location_directory,
        )

        if success:

            successful_assets += 1

        else:

            failed_assets += 1

    total_time = (
        time.time() - total_start_time
    )

    # --------------------------------------------------------
    # VALIDATE OUTPUTS
    # --------------------------------------------------------

    print(
        "\n===== OUTPUT VALIDATION ====="
    )

    valid_files = 0

    for asset_name in REQUIRED_ASSETS:

        file_path = os.path.join(
            location_directory,
            f"{asset_name}.tif",
        )

        if (
            os.path.exists(file_path)
            and validate_output(file_path)
        ):

            print(
                f"{asset_name}: VALID"
            )

            valid_files += 1

        else:

            print(
                f"{asset_name}: INVALID OR MISSING"
            )

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print(
        "\n===== SENTINEL AOI SUMMARY ====="
    )

    print(
        "Requested Assets:",
        len(REQUIRED_ASSETS),
    )

    print(
        "Successful Extractions:",
        successful_assets,
    )

    print(
        "Failed Extractions:",
        failed_assets,
    )

    print(
        "Validated Files:",
        valid_files,
    )

    print(
        "Total Extraction Time:",
        round(total_time, 2),
        "seconds",
    )

    if valid_files == len(REQUIRED_ASSETS):

        print(
            "\n===== SENTINEL AOI EXTRACTION "
            "COMPLETED SUCCESSFULLY ====="
        )

    else:

        print(
            "\n===== SENTINEL AOI EXTRACTION "
            "COMPLETED WITH ERRORS ====="
        )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()