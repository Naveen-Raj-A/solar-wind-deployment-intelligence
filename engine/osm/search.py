"""
OpenStreetMap Search Module

Responsibilities
----------------
• Geocode locations
• Calculate AOI bounds
• Calculate distances
• Create safe folder names

No database logic belongs here.
"""

import math

from geopy.geocoders import Nominatim

from .config import (
    GEOCODER_USER_AGENT,
    GEOCODER_TIMEOUT_SECONDS,
    GEOCODER_COUNTRY,
    EARTH_RADIUS_KM,
    KILOMETERS_PER_DEGREE_LATITUDE,
    MINIMUM_LONGITUDE_SCALE,
)


# ============================================================
# CREATE SAFE LOCATION NAME
# ============================================================

def create_safe_location_name(location_name: str) -> str:
    """
    Convert a location name into a filesystem-safe name.
    """

    safe_name = (
        location_name
        .strip()
        .lower()
    )

    safe_name = "".join(
        character
        if character.isalnum()
        else "_"
        for character in safe_name
    )

    while "__" in safe_name:
        safe_name = safe_name.replace("__", "_")

    return safe_name.strip("_")


# ============================================================
# GEOCODE LOCATION
# ============================================================

def geocode_location(location_name: str):
    """
    Resolve a location using OpenStreetMap Nominatim.

    Returns
    -------
    
    dict | None
    """

    geolocator = Nominatim(
        user_agent=GEOCODER_USER_AGENT,
        timeout=GEOCODER_TIMEOUT_SECONDS,
    )

    search_query = (
        f"{location_name}, {GEOCODER_COUNTRY}"
    )

    location = geolocator.geocode(search_query)

    if location is None:
        return None

    return {
        "resolved_location": location.address,
        "latitude": float(location.latitude),
        "longitude": float(location.longitude),
        "raw": location.raw,
    }


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def calculate_haversine_distance(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """
    Calculate great-circle distance between two coordinates.
    """

    latitude_1_radians = math.radians(latitude_1)
    latitude_2_radians = math.radians(latitude_2)

    latitude_difference = math.radians(
        latitude_2 - latitude_1
    )

    longitude_difference = math.radians(
        longitude_2 - longitude_1
    )

    haversine_value = (
        math.sin(latitude_difference / 2.0) ** 2
        +
        math.cos(latitude_1_radians)
        *
        math.cos(latitude_2_radians)
        *
        math.sin(longitude_difference / 2.0) ** 2
    )

    angular_distance = (
        2.0
        *
        math.atan2(
            math.sqrt(haversine_value),
            math.sqrt(1.0 - haversine_value),
        )
    )

    return (
        EARTH_RADIUS_KM
        * angular_distance
    )


# ============================================================
# AOI BOUNDS
# ============================================================

def calculate_aoi_bounds(
    latitude: float,
    longitude: float,
    radius_km: float,
):
    """
    Calculate the bounding box for an AOI.
    """

    latitude_delta = (
        radius_km
        /
        KILOMETERS_PER_DEGREE_LATITUDE
    )

    latitude_radians = math.radians(latitude)

    longitude_scale = (
        KILOMETERS_PER_DEGREE_LATITUDE
        *
        math.cos(latitude_radians)
    )

    if abs(longitude_scale) < MINIMUM_LONGITUDE_SCALE:
        raise ValueError(
            "Unable to calculate longitude bounds."
        )

    longitude_delta = (
        radius_km
        /
        longitude_scale
    )

    west = longitude - longitude_delta
    east = longitude + longitude_delta

    south = latitude - latitude_delta
    north = latitude + latitude_delta

    return {
        "west": float(west),
        "south": float(south),
        "east": float(east),
        "north": float(north),
    }