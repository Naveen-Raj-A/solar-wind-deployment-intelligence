from pathlib import Path
import re
import time

from geopy.geocoders import Nominatim
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import box, mapping


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

SRTM_DIRECTORY = Path(
    "datasets/srtm/raw_tiles"
)

OUTPUT_BASE_DIRECTORY = Path(
    "datasets/srtm/aoi"
)

AOI_OFFSET_DEGREES = 0.05

EXPECTED_CRS = "EPSG:4326"


# --------------------------------------------------
# CREATE SAFE LOCATION NAME
# --------------------------------------------------

def create_safe_location_name(location_name):
    """
    Convert the entered location into a safe
    directory name.
    """

    safe_name = location_name.strip().lower()

    safe_name = re.sub(
        r"[^a-z0-9]+",
        "_",
        safe_name,
    )

    safe_name = safe_name.strip("_")

    return safe_name


# --------------------------------------------------
# GEOCODE LOCATION
# --------------------------------------------------

def geocode_location(location_name):
    """
    Convert a location name in India into
    latitude and longitude.
    """

    print("\nSearching location...")

    geocoder = Nominatim(
        user_agent=(
            "solar_wind_deployment_"
            "intelligence_srtm"
        )
    )

    search_query = (
        f"{location_name}, India"
    )

    start_time = time.time()

    location = geocoder.geocode(
        search_query,
        timeout=20,
    )

    geocoding_time = (
        time.time() - start_time
    )

    if location is None:
        raise ValueError(
            "Location could not be found."
        )

    print("\n===== LOCATION FOUND =====")

    print(
        "Location:",
        location.address,
    )

    print(
        "Latitude:",
        location.latitude,
    )

    print(
        "Longitude:",
        location.longitude,
    )

    print(
        "Geocoding Time:",
        round(geocoding_time, 4),
        "seconds",
    )

    return (
        location.latitude,
        location.longitude,
        location.address,
    )


# --------------------------------------------------
# CREATE AOI BOUNDS
# --------------------------------------------------

def create_aoi_bounds(
    latitude,
    longitude,
):
    """
    Create a rectangular AOI around the
    geocoded location.
    """

    west = (
        longitude - AOI_OFFSET_DEGREES
    )

    south = (
        latitude - AOI_OFFSET_DEGREES
    )

    east = (
        longitude + AOI_OFFSET_DEGREES
    )

    north = (
        latitude + AOI_OFFSET_DEGREES
    )

    return (
        west,
        south,
        east,
        north,
    )


# --------------------------------------------------
# FIND INTERSECTING SRTM TILES
# --------------------------------------------------

