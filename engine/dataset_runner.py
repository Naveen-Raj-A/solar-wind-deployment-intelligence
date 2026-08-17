"""
Dataset Runner
==============

Runs all dataset analysis modules using a shared SiteInformation
object and returns a combined result.

Coordinate-first architecture:

    User Coordinates
          |
          v
    SiteInformation
          |
          +---- NASA POWER
          |
          +---- WIND
          |
          +---- SRTM
          |
          +---- SENTINEL
          |
          +---- OSM

Latitude and longitude are the authoritative site coordinates.
"""

from __future__ import annotations


from engine.site_information import SiteInformation

from notebooks.analyze_nasa_power_data import analyze_nasa_power
from notebooks.analyze_wind_data import analyze_wind
from notebooks.analyze_srtm_data import analyze_srtm

from engine.sentinel import analyze_sentinel
from engine.osm.analyzer import analyze_location


def run_all_datasets(
    site: SiteInformation,
    save_output: bool = True,
    display_output: bool = True,
) -> dict:
    """
    Execute every dataset analysis module.

    Coordinates from SiteInformation are treated as authoritative.
    """

    if display_output:

        print(
            "\n======================================"
        )

        print(
            "RUNNING DATASET ANALYSIS ENGINE"
        )

        print(
            "======================================"
        )

    results = {}

    # ============================================================
    # DISPLAY SITE COORDINATES
    # ============================================================

    if display_output:

        print(
            "\n===== DATASET SITE COORDINATES ====="
        )

        print(
            "Latitude:",
            site.latitude,
        )

        print(
            "Longitude:",
            site.longitude,
        )

        print(
            "Requested Location:",
            site.requested_location,
        )

        print(
            "Resolved Location:",
            site.resolved_location,
        )

    # ============================================================
    # NASA POWER
    # ============================================================

    if display_output:

        print(
            "\n[1/5] NASA POWER"
        )

    results["nasa_power"] = analyze_nasa_power(
        site=site,
        save_output=save_output,
        display_output=display_output,
    )

    # ============================================================
    # WIND
    # ============================================================

    if display_output:

        print(
            "\n[2/5] WIND"
        )

    results["wind"] = analyze_wind(
        site=site,
        save_output=save_output,
        display_output=display_output,
    )

    # ============================================================
    # SRTM
    # ============================================================

    if display_output:

        print(
            "\n[3/5] SRTM"
        )

    results["srtm"] = analyze_srtm(
        site=site,
        save_output=save_output,
        display_output=display_output,
    )

    # ============================================================
    # SENTINEL
    # ============================================================

    if display_output:

        print(
            "\n[4/5] SENTINEL"
        )

    try:

        results["sentinel"] = analyze_sentinel(
            site=site,
            save_output=save_output,
            display_output=display_output,
        )

    except Exception as error:

        if display_output:

            print(
                f"SENTINEL Analysis Failed: {error}"
            )

        results["sentinel"] = {
            "status": "failed",
            "error": str(error),
        }

    # ============================================================
    # OPENSTREETMAP
    # ============================================================

    if display_output:

        print(
            "\n[5/5] OPENSTREETMAP"
        )

    try:

        results["osm"] = analyze_location(

            # Original user input.
            location_name=(
                site.requested_location
            ),

            # IMPORTANT:
            # Pass exact coordinates.
            latitude=float(
                site.latitude
            ),

            longitude=float(
                site.longitude
            ),

            # Human-readable location is only
            # used for display/reporting.
            resolved_location=(
                site.resolved_location
            ),
        )

    except Exception as error:

        if display_output:

            print(
                f"OSM Analysis Failed: {error}"
            )

        results["osm"] = {
            "status": "failed",
            "error": str(error),
        }

    # ============================================================
    # COMPLETE
    # ============================================================

    if display_output:

        print(
            "\n======================================"
        )

        print(
            "ALL DATASETS COMPLETED"
        )

        print(
            "======================================"
        )

    return results