import math

import rasterio


# Path to the India-wide Global Wind Atlas GeoTIFF
FILE_PATH = "datasets/global_wind_atlas/IND_wind-speed_150m.tif"


def get_wind_speed(latitude, longitude):
    """
    Retrieve the wind-speed value at 150 m
    for the given latitude and longitude.
    """

    with rasterio.open(FILE_PATH) as dataset:

        # Check whether coordinates are inside raster bounds
        if not (
            dataset.bounds.left <= longitude <= dataset.bounds.right
            and dataset.bounds.bottom <= latitude <= dataset.bounds.top
        ):
            return None, "Coordinates are outside the dataset bounds."

        # Read the raster value at the requested coordinates
        wind_speed = next(
            dataset.sample([(longitude, latitude)])
        )[0]

        # Check whether the value is NoData
        if math.isnan(float(wind_speed)):
            return None, "No wind-speed data is available at this location."

        return float(wind_speed), None


print("\n===== WIND SPEED LOCATION QUERY =====")


try:

    # Get coordinates from the user
    latitude = float(
        input("Enter Latitude: ")
    )

    longitude = float(
        input("Enter Longitude: ")
    )


    # Query the wind-speed dataset
    wind_speed, error = get_wind_speed(
        latitude,
        longitude,
    )


    print("\n===== RESULT =====")

    print("Latitude:", latitude)

    print("Longitude:", longitude)


    if error:

        print("Result:", error)

    else:

        print("Height: 150 m")

        print(
            "Wind Speed:",
            round(wind_speed, 2),
            "m/s",
        )


except ValueError:

    print(
        "\nError: Latitude and longitude "
        "must be valid numbers."
    )


print("\n===== QUERY COMPLETED =====")