def find_intersecting_tiles(aoi_geometry):
    """
    Find all SRTM GeoTIFF files whose actual
    raster bounds intersect the AOI.
    """

    print(
        "\n===== SEARCHING SRTM TILES ====="
    )

    srtm_files = sorted(
        SRTM_DIRECTORY.glob("*.tif")
    )

    print(
        "Available SRTM Tiles:",
        len(srtm_files),
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

        except rasterio.errors.RasterioIOError:

            print(
                "Warning: Could not open:",
                file_path.name,
            )

    return intersecting_tiles


# --------------------------------------------------
# MERGE INTERSECTING TILES
# --------------------------------------------------

def merge_srtm_tiles(tile_paths):
    """
    Merge all SRTM tiles intersecting the AOI.
    """

    print(
        "\n===== MERGING SRTM TILES ====="
    )

    source_datasets = []

    try:

        for tile_path in tile_paths:

            dataset = rasterio.open(
                tile_path
            )

            source_datasets.append(
                dataset
            )

        merged_data, merged_transform = merge(
            source_datasets
        )

        merged_metadata = (
            source_datasets[0].meta.copy()
        )

        merged_metadata.update(
            {
                "driver": "GTiff",
                "height": merged_data.shape[1],
                "width": merged_data.shape[2],
                "transform": merged_transform,
            }
        )

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


# --------------------------------------------------
# SAVE TEMPORARY MERGED RASTER
# --------------------------------------------------

def save_temporary_merged_raster(
    merged_data,
    merged_metadata,
    output_path,
):
    """
    Save merged raster temporarily so Rasterio
    mask can clip it to the requested AOI.
    """

    with rasterio.open(
        output_path,
        "w",
        **merged_metadata,
    ) as destination:

        destination.write(
            merged_data
        )


# --------------------------------------------------
# CLIP MERGED RASTER TO AOI
# --------------------------------------------------

def clip_raster_to_aoi(
    merged_raster_path,
    aoi_geometry,
    output_path,
):
    """
    Clip the merged SRTM raster to the
    requested AOI.
    """

    print(
        "\n===== EXTRACTING SRTM AOI ====="
    )

    with rasterio.open(
        merged_raster_path
    ) as source:

        clipped_data, clipped_transform = mask(
            source,
            [mapping(aoi_geometry)],
            crop=True,
        )

        clipped_metadata = (
            source.meta.copy()
        )

        clipped_metadata.update(
            {
                "driver": "GTiff",
                "height": clipped_data.shape[1],
                "width": clipped_data.shape[2],
                "transform": clipped_transform,
            }
        )

    with rasterio.open(
        output_path,
        "w",
        **clipped_metadata,
    ) as destination:

        destination.write(
            clipped_data
        )

    print(
        "Extraction Status: SUCCESSFUL"
    )


# --------------------------------------------------
# VALIDATE OUTPUT RASTER
# --------------------------------------------------

def validate_output(output_path):
    """
    Validate the final extracted elevation raster.
    """

    print(
        "\n===== OUTPUT VALIDATION ====="
    )

    if not output_path.exists():

        print(
            "Output File Status: FAILED"
        )

        return False

    try:

        with rasterio.open(
            output_path
        ) as dataset:

            print(
                "Output File:",
                output_path,
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
                "Bands:",
                dataset.count,
            )

            print(
                "Data Type:",
                dataset.dtypes[0],
            )

            print(
                "NoData Value:",
                dataset.nodata,
            )

            print(
                "Resolution:",
                dataset.res,
            )

            print(
                "Geographic Bounds:",
                dataset.bounds,
            )

            elevation_data = dataset.read(
                1,
                masked=True,
            )

            total_cells = (
                elevation_data.size
            )

            valid_cells = (
                elevation_data.count()
            )

            nodata_cells = (
                total_cells - valid_cells
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

            if valid_cells == 0:

                print(
                    "Data Validation: FAILED"
                )

                print(
                    "Reason: Extracted AOI contains "
                    "no valid elevation cells."
                )

                return False

            print(
                "Minimum Elevation:",
                elevation_data.min(),
                "meters",
            )

            print(
                "Maximum Elevation:",
                elevation_data.max(),
                "meters",
            )

            print(
                "Average Elevation:",
                round(
                    float(
                        elevation_data.mean()
                    ),
                    2,
                ),
                "meters",
            )

            print(
                "Output File Status: VALID"
            )

            return True

    except rasterio.errors.RasterioIOError as error:

        print(
            "Output File Status: FAILED"
        )

        print(
            "Error:",
            error,
        )

        return False


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print(
        "\n===== SRTM DYNAMIC AOI EXTRACTION ====="
    )

    location_name = input(
        "\nEnter location in India: "
    ).strip()

    if not location_name:

        print(
            "\nError: Location cannot be empty."
        )

        return

    total_start_time = time.time()

    try:

        # ------------------------------------------
        # GEOCODE LOCATION
        # ------------------------------------------

        (
            latitude,
            longitude,
            location_address,
        ) = geocode_location(
            location_name
        )


        # ------------------------------------------
        # CREATE AOI
        # ------------------------------------------

        (
            west,
            south,
            east,
            north,
        ) = create_aoi_bounds(
            latitude,
            longitude,
        )

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

        aoi_geometry = box(
            west,
            south,
            east,
            north,
        )


        # ------------------------------------------
        # FIND INTERSECTING TILES
        # ------------------------------------------

        intersecting_tiles = (
            find_intersecting_tiles(
                aoi_geometry
            )
        )

        print(
            "\nIntersecting SRTM Tiles:",
            len(intersecting_tiles),
        )

        if not intersecting_tiles:

            print(
                "\nNo SRTM tiles intersect "
                "the requested AOI."
            )

            return

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


        # ------------------------------------------
        # CREATE OUTPUT DIRECTORY
        # ------------------------------------------

        safe_location_name = (
            create_safe_location_name(
                location_name
            )
        )

        output_directory = (
            OUTPUT_BASE_DIRECTORY
            / safe_location_name
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_merged_path = (
            output_directory
            / "temporary_merged_srtm.tif"
        )

        final_output_path = (
            output_directory
            / "elevation.tif"
        )

        print(
            "\nOutput Directory:",
            output_directory,
        )


        # ------------------------------------------
        # MERGE TILES
        # ------------------------------------------

        (
            merged_data,
            merged_transform,
            merged_metadata,
        ) = merge_srtm_tiles(
            intersecting_tiles
        )


        # ------------------------------------------
        # SAVE TEMPORARY MERGED RASTER
        # ------------------------------------------

        save_temporary_merged_raster(
            merged_data=merged_data,
            merged_metadata=merged_metadata,
            output_path=temporary_merged_path,
        )


        # ------------------------------------------
        # CLIP TO AOI
        # ------------------------------------------

        clip_raster_to_aoi(
            merged_raster_path=temporary_merged_path,
            aoi_geometry=aoi_geometry,
            output_path=final_output_path,
        )


        # ------------------------------------------
        # DELETE TEMPORARY FILE
        # ------------------------------------------

        if temporary_merged_path.exists():

            temporary_merged_path.unlink()

            print(
                "Temporary merged raster removed."
            )


        # ------------------------------------------
        # VALIDATE FINAL OUTPUT
        # ------------------------------------------

        output_valid = validate_output(
            final_output_path
        )


        # ------------------------------------------
        # FINAL SUMMARY
        # ------------------------------------------

        total_processing_time = (
            time.time()
            - total_start_time
        )

        print(
            "\n===== SRTM AOI SUMMARY ====="
        )

        print(
            "Requested Location:",
            location_name,
        )

        print(
            "Resolved Location:",
            location_address,
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
            "Intersecting Tiles:",
            len(intersecting_tiles),
        )

        print(
            "Output File:",
            final_output_path,
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
                total_processing_time,
                2,
            ),
            "seconds",
        )


        # ------------------------------------------
        # FINAL STATUS
        # ------------------------------------------

        if output_valid:

            print(
                "\n===== SRTM AOI EXTRACTION "
                "COMPLETED SUCCESSFULLY ====="
            )

        else:

            print(
                "\n===== SRTM AOI EXTRACTION "
                "FAILED ====="
            )


    except Exception as error:

        print(
            "\n===== SRTM AOI EXTRACTION FAILED ====="
        )

        print(
            "Error:",
            error,
        )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()