"""
Unified Sentinel-2 extraction and analysis module.

Generated from the project's existing extract_sentinel_aoi.py and
analyze_sentinel_data.py implementations for integration with start_engine.py.
"""

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


import json
import os
import time

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject


# ============================================================
# CONFIGURATION
# ============================================================

SENTINEL_DIRECTORY = os.path.join(
    "datasets",
    "sentinel",
    "aoi",
)

PROCESSED_DIRECTORY = os.path.join(
    "datasets",
    "sentinel",
    "processed",
)

os.makedirs(
    PROCESSED_DIRECTORY,
    exist_ok=True,
)


# ============================================================
# SENTINEL SCL CLASS NAMES
# ============================================================

SCL_CLASSES = {
    0: "No Data",
    1: "Saturated or Defective",
    2: "Dark Area Pixels",
    3: "Cloud Shadows",
    4: "Vegetation",
    5: "Bare Soil / Non-Vegetated",
    6: "Water",
    7: "Unclassified",
    8: "Cloud Medium Probability",
    9: "Cloud High Probability",
    10: "Thin Cirrus",
    11: "Snow or Ice",
}


# ============================================================
# INVALID SCL CLASSES
# ============================================================

INVALID_SCL_CLASSES = [
    0,
    1,
    3,
    8,
    9,
    10,
    11,
]


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
# CHECK REQUIRED FILES
# ============================================================

def check_required_files(location_directory):

    required_files = {
        "B04": os.path.join(
            location_directory,
            "B04.tif",
        ),
        "B08": os.path.join(
            location_directory,
            "B08.tif",
        ),
        "B11": os.path.join(
            location_directory,
            "B11.tif",
        ),
        "SCL": os.path.join(
            location_directory,
            "SCL.tif",
        ),
    }

    print(
        "\n===== CHECKING REQUIRED FILES ====="
    )

    all_files_exist = True

    for asset_name, file_path in required_files.items():

        if os.path.exists(file_path):

            print(
                f"{asset_name}: FOUND"
            )

        else:

            print(
                f"{asset_name}: MISSING"
            )

            all_files_exist = False

    return required_files, all_files_exist


# ============================================================
# DISPLAY RASTER INFORMATION
# ============================================================

def display_raster_information(required_files):

    print(
        "\n===== INPUT RASTER INFORMATION ====="
    )

    for asset_name, file_path in required_files.items():

        with rasterio.open(file_path) as dataset:

            print(
                f"\n{asset_name}"
            )

            print(
                "CRS:",
                dataset.crs,
            )

            print(
                "Width:",
                dataset.width,
            )

            print(
                "Height:",
                dataset.height,
            )

            print(
                "Resolution:",
                dataset.res,
            )

            print(
                "Data Type:",
                dataset.dtypes[0],
            )


# ============================================================
# READ REFERENCE RASTER
# ============================================================

def read_reference_raster(file_path):

    with rasterio.open(file_path) as dataset:

        data = dataset.read(1)

        profile = dataset.profile.copy()

        transform = dataset.transform

        crs = dataset.crs

        width = dataset.width

        height = dataset.height

    return (
        data,
        profile,
        transform,
        crs,
        width,
        height,
    )


# ============================================================
# ALIGN RASTER TO REFERENCE GRID
# ============================================================

def align_raster_to_reference(
    source_file,
    reference_transform,
    reference_crs,
    reference_width,
    reference_height,
    resampling_method,
):

    with rasterio.open(source_file) as source:

        destination = np.zeros(
            (
                reference_height,
                reference_width,
            ),
            dtype=source.dtypes[0],
        )

        reproject(
            source=source.read(1),

            destination=destination,

            src_transform=source.transform,

            src_crs=source.crs,

            dst_transform=reference_transform,

            dst_crs=reference_crs,

            dst_width=reference_width,

            dst_height=reference_height,

            resampling=resampling_method,
        )

    return destination


# ============================================================
# SAVE FLOAT RASTER
# ============================================================

