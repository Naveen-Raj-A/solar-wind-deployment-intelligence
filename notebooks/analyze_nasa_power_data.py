import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from engine.site_information import SiteInformation
from engine.input_handler import get_site_information


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

INPUT_FILE_PATH = Path(
    "datasets/nasa_power/raw/"
    "nasa_power_india_climatology.csv"
)

OUTPUT_BASE_DIRECTORY = Path(
    "datasets/nasa_power/processed"
)

OUTPUT_SUMMARY_FILE_NAME = (
    "nasa_power_analysis_summary.json"
)

GEOCODER_USER_AGENT = (
    "solar_wind_deployment_intelligence"
)


# --------------------------------------------------
# REQUIRED DATASET COLUMNS
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "latitude",
    "longitude",
    "solar_radiation_kwh_m2_day",
    "temperature_mean_c",
    "temperature_max_c",
    "temperature_min_c",
    "relative_humidity_pct",
    "precipitation_mm_day",
    "wind_speed_10m_ms",
    "wind_speed_50m_ms",
]


# --------------------------------------------------
# CREATE SAFE LOCATION NAME
# --------------------------------------------------

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


# --------------------------------------------------
# GEOCODE LOCATION
# --------------------------------------------------

def geocode_location(location_name):

    geolocator = Nominatim(
        user_agent=GEOCODER_USER_AGENT,
        timeout=20,
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
# VALIDATE COORDINATES
# --------------------------------------------------

def validate_coordinates(
    latitude,
    longitude,
):

    try:

        latitude = float(latitude)

        longitude = float(longitude)

    except (
        TypeError,
        ValueError,
    ):

        return False

    if not (
        -90.0
        <= latitude
        <= 90.0
    ):

        return False

    if not (
        -180.0
        <= longitude
        <= 180.0
    ):

        return False

    return True


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
            latitude_difference / 2
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
            longitude_difference / 2
        ) ** 2
    )

    angular_distance = (
        2
        *
        math.atan2(
            math.sqrt(haversine_value),
            math.sqrt(
                1 - haversine_value
            ),
        )
    )

    return (
        earth_radius_km
        * angular_distance
    )


# --------------------------------------------------
# VALIDATE DATASET COLUMNS
# --------------------------------------------------

def validate_required_columns(
    dataframe,
):

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column
        not in dataframe.columns
    ]

    return missing_columns


# --------------------------------------------------
# VALIDATE NUMERIC DATA
# --------------------------------------------------

def validate_numeric_columns(
    dataframe,
):

    invalid_columns = []

    for column in REQUIRED_COLUMNS:

        converted_values = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        if converted_values.notna().sum() == 0:

            invalid_columns.append(
                column
            )

    return invalid_columns


# --------------------------------------------------
# CALCULATE COLUMN STATISTICS
# --------------------------------------------------

def calculate_statistics(
    values,
):

    numeric_values = pd.to_numeric(
        values,
        errors="coerce",
    )

    valid_values = (
        numeric_values
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
    )

    if valid_values.empty:

        return None

    return {
        "minimum": float(
            valid_values.min()
        ),
        "maximum": float(
            valid_values.max()
        ),
        "mean": float(
            valid_values.mean()
        ),
        "median": float(
            valid_values.median()
        ),
        "standard_deviation": float(
            valid_values.std(
                ddof=0
            )
        ),
    }


# --------------------------------------------------
# CONVERT VALUES TO JSON SAFE TYPES
# --------------------------------------------------

def convert_to_json_safe(
    value,
):

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


# --------------------------------------------------
# VALIDATE SUMMARY FILE
# --------------------------------------------------

