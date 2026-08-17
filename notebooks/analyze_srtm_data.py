import json
import math
import re
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.mask import mask
from rasterio.merge import merge
from shapely.geometry import box, mapping

from engine.site_information import (
    SiteInformation,
    validate_coordinates,
)

from engine.input_handler import (
    get_site_information,
)

# ==================================================
# CONFIGURATION
# ==================================================

SRTM_DIRECTORY = Path(
    "datasets/srtm/raw_tiles"
)

OUTPUT_BASE_DIRECTORY = Path(
    "datasets/srtm/processed"
)

OUTPUT_ELEVATION_FILE_NAME = (
    "elevation.tif"
)

OUTPUT_SLOPE_FILE_NAME = (
    "slope.tif"
)

OUTPUT_SUMMARY_FILE_NAME = (
    "srtm_analysis_summary.json"
)

AOI_OFFSET_DEGREES = 0.05

EXPECTED_CRS = "EPSG:4326"



# ==================================================
# CREATE SAFE LOCATION NAME
# ==================================================

def create_safe_location_name(
    location_name,
):

    safe_name = (
        str(location_name)
        .strip()
        .lower()
    )

    safe_name = re.sub(
        r"[^a-z0-9]+",
        "_",
        safe_name,
    )

    safe_name = safe_name.strip("_")

    if not safe_name:

        safe_name = "site"

    return safe_name


# ==================================================
# VALIDATE COORDINATES
# ==================================================

# ==================================================
# CREATE AOI BOUNDS
# ==================================================

def create_aoi_bounds(
    latitude,
    longitude,
):

    west = (
        longitude
        - AOI_OFFSET_DEGREES
    )

    south = (
        latitude
        - AOI_OFFSET_DEGREES
    )

    east = (
        longitude
        + AOI_OFFSET_DEGREES
    )

    north = (
        latitude
        + AOI_OFFSET_DEGREES
    )

    return (
        west,
        south,
        east,
        north,
    )


# ==================================================
# FIND INTERSECTING SRTM TILES
# ==================================================

def find_intersecting_tiles(
    aoi_geometry,
    display_output=True,
):

    if display_output:

        print(
            "\n===== SEARCHING SRTM TILES ====="
        )

    if not SRTM_DIRECTORY.exists():

        raise FileNotFoundError(
            "SRTM raw tile directory "
            "was not found: "
            f"{SRTM_DIRECTORY}"
        )

    srtm_files = sorted(
        SRTM_DIRECTORY.glob(
            "*.tif"
        )
    )

    if display_output:

        print(
            "Available SRTM Tiles:",
            len(srtm_files),
        )

    if not srtm_files:

        raise FileNotFoundError(
            "No SRTM GeoTIFF files "
            "were found in: "
            f"{SRTM_DIRECTORY}"
        )

    intersecting_tiles = []

    for file_path in srtm_files:

        try:

            with rasterio.open(
                file_path
            ) as dataset:

                if dataset.crs is None:

                    continue

                raster_bounds = box(

                    dataset.bounds.left,

                    dataset.bounds.bottom,

                    dataset.bounds.right,

                    dataset.bounds.top,
                )

                if raster_bounds.intersects(
                    aoi_geometry
                ):

                    intersecting_tiles.append(
                        file_path
                    )

        except (
            rasterio.errors.RasterioIOError
        ):

            if display_output:

                print(
                    "Warning: Could not open:",
                    file_path.name,
                )

    return intersecting_tiles


# ==================================================
# MERGE SRTM TILES
# ==================================================