def save_float_raster(
    output_path,
    data,
    reference_profile,
):

    output_profile = reference_profile.copy()

    output_profile.update(
        {
            "driver": "GTiff",
            "dtype": "float32",
            "count": 1,
            "nodata": -9999.0,
            "compress": "deflate",
        }
    )

    output_data = data.astype(
        np.float32
    )

    output_data[
        ~np.isfinite(output_data)
    ] = -9999.0

    with rasterio.open(
        output_path,
        "w",
        **output_profile,
    ) as destination:

        destination.write(
            output_data,
            1,
        )


# ============================================================
# CALCULATE STATISTICS
# ============================================================

def calculate_index_statistics(
    data,
    valid_mask,
):

    valid_values = data[
        valid_mask
        & np.isfinite(data)
    ]

    if valid_values.size == 0:

        return {
            "minimum": None,
            "maximum": None,
            "mean": None,
            "median": None,
            "standard_deviation": None,
        }

    return {
        "minimum": float(
            np.min(valid_values)
        ),
        "maximum": float(
            np.max(valid_values)
        ),
        "mean": float(
            np.mean(valid_values)
        ),
        "median": float(
            np.median(valid_values)
        ),
        "standard_deviation": float(
            np.std(valid_values)
        ),
    }


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "\n===== SENTINEL-2 LAND ANALYSIS ====="
    )

    # --------------------------------------------------------
    # LOCATION INPUT
    # --------------------------------------------------------

    location_name = input(
        "\nEnter previously extracted location: "
    ).strip()

    if not location_name:

        print(
            "\nERROR: Location cannot be empty."
        )

        return

    safe_location_name = (
        create_safe_location_name(
            location_name
        )
    )

    location_directory = os.path.join(
        SENTINEL_DIRECTORY,
        safe_location_name,
    )

    output_directory = os.path.join(
        PROCESSED_DIRECTORY,
        safe_location_name,
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    print(
        "\nInput Directory:",
        location_directory,
    )

    print(
        "Output Directory:",
        output_directory,
    )

    # --------------------------------------------------------
    # CHECK INPUT FILES
    # --------------------------------------------------------

    required_files, files_exist = (
        check_required_files(
            location_directory
        )
    )

    if not files_exist:

        print(
            "\nERROR: Required Sentinel files are missing."
        )

        return

    # --------------------------------------------------------
    # DISPLAY RASTER INFORMATION
    # --------------------------------------------------------

    display_raster_information(
        required_files
    )

    total_start_time = time.time()

    # --------------------------------------------------------
    # READ B04 AS REFERENCE GRID
    # --------------------------------------------------------

    print(
        "\n===== READING REFERENCE GRID ====="
    )

    (
        red,
        reference_profile,
        reference_transform,
        reference_crs,
        reference_width,
        reference_height,

    ) = read_reference_raster(
        required_files["B04"]
    )

    print(
        "Reference Asset: B04"
    )

    print(
        "Reference Resolution:",
        reference_profile["transform"].a,
        "meters",
    )

    print(
        "Reference Shape:",
        red.shape,
    )

    # --------------------------------------------------------
    # READ B08
    # --------------------------------------------------------

    print(
        "\nReading B08..."
    )

    with rasterio.open(
        required_files["B08"]
    ) as dataset:

        nir = dataset.read(1)

    # --------------------------------------------------------
    # ALIGN B11
    # --------------------------------------------------------

    print(
        "Aligning B11 from 20 m to 10 m grid..."
    )

    swir = align_raster_to_reference(
        source_file=required_files["B11"],
        reference_transform=reference_transform,
        reference_crs=reference_crs,
        reference_width=reference_width,
        reference_height=reference_height,
        resampling_method=Resampling.bilinear,
    )

    # --------------------------------------------------------
    # ALIGN SCL
    # --------------------------------------------------------

    print(
        "Aligning SCL from 20 m to 10 m grid..."
    )

    scl = align_raster_to_reference(
        source_file=required_files["SCL"],
        reference_transform=reference_transform,
        reference_crs=reference_crs,
        reference_width=reference_width,
        reference_height=reference_height,
        resampling_method=Resampling.nearest,
    )

    print(
        "\nRaster alignment completed."
    )

    print(
        "B04 Shape:",
        red.shape,
    )

    print(
        "B08 Shape:",
        nir.shape,
    )

    print(
        "B11 Shape:",
        swir.shape,
    )

    print(
        "SCL Shape:",
        scl.shape,
    )

    # --------------------------------------------------------
    # CREATE VALID PIXEL MASK
    # --------------------------------------------------------

    print(
        "\n===== CREATING VALID PIXEL MASK ====="
    )

    invalid_mask = np.isin(
        scl,
        INVALID_SCL_CLASSES,
    )

    valid_mask = ~invalid_mask

    valid_pixel_count = int(
        np.sum(valid_mask)
    )

    total_pixel_count = int(
        valid_mask.size
    )

    invalid_pixel_count = (
        total_pixel_count
        - valid_pixel_count
    )

    valid_percentage = (
        valid_pixel_count
        / total_pixel_count
        * 100
    )

    print(
        "Total Pixels:",
        total_pixel_count,
    )

    print(
        "Valid Pixels:",
        valid_pixel_count,
    )

    print(
        "Invalid / Cloud Pixels:",
        invalid_pixel_count,
    )

    print(
        "Valid Percentage:",
        round(valid_percentage, 2),
        "%",
    )

    # --------------------------------------------------------
    # CONVERT BANDS TO FLOAT
    # --------------------------------------------------------

    red_float = red.astype(
        np.float32
    )

    nir_float = nir.astype(
        np.float32
    )

    swir_float = swir.astype(
        np.float32
    )

    # --------------------------------------------------------
    # CALCULATE NDVI
    # --------------------------------------------------------

    print(
        "\n===== CALCULATING NDVI ====="
    )

    ndvi_denominator = (
        nir_float + red_float
    )

    ndvi = np.full(
        red.shape,
        np.nan,
        dtype=np.float32,
    )

    ndvi_calculation_mask = (
        valid_mask
        & (ndvi_denominator != 0)
    )

    ndvi[
        ndvi_calculation_mask
    ] = (

        (
            nir_float[
                ndvi_calculation_mask
            ]
            -
            red_float[
                ndvi_calculation_mask
            ]
        )

        /

        ndvi_denominator[
            ndvi_calculation_mask
        ]
    )

    # --------------------------------------------------------
    # CALCULATE NDMI
    # --------------------------------------------------------

    print(
        "Calculating NDMI..."
    )

    ndmi_denominator = (
        nir_float + swir_float
    )

    ndmi = np.full(
        red.shape,
        np.nan,
        dtype=np.float32,
    )

    ndmi_calculation_mask = (
        valid_mask
        & (ndmi_denominator != 0)
    )

    ndmi[
        ndmi_calculation_mask
    ] = (

        (
            nir_float[
                ndmi_calculation_mask
            ]
            -
            swir_float[
                ndmi_calculation_mask
            ]
        )

        /

        ndmi_denominator[
            ndmi_calculation_mask
        ]
    )

    # --------------------------------------------------------
    # CALCULATE INDEX STATISTICS
    # --------------------------------------------------------

    ndvi_statistics = (
        calculate_index_statistics(
            ndvi,
            valid_mask,
        )
    )

    ndmi_statistics = (
        calculate_index_statistics(
            ndmi,
            valid_mask,
        )
    )

    print(
        "\n===== NDVI STATISTICS ====="
    )

    for key, value in ndvi_statistics.items():

        print(
            f"{key}:",
            value,
        )

    print(
        "\n===== NDMI STATISTICS ====="
    )

    for key, value in ndmi_statistics.items():

        print(
            f"{key}:",
            value,
        )

    # --------------------------------------------------------
    # SCL LAND-COVER STATISTICS
    # --------------------------------------------------------

    print(
        "\n===== SCL LAND-COVER STATISTICS ====="
    )

    unique_classes, class_counts = np.unique(
        scl,
        return_counts=True,
    )

    scl_statistics = {}

    for class_value, class_count in zip(
        unique_classes,
        class_counts,
    ):

        class_value = int(class_value)

        class_count = int(class_count)

        class_name = SCL_CLASSES.get(
            class_value,
            "Unknown",
        )

        percentage = (
            class_count
            / total_pixel_count
            * 100
        )

        scl_statistics[
            str(class_value)
        ] = {
            "class_name": class_name,
            "pixel_count": class_count,
            "percentage": float(
                percentage
            ),
        }

        print(
            f"{class_value} - "
            f"{class_name}: "
            f"{class_count} pixels "
            f"({percentage:.2f}%)"
        )

    # --------------------------------------------------------
    # SAVE NDVI
    # --------------------------------------------------------

    print(
        "\n===== SAVING PROCESSED OUTPUTS ====="
    )

    ndvi_output_path = os.path.join(
        output_directory,
        "ndvi.tif",
    )

    save_float_raster(
        ndvi_output_path,
        ndvi,
        reference_profile,
    )

    print(
        "Saved:",
        ndvi_output_path,
    )

    # --------------------------------------------------------
    # SAVE NDMI
    # --------------------------------------------------------

    ndmi_output_path = os.path.join(
        output_directory,
        "ndmi.tif",
    )

    save_float_raster(
        ndmi_output_path,
        ndmi,
        reference_profile,
    )

    print(
        "Saved:",
        ndmi_output_path,
    )

    # --------------------------------------------------------
    # SAVE ANALYSIS SUMMARY
    # --------------------------------------------------------

    analysis_summary = {
        "location": location_name,
        "total_pixels": total_pixel_count,
        "valid_pixels": valid_pixel_count,
        "invalid_pixels": invalid_pixel_count,
        "valid_percentage": float(
            valid_percentage
        ),
        "ndvi_statistics": ndvi_statistics,
        "ndmi_statistics": ndmi_statistics,
        "scl_statistics": scl_statistics,
    }

    summary_output_path = os.path.join(
        output_directory,
        "sentinel_analysis_summary.json",
    )

    with open(
        summary_output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            analysis_summary,
            file,
            indent=4,
        )

    print(
        "Saved:",
        summary_output_path,
    )

    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    print(
        "\n===== OUTPUT VALIDATION ====="
    )

    output_files = [
        ndvi_output_path,
        ndmi_output_path,
        summary_output_path,
    ]

    valid_output_count = 0

    for output_file in output_files:

        if (
            os.path.exists(output_file)
            and os.path.getsize(output_file) > 0
        ):

            print(
                os.path.basename(output_file),
                ": VALID",
            )

            valid_output_count += 1

        else:

            print(
                os.path.basename(output_file),
                ": INVALID",
            )

    total_processing_time = (
        time.time() - total_start_time
    )

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print(
        "\n===== SENTINEL ANALYSIS SUMMARY ====="
    )

    print(
        "Location:",
        location_name,
    )

    print(
        "Valid Pixel Percentage:",
        round(valid_percentage, 2),
        "%",
    )

    print(
        "Mean NDVI:",
        ndvi_statistics["mean"],
    )

    print(
        "Mean NDMI:",
        ndmi_statistics["mean"],
    )

    print(
        "Valid Output Files:",
        f"{valid_output_count}/3",
    )

    print(
        "Total Processing Time:",
        round(total_processing_time, 2),
        "seconds",
    )

    if valid_output_count == 3:

        print(
            "\n===== SENTINEL ANALYSIS "
            "COMPLETED SUCCESSFULLY ====="
        )

    else:

        print(
            "\n===== SENTINEL ANALYSIS "
            "COMPLETED WITH ERRORS ====="
        )


# ============================================================
# RUN PROGRAM
# ============================================================