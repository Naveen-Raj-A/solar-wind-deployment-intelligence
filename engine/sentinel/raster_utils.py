"""
Raster Utility Functions
Solar & Wind Deployment Intelligence
"""

import numpy as np
import rasterio
from rasterio.warp import reproject


def read_reference_raster(file_path):
    """
    Read a raster and return its data and metadata.
    """

    with rasterio.open(file_path) as dataset:

        data = dataset.read(1)
        profile = dataset.profile.copy()
        transform = dataset.transform
        crs = dataset.crs
        width = dataset.width
        height = dataset.height

    return (
        data,
        profile,
        transform,
        crs,
        width,
        height,
    )


def align_raster_to_reference(
    source_file,
    reference_transform,
    reference_crs,
    reference_width,
    reference_height,
    resampling_method,
):
    """
    Align a raster to the reference grid.
    """

    with rasterio.open(source_file) as source:

        destination = np.zeros(
            (
                reference_height,
                reference_width,
            ),
            dtype=source.dtypes[0],
        )

        reproject(
            source=source.read(1),
            destination=destination,
            src_transform=source.transform,
            src_crs=source.crs,
            dst_transform=reference_transform,
            dst_crs=reference_crs,
            dst_width=reference_width,
            dst_height=reference_height,
            resampling=resampling_method,
        )

    return destination


def save_float_raster(
    output_path,
    data,
    reference_profile,
):
    """
    Save a float32 raster.
    """

    output_profile = reference_profile.copy()

    output_profile.update(
        {
            "driver": "GTiff",
            "dtype": "float32",
            "count": 1,
            "nodata": -9999.0,
            "compress": "deflate",
        }
    )

    output_data = data.astype(np.float32)

    output_data[~np.isfinite(output_data)] = -9999.0

    with rasterio.open(
        output_path,
        "w",
        **output_profile,
    ) as destination:

        destination.write(
            output_data,
            1,
        )