"""
Input Handler Module

Collects and validates user input for the
Solar-Wind Deployment Intelligence Engine.

Supports:
- Location name
- Latitude/Longitude
"""

from engine.site_information import (
    SiteInformation,
    geocode_location,
    create_site_information_from_coordinates,
)


def parse_coordinate(
    value: str,
) -> float:
    """
    Convert coordinate text into float.

    Examples:

    10.7903
    10.7903°
    10.7903 N
    10.7903° N
    """

    value = value.upper().strip()

    sign = 1

    if value.endswith(("S", "W")):
        sign = -1

    value = (
        value
        .replace("°", "")
        .replace("N", "")
        .replace("S", "")
        .replace("E", "")
        .replace("W", "")
        .strip()
    )

    return sign * float(value)


def get_location_from_name() -> SiteInformation:

    while True:

        location_name = input(
            "\nEnter location in India: "
        ).strip()

        if not location_name:

            print(
                "Location cannot be empty."
            )

            continue

        site = geocode_location(
            location_name
        )

        if site is None:

            print(
                "Location not found."
            )

            continue

        return site


def get_location_from_coordinates() -> SiteInformation:

    while True:

        try:

            latitude = parse_coordinate(
                input(
                    "\nEnter Latitude: "
                )
            )

            longitude = parse_coordinate(
                input(
                    "Enter Longitude: "
                )
            )

            return create_site_information_from_coordinates(
                latitude,
                longitude,
            )

        except ValueError as error:

            print(error)


def get_site_information() -> SiteInformation:

    while True:

        print(
            "\n===== LOCATION INPUT ====="
        )

        print("1. Search by Location Name")
        print("2. Enter Coordinates")

        choice = input(
            "\nSelect option (1/2): "
        ).strip()

        if choice == "1":

            return get_location_from_name()

        elif choice == "2":

            return get_location_from_coordinates()

        else:

            print(
                "Invalid option."
            )


if __name__ == "__main__":

    site = get_site_information()

    print("\n===== INPUT RESULT =====")

    print(site)