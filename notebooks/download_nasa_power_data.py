import csv
import json
import math
import time
from pathlib import Path

import requests
from shapely.geometry import Point, shape


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

NASA_POWER_API_URL = (
    "https://power.larc.nasa.gov/api/temporal/climatology/point"
)

INDIA_BOUNDARY_PATH = Path(
    "datasets/boundaries/geoBoundaries-IND-ADM0.geojson"
)

OUTPUT_DIRECTORY = Path(
    "datasets/nasa_power/raw"
)

OUTPUT_CSV_PATH = (
    OUTPUT_DIRECTORY
    / "nasa_power_india_climatology.csv"
)

PROGRESS_FILE_PATH = (
    OUTPUT_DIRECTORY
    / "download_progress.json"
)


# --------------------------------------------------
# GRID CONFIGURATION
# --------------------------------------------------

GRID_SPACING = 0.5


# --------------------------------------------------
# TEST MODE CONFIGURATION
# --------------------------------------------------

TEST_MODE = False

TEST_POINT_LIMIT = 5


# --------------------------------------------------
# REQUEST CONFIGURATION
# --------------------------------------------------

MAX_RETRIES = 3

RETRY_DELAY_SECONDS = 10

REQUEST_DELAY_SECONDS = 2

REQUEST_TIMEOUT_SECONDS = 120


# --------------------------------------------------
# INDIA APPROXIMATE BOUNDING BOX
# --------------------------------------------------

INDIA_MIN_LATITUDE = 6.5

INDIA_MAX_LATITUDE = 37.5

INDIA_MIN_LONGITUDE = 68.0

INDIA_MAX_LONGITUDE = 97.5


# --------------------------------------------------
# NASA POWER PARAMETERS
# --------------------------------------------------

NASA_PARAMETERS = [
    "ALLSKY_SFC_SW_DWN",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "PRECTOTCORR",
    "WS10M",
    "WS50M",
]


# --------------------------------------------------
# OUTPUT CSV COLUMNS
# --------------------------------------------------

CSV_COLUMNS = [
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
# CREATE OUTPUT DIRECTORY
# --------------------------------------------------

def create_output_directory():

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )


# --------------------------------------------------
# LOAD INDIA BOUNDARY
# --------------------------------------------------

def load_india_boundary():

    print(
        "\n===== LOADING INDIA BOUNDARY ====="
    )

    if not INDIA_BOUNDARY_PATH.exists():

        raise FileNotFoundError(
            f"India boundary file not found: "
            f"{INDIA_BOUNDARY_PATH}"
        )


    with open(
        INDIA_BOUNDARY_PATH,
        "r",
        encoding="utf-8",
    ) as boundary_file:

        boundary_data = json.load(
            boundary_file
        )


    if (
        "features" not in boundary_data
        or len(boundary_data["features"]) == 0
    ):

        raise ValueError(
            "India boundary GeoJSON "
            "contains no features."
        )


    india_boundary = shape(
        boundary_data["features"][0]["geometry"]
    )


    if not india_boundary.is_valid:

        print(
            "Boundary geometry is invalid."
        )

        print(
            "Attempting geometry repair..."
        )

        india_boundary = (
            india_boundary.buffer(0)
        )


    if not india_boundary.is_valid:

        raise ValueError(
            "India boundary geometry "
            "could not be repaired."
        )


    print(
        "India Boundary: LOADED"
    )

    print(
        "Geometry Type:",
        india_boundary.geom_type,
    )


    return india_boundary


# --------------------------------------------------
# GENERATE INDIA GRID POINTS
# --------------------------------------------------

def generate_india_grid(
    india_boundary,
):

    print(
        "\n===== GENERATING INDIA GRID ====="
    )

    grid_points = []


    latitude = INDIA_MIN_LATITUDE


    while (
        latitude
        <= INDIA_MAX_LATITUDE
    ):

        longitude = (
            INDIA_MIN_LONGITUDE
        )


        while (
            longitude
            <= INDIA_MAX_LONGITUDE
        ):

            point = Point(
                longitude,
                latitude,
            )


            if india_boundary.covers(point):

                grid_points.append(
                    (
                        round(latitude, 4),
                        round(longitude, 4),
                    )
                )


            longitude += GRID_SPACING


        latitude += GRID_SPACING


    print(
        "Grid Spacing:",
        GRID_SPACING,
        "degrees",
    )

    print(
        "India Grid Points:",
        len(grid_points),
    )


    if len(grid_points) == 0:

        raise ValueError(
            "No grid points were generated."
        )


    return grid_points


# --------------------------------------------------
# LOAD COMPLETED POINTS
# --------------------------------------------------

