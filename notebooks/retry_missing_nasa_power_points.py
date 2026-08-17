import csv
import math
import time
from pathlib import Path

import requests


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

NASA_POWER_API_URL = (
    "https://power.larc.nasa.gov/api/temporal/climatology/point"
)

DATA_DIRECTORY = Path(
    "datasets/nasa_power/raw"
)

MAIN_DATASET_PATH = (
    DATA_DIRECTORY
    / "nasa_power_india_climatology.csv"
)

MISSING_POINTS_PATH = (
    DATA_DIRECTORY
    / "missing_nasa_power_points.csv"
)


# --------------------------------------------------
# REQUEST CONFIGURATION
# --------------------------------------------------

MAX_RETRIES = 5

RETRY_DELAY_SECONDS = 15

REQUEST_DELAY_SECONDS = 3

REQUEST_TIMEOUT_SECONDS = 180


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
# CSV COLUMNS
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
# EXTRACT NASA POWER PARAMETER
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

    if annual_value <= -900:
        return None

    if not math.isfinite(
        annual_value
    ):
        return None

    return annual_value


# --------------------------------------------------
# LOAD MISSING POINTS
# --------------------------------------------------

def load_missing_points():

    print(
        "\n===== LOADING MISSING NASA POWER POINTS ====="
    )

    if not MISSING_POINTS_PATH.exists():

        raise FileNotFoundError(
            f"Missing points file not found: "
            f"{MISSING_POINTS_PATH}"
        )

    missing_points = []

    with open(
        MISSING_POINTS_PATH,
        "r",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        reader = csv.DictReader(
            csv_file
        )

        if (
            "latitude" not in reader.fieldnames
            or "longitude" not in reader.fieldnames
        ):

            raise ValueError(
                "Missing points CSV does not contain "
                "latitude and longitude columns."
            )

        for row in reader:

            try:

                latitude = float(
                    row["latitude"]
                )

                longitude = float(
                    row["longitude"]
                )

                missing_points.append(
                    (
                        round(latitude, 4),
                        round(longitude, 4),
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

    print(
        "Missing Points Loaded:",
        len(missing_points),
    )

    return missing_points


# --------------------------------------------------
# LOAD EXISTING DATASET POINTS
# --------------------------------------------------

def load_existing_points():

    print(
        "\n===== LOADING EXISTING NASA POWER DATASET ====="
    )

    if not MAIN_DATASET_PATH.exists():

        raise FileNotFoundError(
            f"NASA POWER dataset not found: "
            f"{MAIN_DATASET_PATH}"
        )

    existing_points = set()

    with open(
        MAIN_DATASET_PATH,
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

                existing_points.add(
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

    print(
        "Existing Unique Points:",
        len(existing_points),
    )

    return existing_points


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
                timeout=REQUEST_TIMEOUT_SECONDS,
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

                else:

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

                    else:

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

                        if all(
                            value is not None
                            for value
                            in required_values
                        ):

                            return record

                        print(
                            "Required NASA POWER "
                            "values are missing."
                        )

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
                f"{RETRY_DELAY_SECONDS} seconds "
                f"before retry..."
            )

            time.sleep(
                RETRY_DELAY_SECONDS
            )

    return None


# --------------------------------------------------
# APPEND RECORD TO MAIN DATASET
# --------------------------------------------------

def append_record_to_dataset(
    record,
):

    with open(
        MAIN_DATASET_PATH,
        "a",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_COLUMNS,
        )

        writer.writerow(
            record
        )


# --------------------------------------------------
# VALIDATE FINAL DATASET
# --------------------------------------------------

def validate_final_dataset():

    print(
        "\n===== VALIDATING FINAL NASA POWER DATASET ====="
    )

    records = []

    coordinate_points = set()

    with open(
        MAIN_DATASET_PATH,
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

            return False, 0, 0

        for row in reader:

            records.append(
                row
            )

            try:

                latitude = float(
                    row["latitude"]
                )

                longitude = float(
                    row["longitude"]
                )

                coordinate_points.add(
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

    total_records = len(records)

    unique_points = len(
        coordinate_points
    )

    duplicate_records = (
        total_records
        - unique_points
    )

    print(
        "CSV Columns: VALID"
    )

    print(
        "Total CSV Records:",
        total_records,
    )

    print(
        "Unique Coordinate Points:",
        unique_points,
    )

    print(
        "Duplicate Records:",
        duplicate_records,
    )

    dataset_valid = (
        total_records == unique_points
        and unique_points > 0
    )

    print(
        "Dataset Validation:",
        (
            "PASSED"
            if dataset_valid
            else "FAILED"
        ),
    )

    return (
        dataset_valid,
        total_records,
        unique_points,
    )


# --------------------------------------------------
# SAVE REMAINING FAILED POINTS
# --------------------------------------------------

def save_remaining_missing_points(
    failed_points,
):

    if not failed_points:

        if MISSING_POINTS_PATH.exists():

            MISSING_POINTS_PATH.unlink()

        print(
            "Remaining Missing Points: 0"
        )

        print(
            "Missing points report removed."
        )

        return

    with open(
        MISSING_POINTS_PATH,
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "latitude",
                "longitude",
            ],
        )

        writer.writeheader()

        for (
            latitude,
            longitude,
        ) in failed_points:

            writer.writerow(
                {
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )

    print(
        "Remaining Missing Points:",
        len(failed_points),
    )

    print(
        "Updated Missing Points Report:",
        MISSING_POINTS_PATH,
    )


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print(
        "\n===== NASA POWER MISSING POINT RETRY ====="
    )

    processing_start_time = (
        time.time()
    )


    # --------------------------------------------------
    # LOAD MISSING POINTS
    # --------------------------------------------------

    missing_points = (
        load_missing_points()
    )


    # --------------------------------------------------
    # LOAD EXISTING POINTS
    # --------------------------------------------------

    existing_points = (
        load_existing_points()
    )


    # --------------------------------------------------
    # REMOVE POINTS ALREADY IN DATASET
    # --------------------------------------------------

    points_to_retry = [

        point

        for point in missing_points

        if point not in existing_points
    ]


    print(
        "\n===== RETRY INFORMATION ====="
    )

    print(
        "Points In Missing Report:",
        len(missing_points),
    )

    print(
        "Points Already Downloaded:",
        (
            len(missing_points)
            - len(points_to_retry)
        ),
    )

    print(
        "Points Selected For Retry:",
        len(points_to_retry),
    )


    # --------------------------------------------------
    # COUNTERS
    # --------------------------------------------------

    successful_downloads = 0

    failed_downloads = 0

    failed_points = []


    # --------------------------------------------------
    # RETRY MISSING POINTS
    # --------------------------------------------------

    for index, (
        latitude,
        longitude,
    ) in enumerate(
        points_to_retry,
        start=1,
    ):

        print(
            "\n----------------------------------------"
        )

        print(
            f"Point "
            f"{index}/{len(points_to_retry)}"
        )

        print(
            "Latitude:",
            latitude,
        )

        print(
            "Longitude:",
            longitude,
        )

        record = (
            download_nasa_power_point(
                latitude=latitude,
                longitude=longitude,
            )
        )

        if record is not None:

            append_record_to_dataset(
                record
            )

            existing_points.add(
                (
                    latitude,
                    longitude,
                )
            )

            successful_downloads += 1

            print(
                "Status: Retry successful."
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

            failed_points.append(
                (
                    latitude,
                    longitude,
                )
            )

            print(
                "Status: Retry failed."
            )

        print(
            "Successful Retries:",
            successful_downloads,
        )

        print(
            "Failed Retries:",
            failed_downloads,
        )

        if index < len(
            points_to_retry
        ):

            time.sleep(
                REQUEST_DELAY_SECONDS
            )


    # --------------------------------------------------
    # SAVE REMAINING MISSING POINTS
    # --------------------------------------------------

    print(
        "\n===== UPDATING MISSING POINT REPORT ====="
    )

    save_remaining_missing_points(
        failed_points
    )


    # --------------------------------------------------
    # FINAL DATASET VALIDATION
    # --------------------------------------------------

    (
        dataset_valid,
        total_records,
        unique_points,
    ) = validate_final_dataset()


    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    processing_time = (
        time.time()
        - processing_start_time
    )

    print(
        "\n===== NASA POWER RETRY SUMMARY ====="
    )

    print(
        "Points Selected For Retry:",
        len(points_to_retry),
    )

    print(
        "Successful Retries:",
        successful_downloads,
    )

    print(
        "Failed Retries:",
        failed_downloads,
    )

    print(
        "Final CSV Records:",
        total_records,
    )

    print(
        "Final Unique Points:",
        unique_points,
    )

    print(
        "Expected India Grid Points:",
        1149,
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

    if (
        dataset_valid
        and unique_points == 1149
        and failed_downloads == 0
    ):

        print(
            "\n===== NASA POWER INDIA DATASET "
            "COMPLETED SUCCESSFULLY ====="
        )

        print(
            "All 1149 expected India grid points "
            "are present."
        )

    elif dataset_valid:

        print(
            "\n===== NASA POWER DATASET "
            "RETRY COMPLETED WITH "
            "REMAINING MISSING POINTS ====="
        )

    else:

        print(
            "\n===== NASA POWER DATASET "
            "VALIDATION FAILED ====="
        )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()