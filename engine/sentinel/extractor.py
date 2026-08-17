"""
Sentinel AOI Extraction Module
Solar & Wind Deployment Intelligence
"""

import os
import time

import planetary_computer
import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
from shapely.geometry import box, mapping

from engine.sentinel.config import (
    RAW_DIRECTORY,
    REQUIRED_ASSETS,
)


# ============================================================
# CREATE LOCATION DIRECTORY
# ============================================================

def create_location_directory(location_name: str):
    """
    Create a folder for a location inside datasets/sentinel/raw.
    """

    safe_name = ""

    for character in location_name.lower():
        if character.isalnum():
            safe_name += character
        elif character in (" ", "-", "_"):
            safe_name += "_"

    safe_name = safe_name.strip("_")

    directory = os.path.join(
        RAW_DIRECTORY,
        safe_name,
    )

    os.makedirs(directory, exist_ok=True)

    return directory


# ============================================================
# DOWNLOAD SINGLE ASSET
# ============================================================

def extract_asset(
    scene,
    asset_name,
    bounding_box,
    output_directory,
):
    """
    Download and crop one Sentinel asset.
    """

    if asset_name not in scene.assets:
        raise ValueError(f"{asset_name} not available.")

    signed_asset = planetary_computer.sign(
        scene.assets[asset_name]
    )

    output_file = os.path.join(
        output_directory,
        f"{asset_name}.tif",
    )

    start = time.time()

    with rasterio.open(signed_asset.href) as src:

        west, south, east, north = bounding_box

        geometry = mapping(
            box(
                west,
                south,
                east,
                north,
            )
        )

        transformed = transform_geom(
            "EPSG:4326",
            src.crs,
            geometry,
        )

        image, transform = mask(
            src,
            [transformed],
            crop=True,
        )

        metadata = src.meta.copy()

        metadata.update(
            {
                "driver": "GTiff",
                "height": image.shape[1],
                "width": image.shape[2],
                "transform": transform,
                "compress": "deflate",
            }
        )

        with rasterio.open(
            output_file,
            "w",
            **metadata,
        ) as dst:
            dst.write(image)

    return {
        "asset": asset_name,
        "file": output_file,
        "processing_time": time.time() - start,
        "size_mb": round(
            os.path.getsize(output_file) / (1024 * 1024),
            2,
        ),
    }


# ============================================================
# VALIDATE TIFF
# ============================================================

def validate_asset(file_path):
    """
    Validate a GeoTIFF.
    """

    try:
        with rasterio.open(file_path) as dataset:

            return (
                dataset.count > 0
                and dataset.width > 0
                and dataset.height > 0
            )

    except Exception:
        return False


# ============================================================
# DOWNLOAD ALL REQUIRED ASSETS
# ============================================================

def extract_required_assets(
    scene,
    location_name,
    bounding_box,
):
    """
    Download all required Sentinel assets.
    """

    directory = create_location_directory(
        location_name
    )

    assets = {}

    for asset in REQUIRED_ASSETS:

        result = extract_asset(
            scene,
            asset,
            bounding_box,
            directory,
        )

        result["valid"] = validate_asset(
            result["file"]
        )

        assets[asset] = result

    return {
        "directory": directory,
        "assets": assets,
    }