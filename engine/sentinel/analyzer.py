"""
Sentinel Analyzer
=================

Solar & Wind Deployment Intelligence

Responsibilities
----------------

1. Receive site information.
2. Search for the best Sentinel-2 scene.
3. Extract required Sentinel-2 assets.
4. Load Sentinel bands.
5. Align raster resolutions.
6. Create a valid-pixel mask.
7. Calculate NDVI.
8. Calculate NDMI.
9. Calculate Sentinel scene classification statistics.
10. Generate and save the Sentinel summary.

Coordinate-first design
-----------------------

The latitude and longitude stored in SiteInformation
are the authoritative site coordinates.

When coordinates are available, Sentinel scene search
uses those coordinates directly and does NOT geocode
the string "Coordinates".
"""

from __future__ import annotations

import os

import rasterio
from rasterio.enums import Resampling


from engine.utils import (
    create_safe_location_name,
)


from engine.sentinel.config import (
    PROCESSED_DIRECTORY,
)


from engine.sentinel.search import (
    search_best_scene,
)


from engine.sentinel.extractor import (
    extract_required_assets,
)


from engine.sentinel.raster_utils import (
    read_reference_raster,
    align_raster_to_reference,
    save_float_raster,
)


from engine.sentinel.indices import (
    create_valid_pixel_mask,
    calculate_ndvi,
    calculate_ndmi,
    calculate_index_statistics,
    calculate_scl_statistics,
)


from engine.sentinel.summary import (
    build_summary,
    save_summary,
)


# ============================================================
# MAIN SENTINEL ANALYSIS
# ============================================================

