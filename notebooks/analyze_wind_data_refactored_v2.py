import json
import math
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping

from engine.site_information import SiteInformation, validate_coordinates
from engine.input_handler import get_site_information


# ==================================================
# CONFIGURATION
# ==================================================

INPUT_FILE_PATH = Path(
    "datasets/global_wind_atlas/"
    "IND_wind-speed_150m.tif"
)

OUTPUT_BASE_DIRECTORY = Path(
    "datasets/global_wind_atlas/processed"
)

OUTPUT_WIND_FILE_NAME = "wind_speed.tif"

OUTPUT_SUMMARY_FILE_NAME = (
    "wind_analysis_summary.json"
)

AOI_BUFFER_DEGREES = 0.05

WIND_MEASUREMENT_HEIGHT_METERS = 150

GEOCODER_USER_AGENT = (
    "solar_wind_deployment_intelligence"
)

GEOCODER_TIMEOUT_SECONDS = 20


# ==================================================
# CREATE SAFE LOCATION NAME
# ==================================================

def create_safe_location_name(location_name):

    safe_name = (
        str(location_name)
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

    safe_name = safe_name.strip("_")

    if not safe_name:

        safe_name = "site"

    return safe_name


# ==================================================
# CALCULATE RASTER STATISTICS
# ==================================================

def calculate_statistics(data):

    valid_data = data.compressed()

    if valid_data.size == 0:

        return None

    return {
        "minimum": float(
            np.min(valid_data)
        ),
        "maximum": float(
            np.max(valid_data)
        ),
        "mean": float(
            np.mean(valid_data)
        ),
        "median": float(
            np.median(valid_data)
        ),
        "standard_deviation": float(
            np.std(valid_data)
        ),
    }


# ==================================================
# CLASSIFY WIND RESOURCE
# ==================================================

def classify_wind_resource(
    wind_data,
):

    valid_values = (
        wind_data.compressed()
    )

    if valid_values.size == 0:

        return None

    low_cells = int(
        np.sum(
            valid_values < 4.0
        )
    )

    moderate_cells = int(
        np.sum(
            (
                valid_values >= 4.0
            )
            &
            (
                valid_values < 6.0
            )
        )
    )

    good_cells = int(
        np.sum(
            (
                valid_values >= 6.0
            )
            &
            (
                valid_values < 8.0
            )
        )
    )

    excellent_cells = int(
        np.sum(
            valid_values >= 8.0
        )
    )

    total_classified_cells = int(
        valid_values.size
    )

    low_percentage = float(
        (
            low_cells
            / total_classified_cells
        )
        * 100
    )

    moderate_percentage = float(
        (
            moderate_cells
            / total_classified_cells
        )
        * 100
    )

    good_percentage = float(
        (
            good_cells
            / total_classified_cells
        )
        * 100
    )

    excellent_percentage = float(
        (
            excellent_cells
            / total_classified_cells
        )
        * 100
    )

    classified_cell_count = (
        low_cells
        + moderate_cells
        + good_cells
        + excellent_cells
    )

    classification_valid = bool(
        classified_cell_count
        == total_classified_cells
    )

    return {
        "low": {
            "minimum_wind_speed_ms": None,
            "maximum_wind_speed_ms": 4.0,
            "cells": low_cells,
            "percentage": low_percentage,
        },
        "moderate": {
            "minimum_wind_speed_ms": 4.0,
            "maximum_wind_speed_ms": 6.0,
            "cells": moderate_cells,
            "percentage": moderate_percentage,
        },
        "good": {
            "minimum_wind_speed_ms": 6.0,
            "maximum_wind_speed_ms": 8.0,
            "cells": good_cells,
            "percentage": good_percentage,
        },
        "excellent": {
            "minimum_wind_speed_ms": 8.0,
            "maximum_wind_speed_ms": None,
            "cells": excellent_cells,
            "percentage": excellent_percentage,
        },
        "total_classified_cells": (
            classified_cell_count
        ),
        "classification_valid": (
            classification_valid
        ),
    }


# ==================================================
# VALIDATE OUTPUT RASTER
# ==================================================

def validate_raster(output_path):

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
# VALIDATE JSON SUMMARY
# ==================================================

def validate_json(output_path):

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
            "dataset",
            "aoi",
            "pixel_information",
            "wind_speed_statistics",
            "wind_resource_classification",
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


# ==================================================
# CONVERT TO JSON SAFE TYPES
# ==================================================

def convert_to_json_safe(value):

    if isinstance(
        value,
        dict,
    ):

        return {
            str(key): convert_to_json_safe(
                item
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

        return [
            convert_to_json_safe(
                item
            )
            for item in value.tolist()
        ]

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
# ANALYZE WIND DATA
# ==================================================

def analyze_wind(
    site: SiteInformation,
    save_output=True,
    display_output=True,
):

    processing_start_time = time.time()

    latitude = float(site.latitude)
    longitude = float(site.longitude)

    validate_coordinates(
        latitude,
        longitude,
    )

    requested_location = site.requested_location
    resolved_location = site.resolved_location

    safe_location_name = create_safe_location_name(
        requested_location
    )


    # ==================================================
    # DISPLAY ANALYSIS HEADER
    # ==================================================

    if display_output:

        print(
            "\n===== GLOBAL WIND ATLAS ANALYSIS ====="
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
    # CHECK INPUT DATASET
    # ==================================================

    if display_output:

        print(
            "\n===== CHECKING WIND DATASET ====="
        )

    if not INPUT_FILE_PATH.exists():

        raise FileNotFoundError(
            "Global Wind Atlas dataset "
            "was not found: "
            f"{INPUT_FILE_PATH}"
        )

    if display_output:

        print(
            "Wind Dataset: FOUND"
        )

        print(
            "Input File:",
            INPUT_FILE_PATH,
        )


    # ==================================================
    # CREATE OUTPUT PATHS
    # ==================================================

    output_directory = (
        OUTPUT_BASE_DIRECTORY
        / safe_location_name
    )

    output_wind_path = (
        output_directory
        / OUTPUT_WIND_FILE_NAME
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

    west = (
        longitude
        - AOI_BUFFER_DEGREES
    )

    south = (
        latitude
        - AOI_BUFFER_DEGREES
    )

    east = (
        longitude
        + AOI_BUFFER_DEGREES
    )

    north = (
        latitude
        + AOI_BUFFER_DEGREES
    )

    if display_output:

        print(
            "\n===== WIND AOI BOUNDS ====="
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

    aoi_geometry = box(
        west,
        south,
        east,
        north,
    )


    # ==================================================
    # OPEN SOURCE RASTER
    # ==================================================

    with rasterio.open(
        INPUT_FILE_PATH
    ) as source_dataset:


        # ==================================================
        # CAPTURE SOURCE METADATA
        # ==================================================

        source_crs = str(
            source_dataset.crs
        )

        source_width = int(
            source_dataset.width
        )

        source_height = int(
            source_dataset.height
        )

        source_band_count = int(
            source_dataset.count
        )

        source_data_type = str(
            source_dataset.dtypes[0]
        )

        source_nodata_value = (
            source_dataset.nodata
        )

        source_resolution_x = float(
            source_dataset.res[0]
        )

        source_resolution_y = float(
            source_dataset.res[1]
        )

        source_bounds_left = float(
            source_dataset.bounds.left
        )

        source_bounds_bottom = float(
            source_dataset.bounds.bottom
        )

        source_bounds_right = float(
            source_dataset.bounds.right
        )

        source_bounds_top = float(
            source_dataset.bounds.top
        )


        # ==================================================
        # DISPLAY RASTER INFORMATION
        # ==================================================

        if display_output:

            print(
                "\n===== INPUT RASTER INFORMATION ====="
            )

            print(
                "CRS:",
                source_dataset.crs,
            )

            print(
                "Width:",
                source_width,
            )

            print(
                "Height:",
                source_height,
            )

            print(
                "Bands:",
                source_band_count,
            )

            print(
                "Data Type:",
                source_data_type,
            )

            print(
                "NoData Value:",
                source_nodata_value,
            )

            print(
                "Resolution:",
                source_dataset.res,
            )

            print(
                "Geographic Bounds:",
                source_dataset.bounds,
            )


        # ==================================================
        # VALIDATE SOURCE RASTER
        # ==================================================

        if source_dataset.crs is None:

            raise ValueError(
                "Wind raster does not have "
                "a valid coordinate reference system."
            )

        if source_band_count != 1:

            raise ValueError(
                "Expected one wind raster band, "
                f"but found {source_band_count}."
            )


        # ==================================================
        # VALIDATE REQUESTED LOCATION
        # ==================================================

        site_inside_raster = (

            source_bounds_left
            <= longitude
            <= source_bounds_right

            and

            source_bounds_bottom
            <= latitude
            <= source_bounds_top
        )

        if not site_inside_raster:

            raise ValueError(
                "Requested coordinates are outside "
                "the Global Wind Atlas dataset bounds."
            )


        # ==================================================
        # CLIP AOI TO RASTER BOUNDS
        # ==================================================

        raster_geometry = box(
            source_bounds_left,
            source_bounds_bottom,
            source_bounds_right,
            source_bounds_top,
        )

        clipped_aoi_geometry = (
            aoi_geometry.intersection(
                raster_geometry
            )
        )

        if clipped_aoi_geometry.is_empty:

            raise ValueError(
                "Requested AOI does not intersect "
                "the Global Wind Atlas dataset."
            )


        # ==================================================
        # EXTRACT WIND AOI
        # ==================================================

        if display_output:

            print(
                "\n===== EXTRACTING WIND AOI ====="
            )

        extracted_data, extracted_transform = (
            mask(
                source_dataset,
                [
                    mapping(
                        clipped_aoi_geometry
                    )
                ],
                crop=True,
                filled=False,
            )
        )

        if extracted_data.size == 0:

            raise ValueError(
                "Wind AOI extraction returned "
                "an empty raster."
            )

        if extracted_data.shape[0] != 1:

            raise ValueError(
                "Expected one extracted wind band, "
                f"but found {extracted_data.shape[0]}."
            )

        if display_output:

            print(
                "AOI Extraction: COMPLETED"
            )


        # ==================================================
        # EXTRACT WIND BAND
        # ==================================================

        wind_data = (
            extracted_data[0]
        )

        wind_data = np.ma.masked_invalid(
            wind_data
        )


        # ==================================================
        # CALCULATE PIXEL INFORMATION
        # ==================================================

        total_cells = int(
            wind_data.size
        )

        valid_cells = int(
            wind_data.count()
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
                "No valid wind-speed cells "
                "are available inside the AOI."
            )


        # ==================================================
        # DISPLAY PIXEL INFORMATION
        # ==================================================

        if display_output:

            print(
                "\n===== WIND PIXEL INFORMATION ====="
            )

            print(
                "Total Cells:",
                total_cells,
            )

            print(
                "Valid Wind Cells:",
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
        # CALCULATE WIND STATISTICS
        # ==================================================

        wind_statistics = (
            calculate_statistics(
                wind_data
            )
        )

        if wind_statistics is None:

            raise ValueError(
                "Unable to calculate "
                "wind-speed statistics."
            )


        # ==================================================
        # DISPLAY WIND STATISTICS
        # ==================================================

        if display_output:

            print(
                "\n===== WIND SPEED STATISTICS ====="
            )

            print(
                "Minimum Wind Speed:",
                round(
                    wind_statistics[
                        "minimum"
                    ],
                    4,
                ),
                "m/s",
            )

            print(
                "Maximum Wind Speed:",
                round(
                    wind_statistics[
                        "maximum"
                    ],
                    4,
                ),
                "m/s",
            )

            print(
                "Mean Wind Speed:",
                round(
                    wind_statistics[
                        "mean"
                    ],
                    4,
                ),
                "m/s",
            )

            print(
                "Median Wind Speed:",
                round(
                    wind_statistics[
                        "median"
                    ],
                    4,
                ),
                "m/s",
            )

            print(
                "Standard Deviation:",
                round(
                    wind_statistics[
                        "standard_deviation"
                    ],
                    4,
                ),
                "m/s",
            )


        # ==================================================
        # CLASSIFY WIND RESOURCE
        # ==================================================

        wind_classification = (
            classify_wind_resource(
                wind_data
            )
        )

        if wind_classification is None:

            raise ValueError(
                "Unable to classify "
                "wind resources."
            )


        # ==================================================
        # DISPLAY CLASSIFICATION
        # ==================================================

        if display_output:

            print(
                "\n===== WIND RESOURCE CLASSIFICATION ====="
            )

            print(
                "Low Wind (< 4 m/s):",
                wind_classification[
                    "low"
                ][
                    "cells"
                ],
                "cells "
                f"({wind_classification['low']['percentage']:.2f}%)",
            )

            print(
                "Moderate Wind "
                "(>= 4 and < 6 m/s):",
                wind_classification[
                    "moderate"
                ][
                    "cells"
                ],
                "cells "
                f"({wind_classification['moderate']['percentage']:.2f}%)",
            )

            print(
                "Good Wind "
                "(>= 6 and < 8 m/s):",
                wind_classification[
                    "good"
                ][
                    "cells"
                ],
                "cells "
                f"({wind_classification['good']['percentage']:.2f}%)",
            )

            print(
                "Excellent Wind "
                "(>= 8 m/s):",
                wind_classification[
                    "excellent"
                ][
                    "cells"
                ],
                "cells "
                f"({wind_classification['excellent']['percentage']:.2f}%)",
            )

            print(
                "Total Classified Cells:",
                wind_classification[
                    "total_classified_cells"
                ],
            )

            print(
                "Classification Validation:",
                (
                    "PASSED"
                    if wind_classification[
                        "classification_valid"
                    ]
                    else "FAILED"
                ),
            )


        # ==================================================
        # PREPARE OUTPUT RASTER METADATA
        # ==================================================

        output_metadata = (
            source_dataset.meta.copy()
        )

        output_metadata.update(
            {
                "driver": "GTiff",
                "height": int(
                    extracted_data.shape[1]
                ),
                "width": int(
                    extracted_data.shape[2]
                ),
                "transform": (
                    extracted_transform
                ),
                "count": 1,
            }
        )


        # ==================================================
        # SAVE OUTPUT WIND RASTER
        # ==================================================

        if save_output:

            if display_output:

                print(
                    "\n===== SAVING PROCESSED OUTPUTS ====="
                )

            output_data = (
                extracted_data.filled(
                    source_nodata_value
                    if source_nodata_value
                    is not None
                    else np.nan
                )
            )

            with rasterio.open(
                output_wind_path,
                "w",
                **output_metadata,
            ) as output_dataset:

                output_dataset.write(
                    output_data
                )

            if display_output:

                print(
                    "Saved:",
                    output_wind_path,
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

            "input_file": str(
                INPUT_FILE_PATH
            ),

            "wind_measurement_height_m": (
                WIND_MEASUREMENT_HEIGHT_METERS
            ),

            "aoi_buffer_degrees": (
                AOI_BUFFER_DEGREES
            ),

            "source_crs": (
                source_crs
            ),

            "source_width": (
                source_width
            ),

            "source_height": (
                source_height
            ),

            "source_band_count": (
                source_band_count
            ),

            "source_data_type": (
                source_data_type
            ),

            "source_nodata_value": (
                source_nodata_value
            ),

            "source_resolution": {

                "x": (
                    source_resolution_x
                ),

                "y": (
                    source_resolution_y
                ),
            },

            "source_bounds": {

                "left": (
                    source_bounds_left
                ),

                "bottom": (
                    source_bounds_bottom
                ),

                "right": (
                    source_bounds_right
                ),

                "top": (
                    source_bounds_top
                ),
            },
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

            "valid_wind_cells": (
                valid_cells
            ),

            "nodata_cells": (
                nodata_cells
            ),

            "valid_percentage": (
                valid_percentage
            ),
        },


        "wind_speed_statistics": {

            "minimum_ms": float(
                wind_statistics[
                    "minimum"
                ]
            ),

            "maximum_ms": float(
                wind_statistics[
                    "maximum"
                ]
            ),

            "mean_ms": float(
                wind_statistics[
                    "mean"
                ]
            ),

            "median_ms": float(
                wind_statistics[
                    "median"
                ]
            ),

            "standard_deviation_ms": float(
                wind_statistics[
                    "standard_deviation"
                ]
            ),
        },


        "wind_resource_classification": (
            wind_classification
        ),
    }

    analysis_summary = (
        convert_to_json_safe(
            analysis_summary
        )
    )


    # ==================================================
    # SAVE JSON SUMMARY
    # ==================================================

    wind_raster_valid = True

    summary_json_valid = True

    if save_output:

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

        wind_raster_valid = (
            validate_raster(
                output_wind_path
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
                OUTPUT_WIND_FILE_NAME,
                ":",
                (
                    "VALID"
                    if wind_raster_valid
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
    # CALCULATE PROCESSING TIME
    # ==================================================

    processing_time = (
        time.time()
        - processing_start_time
    )


    # ==================================================
    # ADD PROCESSING METADATA
    # ==================================================

    analysis_summary[
        "processing"
    ] = {

        "processing_time_seconds": float(
            processing_time
        ),

        "output_saved": bool(
            save_output
        ),

        "wind_raster_valid": bool(
            wind_raster_valid
        ),

        "summary_json_valid": bool(
            summary_json_valid
        ),

        "wind_raster_output_file": (
            str(output_wind_path)
            if save_output
            else None
        ),

        "summary_output_file": (
            str(output_summary_path)
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
            "\n===== WIND ANALYSIS SUMMARY ====="
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
            "Wind Measurement Height:",
            WIND_MEASUREMENT_HEIGHT_METERS,
            "meters",
        )

        print(
            "Valid Wind Percentage:",
            round(
                valid_percentage,
                2,
            ),
            "%",
        )

        print(
            "Mean Wind Speed:",
            round(
                wind_statistics[
                    "mean"
                ],
                4,
            ),
            "m/s",
        )

        print(
            "Good Wind Percentage:",
            round(
                wind_classification[
                    "good"
                ][
                    "percentage"
                ],
                2,
            ),
            "%",
        )

        print(
            "Excellent Wind Percentage:",
            round(
                wind_classification[
                    "excellent"
                ][
                    "percentage"
                ],
                2,
            ),
            "%",
        )

        print(
            "Classification Validation:",
            (
                "PASSED"
                if wind_classification[
                    "classification_valid"
                ]
                else "FAILED"
            ),
        )

        if save_output:

            valid_output_count = sum(
                [
                    wind_raster_valid,
                    summary_json_valid,
                ]
            )

            print(
                "Valid Output Files:",
                f"{valid_output_count}/2",
            )

        print(
            "Total Processing Time:",
            round(
                processing_time,
                2,
            ),
            "seconds",
        )


        # ==================================================
        # DISPLAY FINAL STATUS
        # ==================================================

        analysis_successful = (

            wind_classification[
                "classification_valid"
            ]

            and

            (
                not save_output

                or

                (
                    wind_raster_valid

                    and

                    summary_json_valid
                )
            )
        )

        if analysis_successful:

            print(
                "\n===== WIND ANALYSIS "
                "COMPLETED SUCCESSFULLY ====="
            )

        else:

            print(
                "\n===== WIND ANALYSIS "
                "COMPLETED WITH ERRORS ====="
            )


    # ==================================================
    # RETURN RESULT TO ENGINE
    # ==================================================

    return analysis_summary


# ==================================================
# STANDALONE MAIN PROGRAM
# ==================================================

def main():

    print(
        "\n===== GLOBAL WIND ATLAS ANALYSIS ====="
    )

    try:

        site = get_site_information()

        analyze_wind(
            site=site,
            save_output=True,
            display_output=True,
        )

    except Exception as error:

        print(
            "\nWind Analysis Error:",
            error,
        )

        print(
            "\n===== WIND ANALYSIS FAILED =====")


# ==================================================
# RUN PROGRAM
# ==================================================

if __name__ == "__main__":

    main()