def load_completed_points():

    completed_points = set()


    if not OUTPUT_CSV_PATH.exists():

        return completed_points


    try:

        with open(
            OUTPUT_CSV_PATH,
            "r",
            encoding="utf-8",
            newline="",
        ) as csv_file:

            reader = csv.DictReader(
                csv_file
            )


            for row in reader:

                try:

                    latitude = float(
                        row["latitude"]
                    )

                    longitude = float(
                        row["longitude"]
                    )


                    completed_points.add(
                        (
                            round(latitude, 4),
                            round(longitude, 4),
                        )
                    )


                except (
                    KeyError,
                    TypeError,
                    ValueError,
                ):

                    continue


    except OSError as error:

        print(
            "Warning: Could not read "
            "existing CSV:"
        )

        print(error)


    return completed_points


# --------------------------------------------------
# SAVE PROGRESS
# --------------------------------------------------

def save_progress(
    total_points,
    successful_downloads,
    failed_downloads,
    skipped_points,
):

    progress_data = {

        "total_points": int(
            total_points
        ),

        "successful_downloads": int(
            successful_downloads
        ),

        "failed_downloads": int(
            failed_downloads
        ),

        "skipped_existing_points": int(
            skipped_points
        ),

        "test_mode": bool(
            TEST_MODE
        ),

        "grid_spacing_degrees": float(
            GRID_SPACING
        ),
    }


    with open(
        PROGRESS_FILE_PATH,
        "w",
        encoding="utf-8",
    ) as progress_file:

        json.dump(
            progress_data,
            progress_file,
            indent=4,
        )


# --------------------------------------------------
# EXTRACT NASA PARAMETER VALUE
# --------------------------------------------------

def extract_parameter_value(
    parameter_data,
    parameter_name,
):

    parameter = parameter_data.get(
        parameter_name
    )


    if parameter is None:

        return None


    annual_value = parameter.get(
        "ANN"
    )


    if annual_value is None:

        return None


    try:

        annual_value = float(
            annual_value
        )


    except (
        TypeError,
        ValueError,
    ):

        return None


    # NASA POWER commonly uses -999
    # for unavailable values.

    if annual_value <= -900:

        return None


    if not math.isfinite(
        annual_value
    ):

        return None


    return annual_value


# --------------------------------------------------
# DOWNLOAD ONE NASA POWER POINT
# --------------------------------------------------

def download_nasa_power_point(
    latitude,
    longitude,
):

    parameters = {

        "parameters": ",".join(
            NASA_PARAMETERS
        ),

        "community": "RE",

        "longitude": longitude,

        "latitude": latitude,

        "format": "JSON",
    }


    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        print(
            f"Request attempt "
            f"{attempt}/{MAX_RETRIES}"
        )


        try:

            response = requests.get(

                NASA_POWER_API_URL,

                params=parameters,

                timeout=(
                    REQUEST_TIMEOUT_SECONDS
                ),
            )


            if response.status_code != 200:

                print(
                    "HTTP Error:",
                    response.status_code,
                )

                print(
                    "Server Response:",
                    response.text[:500],
                )


            else:

                response_data = (
                    response.json()
                )


                properties = (
                    response_data.get(
                        "properties"
                    )
                )


                if properties is None:

                    print(
                        "Invalid response: "
                        "properties missing."
                    )

                    return None


                parameter_data = (
                    properties.get(
                        "parameter"
                    )
                )


                if parameter_data is None:

                    print(
                        "Invalid response: "
                        "parameter data missing."
                    )

                    return None


                record = {

                    "latitude":
                        float(latitude),

                    "longitude":
                        float(longitude),

                    "solar_radiation_kwh_m2_day":
                        extract_parameter_value(
                            parameter_data,
                            "ALLSKY_SFC_SW_DWN",
                        ),

                    "temperature_mean_c":
                        extract_parameter_value(
                            parameter_data,
                            "T2M",
                        ),

                    "temperature_max_c":
                        extract_parameter_value(
                            parameter_data,
                            "T2M_MAX",
                        ),

                    "temperature_min_c":
                        extract_parameter_value(
                            parameter_data,
                            "T2M_MIN",
                        ),

                    "relative_humidity_pct":
                        extract_parameter_value(
                            parameter_data,
                            "RH2M",
                        ),

                    "precipitation_mm_day":
                        extract_parameter_value(
                            parameter_data,
                            "PRECTOTCORR",
                        ),

                    "wind_speed_10m_ms":
                        extract_parameter_value(
                            parameter_data,
                            "WS10M",
                        ),

                    "wind_speed_50m_ms":
                        extract_parameter_value(
                            parameter_data,
                            "WS50M",
                        ),
                }


                required_values = [

                    record[
                        "solar_radiation_kwh_m2_day"
                    ],

                    record[
                        "temperature_mean_c"
                    ],

                    record[
                        "wind_speed_10m_ms"
                    ],
                ]


                if any(
                    value is None
                    for value
                    in required_values
                ):

                    print(
                        "Required NASA POWER "
                        "values are missing."
                    )

                    return None


                return record


        except requests.RequestException as error:

            print(
                "Request Error:",
                error,
            )


        except ValueError as error:

            print(
                "JSON Parsing Error:",
                error,
            )


        if attempt < MAX_RETRIES:

            print(
                f"Waiting "
                f"{RETRY_DELAY_SECONDS} "
                f"seconds before retry..."
            )

            time.sleep(
                RETRY_DELAY_SECONDS
            )


    return None


