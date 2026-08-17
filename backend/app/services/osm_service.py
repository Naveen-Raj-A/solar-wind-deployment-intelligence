
"""
backend/app/services/osm_service.py

Backend OSM infrastructure service extracted from the offline analysis
pipeline. This version removes CLI/report generation and exposes a single
API:

    get_osm_features(latitude, longitude)

Adjust DATABASE_PATH if your project layout differs.
"""

import math
import sqlite3
from pathlib import Path

AOI_RADIUS_KM = 5.0

BASE_DIR = Path(__file__).resolve().parents[3]
DATABASE_PATH = (
    BASE_DIR
    / "datasets"
    / "openstreetmap"
    / "processed"
    / "india_osm_spatial.db"
)

EXPECTED_FEATURE_TYPES = [
    "building",
    "road",
    "power_infrastructure",
    "substation",
]


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371.0088
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def calculate_aoi_bounds(latitude, longitude, radius_km=AOI_RADIUS_KM):
    lat_delta = radius_km / 111.32
    lon_delta = radius_km / (111.32 * math.cos(math.radians(latitude)))
    return {
        "west": longitude - lon_delta,
        "east": longitude + lon_delta,
        "south": latitude - lat_delta,
        "north": latitude + lat_delta,
    }


def validate_database(connection):
    required = {"osm_features", "osm_features_rtree"}
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    existing = {r[0] for r in rows}
    missing = required - existing
    if missing:
        raise RuntimeError(f"Missing tables: {missing}")


def query_features(connection, bounds):
    sql = """
    SELECT
        f.feature_id,
        f.osm_id,
        f.osm_type,
        f.feature_type,
        r.min_lon,
        r.max_lon,
        r.min_lat,
        r.max_lat
    FROM osm_features_rtree r
    JOIN osm_features f
      ON f.feature_id=r.feature_id
    WHERE
      r.max_lon>=?
      AND r.min_lon<=?
      AND r.max_lat>=?
      AND r.min_lat<=?
    """
    return connection.execute(
        sql,
        (
            bounds["west"],
            bounds["east"],
            bounds["south"],
            bounds["north"],
        ),
    ).fetchall()


def get_osm_features(latitude: float, longitude: float):
    if not DATABASE_PATH.exists():
        return {
            "success": False,
            "error": f"Database not found: {DATABASE_PATH}"
        }

    conn = sqlite3.connect(DATABASE_PATH)
    try:
        validate_database(conn)
        bounds = calculate_aoi_bounds(latitude, longitude)
        rows = query_features(conn, bounds)

        stats = {
            k: {"count": 0, "nearest_distance_km": None}
            for k in EXPECTED_FEATURE_TYPES
        }

        for row in rows:
            _, _, _, feature_type, min_lon, max_lon, min_lat, max_lat = row
            c_lat = (min_lat + max_lat) / 2
            c_lon = (min_lon + max_lon) / 2
            d = calculate_haversine_distance(
                latitude, longitude, c_lat, c_lon
            )
            if d > AOI_RADIUS_KM:
                continue

            if feature_type not in stats:
                stats[feature_type] = {
                    "count": 0,
                    "nearest_distance_km": None,
                }

            stats[feature_type]["count"] += 1
            current = stats[feature_type]["nearest_distance_km"]
            if current is None or d < current:
                stats[feature_type]["nearest_distance_km"] = d

        return {
            "success": True,
            "building_count": stats["building"]["count"],
            "road_count": stats["road"]["count"],
            "power_infrastructure_count":
                stats["power_infrastructure"]["count"],
            "substation_count": stats["substation"]["count"],
            "nearest_road_distance":
                stats["road"]["nearest_distance_km"],
            "nearest_power_distance":
                stats["power_infrastructure"]["nearest_distance_km"],
            "nearest_substation_distance":
                stats["substation"]["nearest_distance_km"],
            "road_access":
                stats["road"]["count"] > 0,
            "power_available":
                stats["power_infrastructure"]["count"] > 0,
            "substation_available":
                stats["substation"]["count"] > 0,
        }
    finally:
        conn.close()
