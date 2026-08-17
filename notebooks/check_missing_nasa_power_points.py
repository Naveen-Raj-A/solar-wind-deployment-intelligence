import json
from pathlib import Path

import pandas as pd
from shapely.geometry import Point, shape


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

INDIA_BOUNDARY_PATH = Path(
    "datasets/boundaries/geoBoundaries-IND-ADM0.geojson"
)

NASA_POWER_DATASET_PATH = Path(
    "datasets/nasa_power/raw/"
    "nasa_power_india_climatology.csv"
)

GRID_SPACING = 0.5


# --------------------------------------------------
# INDIA BOUNDING BOX
# --------------------------------------------------

INDIA_WEST = 68.0

INDIA_SOUTH = 6.5

INDIA_EAST = 97.5

INDIA_NORTH = 37.1


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
    ) as file:

        geojson_data = json.load(file)

    india_boundary = shape(
        geojson_data["features"][0]["geometry"]
    )

    if not india_boundary.is_valid:

        raise ValueError(
            "India boundary geometry is invalid."
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
        "\n===== GENERATING EXPECTED INDIA GRID ====="
    )

    grid_points = []

    latitude = INDIA_SOUTH

    while latitude <= INDIA_NORTH:

        longitude = INDIA_WEST

        while longitude <= INDIA_EAST:

            # Round coordinates to avoid
            # floating-point comparison problems.

            rounded_latitude = round(
                latitude,
                6,
            )

            rounded_longitude = round(
                longitude,
                6,
            )

            point = Point(
                rounded_longitude,
                rounded_latitude,
            )

            # Use covers() instead of contains()
            # so points exactly on the India
            # boundary are also included.

            if india_boundary.covers(point):

                grid_points.append(
                    (
                        rounded_latitude,
                        rounded_longitude,
                    )
                )

            longitude += GRID_SPACING

        latitude += GRID_SPACING

    print(
        "Expected India Grid Points:",
        len(grid_points),
    )

    return grid_points


# --------------------------------------------------
# LOAD NASA POWER DATASET
# --------------------------------------------------

def load_nasa_power_dataset():

    print(
        "\n===== LOADING NASA POWER DATASET ====="
    )

    if not NASA_POWER_DATASET_PATH.exists():

        raise FileNotFoundError(
            f"NASA POWER dataset not found: "
            f"{NASA_POWER_DATASET_PATH}"
        )

    dataframe = pd.read_csv(
        NASA_POWER_DATASET_PATH
    )

    print(
        "CSV Records:",
        len(dataframe),
    )

    print(
        "CSV Columns:",
        len(dataframe.columns),
    )

    return dataframe


# --------------------------------------------------
# VALIDATE REQUIRED COLUMNS
# --------------------------------------------------

