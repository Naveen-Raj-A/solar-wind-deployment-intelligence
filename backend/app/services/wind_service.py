import math
import os

import rasterio


# Get the absolute path of the project root directory
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
    )
)


# Path to the India-wide Global Wind Atlas GeoTIFF
WIND_DATA_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "global_wind_atlas",
    "IND_wind-speed_150m.tif",
)


def get_wind_speed(latitude: float, longitude: float):
    """
    Retrieve the wind-speed value at 150 m
    for the given latitude and longitude.
    """

    # Open the Global Wind Atlas GeoTIFF
    with rasterio.open(WIND_DATA_PATH) as dataset:

        # Check whether the coordinates are
        # inside the GeoTIFF geographic bounds
        if not (
            dataset.bounds.left
            <= longitude
            <= dataset.bounds.right
            and dataset.bounds.bottom
            <= latitude
            <= dataset.bounds.top
        ):
            return {
                "success": False,
                "message": (
                    "Coordinates are outside "
                    "the wind dataset bounds."
                ),
            }

        # Read the wind-speed value for the
        # requested latitude and longitude
        wind_speed = next(
            dataset.sample(
                [(longitude, latitude)]
            )
        )[0]

        # Check whether the selected location
        # contains a NoData value
        if math.isnan(float(wind_speed)):
            return {
                "success": False,
                "message": (
                    "No wind-speed data is "
                    "available at this location."
                ),
            }

        # Return the successful wind-data result
        return {
            "success": True,
            "latitude": latitude,
            "longitude": longitude,
            "height": 150,
            "wind_speed": round(
                float(wind_speed),
                2,
            ),
            "unit": "m/s",
        }