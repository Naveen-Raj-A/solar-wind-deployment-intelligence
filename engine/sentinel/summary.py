"""
Sentinel Summary Module
Solar & Wind Deployment Intelligence
"""

import json
import os


# ============================================================
# BUILD SUMMARY
# ============================================================

def build_summary(
    location,
    total_pixels,
    valid_pixels,
    invalid_pixels,
    valid_percentage,
    ndvi_statistics,
    ndmi_statistics,
    scl_statistics,
):
    """
    Build the Sentinel analysis summary dictionary.
    """

    return {
        "location": location,
        "total_pixels": total_pixels,
        "valid_pixels": valid_pixels,
        "invalid_pixels": invalid_pixels,
        "valid_percentage": float(valid_percentage),
        "ndvi_statistics": ndvi_statistics,
        "ndmi_statistics": ndmi_statistics,
        "scl_statistics": scl_statistics,
    }


# ============================================================
# SAVE SUMMARY
# ============================================================

def save_summary(
    summary,
    output_directory,
    filename="sentinel_analysis_summary.json",
):
    """
    Save the Sentinel analysis summary as JSON.
    """

    os.makedirs(output_directory, exist_ok=True)

    output_path = os.path.join(
        output_directory,
        filename,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )

    return output_path