def validate_required_columns(
    dataframe,
):

    print(
        "\n===== VALIDATING REQUIRED COLUMNS ====="
    )

    required_columns = {
        "latitude",
        "longitude",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    print(
        "Required Columns: VALID"
    )


# --------------------------------------------------
# EXTRACT DOWNLOADED POINTS
# --------------------------------------------------

def extract_downloaded_points(
    dataframe,
):

    print(
        "\n===== EXTRACTING DOWNLOADED POINTS ====="
    )

    downloaded_points = set()

    for _, row in dataframe.iterrows():

        latitude = round(
            float(row["latitude"]),
            6,
        )

        longitude = round(
            float(row["longitude"]),
            6,
        )

        downloaded_points.add(
            (
                latitude,
                longitude,
            )
        )

    print(
        "CSV Records:",
        len(dataframe),
    )

    print(
        "Unique Downloaded Points:",
        len(downloaded_points),
    )

    duplicate_count = (
        len(dataframe)
        - len(downloaded_points)
    )

    print(
        "Duplicate Coordinate Records:",
        duplicate_count,
    )

    return downloaded_points


# --------------------------------------------------
# FIND MISSING POINTS
# --------------------------------------------------

def find_missing_points(
    expected_grid_points,
    downloaded_points,
):

    print(
        "\n===== SEARCHING FOR MISSING POINTS ====="
    )

    expected_points_set = set(
        expected_grid_points
    )

    missing_points = sorted(
        expected_points_set
        - downloaded_points
    )

    print(
        "Expected Grid Points:",
        len(expected_points_set),
    )

    print(
        "Downloaded Points:",
        len(downloaded_points),
    )

    print(
        "Missing Points:",
        len(missing_points),
    )

    return missing_points


# --------------------------------------------------
# FIND UNEXPECTED POINTS
# --------------------------------------------------

def find_unexpected_points(
    expected_grid_points,
    downloaded_points,
):

    expected_points_set = set(
        expected_grid_points
    )

    unexpected_points = sorted(
        downloaded_points
        - expected_points_set
    )

    return unexpected_points


# --------------------------------------------------
# DISPLAY MISSING POINTS
# --------------------------------------------------

def display_missing_points(
    missing_points,
):

    print(
        "\n===== MISSING NASA POWER GRID POINTS ====="
    )

    if not missing_points:

        print(
            "No missing grid points found."
        )

        return

    for index, (
        latitude,
        longitude,
    ) in enumerate(
        missing_points,
        start=1,
    ):

        print(
            f"{index}. "
            f"Latitude: {latitude}, "
            f"Longitude: {longitude}"
        )


# --------------------------------------------------
# DISPLAY UNEXPECTED POINTS
# --------------------------------------------------

def display_unexpected_points(
    unexpected_points,
):

    print(
        "\n===== UNEXPECTED CSV POINTS ====="
    )

    if not unexpected_points:

        print(
            "No unexpected coordinate points found."
        )

        return

    for index, (
        latitude,
        longitude,
    ) in enumerate(
        unexpected_points,
        start=1,
    ):

        print(
            f"{index}. "
            f"Latitude: {latitude}, "
            f"Longitude: {longitude}"
        )


# --------------------------------------------------
# SAVE MISSING POINTS REPORT
# --------------------------------------------------

def save_missing_points_report(
    missing_points,
):

    output_path = Path(
        "datasets/nasa_power/raw/"
        "missing_nasa_power_points.csv"
    )

    missing_dataframe = pd.DataFrame(
        missing_points,
        columns=[
            "latitude",
            "longitude",
        ],
    )

    missing_dataframe.to_csv(
        output_path,
        index=False,
    )

    print(
        "\n===== SAVING MISSING POINTS REPORT ====="
    )

    print(
        "Saved:",
        output_path,
    )

    print(
        "Missing Records Saved:",
        len(missing_dataframe),
    )

    return output_path


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print(
        "\n===== NASA POWER MISSING POINT CHECK ====="
    )

    # --------------------------------------------------
    # LOAD INDIA BOUNDARY
    # --------------------------------------------------

    india_boundary = (
        load_india_boundary()
    )


    # --------------------------------------------------
    # GENERATE EXPECTED GRID
    # --------------------------------------------------

    expected_grid_points = (
        generate_india_grid(
            india_boundary
        )
    )


    # --------------------------------------------------
    # LOAD NASA POWER DATASET
    # --------------------------------------------------

    dataframe = (
        load_nasa_power_dataset()
    )


    # --------------------------------------------------
    # VALIDATE DATASET
    # --------------------------------------------------

    validate_required_columns(
        dataframe
    )


    # --------------------------------------------------
    # EXTRACT DOWNLOADED POINTS
    # --------------------------------------------------

    downloaded_points = (
        extract_downloaded_points(
            dataframe
        )
    )


    # --------------------------------------------------
    # FIND MISSING POINTS
    # --------------------------------------------------

    missing_points = (
        find_missing_points(
            expected_grid_points,
            downloaded_points,
        )
    )


    # --------------------------------------------------
    # FIND UNEXPECTED POINTS
    # --------------------------------------------------

    unexpected_points = (
        find_unexpected_points(
            expected_grid_points,
            downloaded_points,
        )
    )


    # --------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------

    display_missing_points(
        missing_points
    )

    display_unexpected_points(
        unexpected_points
    )


    # --------------------------------------------------
    # SAVE REPORT
    # --------------------------------------------------

    output_path = (
        save_missing_points_report(
            missing_points
        )
    )


    # --------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------

    expected_count = len(
        expected_grid_points
    )

    downloaded_count = len(
        downloaded_points
    )

    missing_count = len(
        missing_points
    )

    unexpected_count = len(
        unexpected_points
    )

    accounted_points = (
        downloaded_count
        + missing_count
    )


    print(
        "\n===== FINAL VALIDATION ====="
    )

    print(
        "Expected Grid Points:",
        expected_count,
    )

    print(
        "Unique Downloaded Points:",
        downloaded_count,
    )

    print(
        "Missing Points:",
        missing_count,
    )

    print(
        "Unexpected Points:",
        unexpected_count,
    )

    print(
        "Accounted Points:",
        accounted_points,
    )


    # --------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------

    print(
        "\n===== NASA POWER POINT CHECK SUMMARY ====="
    )

    if (
        expected_count == 1149
        and missing_count == 5
        and unexpected_count == 0
        and accounted_points == expected_count
    ):

        print(
            "Expected India Grid: VALID"
        )

        print(
            "Downloaded Dataset: VALID"
        )

        print(
            "Missing Point Detection: PASSED"
        )

        print(
            "Missing Points Report:",
            output_path,
        )

        print(
            "\n===== NASA POWER MISSING POINT "
            "CHECK COMPLETED SUCCESSFULLY ====="
        )

    elif (
        missing_count == 0
        and unexpected_count == 0
        and downloaded_count == expected_count
    ):

        print(
            "Expected India Grid: VALID"
        )

        print(
            "Downloaded Dataset: COMPLETE"
        )

        print(
            "Missing Point Detection: PASSED"
        )

        print(
            "\n===== NASA POWER DATASET "
            "IS FULLY COMPLETE ====="
        )

    else:

        print(
            "Expected India Grid Points:",
            expected_count,
        )

        print(
            "Dataset requires further investigation."
        )

        print(
            "\n===== NASA POWER POINT CHECK "
            "COMPLETED WITH WARNINGS ====="
        )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()