def analyze_sentinel(
    site,
    save_output: bool = True,
    display_output: bool = True,
):
    """
    Perform Sentinel-2 analysis for the selected site.

    Coordinates are authoritative.

    If latitude and longitude exist, Sentinel uses them
    directly instead of attempting to geocode the requested
    location name.
    """

    # ========================================================
    # START
    # ========================================================

    if display_output:

        print(
            "\n======================================"
        )

        print(
            "===== SENTINEL-2 ANALYSIS ====="
        )

        print(
            "======================================"
        )

    # ========================================================
    # SITE INFORMATION
    # ========================================================

    if display_output:

        print(
            "\n===== SITE INFORMATION ====="
        )

        print(
            f"Requested Location: "
            f"{site.requested_location}"
        )

        print(
            f"Resolved Location : "
            f"{site.resolved_location}"
        )

        print(
            f"Latitude          : "
            f"{site.latitude}"
        )

        print(
            f"Longitude         : "
            f"{site.longitude}"
        )

    # ========================================================
    # VALIDATE COORDINATES
    # ========================================================

    if (
        site.latitude is None
        or site.longitude is None
    ):

        raise ValueError(
            "Sentinel analysis requires valid "
            "latitude and longitude."
        )

    latitude = float(
        site.latitude
    )

    longitude = float(
        site.longitude
    )

    # ========================================================
    # SEARCH BEST SENTINEL SCENE
    # ========================================================

    if display_output:

        print(
            "\n===== SEARCHING SENTINEL SCENE ====="
        )

        print(
            "Search Coordinates:"
        )

        print(
            "Latitude :",
            latitude,
        )

        print(
            "Longitude:",
            longitude,
        )

        print(
            "Geocoding: SKIPPED"
        )

    try:

        search = search_best_scene(
            latitude=latitude,
            longitude=longitude,
        )

    except Exception as error:

        if display_output:

            print(
                "\nSentinel scene search failed."
            )

            print(
                "Error:",
                error,
            )

        raise RuntimeError(
            "Sentinel scene search failed."
        ) from error

    # ========================================================
    # CHECK SEARCH RESULT
    # ========================================================

    if search is None:

        raise RuntimeError(
            "Sentinel search returned no result."
        )

    if search.get("scene") is None:

        raise RuntimeError(
            "No Sentinel scene found."
        )

    # ========================================================
    # SEARCH SUCCESS
    # ========================================================

    if display_output:

        print(
            "Scene Search: SUCCESS"
        )

        print(
            "Bounding Box:",
            search.get(
                "bounding_box"
            ),
        )

    # ========================================================
    # DOWNLOAD / EXTRACT REQUIRED ASSETS
    # ========================================================

    if display_output:

        print(
            "\n===== EXTRACTING REQUIRED ASSETS ====="
        )

    try:

        extraction = (
            extract_required_assets(
                search["scene"],

                # IMPORTANT:
                # Use a stable coordinate-based
                # location identifier when the
                # original request is "Coordinates".
                "coordinates"
                if str(
                    site.requested_location
                ).strip().lower()
                in {
                    "coordinates",
                    "coordinate",
                }
                else site.requested_location,

                search["bounding_box"],
            )
        )

    except Exception as error:

        if display_output:

            print(
                "\nSentinel asset extraction failed."
            )

            print(
                "Error:",
                error,
            )

        raise RuntimeError(
            "Sentinel asset extraction failed."
        ) from error

    # ========================================================
    # RAW DIRECTORY
    # ========================================================

    raw_dir = extraction[
        "directory"
    ]

    # ========================================================
    # PROCESSED DIRECTORY
    # ========================================================

    processed_location_name = (
        "coordinates"
        if str(
            site.requested_location
        ).strip().lower()
        in {
            "coordinates",
            "coordinate",
        }
        else site.requested_location
    )

    processed_dir = os.path.join(
        PROCESSED_DIRECTORY,

        create_safe_location_name(
            processed_location_name
        ),
    )

    os.makedirs(
        processed_dir,
        exist_ok=True,
    )

    if display_output:

        print(
            "Raw Directory      :",
            raw_dir,
        )

        print(
            "Processed Directory:",
            processed_dir,
        )

    # ========================================================
    # REQUIRED SENTINEL FILES
    # ========================================================

    files = {

        "B04": os.path.join(
            raw_dir,
            "B04.tif",
        ),

        "B08": os.path.join(
            raw_dir,
            "B08.tif",
        ),

        "B11": os.path.join(
            raw_dir,
            "B11.tif",
        ),

        "SCL": os.path.join(
            raw_dir,
            "SCL.tif",
        ),
    }

    # ========================================================
    # CHECK REQUIRED FILES
    # ========================================================

    if display_output:

        print(
            "\n===== CHECKING SENTINEL ASSETS ====="
        )

    missing_files = []

    for (
        band_name,
        file_path,
    ) in files.items():

        if not os.path.exists(
            file_path
        ):

            missing_files.append(
                f"{band_name}: {file_path}"
            )

    if missing_files:

        print(
            "\nMissing Sentinel files:"
        )

        for missing_file in (
            missing_files
        ):

            print(
                " -",
                missing_file,
            )

        raise FileNotFoundError(
            "Required Sentinel-2 assets are missing."
        )

    if display_output:

        print(
            "Required assets: OK"
        )

    # ========================================================
    # LOAD REQUIRED RASTERS
    # ========================================================

    if display_output:

        print(
            "\n===== LOADING RASTERS ====="
        )

    # --------------------------------------------------------
    # B04 - RED
    # --------------------------------------------------------

    (
        red,
        profile,
        transform,
        crs,
        width,
        height,
    ) = read_reference_raster(
        files["B04"]
    )

    # --------------------------------------------------------
    # B08 - NIR
    # --------------------------------------------------------

    with rasterio.open(
        files["B08"]
    ) as dataset:

        nir = dataset.read(
            1
        )

    # --------------------------------------------------------
    # B11 - SWIR
    # --------------------------------------------------------

    swir = align_raster_to_reference(
        files["B11"],
        transform,
        crs,
        width,
        height,
        Resampling.bilinear,
    )

    # --------------------------------------------------------
    # SCL
    # --------------------------------------------------------

    scl = align_raster_to_reference(
        files["SCL"],
        transform,
        crs,
        width,
        height,
        Resampling.nearest,
    )

    if display_output:

        print(
            "Raster Loading: COMPLETED"
        )

    # ========================================================
    # VALID PIXEL MASK
    # ========================================================

    if display_output:

        print(
            "\n===== VALID PIXEL MASK ====="
        )

    mask = (
        create_valid_pixel_mask(
            scl
        )
    )

    if display_output:

        print(
            "Total Pixels   :",
            mask["total_pixels"],
        )

        print(
            "Valid Pixels   :",
            mask["valid_pixels"],
        )

        print(
            "Invalid Pixels :",
            mask["invalid_pixels"],
        )

        print(
            f"Valid %        : "
            f"{mask['valid_percentage']:.2f}"
        )

    # ========================================================
    # NDVI
    # ========================================================

    if display_output:

        print(
            "\n===== CALCULATING NDVI ====="
        )

    ndvi = calculate_ndvi(
        red,
        nir,
        mask["valid_mask"],
    )

    if display_output:

        print(
            "NDVI: COMPLETED"
        )

    # ========================================================
    # NDMI
    # ========================================================

    if display_output:

        print(
            "\n===== CALCULATING NDMI ====="
        )

    ndmi = calculate_ndmi(
        nir,
        swir,
        mask["valid_mask"],
    )

    if display_output:

        print(
            "NDMI: COMPLETED"
        )

    # ========================================================
    # NDVI STATISTICS
    # ========================================================

    if display_output:

        print(
            "\n===== CALCULATING NDVI STATISTICS ====="
        )

    ndvi_stats = (
        calculate_index_statistics(
            ndvi,
            mask["valid_mask"],
        )
    )

    # ========================================================
    # NDMI STATISTICS
    # ========================================================

    if display_output:

        print(
            "\n===== CALCULATING NDMI STATISTICS ====="
        )

    ndmi_stats = (
        calculate_index_statistics(
            ndmi,
            mask["valid_mask"],
        )
    )

    # ========================================================
    # SCL STATISTICS
    # ========================================================

    if display_output:

        print(
            "\n===== CALCULATING SCL STATISTICS ====="
        )

    scl_stats = (
        calculate_scl_statistics(
            scl,
            mask["total_pixels"],
        )
    )

    # ========================================================
    # DISPLAY STATISTICS
    # ========================================================

    if display_output:

        print(
            "\n===== NDVI STATISTICS ====="
        )

        print(
            ndvi_stats
        )

        print(
            "\n===== NDMI STATISTICS ====="
        )

        print(
            ndmi_stats
        )

        print(
            "\n===== SCL STATISTICS ====="
        )

        print(
            scl_stats
        )

    # ========================================================
    # SAVE PROCESSED RASTERS
    # ========================================================

    if save_output:

        if display_output:

            print(
                "\n===== SAVING PROCESSED RASTERS ====="
            )

        ndvi_output = os.path.join(
            processed_dir,
            "ndvi.tif",
        )

        ndmi_output = os.path.join(
            processed_dir,
            "ndmi.tif",
        )

        save_float_raster(
            ndvi_output,
            ndvi,
            profile,
        )

        save_float_raster(
            ndmi_output,
            ndmi,
            profile,
        )

        if display_output:

            print(
                "NDVI saved:",
                ndvi_output,
            )

            print(
                "NDMI saved:",
                ndmi_output,
            )

    # ========================================================
    # BUILD SUMMARY
    # ========================================================

    if display_output:

        print(
            "\n===== BUILDING SENTINEL SUMMARY ====="
        )

    summary = build_summary(
        location=(
            site.resolved_location
            if site.resolved_location
            else site.requested_location
        ),

        total_pixels=
            mask["total_pixels"],

        valid_pixels=
            mask["valid_pixels"],

        invalid_pixels=
            mask["invalid_pixels"],

        valid_percentage=
            mask["valid_percentage"],

        ndvi_statistics=
            ndvi_stats,

        ndmi_statistics=
            ndmi_stats,

        scl_statistics=
            scl_stats,
    )

    # ========================================================
    # ADD COORDINATE INFORMATION
    # ========================================================

    summary[
        "requested_location"
    ] = site.requested_location

    summary[
        "resolved_location"
    ] = site.resolved_location

    summary[
        "latitude"
    ] = latitude

    summary[
        "longitude"
    ] = longitude

    summary[
        "bounding_box"
    ] = search.get(
        "bounding_box"
    )

    summary[
        "coordinate_mode"
    ] = True

    summary[
        "geocoding"
    ] = "SKIPPED"

    summary[
        "status"
    ] = "SUCCESS"

    # ========================================================
    # SAVE SUMMARY
    # ========================================================

    if save_output:

        if display_output:

            print(
                "\n===== SAVING SENTINEL SUMMARY ====="
            )

        save_summary(
            summary,
            processed_dir,
        )

        if display_output:

            print(
                "Sentinel summary saved."
            )

    # ========================================================
    # FINAL
    # ========================================================

    if display_output:

        print(
            "\n======================================"
        )

        print(
            "SENTINEL-2 ANALYSIS COMPLETED"
        )

        print(
            "======================================"
        )

    return summary