def merge_srtm_tiles(
    tile_paths,
    display_output=True,
):

    if not tile_paths:

        raise ValueError(
            "No SRTM tiles were supplied "
            "for merging."
        )

    if display_output:

        print(
            "\n===== MERGING SRTM TILES ====="
        )

    source_datasets = []

    try:

        for tile_path in tile_paths:

            dataset = rasterio.open(
                tile_path
            )

            if dataset.crs is None:

                dataset.close()

                raise ValueError(
                    "SRTM tile has no CRS: "
                    f"{tile_path}"
                )

            source_datasets.append(
                dataset
            )

        source_crs = (
            source_datasets[0].crs
        )

        for dataset in source_datasets:

            if dataset.crs != source_crs:

                raise ValueError(
                    "Intersecting SRTM tiles "
                    "do not use the same CRS."
                )

        merged_data, merged_transform = (
            merge(
                source_datasets
            )
        )

        merged_metadata = (
            source_datasets[
                0
            ].meta.copy()
        )

        merged_metadata.update(
            {
                "driver": "GTiff",

                "height": int(
                    merged_data.shape[1]
                ),

                "width": int(
                    merged_data.shape[2]
                ),

                "transform": (
                    merged_transform
                ),

                "count": int(
                    merged_data.shape[0]
                ),
            }
        )

        if display_output:

            print(
                "Merged Shape:",
                merged_data.shape,
            )

            print(
                "Merge Status: SUCCESSFUL"
            )

        return (
            merged_data,
            merged_transform,
            merged_metadata,
        )

    finally:

        for dataset in source_datasets:

            dataset.close()


# ==================================================
# CLIP MERGED DATA IN MEMORY
# ==================================================

def clip_merged_data_to_aoi(
    merged_data,
    merged_metadata,
    aoi_geometry,
    display_output=True,
):

    if display_output:

        print(
            "\n===== EXTRACTING SRTM AOI ====="
        )

    memory_metadata = (
        merged_metadata.copy()
    )

    memory_metadata.update(
        {
            "driver": "GTiff",

            "height": int(
                merged_data.shape[1]
            ),

            "width": int(
                merged_data.shape[2]
            ),

            "count": int(
                merged_data.shape[0]
            ),
        }
    )

    with MemoryFile() as memory_file:

        with memory_file.open(
            **memory_metadata
        ) as memory_dataset:

            memory_dataset.write(
                merged_data
            )

            clipped_data, clipped_transform = (
                mask(
                    memory_dataset,
                    [
                        mapping(
                            aoi_geometry
                        )
                    ],
                    crop=True,
                    filled=False,
                )
            )

            clipped_metadata = (
                memory_dataset.meta.copy()
            )

            clipped_metadata.update(
                {
                    "driver": "GTiff",

                    "height": int(
                        clipped_data.shape[1]
                    ),

                    "width": int(
                        clipped_data.shape[2]
                    ),

                    "transform": (
                        clipped_transform
                    ),

                    "count": int(
                        clipped_data.shape[0]
                    ),
                }
            )

    if clipped_data.size == 0:

        raise ValueError(
            "SRTM AOI extraction "
            "returned empty raster data."
        )

    if clipped_data.shape[0] != 1:

        raise ValueError(
            "Expected one SRTM elevation band, "
            f"but found {clipped_data.shape[0]}."
        )

    if display_output:

        print(
            "Extraction Status: SUCCESSFUL"
        )

    return (
        clipped_data,
        clipped_transform,
        clipped_metadata,
    )


# ==================================================
# CALCULATE ELEVATION STATISTICS
# ==================================================

def calculate_elevation_statistics(
    elevation_data,
):

    valid_data = (
        elevation_data.compressed()
    )

    if valid_data.size == 0:

        return None

    return {

        "minimum_m": float(
            np.min(valid_data)
        ),

        "maximum_m": float(
            np.max(valid_data)
        ),

        "mean_m": float(
            np.mean(valid_data)
        ),

        "median_m": float(
            np.median(valid_data)
        ),

        "standard_deviation_m": float(
            np.std(valid_data)
        ),
    }


# ==================================================
# CALCULATE PIXEL DIMENSIONS IN METERS
# ==================================================

def calculate_pixel_dimensions_meters(
    latitude,
    transform,
):

    latitude_radians = math.radians(
        latitude
    )

    longitude_degree_distance = (
        111320.0
        * math.cos(
            latitude_radians
        )
    )

    latitude_degree_distance = (
        110574.0
    )

    pixel_width_meters = abs(
        transform.a
    ) * longitude_degree_distance

    pixel_height_meters = abs(
        transform.e
    ) * latitude_degree_distance

    if pixel_width_meters <= 0:

        raise ValueError(
            "Invalid SRTM pixel width."
        )

    if pixel_height_meters <= 0:

        raise ValueError(
            "Invalid SRTM pixel height."
        )

    return (
        float(
            pixel_width_meters
        ),
        float(
            pixel_height_meters
        ),
    )


# ==================================================
# CALCULATE SLOPE
# ==================================================