# --------------------------------------------------
# APPEND RECORD TO CSV
# --------------------------------------------------

def append_record_to_csv(
    record,
):

    file_exists = (
        OUTPUT_CSV_PATH.exists()
    )


    with open(
        OUTPUT_CSV_PATH,
        "a",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_COLUMNS,
        )


        if not file_exists:

            writer.writeheader()


        writer.writerow(
            record
        )


# --------------------------------------------------
# VALIDATE OUTPUT DATASET
# --------------------------------------------------

def validate_output_dataset():

    print(
        "\n===== VALIDATING OUTPUT DATASET ====="
    )


    if not OUTPUT_CSV_PATH.exists():

        print(
            "Output CSV: NOT FOUND"
        )

        return False


    try:

        with open(
            OUTPUT_CSV_PATH,
            "r",
            encoding="utf-8",
            newline="",
        ) as csv_file:

            reader = csv.DictReader(
                csv_file
            )


            if reader.fieldnames != CSV_COLUMNS:

                print(
                    "CSV Columns: INVALID"
                )

                return False


            records = list(
                reader
            )


        if len(records) == 0:

            print(
                "CSV Records: EMPTY"
            )

            return False


        print(
            "CSV Columns: VALID"
        )

        print(
            "CSV Records:",
            len(records),
        )


        valid_records = 0


        for record in records:

            try:

                latitude = float(
                    record["latitude"]
                )

                longitude = float(
                    record["longitude"]
                )

                solar_radiation = float(
                    record[
                        "solar_radiation_kwh_m2_day"
                    ]
                )

                temperature = float(
                    record[
                        "temperature_mean_c"
                    ]
                )

                wind_speed = float(
                    record[
                        "wind_speed_10m_ms"
                    ]
                )


                if (
                    math.isfinite(latitude)
                    and math.isfinite(longitude)
                    and math.isfinite(
                        solar_radiation
                    )
                    and math.isfinite(
                        temperature
                    )
                    and math.isfinite(
                        wind_speed
                    )
                ):

                    valid_records += 1


            except (
                KeyError,
                TypeError,
                ValueError,
            ):

                continue


        print(
            "Valid Records:",
            valid_records,
        )


        if (
            valid_records
            != len(records)
        ):

            print(
                "Dataset Validation: FAILED"
            )

            return False


        print(
            "Dataset Validation: PASSED"
        )

        return True


    except OSError as error:

        print(
            "Dataset Validation Error:",
            error,
        )

        return False


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print(
        "\n===== NASA POWER INDIA "
        "DATASET DOWNLOAD ====="
    )


    print(
        "\nNASA POWER Dataset Type:"
    )

    print(
        "Long-Term Climatology"
    )


    print(
        "\nGrid Spacing:",
        GRID_SPACING,
        "degrees",
    )


    print(
        "Test Mode:",
        TEST_MODE,
    )


    if TEST_MODE:

        print(
            "Test Point Limit:",
            TEST_POINT_LIMIT,
        )


    # --------------------------------------------------
    # CREATE DIRECTORIES
    # --------------------------------------------------

    create_output_directory()


    # --------------------------------------------------
    # LOAD BOUNDARY
    # --------------------------------------------------

    india_boundary = (
        load_india_boundary()
    )


    # --------------------------------------------------
    # GENERATE GRID
    # --------------------------------------------------

    grid_points = (
        generate_india_grid(
            india_boundary
        )
    )


    total_india_points = len(
        grid_points
    )


    # --------------------------------------------------
    # TEST MODE
    # --------------------------------------------------

    if TEST_MODE:

        grid_points = grid_points[
            :TEST_POINT_LIMIT
        ]


    total_processing_points = len(
        grid_points
    )


    print(
        "\nTotal India Grid Points:",
        total_india_points,
    )


    print(
        "Points Selected For Processing:",
        total_processing_points,
    )


    # --------------------------------------------------
    # LOAD EXISTING DOWNLOADS
    # --------------------------------------------------

    completed_points = (
        load_completed_points()
    )


    print(
        "Previously Downloaded Points:",
        len(completed_points),
    )


    # --------------------------------------------------
    # COUNTERS
    # --------------------------------------------------

    successful_downloads = 0

    failed_downloads = 0

    skipped_points = 0


    processing_start_time = (
        time.time()
    )


    # --------------------------------------------------
    # PROCESS GRID POINTS
    # --------------------------------------------------

    for index, (
        latitude,
        longitude,
    ) in enumerate(
        grid_points,
        start=1,
    ):

        print(
            "\n----------------------------------------"
        )


        print(
            f"Point "
            f"{index}/{total_processing_points}"
        )


        print(
            "Latitude:",
            latitude,
        )


        print(
            "Longitude:",
            longitude,
        )


        point_key = (

            round(latitude, 4),

            round(longitude, 4),
        )


        # --------------------------------------------------
        # SKIP EXISTING POINT
        # --------------------------------------------------

        if point_key in completed_points:

            print(
                "Status: Already downloaded. "
                "Skipping."
            )

            skipped_points += 1


        else:

            # --------------------------------------------------
            # DOWNLOAD POINT
            # --------------------------------------------------

            record = (
                download_nasa_power_point(
                    latitude=latitude,
                    longitude=longitude,
                )
            )


            if record is not None:

                append_record_to_csv(
                    record
                )


                completed_points.add(
                    point_key
                )


                successful_downloads += 1


                print(
                    "Status: Download successful."
                )


                print(
                    "Solar Radiation:",
                    record[
                        "solar_radiation_kwh_m2_day"
                    ],
                    "kWh/m²/day",
                )


                print(
                    "Mean Temperature:",
                    record[
                        "temperature_mean_c"
                    ],
                    "°C",
                )


                print(
                    "Wind Speed 10m:",
                    record[
                        "wind_speed_10m_ms"
                    ],
                    "m/s",
                )


            else:

                failed_downloads += 1


                print(
                    "Status: Download failed."
                )


        # --------------------------------------------------
        # SAVE PROGRESS
        # --------------------------------------------------

        save_progress(

            total_points=(
                total_processing_points
            ),

            successful_downloads=(
                successful_downloads
            ),

            failed_downloads=(
                failed_downloads
            ),

            skipped_points=(
                skipped_points
            ),
        )


        # --------------------------------------------------
        # DISPLAY PROGRESS
        # --------------------------------------------------

        print(
            "Progress:",
            f"{index}/{total_processing_points}",
        )


        print(
            "Successful:",
            successful_downloads,
        )


        print(
            "Failed:",
            failed_downloads,
        )


        print(
            "Skipped:",
            skipped_points,
        )


        # --------------------------------------------------
        # API DELAY
        # --------------------------------------------------

        if (
            index
            < total_processing_points
        ):

            time.sleep(
                REQUEST_DELAY_SECONDS
            )


    # --------------------------------------------------
    # VALIDATE DATASET
    # --------------------------------------------------

    dataset_valid = (
        validate_output_dataset()
    )


    # --------------------------------------------------
    # PROCESSING TIME
    # --------------------------------------------------

    total_processing_time = (

        time.time()
        - processing_start_time
    )


    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    print(
        "\n===== NASA POWER DOWNLOAD SUMMARY ====="
    )


    print(
        "Total India Grid Points:",
        total_india_points,
    )


    print(
        "Processed This Run:",
        total_processing_points,
    )


    print(
        "Successful Downloads:",
        successful_downloads,
    )


    print(
        "Failed Downloads:",
        failed_downloads,
    )


    print(
        "Skipped Existing Points:",
        skipped_points,
    )


    print(
        "Output File:",
        OUTPUT_CSV_PATH,
    )


    print(
        "Dataset Validation:",
        (
            "PASSED"
            if dataset_valid
            else "FAILED"
        ),
    )


    print(
        "Total Processing Time:",
        round(
            total_processing_time,
            2,
        ),
        "seconds",
    )


    # --------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------

    if (
        dataset_valid
        and failed_downloads == 0
    ):

        print(
            "\n===== NASA POWER DATASET "
            "TEST COMPLETED SUCCESSFULLY ====="
        )


    elif dataset_valid:

        print(
            "\n===== NASA POWER DATASET "
            "COMPLETED WITH SOME FAILURES ====="
        )


    else:

        print(
            "\n===== NASA POWER DATASET "
            "PROCESSING FAILED ====="
        )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()