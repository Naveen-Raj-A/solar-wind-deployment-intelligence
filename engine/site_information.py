"""
Site Information Module

This module provides a common location interface for the
Solar-Wind Deployment Intelligence Engine.

Features
--------
- Location geocoding using OpenStreetMap Nominatim
- Coordinate validation
- Manual coordinate support
- Standard SiteInformation object shared across all datasets
"""

from dataclasses import dataclass

from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim


GEOCODER_USER_AGENT = "solar_wind_deployment_intelligence"
GEOCODER_TIMEOUT_SECONDS = 20


__all__ = [
    "SiteInformation",
    "validate_coordinates",
    "geocode_location",
    "create_site_information_from_coordinates",
]


@dataclass(slots=True)
class SiteInformation:
    requested_location: str
    resolved_location: str
    latitude: float
    longitude: float
    country: str
    state: str
    source: str = "Nominatim"


def validate_coordinates(
    latitude: float,
    longitude: float,
) -> None:
    """
    Validate latitude and longitude.
    """

    if not (-90.0 <= latitude <= 90.0):
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not (-180.0 <= longitude <= 180.0):
        raise ValueError(
            "Longitude must be between -180 and 180."
        )


def geocode_location(
    location_name: str,
) -> SiteInformation | None:
    """
    Convert a location name into a SiteInformation object.
    """

    location_name = location_name.strip()

    if not location_name:
        raise ValueError(
            "Location name cannot be empty."
        )

    geolocator = Nominatim(
        user_agent=GEOCODER_USER_AGENT,
        timeout=GEOCODER_TIMEOUT_SECONDS,
    )

    try:

        location = geolocator.geocode(
            f"{location_name}, India"
        )

    except GeocoderServiceError:
        return None

    if location is None:
        return None

    validate_coordinates(
        float(location.latitude),
        float(location.longitude),
    )

    address_parts = [
        part.strip()
        for part in location.address.split(",")
    ]

    country = (
        address_parts[-1]
        if len(address_parts) >= 1
        else "Unknown"
    )

    state = (
        address_parts[-2]
        if len(address_parts) >= 2
        else "Unknown"
    )

    return SiteInformation(
        requested_location=location_name,
        resolved_location=location.address,
        latitude=float(location.latitude),
        longitude=float(location.longitude),
        country=country,
        state=state,
        source="Nominatim",
    )


def create_site_information_from_coordinates(
    latitude: float,
    longitude: float,
) -> SiteInformation:
    """
    Create SiteInformation directly from coordinates.
    """

    validate_coordinates(
        latitude,
        longitude,
    )

    return SiteInformation(
        requested_location="Coordinates",
        resolved_location="Coordinates",
        latitude=float(latitude),
        longitude=float(longitude),
        country="Unknown",
        state="Unknown",
        source="Manual",
    )


def print_site_information(
    site: SiteInformation,
) -> None:
    """
    Print SiteInformation in a readable format.
    """

    print("\n===== SITE INFORMATION =====")

    print(
        "Requested Location:",
        site.requested_location,
    )

    print(
        "Resolved Location:",
        site.resolved_location,
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
        "State:",
        site.state,
    )

    print(
        "Country:",
        site.country,
    )

    print(
        "Source:",
        site.source,
    )


if __name__ == "__main__":

    location_name = input(
        "Enter location in India: "
    ).strip()

    site = geocode_location(location_name)

    if site is None:

        print("Location not found.")

    else:

        print_site_information(site)