def calculate_slope(elevation_data, pixel_width_meters, pixel_height_meters):
    elevation_mask = np.ma.getmaskarray(elevation_data)
    elevation_array = np.asarray(elevation_data.data, dtype=np.float64).copy()
    elevation_array[elevation_mask] = np.nan
    if np.all(np.isnan(elevation_array)):
        raise ValueError("Elevation raster contains no valid data for slope analysis.")
    gradient_y, gradient_x = np.gradient(elevation_array, pixel_height_meters, pixel_width_meters)
    slope_degrees = np.degrees(np.arctan(np.sqrt(np.square(gradient_x) + np.square(gradient_y))))
    invalid_mask = elevation_mask | np.isnan(slope_degrees)
    return np.ma.array(slope_degrees, mask=invalid_mask)


def calculate_slope_statistics(slope_data):
    valid_data = slope_data.compressed()
    if valid_data.size == 0:
        return None
    return {
        "minimum_degrees": float(np.min(valid_data)),
        "maximum_degrees": float(np.max(valid_data)),
        "mean_degrees": float(np.mean(valid_data)),
        "median_degrees": float(np.median(valid_data)),
        "standard_deviation_degrees": float(np.std(valid_data)),
    }


def classify_terrain(
    slope_data,
):

    valid_values = (
        slope_data.compressed()
    )

    if valid_values.size == 0:

        return None

    flat_cells = int(
        np.sum(
            valid_values < 3.0
        )
    )

    gentle_cells = int(
        np.sum(
            (
                valid_values >= 3.0
            )
            &
            (
                valid_values < 8.0
            )
        )
    )

    moderate_cells = int(
        np.sum(
            (
                valid_values >= 8.0
            )
            &
            (
                valid_values < 15.0
            )
        )
    )

    steep_cells = int(
        np.sum(
            valid_values >= 15.0
        )
    )

    total_classified_cells = int(
        valid_values.size
    )

    def percentage(
        cell_count,
    ):

        return float(
            (
                cell_count
                / total_classified_cells
            )
            * 100
        )

    classified_cell_count = (

        flat_cells

        + gentle_cells

        + moderate_cells

        + steep_cells
    )

    classification_valid = bool(
        classified_cell_count
        == total_classified_cells
    )

    return {

        "flat": {

            "minimum_slope_degrees": None,

            "maximum_slope_degrees": 3.0,

            "cells": flat_cells,

            "percentage": percentage(
                flat_cells
            ),
        },


        "gentle": {

            "minimum_slope_degrees": 3.0,

            "maximum_slope_degrees": 8.0,

            "cells": gentle_cells,

            "percentage": percentage(
                gentle_cells
            ),
        },


        "moderate": {

            "minimum_slope_degrees": 8.0,

            "maximum_slope_degrees": 15.0,

            "cells": moderate_cells,

            "percentage": percentage(
                moderate_cells
            ),
        },


        "steep": {

            "minimum_slope_degrees": 15.0,

            "maximum_slope_degrees": None,

            "cells": steep_cells,

            "percentage": percentage(
                steep_cells
            ),
        },


        "total_classified_cells": (
            classified_cell_count
        ),

        "classification_valid": (
            classification_valid
        ),
    }


# ==================================================
# DETERMINE TERRAIN SUITABILITY
# ==================================================

def determine_terrain_suitability(
    terrain_classification,
):

    flat_percentage = (
        terrain_classification[
            "flat"
        ][
            "percentage"
        ]
    )

    gentle_percentage = (
        terrain_classification[
            "gentle"
        ][
            "percentage"
        ]
    )

    moderate_percentage = (
        terrain_classification[
            "moderate"
        ][
            "percentage"
        ]
    )

    steep_percentage = (
        terrain_classification[
            "steep"
        ][
            "percentage"
        ]
    )

    favorable_percentage = (
        flat_percentage
        + gentle_percentage
    )

    if (
        favorable_percentage >= 80.0
        and steep_percentage < 5.0
    ):

        suitability_class = (
            "HIGHLY SUITABLE"
        )

    elif favorable_percentage >= 60.0:

        suitability_class = (
            "SUITABLE"
        )

    elif (
        favorable_percentage >= 40.0
        and steep_percentage < 30.0
    ):

        suitability_class = (
            "MODERATELY SUITABLE"
        )

    else:

        suitability_class = (
            "CHALLENGING TERRAIN"
        )

    return {

        "suitability_class": (
            suitability_class
        ),

        "favorable_terrain_percentage": float(
            favorable_percentage
        ),

        "moderate_terrain_percentage": float(
            moderate_percentage
        ),

        "steep_terrain_percentage": float(
            steep_percentage
        ),
    }