def validate_summary_file(
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

        required_summary_sections = [
            "location",
            "nearest_grid_point",
            "solar_resource",
            "temperature",
            "relative_humidity",
            "precipitation",
            "wind_resource",
        ]

        for section in (
            required_summary_sections
        ):

            if section not in summary_data:

                return False

        return True

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return False


# --------------------------------------------------
# ANALYZE NASA POWER DATA
# --------------------------------------------------

def analyze_nasa_power(
    site: SiteInformation,
    save_output=True,
    display_output=True,
):

    processing_start_time = time.time()

    latitude = site.latitude
    longitude = site.longitude

    requested_location = site.requested_location
    resolved_location = site.resolved_location

    safe_location_name = create_safe_location_name(
        requested_location
    )

    if not validate_coordinates(
        latitude,
        longitude,
    ):

        raise ValueError(
            "Invalid latitude or longitude."
        )

    if display_output:

        print(
            "\n===== NASA POWER INDIA ANALYSIS ====="
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


    # --------------------------------------------------
    # CHECK INPUT DATASET
    # --------------------------------------------------

    if display_output:

        print(
            "\n===== CHECKING NASA POWER DATASET ====="
        )

    if not INPUT_FILE_PATH.exists():

        raise FileNotFoundError(
            "NASA POWER dataset was not found: "
            f"{INPUT_FILE_PATH}"
        )

    if display_output:

        print(
            "NASA POWER Dataset: FOUND"
        )

        print(
            "Input File:",
            INPUT_FILE_PATH,
        )


    # --------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------

    output_directory = (
        OUTPUT_BASE_DIRECTORY
        / safe_location_name
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


    # --------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------

    if display_output:

        print(
            "\n===== LOADING NASA POWER DATASET ====="
        )

    dataframe = pd.read_csv(
        INPUT_FILE_PATH
    )

    if display_output:

        print(
            "Dataset Records:",
            len(dataframe),
        )

        print(
            "Dataset Columns:",
            len(dataframe.columns),
        )


    # --------------------------------------------------
    # VALIDATE DATASET
    # --------------------------------------------------

    if display_output:

        print(
            "\n===== VALIDATING DATASET ====="
        )

    missing_columns = (
        validate_required_columns(
            dataframe
        )
    )

    if missing_columns:

        raise ValueError(
            "Missing required NASA POWER "
            f"columns: {missing_columns}"
        )

    if display_output:

        print(
            "Required Columns: VALID"
        )

    invalid_numeric_columns = (
        validate_numeric_columns(
            dataframe
        )
    )

    if invalid_numeric_columns:

        raise ValueError(
            "Invalid numeric NASA POWER "
            f"columns: {invalid_numeric_columns}"
        )

    if display_output:

        print(
            "Numeric Columns: VALID"
        )


    # --------------------------------------------------
    # CONVERT COLUMNS TO NUMERIC
    # --------------------------------------------------

    for column in REQUIRED_COLUMNS:

        dataframe[column] = (
            pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )
        )


    # --------------------------------------------------
    # COORDINATE VALIDATION
    # --------------------------------------------------

    original_record_count = (
        len(dataframe)
    )

    dataframe = dataframe.dropna(
        subset=[
            "latitude",
            "longitude",
        ]
    ).copy()

    valid_coordinate_records = (
        len(dataframe)
    )

    invalid_coordinate_records = (
        original_record_count
        - valid_coordinate_records
    )

    if display_output:

        print(
            "\n===== COORDINATE VALIDATION ====="
        )

        print(
            "Original Records:",
            original_record_count,
        )

        print(
            "Valid Coordinate Records:",
            valid_coordinate_records,
        )

        print(
            "Invalid Coordinate Records:",
            invalid_coordinate_records,
        )

    if dataframe.empty:

        raise ValueError(
            "NASA POWER dataset contains "
            "no valid coordinate records."
        )


    # --------------------------------------------------
    # CALCULATE DISTANCES
    # --------------------------------------------------

    if display_output:

        print(
            "\n===== SEARCHING NEAREST "
            "NASA POWER GRID POINT ====="
        )

    distances = []

    for row in dataframe.itertuples(
        index=False
    ):

        distance = (
            calculate_haversine_distance(
                latitude,
                longitude,
                float(row.latitude),
                float(row.longitude),
            )
        )

        distances.append(
            distance
        )

    dataframe[
        "distance_from_location_km"
    ] = distances


    # --------------------------------------------------
    # FIND NEAREST GRID POINT
    # --------------------------------------------------

    nearest_index = (
        dataframe[
            "distance_from_location_km"
        ]
        .idxmin()
    )

    nearest_record = (
        dataframe.loc[
            nearest_index
        ]
    )

    nearest_latitude = float(
        nearest_record[
            "latitude"
        ]
    )

    nearest_longitude = float(
        nearest_record[
            "longitude"
        ]
    )

    nearest_distance_km = float(
        nearest_record[
            "distance_from_location_km"
        ]
    )

    if display_output:

        print(
            "Nearest Grid Latitude:",
            nearest_latitude,
        )

        print(
            "Nearest Grid Longitude:",
            nearest_longitude,
        )

        print(
            "Distance From Requested Location:",
            round(
                nearest_distance_km,
                4,
            ),
            "km",
        )


    # --------------------------------------------------
    # EXTRACT RESOURCE VALUES
    # --------------------------------------------------

    solar_radiation = float(
        nearest_record[
            "solar_radiation_kwh_m2_day"
        ]
    )

    temperature_mean = float(
        nearest_record[
            "temperature_mean_c"
        ]
    )

    temperature_maximum = float(
        nearest_record[
            "temperature_max_c"
        ]
    )

    temperature_minimum = float(
        nearest_record[
            "temperature_min_c"
        ]
    )

    relative_humidity = float(
        nearest_record[
            "relative_humidity_pct"
        ]
    )

    precipitation = float(
        nearest_record[
            "precipitation_mm_day"
        ]
    )

    wind_speed_10m = float(
        nearest_record[
            "wind_speed_10m_ms"
        ]
    )

    wind_speed_50m = float(
        nearest_record[
            "wind_speed_50m_ms"
        ]
    )


    # --------------------------------------------------
    # DISPLAY GRID VALUES
    # --------------------------------------------------

    if display_output:

        print(
            "\n===== NEAREST GRID POINT DATA ====="
        )

        print(
            "Solar Radiation:",
            round(
                solar_radiation,
                4,
            ),
            "kWh/m²/day",
        )

        print(
            "Mean Temperature:",
            round(
                temperature_mean,
                4,
            ),
            "°C",
        )

        print(
            "Maximum Temperature:",
            round(
                temperature_maximum,
                4,
            ),
            "°C",
        )

        print(
            "Minimum Temperature:",
            round(
                temperature_minimum,
                4,
            ),
            "°C",
        )

        print(
            "Relative Humidity:",
            round(
                relative_humidity,
                4,
            ),
            "%",
        )

        print(
            "Precipitation:",
            round(
                precipitation,
                4,
            ),
            "mm/day",
        )

        print(
            "Wind Speed at 10 m:",
            round(
                wind_speed_10m,
                4,
            ),
            "m/s",
        )

        print(
            "Wind Speed at 50 m:",
            round(
                wind_speed_50m,
                4,
            ),
            "m/s",
        )


    # --------------------------------------------------
    # RESOURCE CLASSIFICATIONS
    # --------------------------------------------------

    if solar_radiation < 4.0:

        solar_classification = "LOW"

    elif solar_radiation < 5.0:

        solar_classification = "MODERATE"

    elif solar_radiation < 6.0:

        solar_classification = "GOOD"

    else:

        solar_classification = "EXCELLENT"


    if wind_speed_50m < 4.0:

        wind_classification = "LOW"

    elif wind_speed_50m < 6.0:

        wind_classification = "MODERATE"

    elif wind_speed_50m < 8.0:

        wind_classification = "GOOD"

    else:

        wind_classification = "EXCELLENT"


    if display_output:

        print(
            "\n===== SOLAR RESOURCE "
            "CLASSIFICATION ====="
        )

        print(
            "Solar Resource Class:",
            solar_classification,
        )

        print(
            "\n===== NASA WIND RESOURCE "
            "CLASSIFICATION ====="
        )

        print(
            "50 m Wind Resource Class:",
            wind_classification,
        )


    # --------------------------------------------------
    # CALCULATE DATASET STATISTICS
    # --------------------------------------------------

    if display_output:

        print(
            "\n===== CALCULATING "
            "DATASET STATISTICS ====="
        )

    solar_statistics = (
        calculate_statistics(
            dataframe[
                "solar_radiation_kwh_m2_day"
            ]
        )
    )

    temperature_statistics = (
        calculate_statistics(
            dataframe[
                "temperature_mean_c"
            ]
        )
    )

    humidity_statistics = (
        calculate_statistics(
            dataframe[
                "relative_humidity_pct"
            ]
        )
    )

    precipitation_statistics = (
        calculate_statistics(
            dataframe[
                "precipitation_mm_day"
            ]
        )
    )

    wind_10m_statistics = (
        calculate_statistics(
            dataframe[
                "wind_speed_10m_ms"
            ]
        )
    )

    wind_50m_statistics = (
        calculate_statistics(
            dataframe[
                "wind_speed_50m_ms"
            ]
        )
    )

    if display_output:

        print(
            "Dataset Statistics: COMPLETED"
        )


    # --------------------------------------------------
    # CREATE ANALYSIS SUMMARY
    # --------------------------------------------------

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

            "total_records": int(
                original_record_count
            ),

            "valid_coordinate_records": int(
                valid_coordinate_records
            ),

            "invalid_coordinate_records": int(
                invalid_coordinate_records
            ),
        },


        "nearest_grid_point": {

            "latitude": (
                nearest_latitude
            ),

            "longitude": (
                nearest_longitude
            ),

            "distance_from_location_km": (
                nearest_distance_km
            ),
        },


        "solar_resource": {

            "solar_radiation_kwh_m2_day": (
                solar_radiation
            ),

            "classification": (
                solar_classification
            ),

            "india_dataset_statistics": (
                solar_statistics
            ),
        },


        "temperature": {

            "mean_c": (
                temperature_mean
            ),

            "maximum_c": (
                temperature_maximum
            ),

            "minimum_c": (
                temperature_minimum
            ),

            "india_dataset_statistics": (
                temperature_statistics
            ),
        },


        "relative_humidity": {

            "percentage": (
                relative_humidity
            ),

            "india_dataset_statistics": (
                humidity_statistics
            ),
        },


        "precipitation": {

            "mm_per_day": (
                precipitation
            ),

            "india_dataset_statistics": (
                precipitation_statistics
            ),
        },


        "wind_resource": {

            "wind_speed_10m_ms": (
                wind_speed_10m
            ),

            "wind_speed_50m_ms": (
                wind_speed_50m
            ),

            "classification_50m": (
                wind_classification
            ),

            "wind_10m_india_statistics": (
                wind_10m_statistics
            ),

            "wind_50m_india_statistics": (
                wind_50m_statistics
            ),
        },
    }

    analysis_summary = (
        convert_to_json_safe(
            analysis_summary
        )
    )


    # --------------------------------------------------
    # SAVE OUTPUT
    # --------------------------------------------------

    output_valid = True

    if save_output:

        if display_output:

            print(
                "\n===== SAVING PROCESSED OUTPUT ====="
            )

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

        output_valid = (
            validate_summary_file(
                output_summary_path
            )
        )

        if display_output:

            print(
                "Saved:",
                output_summary_path,
            )

            print(
                "\n===== OUTPUT VALIDATION ====="
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
    # FINAL INFORMATION
    # --------------------------------------------------

    processing_time = (
        time.time()
        - processing_start_time
    )

    analysis_summary[
        "processing"
    ] = {

        "processing_time_seconds": (
            processing_time
        ),

        "output_saved": bool(
            save_output
        ),

        "output_valid": bool(
            output_valid
        ),

        "output_file": (
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

    if display_output:

        print(
            "\n===== NASA POWER "
            "ANALYSIS SUMMARY ====="
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
            "Requested Latitude:",
            latitude,
        )

        print(
            "Requested Longitude:",
            longitude,
        )

        print(
            "Nearest Grid Latitude:",
            nearest_latitude,
        )

        print(
            "Nearest Grid Longitude:",
            nearest_longitude,
        )

        print(
            "Distance To Nearest Grid:",
            round(
                nearest_distance_km,
                4,
            ),
            "km",
        )

        print(
            "Solar Radiation:",
            round(
                solar_radiation,
                4,
            ),
            "kWh/m²/day",
        )

        print(
            "Solar Resource Class:",
            solar_classification,
        )

        print(
            "Mean Temperature:",
            round(
                temperature_mean,
                4,
            ),
            "°C",
        )

        print(
            "Relative Humidity:",
            round(
                relative_humidity,
                4,
            ),
            "%",
        )

        print(
            "Precipitation:",
            round(
                precipitation,
                4,
            ),
            "mm/day",
        )

        print(
            "Wind Speed at 10 m:",
            round(
                wind_speed_10m,
                4,
            ),
            "m/s",
        )

        print(
            "Wind Speed at 50 m:",
            round(
                wind_speed_50m,
                4,
            ),
            "m/s",
        )

        print(
            "50 m Wind Resource Class:",
            wind_classification,
        )

        if save_output:

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

        if output_valid:

            print(
                "\n===== NASA POWER ANALYSIS "
                "COMPLETED SUCCESSFULLY ====="
            )

        else:

            print(
                "\n===== NASA POWER "
                "ANALYSIS FAILED ====="
            )
    analysis_summary["status"] = "success"
    analysis_summary["error"] = None

    return analysis_summary


# --------------------------------------------------
# STANDALONE MAIN PROGRAM
# --------------------------------------------------
def main():

    print(
        "\n===== NASA POWER INDIA ANALYSIS ====="
    )

    try:

        site = get_site_information()

        analyze_nasa_power(
            site=site,
            save_output=True,
            display_output=True,
        )

    except Exception as error:

        print(
            "\nNASA POWER Analysis Error:",
            error,
        )

        print(
            "\n===== NASA POWER ANALYSIS FAILED ====="
        )

# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()