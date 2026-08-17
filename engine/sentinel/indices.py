"""
Sentinel Index Calculations
Solar & Wind Deployment Intelligence
"""

import numpy as np


# ============================================================
# INVALID SCL CLASSES
# ============================================================

INVALID_SCL_CLASSES = [
    0,   # No Data
    1,   # Saturated
    3,   # Cloud Shadow
    8,   # Medium Cloud
    9,   # High Cloud
    10,  # Thin Cirrus
    11,  # Snow / Ice
]


# ============================================================
# SCL CLASS NAMES
# ============================================================

SCL_CLASSES = {
    0: "No Data",
    1: "Saturated or Defective",
    2: "Dark Area Pixels",
    3: "Cloud Shadows",
    4: "Vegetation",
    5: "Bare Soil / Non-Vegetated",
    6: "Water",
    7: "Unclassified",
    8: "Cloud Medium Probability",
    9: "Cloud High Probability",
    10: "Thin Cirrus",
    11: "Snow or Ice",
}


# ============================================================
# VALID PIXEL MASK
# ============================================================

def create_valid_pixel_mask(scl):
    """
    Create valid and invalid pixel masks from SCL.
    """

    invalid_mask = np.isin(
        scl,
        INVALID_SCL_CLASSES,
    )

    valid_mask = ~invalid_mask

    valid_pixels = int(np.sum(valid_mask))

    total_pixels = int(valid_mask.size)

    invalid_pixels = total_pixels - valid_pixels

    valid_percentage = (
        valid_pixels / total_pixels * 100
        if total_pixels > 0 else 0
    )

    return {
        "valid_mask": valid_mask,
        "invalid_mask": invalid_mask,
        "valid_pixels": valid_pixels,
        "invalid_pixels": invalid_pixels,
        "total_pixels": total_pixels,
        "valid_percentage": valid_percentage,
    }


# ============================================================
# NDVI
# ============================================================

def calculate_ndvi(
    red,
    nir,
    valid_mask,
):
    """
    Calculate NDVI.
    """

    red = red.astype(np.float32)
    nir = nir.astype(np.float32)

    denominator = nir + red

    ndvi = np.full(
        red.shape,
        np.nan,
        dtype=np.float32,
    )

    calculation_mask = (
        valid_mask
        & (denominator != 0)
    )

    ndvi[calculation_mask] = (

        (
            nir[calculation_mask]
            -
            red[calculation_mask]
        )

        /

        denominator[calculation_mask]

    )

    return ndvi


# ============================================================
# NDMI
# ============================================================

def calculate_ndmi(
    nir,
    swir,
    valid_mask,
):
    """
    Calculate NDMI.
    """

    nir = nir.astype(np.float32)
    swir = swir.astype(np.float32)

    denominator = nir + swir

    ndmi = np.full(
        nir.shape,
        np.nan,
        dtype=np.float32,
    )

    calculation_mask = (
        valid_mask
        & (denominator != 0)
    )

    ndmi[calculation_mask] = (

        (
            nir[calculation_mask]
            -
            swir[calculation_mask]
        )

        /

        denominator[calculation_mask]

    )

    return ndmi


# ============================================================
# INDEX STATISTICS
# ============================================================

def calculate_index_statistics(
    data,
    valid_mask,
):
    """
    Calculate statistics for an index.
    """

    valid_values = data[
        valid_mask
        & np.isfinite(data)
    ]

    if valid_values.size == 0:

        return {
            "minimum": None,
            "maximum": None,
            "mean": None,
            "median": None,
            "standard_deviation": None,
        }

    return {
        "minimum": float(np.min(valid_values)),
        "maximum": float(np.max(valid_values)),
        "mean": float(np.mean(valid_values)),
        "median": float(np.median(valid_values)),
        "standard_deviation": float(np.std(valid_values)),
    }


# ============================================================
# SCL STATISTICS
# ============================================================

def calculate_scl_statistics(
    scl,
    total_pixels,
):
    """
    Calculate SCL class statistics.
    """

    unique_classes, class_counts = np.unique(
        scl,
        return_counts=True,
    )

    statistics = {}

    for class_value, class_count in zip(
        unique_classes,
        class_counts,
    ):

        class_value = int(class_value)
        class_count = int(class_count)

        percentage = (
            class_count
            / total_pixels
            * 100
        )

        statistics[str(class_value)] = {
            "class_name": SCL_CLASSES.get(
                class_value,
                "Unknown",
            ),
            "pixel_count": class_count,
            "percentage": float(percentage),
        }

    return statistics