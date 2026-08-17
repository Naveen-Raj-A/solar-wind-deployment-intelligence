"""
Sentinel Scene Search Module
============================

Solar & Wind Deployment Intelligence

Coordinate-first Sentinel-2 scene search.

The supplied latitude and longitude are authoritative.
Location-name geocoding is retained only for legacy
location-name analysis.
"""

from __future__ import annotations

import time

import planetary_computer
from pystac_client import Client
import requests

from engine.sentinel.config import (
    NOMINATIM_URL,
    STAC_URL,
    SENTINEL_COLLECTION,
    SEARCH_OFFSET,
    MAX_CLOUD_COVER,
    DATE_RANGE,
    MAX_RESULTS,
)


# ============================================================
# GEOCODE LOCATION
# ============================================================

def get_location_coordinates(
    location_name: str,
):
    """
    Convert a location name into coordinates.

    This function is retained for legacy name-based analysis.

    Coordinate-based analysis must NOT call this function.
    """

    params = {
        "q": f"{location_name}, India",
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in",
    }

    headers = {
        "User-Agent":
            "solar-wind-deployment-intelligence/1.0"
    }

    start_time = time.time()

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    results = response.json()

    if not results:

        raise ValueError(
            f"Location '{location_name}' not found."
        )

    result = results[0]

    return {
        "display_name":
            result["display_name"],

        "latitude":
            float(result["lat"]),

        "longitude":
            float(result["lon"]),

        "geocoding_time":
            time.time() - start_time,
    }


# ============================================================
# CREATE SEARCH BOUNDS
# ============================================================

def create_search_bounds(
    latitude: float,
    longitude: float,
):
    """
    Create Sentinel search bounding box.

    Format:

        [west, south, east, north]
    """

    latitude = float(latitude)
    longitude = float(longitude)

    return [
        longitude - SEARCH_OFFSET,
        latitude - SEARCH_OFFSET,
        longitude + SEARCH_OFFSET,
        latitude + SEARCH_OFFSET,
    ]


# ============================================================
# SEARCH SENTINEL SCENES
# ============================================================

def search_sentinel_scenes(
    bounding_box,
):
    """
    Search Sentinel-2 scenes using the supplied
    bounding box.
    """

    catalog = Client.open(
        STAC_URL,
        modifier=planetary_computer.sign_inplace,
    )

    start_time = time.time()

    search = catalog.search(
        collections=[
            SENTINEL_COLLECTION
        ],

        bbox=bounding_box,

        datetime=DATE_RANGE,

        query={
            "eo:cloud_cover": {
                "lt": MAX_CLOUD_COVER
            }
        },

        max_items=MAX_RESULTS,
    )

    scenes = list(
        search.items()
    )

    return {
        "scenes":
            scenes,

        "search_time":
            time.time() - start_time,
    }


# ============================================================
# SELECT BEST SCENE
# ============================================================

def select_best_scene(
    scenes,
):
    """
    Select the Sentinel scene with
    the lowest cloud cover.
    """

    if not scenes:

        return None

    return min(
        scenes,

        key=lambda scene:
            scene.properties.get(
                "eo:cloud_cover",
                100,
            ),
    )


# ============================================================
# SEARCH USING COORDINATES
# ============================================================

def search_best_scene_by_coordinates(
    latitude: float,
    longitude: float,
):
    """
    Search Sentinel-2 using exact coordinates.

    NO GEOCODING IS PERFORMED.

    Parameters
    ----------
    latitude:
        Exact site latitude.

    longitude:
        Exact site longitude.
    """

    latitude = float(
        latitude
    )

    longitude = float(
        longitude
    )

    # --------------------------------------------------------
    # Create AOI
    # --------------------------------------------------------

    bounding_box = create_search_bounds(
        latitude,
        longitude,
    )

    # --------------------------------------------------------
    # Search scenes
    # --------------------------------------------------------

    search = search_sentinel_scenes(
        bounding_box
    )

    scene = select_best_scene(
        search["scenes"]
    )

    return {
        "location": {
            "display_name":
                f"{latitude}, {longitude}",

            "latitude":
                latitude,

            "longitude":
                longitude,

            "geocoding_time":
                0.0,
        },

        "bounding_box":
            bounding_box,

        "scene":
            scene,

        "scene_count":
            len(
                search["scenes"]
            ),

        "search_time":
            search["search_time"],

        "coordinate_mode":
            True,
    }


# ============================================================
# COMPLETE SEARCH PIPELINE
# ============================================================

def search_best_scene(
    location_name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
):
    """
    Complete Sentinel scene search pipeline.

    Coordinate mode
    ---------------

    If latitude and longitude are supplied:

        latitude + longitude
                ↓
        create bounding box
                ↓
        Sentinel STAC search

    NO geocoding is performed.

    Legacy location mode
    --------------------

    If coordinates are not supplied, the function falls back
    to the existing location-name geocoding workflow.
    """

    # ========================================================
    # COORDINATE MODE
    # ========================================================

    if (
        latitude is not None
        and longitude is not None
    ):

        return search_best_scene_by_coordinates(
            latitude=latitude,
            longitude=longitude,
        )

    # ========================================================
    # LEGACY LOCATION-NAME MODE
    # ========================================================

    if not location_name:

        raise ValueError(
            "Either location_name or "
            "latitude/longitude must be provided."
        )

    location = get_location_coordinates(
        location_name
    )

    bbox = create_search_bounds(
        location["latitude"],
        location["longitude"],
    )

    search = search_sentinel_scenes(
        bbox
    )

    scene = select_best_scene(
        search["scenes"]
    )

    return {
        "location":
            location,

        "bounding_box":
            bbox,

        "scene":
            scene,

        "scene_count":
            len(
                search["scenes"]
            ),

        "search_time":
            search["search_time"],

        "coordinate_mode":
            False,
    }