from pathlib import Path

import rasterio


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SRTM_DIRECTORY = Path("datasets/srtm/raw_tiles")

EXPECTED_TILE_COUNT = 121


# --------------------------------------------------
# MAIN VALIDATION FUNCTION
# --------------------------------------------------

def main():

    print("\n===== INDIA SRTM DATASET VALIDATION =====")

    print("\nSRTM Directory:", SRTM_DIRECTORY)

    # Find all SRTM GeoTIFF files
    srtm_files = sorted(SRTM_DIRECTORY.glob("*.tif"))

    total_files = len(srtm_files)

    print("Expected SRTM Tiles:", EXPECTED_TILE_COUNT)
    print("Found SRTM Tiles:", total_files)


    # --------------------------------------------------
    # FILE COUNT VALIDATION
    # --------------------------------------------------

    print("\n===== FILE COUNT VALIDATION =====")

    if total_files == EXPECTED_TILE_COUNT:

        print("Status: PASSED")

    else:

        print("Status: FAILED")

        print(
            "Difference:",
            total_files - EXPECTED_TILE_COUNT,
        )


    # --------------------------------------------------
    # VALIDATION COUNTERS
    # --------------------------------------------------

    valid_files = 0

    corrupted_files = []

    invalid_crs_files = []

    invalid_band_files = []

    nodata_only_files = []

    total_valid_cells = 0

    total_nodata_cells = 0


    # --------------------------------------------------
    # VALIDATE EACH SRTM TILE
    # --------------------------------------------------

    print("\n===== VALIDATING SRTM TILES =====")

    for index, file_path in enumerate(
        srtm_files,
        start=1,
    ):

        print(
            f"\nValidating Tile {index}/{total_files}"
        )

        print("File:", file_path.name)

        try:

            with rasterio.open(file_path) as dataset:

                # --------------------------------------
                # BASIC RASTER INFORMATION
                # --------------------------------------

                print("CRS:", dataset.crs)

                print(
                    "Dimensions:",
                    f"{dataset.width} x {dataset.height}",
                )

                print("Bands:", dataset.count)

                print("Data Type:", dataset.dtypes[0])

                print("NoData Value:", dataset.nodata)

                print("Resolution:", dataset.res)


                # --------------------------------------
                # CRS VALIDATION
                # --------------------------------------

                if dataset.crs is None:

                    print("CRS Status: FAILED")

                    invalid_crs_files.append(
                        file_path.name
                    )

                    continue

                print("CRS Status: PASSED")


                # --------------------------------------
                # BAND VALIDATION
                # --------------------------------------

                if dataset.count < 1:

                    print("Band Status: FAILED")

                    invalid_band_files.append(
                        file_path.name
                    )

                    continue

                print("Band Status: PASSED")


                # --------------------------------------
                # READ ELEVATION DATA
                # --------------------------------------

                elevation_data = dataset.read(
                    1,
                    masked=True,
                )

                total_cells = elevation_data.size

                valid_cells = elevation_data.count()

                nodata_cells = (
                    total_cells - valid_cells
                )


                # --------------------------------------
                # UPDATE CELL COUNTERS
                # --------------------------------------

                total_valid_cells += valid_cells

                total_nodata_cells += nodata_cells


                # --------------------------------------
                # NODATA-ONLY TILE CHECK
                # --------------------------------------

                if valid_cells == 0:

                    print(
                        "Data Status: NODATA-ONLY TILE"
                    )

                    print("Valid Cells: 0")

                    print(
                        "NoData Cells:",
                        nodata_cells,
                    )

                    nodata_only_files.append(
                        file_path.name
                    )

                    print(
                        "Tile Status: VALID NODATA/OCEAN TILE"
                    )

                    continue


                # --------------------------------------
                # VALID ELEVATION DATA
                # --------------------------------------

                print("Data Status: PASSED")

                minimum_elevation = (
                    elevation_data.min()
                )

                maximum_elevation = (
                    elevation_data.max()
                )

                average_elevation = (
                    elevation_data.mean()
                )


                print(
                    "Valid Cells:",
                    valid_cells,
                )

                print(
                    "NoData Cells:",
                    nodata_cells,
                )

                print(
                    "Minimum Elevation:",
                    minimum_elevation,
                    "meters",
                )

                print(
                    "Maximum Elevation:",
                    maximum_elevation,
                    "meters",
                )

                print(
                    "Average Elevation:",
                    round(
                        float(average_elevation),
                        2,
                    ),
                    "meters",
                )


                # --------------------------------------
                # UPDATE VALID FILE COUNTER
                # --------------------------------------

                valid_files += 1

                print(
                    "Tile Status: VALID ELEVATION TILE"
                )


        except Exception as error:

            corrupted_files.append(
                file_path.name
            )

            print("Tile Status: CORRUPTED")

            print("Error:", error)


    # --------------------------------------------------
    # FINAL VALIDATION SUMMARY
    # --------------------------------------------------

    print("\n===== SRTM VALIDATION SUMMARY =====")

    print(
        "Expected Tiles:",
        EXPECTED_TILE_COUNT,
    )

    print(
        "Found Tiles:",
        total_files,
    )

    print(
        "Valid Elevation Tiles:",
        valid_files,
    )

    print(
        "NoData / Ocean Tiles:",
        len(nodata_only_files),
    )

    print(
        "Corrupted Tiles:",
        len(corrupted_files),
    )

    print(
        "Invalid CRS Tiles:",
        len(invalid_crs_files),
    )

    print(
        "Invalid Band Tiles:",
        len(invalid_band_files),
    )

    print(
        "Total Valid Elevation Cells:",
        total_valid_cells,
    )

    print(
        "Total NoData Cells:",
        total_nodata_cells,
    )


    # --------------------------------------------------
    # DISPLAY NODATA / OCEAN FILES
    # --------------------------------------------------

    if nodata_only_files:

        print("\n===== NODATA / OCEAN TILES =====")

        for file_name in nodata_only_files:

            print("-", file_name)


    # --------------------------------------------------
    # DISPLAY PROBLEM FILES
    # --------------------------------------------------

    if corrupted_files:

        print("\n===== CORRUPTED FILES =====")

        for file_name in corrupted_files:

            print("-", file_name)


    if invalid_crs_files:

        print("\n===== INVALID CRS FILES =====")

        for file_name in invalid_crs_files:

            print("-", file_name)


    if invalid_band_files:

        print("\n===== INVALID BAND FILES =====")

        for file_name in invalid_band_files:

            print("-", file_name)


    # --------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------

    print("\n===== FINAL SRTM STATUS =====")

    processed_tile_count = (
        valid_files
        + len(nodata_only_files)
    )

    if (
        total_files == EXPECTED_TILE_COUNT
        and processed_tile_count == EXPECTED_TILE_COUNT
        and len(corrupted_files) == 0
        and len(invalid_crs_files) == 0
        and len(invalid_band_files) == 0
    ):

        print(
            "SRTM DATASET VALIDATION PASSED"
        )

        print(
            f"{valid_files} tiles contain "
            "valid elevation data."
        )

        print(
            f"{len(nodata_only_files)} tiles contain "
            "only NoData values and are classified "
            "as NoData / ocean-region tiles."
        )

        print(
            "All 121 expected SRTM tiles "
            "were successfully accounted for."
        )

    else:

        print(
            "SRTM DATASET VALIDATION FAILED"
        )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()