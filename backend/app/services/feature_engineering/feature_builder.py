"""
feature_builder.py

Builds the ML feature vector required by PredictionService.

Pipeline

Latitude/Longitude
        │
        ▼
NASA POWER
Global Wind Atlas
SRTM
OpenStreetMap
        │
        ▼
Raw Dataset Bundle
        │
        ▼
ML Feature Vector
"""

from typing import Dict

from app.services.nasa_power_service import get_nasa_power_features
from app.services.wind_service import get_wind_speed
from app.services.terrain_service import get_terrain_features
from app.services.osm_service import get_osm_features


def _safe(result: Dict) -> Dict:
    """
    Returns an empty dictionary if a dataset query failed.
    """

    if not isinstance(result, dict):
        return {}

    if result.get("success") is False:
        return {}

    return result


def _collect_nasa(latitude: float, longitude: float) -> Dict:
    return _safe(
        get_nasa_power_features(latitude, longitude)
    )


def _collect_wind(latitude: float, longitude: float) -> Dict:
    return _safe(
        get_wind_speed(latitude, longitude)
    )


def _collect_terrain(latitude: float, longitude: float) -> Dict:
    return _safe(
        get_terrain_features(latitude, longitude)
    )


def _collect_osm(latitude: float, longitude: float) -> Dict:
    return _safe(
        get_osm_features(latitude, longitude)
    )


def _build_raw_bundle(
    nasa: Dict,
    wind: Dict,
    terrain: Dict,
    osm: Dict,
) -> Dict:

    return {

        "nasa": {

            "solar_irradiance": nasa.get("solar_irradiance"),

            "temperature": nasa.get("temperature"),

            "humidity": nasa.get("humidity"),

        },

        "wind": {

            "wind_speed": wind.get("wind_speed"),

        },

        "terrain": {

            "mean_elevation": terrain.get("elevation"),

            "mean_slope": terrain.get("slope"),

            "terrain_type": terrain.get("terrain"),

        },

        "osm": {

            "building_count":
                osm.get("building_count"),

            "road_count":
                osm.get("road_count"),

            "power_infrastructure_count":
                osm.get("power_infrastructure_count"),

            "substation_count":
                osm.get("substation_count"),

            "nearest_road_distance":
                osm.get("nearest_road_distance"),

            "nearest_power_distance":
                osm.get("nearest_power_distance"),

            "nearest_substation_distance":
                osm.get("nearest_substation_distance"),

            "road_access":
                osm.get("road_access"),

            "power_available":
                osm.get("power_available"),

            "substation_available":
                osm.get("substation_available"),

        },

    }


def _build_features(raw: Dict) -> Dict:
    """
    Creates the feature vector expected by the ML models.
    """

    return {

        "solar_irradiance":
            raw["nasa"]["solar_irradiance"] or 0.0,

        "temperature":
            raw["nasa"]["temperature"] or 0.0,

        "humidity":
            raw["nasa"]["humidity"] or 0.0,

        "wind_speed":
            raw["wind"]["wind_speed"] or 0.0,

        "elevation":
            raw["terrain"]["mean_elevation"] or 0.0,

        "slope":
            raw["terrain"]["mean_slope"] or 0.0,

        "distance_to_road":
            raw["osm"]["nearest_road_distance"] or 0.0,

    }


def build_feature_vector(
    latitude: float,
    longitude: float,
) -> Dict:
    """
    Build the feature vector required by the ML models.

    Returns

    {
        "features": {...},
        "raw": {...}
    }
    """

    nasa = _collect_nasa(latitude, longitude)

    wind = _collect_wind(latitude, longitude)

    terrain = _collect_terrain(latitude, longitude)

    osm = _collect_osm(latitude, longitude)

    raw = _build_raw_bundle(
        nasa,
        wind,
        terrain,
        osm,
    )

    features = _build_features(raw)

    return {

        "features": features,

        "raw": raw,

    }