# ==================================================
# VALIDATE OUTPUT RASTER
# ==================================================

def validate_raster(
    output_path,
):

    if not output_path.exists():

        return False

    if output_path.stat().st_size == 0:

        return False

    try:

        with rasterio.open(
            output_path
        ) as dataset:

            if dataset.count != 1:

                return False

            if dataset.width <= 0:

                return False

            if dataset.height <= 0:

                return False

            data = dataset.read(
                1,
                masked=True,
            )

            if data.count() == 0:

                return False

        return True

    except (
        rasterio.errors.RasterioIOError,
        OSError,
    ):

        return False


# ==================================================
# VALIDATE JSON
# ==================================================

def validate_json(
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

            summary = json.load(
                file
            )

        required_sections = [

            "location",

            "dataset",

            "aoi",

            "pixel_information",

            "elevation_statistics",

            "slope_statistics",

            "terrain_classification",

            "terrain_suitability",
        ]

        for section in required_sections:

            if section not in summary:

                return False

        return True

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return False


# ==================================================
# CONVERT TO JSON SAFE TYPES
# ==================================================

def convert_to_json_safe(
    value,
):

    if isinstance(
        value,
        dict,
    ):

        return {

            str(key): (
                convert_to_json_safe(
                    item
                )
            )

            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (list, tuple),
    ):

        return [

            convert_to_json_safe(
                item
            )

            for item in value
        ]

    if isinstance(
        value,
        np.ndarray,
    ):

        return convert_to_json_safe(
            value.tolist()
        )

    if isinstance(
        value,
        np.bool_,
    ):

        return bool(value)

    if isinstance(
        value,
        np.integer,
    ):

        return int(value)

    if isinstance(
        value,
        np.floating,
    ):

        if np.isnan(value):

            return None

        if np.isinf(value):

            return None

        return float(value)

    if isinstance(
        value,
        float,
    ):

        if math.isnan(value):

            return None

        if math.isinf(value):

            return None

        return value

    return value


# ==================================================
# ANALYZE SRTM
# ==================================================

def analyze_srtm(
    site: SiteInformation,
    save_output=True,
    display_output=True,
):

    processing_start_time = (
        time.time()
    )

    latitude = float(site.latitude)
    longitude = float(site.longitude)

    validate_coordinates(
        latitude,
        longitude,
    )

    requested_location = site.requested_location
    resolved_location = site.resolved_location
    safe_location_name = create_safe_location_name(
    site.requested_location
    )

    if display_output:

        print(
            "\n===== SRTM TERRAIN ANALYSIS ====="
        )

        print(
            "\n===== SITE INFORMATION ====="
        )

        print(
            "Requested Location:",
            requested_location,
        )

        print(
            "Resolved Location:",
            resolved_location,
        )

        print(
            "Latitude:",
            latitude,
        )

        print(
            "Longitude:",
            longitude,
        )


    # ==================================================
    # CHECK RAW SRTM DATASET
    # ==================================================

    if display_output:

        print(
            "\n===== CHECKING SRTM DATASET ====="
        )

    if not SRTM_DIRECTORY.exists():

        raise FileNotFoundError(
            "SRTM raw tile directory "
            "was not found: "
            f"{SRTM_DIRECTORY}"
        )

    available_srtm_tiles = list(
        SRTM_DIRECTORY.glob(
            "*.tif"
        )
    )

    if not available_srtm_tiles:

        raise FileNotFoundError(
            "No SRTM GeoTIFF tiles "
            "were found in: "
            f"{SRTM_DIRECTORY}"
        )

    if display_output:

        print(
            "SRTM Dataset: FOUND"
        )

        print(
            "Raw Tile Directory:",
            SRTM_DIRECTORY,
        )

        print(
            "Available Tiles:",
            len(
                available_srtm_tiles
            ),
        )


    # ==================================================
    # CREATE OUTPUT PATHS
    # ==================================================

    output_directory = (
        OUTPUT_BASE_DIRECTORY
        / safe_location_name
    )

    output_elevation_path = (
        output_directory
        / OUTPUT_ELEVATION_FILE_NAME
    )

    output_slope_path = (
        output_directory
        / OUTPUT_SLOPE_FILE_NAME
    )

    output_summary_path = (
        output_directory
        / OUTPUT_SUMMARY_FILE_NAME
    )

    if save_output:

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    if display_output:

        print(
            "\nOutput Directory:",
            output_directory,
        )


    # ==================================================
    # CREATE AOI
    # ==================================================

    (
        west,
        south,
        east,
        north,
    ) = create_aoi_bounds(
        latitude,
        longitude,
    )

    aoi_geometry = box(
        west,
        south,
        east,
        north,
    )

    if display_output:

        print(
            "\n===== SRTM AOI BOUNDS ====="
        )

        print(
            "West:",
            west,
        )

        print(
            "South:",
            south,
        )

        print(
            "East:",
            east,
        )

        print(
            "North:",
            north,
        )


    # ==================================================
    # FIND INTERSECTING TILES
    # ==================================================

    intersecting_tiles = (
        find_intersecting_tiles(
            aoi_geometry,
            display_output=(
                display_output
            ),
        )
    )

    if display_output:

        print(
            "\nIntersecting SRTM Tiles:",
            len(
                intersecting_tiles
            ),
        )

    if not intersecting_tiles:

        raise ValueError(
            "No SRTM tiles intersect "
            "the requested AOI."
        )

    if display_output:

        print(
            "\n===== SELECTED SRTM TILES ====="
        )

        for index, tile_path in enumerate(
            intersecting_tiles,
            start=1,
        ):

            print(
                f"{index}.",
                tile_path.name,
            )


    # ==================================================
    # MERGE TILES
    # ==================================================

    (
        merged_data,
        merged_transform,
        merged_metadata,
    ) = merge_srtm_tiles(
        intersecting_tiles,
        display_output=(
            display_output
        ),
    )


    # ==================================================
    # CLIP MERGED DATA
    # ==================================================

    (
        clipped_data,
        clipped_transform,
        clipped_metadata,
    ) = clip_merged_data_to_aoi(
        merged_data=(
            merged_data
        ),
        merged_metadata=(
            merged_metadata
        ),
        aoi_geometry=(
            aoi_geometry
        ),
        display_output=(
            display_output
        ),
    )

    del merged_data


    # ==================================================
    # EXTRACT ELEVATION BAND
    # ==================================================

    elevation_data = (
        clipped_data[0]
    )

    elevation_data = (
        np.ma.masked_invalid(
            elevation_data
        )
    )


    # ==================================================
    # CALCULATE PIXEL INFORMATION
    # ==================================================

    total_cells = int(
        elevation_data.size
    )

    valid_cells = int(
        elevation_data.count()
    )

    nodata_cells = int(
        total_cells
        - valid_cells
    )

    if total_cells > 0:

        valid_percentage = float(
            (
                valid_cells
                / total_cells
            )
            * 100
        )

    else:

        valid_percentage = 0.0

    if valid_cells == 0:

        raise ValueError(
            "Extracted SRTM AOI contains "
            "no valid elevation cells."
        )

    if display_output:

        print(
            "\n===== ELEVATION PIXEL INFORMATION ====="
        )

        print(
            "Total Cells:",
            total_cells,
        )

        print(
            "Valid Elevation Cells:",
            valid_cells,
        )

        print(
            "NoData Cells:",
            nodata_cells,
        )

        print(
            "Valid Percentage:",
            round(
                valid_percentage,
                2,
            ),
            "%",
        )


    # ==================================================
    # ELEVATION STATISTICS
    # ==================================================

    elevation_statistics = (
        calculate_elevation_statistics(
            elevation_data
        )
    )

    if elevation_statistics is None:

        raise ValueError(
            "Unable to calculate "
            "elevation statistics."
        )

    if display_output:

        print(
            "\n===== ELEVATION STATISTICS ====="
        )

        print(
            "Minimum Elevation:",
            round(
                elevation_statistics[
                    "minimum_m"
                ],
                2,
            ),
            "meters",
        )

        print(
            "Maximum Elevation:",
            round(
                elevation_statistics[
                    "maximum_m"
                ],
                2,
            ),
            "meters",
        )

        print(
            "Mean Elevation:",
            round(
                elevation_statistics[
                    "mean_m"
                ],
                2,
            ),
            "meters",
        )

        print(
            "Median Elevation:",
            round(
                elevation_statistics[
                    "median_m"
                ],
                2,
            ),
            "meters",
        )

        print(
            "Standard Deviation:",
            round(
                elevation_statistics[
                    "standard_deviation_m"
                ],
                2,
            ),
            "meters",
        )


    # ==================================================
    # CALCULATE PIXEL DIMENSIONS
    # ==================================================

    (
        pixel_width_meters,
        pixel_height_meters,
    ) = calculate_pixel_dimensions_meters(
        latitude,
        clipped_transform,
    )

    if display_output:

        print(
            "\n===== PIXEL DIMENSIONS ====="
        )

        print(
            "Pixel Width:",
            round(
                pixel_width_meters,
                4,
            ),
            "meters",
        )

        print(
            "Pixel Height:",
            round(
                pixel_height_meters,
                4,
            ),
            "meters",
        )


    # ==================================================
    # CALCULATE SLOPE
    # ==================================================

    if display_output:

        print(
            "\n===== CALCULATING SLOPE ====="
        )

    slope_data = calculate_slope(
        elevation_data=(
            elevation_data
        ),
        pixel_width_meters=(
            pixel_width_meters
        ),
        pixel_height_meters=(
            pixel_height_meters
        ),
    )

    if display_output:

        print(
            "Slope Calculation: COMPLETED"
        )


    # ==================================================
    # SLOPE STATISTICS
    # ==================================================

    slope_statistics = (
        calculate_slope_statistics(
            slope_data
        )
    )

    if slope_statistics is None:

        raise ValueError(
            "Unable to calculate "
            "slope statistics."
        )

    if display_output:

        print(
            "\n===== SLOPE STATISTICS ====="
        )

        print(
            "Minimum Slope:",
            round(
                slope_statistics[
                    "minimum_degrees"
                ],
                4,
            ),
            "degrees",
        )

        print(
            "Maximum Slope:",
            round(
                slope_statistics[
                    "maximum_degrees"
                ],
                4,
            ),
            "degrees",
        )

        print(
            "Mean Slope:",
            round(
                slope_statistics[
                    "mean_degrees"
                ],
                4,
            ),
            "degrees",
        )

        print(
            "Median Slope:",
            round(
                slope_statistics[
                    "median_degrees"
                ],
                4,
            ),
            "degrees",
        )


    # ==================================================
    # CLASSIFY TERRAIN
    # ==================================================

    terrain_classification = (
        classify_terrain(
            slope_data
        )
    )

    if terrain_classification is None:

        raise ValueError(
            "Unable to classify terrain."
        )

    if display_output:

        print(
            "\n===== TERRAIN CLASSIFICATION ====="
        )

        print(
            "Flat Terrain (< 3°):",
            terrain_classification[
                "flat"
            ][
                "cells"
            ],
            "cells "
            f"({terrain_classification['flat']['percentage']:.2f}%)",
        )

        print(
            "Gentle Terrain (>= 3° and < 8°):",
            terrain_classification[
                "gentle"
            ][
                "cells"
            ],
            "cells "
            f"({terrain_classification['gentle']['percentage']:.2f}%)",
        )

        print(
            "Moderate Terrain "
            "(>= 8° and < 15°):",
            terrain_classification[
                "moderate"
            ][
                "cells"
            ],
            "cells "
            f"({terrain_classification['moderate']['percentage']:.2f}%)",
        )

        print(
            "Steep Terrain (>= 15°):",
            terrain_classification[
                "steep"
            ][
                "cells"
            ],
            "cells "
            f"({terrain_classification['steep']['percentage']:.2f}%)",
        )

        print(
            "Classification Validation:",
            (
                "PASSED"
                if terrain_classification[
                    "classification_valid"
                ]
                else "FAILED"
            ),
        )


    # ==================================================
    # DETERMINE TERRAIN SUITABILITY
    # ==================================================

    terrain_suitability = (
        determine_terrain_suitability(
            terrain_classification
        )
    )

    if display_output:

        print(
            "\n===== TERRAIN SUITABILITY ====="
        )

        print(
            "Terrain Suitability:",
            terrain_suitability[
                "suitability_class"
            ],
        )

        print(
            "Favorable Terrain:",
            round(
                terrain_suitability[
                    "favorable_terrain_percentage"
                ],
                2,
            ),
            "%",
        )


    # ==================================================
    # CREATE ANALYSIS SUMMARY
    # ==================================================

    analysis_summary = {

        "location": {

            "requested_location": (
                requested_location
            ),

            "resolved_location": (
                resolved_location
            ),

            "latitude": latitude,

            "longitude": longitude,
        },


        "dataset": {

            "raw_tile_directory": str(
                SRTM_DIRECTORY
            ),

            "available_tile_count": int(
                len(
                    available_srtm_tiles
                )
            ),

            "intersecting_tile_count": int(
                len(
                    intersecting_tiles
                )
            ),

            "intersecting_tiles": [

                tile.name

                for tile in (
                    intersecting_tiles
                )
            ],

            "crs": str(
                clipped_metadata.get(
                    "crs"
                )
            ),

            "data_type": str(
                clipped_metadata.get(
                    "dtype"
                )
            ),

            "nodata_value": (
                clipped_metadata.get(
                    "nodata"
                )
            ),

            "aoi_offset_degrees": (
                AOI_OFFSET_DEGREES
            ),
        },


        "aoi": {

            "west": float(
                west
            ),

            "south": float(
                south
            ),

            "east": float(
                east
            ),

            "north": float(
                north
            ),
        },


        "pixel_information": {

            "total_cells": (
                total_cells
            ),

            "valid_elevation_cells": (
                valid_cells
            ),

            "nodata_cells": (
                nodata_cells
            ),

            "valid_percentage": (
                valid_percentage
            ),

            "pixel_width_meters": (
                pixel_width_meters
            ),

            "pixel_height_meters": (
                pixel_height_meters
            ),
        },


        "elevation_statistics": (
            elevation_statistics
        ),


        "slope_statistics": (
            slope_statistics
        ),


        "terrain_classification": (
            terrain_classification
        ),


        "terrain_suitability": (
            terrain_suitability
        ),
    }

    analysis_summary = (
        convert_to_json_safe(
            analysis_summary
        )
    )


    # ==================================================
    # INITIALIZE OUTPUT VALIDATION
    # ==================================================

    elevation_raster_valid = True

    slope_raster_valid = True

    summary_json_valid = True


    # ==================================================
    # SAVE OUTPUTS
    # ==================================================

    if save_output:

        if display_output:

            print(
                "\n===== SAVING PROCESSED OUTPUTS ====="
            )


        # ==================================================
        # SAVE ELEVATION RASTER
        # ==================================================

        elevation_metadata = (
            clipped_metadata.copy()
        )

        elevation_metadata.update(
            {
                "driver": "GTiff",

                "height": int(
                    elevation_data.shape[0]
                ),

                "width": int(
                    elevation_data.shape[1]
                ),

                "count": 1,

                "transform": (
                    clipped_transform
                ),
            }
        )

        elevation_nodata = (
            elevation_metadata.get(
                "nodata"
            )
        )

        if elevation_nodata is None:

            elevation_nodata = -9999.0

            elevation_metadata[
                "nodata"
            ] = elevation_nodata

        with rasterio.open(
            output_elevation_path,
            "w",
            **elevation_metadata,
        ) as output_dataset:

            output_dataset.write(
                elevation_data.filled(
                    elevation_nodata
                ),
                1,
            )

        if display_output:

            print(
                "Saved:",
                output_elevation_path,
            )


        # ==================================================
        # SAVE SLOPE RASTER
        # ==================================================

        slope_metadata = (
            elevation_metadata.copy()
        )

        slope_metadata.update(
            {
                "dtype": "float32",

                "nodata": -9999.0,
            }
        )

        with rasterio.open(
            output_slope_path,
            "w",
            **slope_metadata,
        ) as output_dataset:

            output_dataset.write(

                slope_data.filled(
                    -9999.0
                ).astype(
                    np.float32
                ),

                1,
            )

        if display_output:

            print(
                "Saved:",
                output_slope_path,
            )


        # ==================================================
        # SAVE JSON SUMMARY
        # ==================================================

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

        if display_output:

            print(
                "Saved:",
                output_summary_path,
            )


        # ==================================================
        # VALIDATE OUTPUTS
        # ==================================================

        elevation_raster_valid = (
            validate_raster(
                output_elevation_path
            )
        )

        slope_raster_valid = (
            validate_raster(
                output_slope_path
            )
        )

        summary_json_valid = (
            validate_json(
                output_summary_path
            )
        )

        if display_output:

            print(
                "\n===== OUTPUT VALIDATION ====="
            )

            print(
                OUTPUT_ELEVATION_FILE_NAME,
                ":",
                (
                    "VALID"
                    if elevation_raster_valid
                    else "INVALID"
                ),
            )

            print(
                OUTPUT_SLOPE_FILE_NAME,
                ":",
                (
                    "VALID"
                    if slope_raster_valid
                    else "INVALID"
                ),
            )

            print(
                OUTPUT_SUMMARY_FILE_NAME,
                ":",
                (
                    "VALID"
                    if summary_json_valid
                    else "INVALID"
                ),
            )


    # ==================================================
    # PROCESSING INFORMATION
    # ==================================================

    processing_time = (
        time.time()
        - processing_start_time
    )

    analysis_summary[
        "processing"
    ] = {

        "processing_time_seconds": float(
            processing_time
        ),

        "output_saved": bool(
            save_output
        ),

        "elevation_raster_valid": bool(
            elevation_raster_valid
        ),

        "slope_raster_valid": bool(
            slope_raster_valid
        ),

        "summary_json_valid": bool(
            summary_json_valid
        ),

        "elevation_output_file": (
            str(
                output_elevation_path
            )
            if save_output
            else None
        ),

        "slope_output_file": (
            str(
                output_slope_path
            )
            if save_output
            else None
        ),

        "summary_output_file": (
            str(
                output_summary_path
            )
            if save_output
            else None
        ),
    }

    analysis_summary = (
        convert_to_json_safe(
            analysis_summary
        )
    )


    # ==================================================
    # DISPLAY FINAL SUMMARY
    # ==================================================

    if display_output:

        print(
            "\n===== SRTM ANALYSIS SUMMARY ====="
        )

        print(
            "Requested Location:",
            requested_location,
        )

        print(
            "Resolved Location:",
            resolved_location,
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
            "Intersecting SRTM Tiles:",
            len(
                intersecting_tiles
            ),
        )

        print(
            "Mean Elevation:",
            round(
                elevation_statistics[
                    "mean_m"
                ],
                2,
            ),
            "meters",
        )

        print(
            "Mean Slope:",
            round(
                slope_statistics[
                    "mean_degrees"
                ],
                4,
            ),
            "degrees",
        )

        print(
            "Terrain Suitability:",
            terrain_suitability[
                "suitability_class"
            ],
        )

        print(
            "Classification Validation:",
            (
                "PASSED"
                if terrain_classification[
                    "classification_valid"
                ]
                else "FAILED"
            ),
        )

        if save_output:

            valid_output_count = sum(
                [
                    elevation_raster_valid,
                    slope_raster_valid,
                    summary_json_valid,
                ]
            )

            print(
                "Valid Output Files:",
                f"{valid_output_count}/3",
            )

        print(
            "Total Processing Time:",
            round(
                processing_time,
                2,
            ),
            "seconds",
        )

        analysis_successful = (

            terrain_classification[
                "classification_valid"
            ]

            and

            (
                not save_output

                or

                (
                    elevation_raster_valid

                    and

                    slope_raster_valid

                    and

                    summary_json_valid
                )
            )
        )

        if analysis_successful:

            print(
                "\n===== SRTM ANALYSIS "
                "COMPLETED SUCCESSFULLY ====="
            )

        else:

            print(
                "\n===== SRTM ANALYSIS "
                "COMPLETED WITH ERRORS ====="
            )


    # ==================================================
    # RETURN RESULT TO ENGINE
    # ==================================================
    analysis_summary["status"] = "success"
    analysis_summary["error"] = None

    return analysis_summary

# ==================================================
# STANDALONE MAIN
# ==================================================

def main():

    site = get_site_information()

    try:

        analyze_srtm(
            site=site,
            save_output=True,
            display_output=True,
        )

    except Exception as error:

        print(
            "\nSRTM Analysis Error:",
            error,
        )

        print(
            "\n===== SRTM ANALYSIS FAILED ====="
        )


if __name__ == "__main__":

    main()