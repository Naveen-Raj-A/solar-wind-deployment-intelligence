"""
OpenStreetMap Configuration

This module contains all configuration constants used by the
OpenStreetMap analysis engine.

No processing logic should exist in this file.
"""

from pathlib import Path

# ============================================================
# DATASET PATHS
# ============================================================

# Root OpenStreetMap directory
OPENSTREETMAP_DIRECTORY = Path(
    "datasets/openstreetmap"
)

# Processed dataset directory
PROCESSED_DIRECTORY = (
    OPENSTREETMAP_DIRECTORY
    / "processed"
)

# SQLite spatial database
DATABASE_PATH = (
    PROCESSED_DIRECTORY
    / "india_osm_spatial.db"
)

# ============================================================
# OUTPUT CONFIGURATION
# ============================================================

OUTPUT_BASE_DIRECTORY = (
    PROCESSED_DIRECTORY
)

OUTPUT_SUMMARY_FILENAME = (
    "osm_analysis_summary.json"
)

# ============================================================
# GEOCODER CONFIGURATION
# ============================================================

GEOCODER_USER_AGENT = (
    "solar_wind_deployment_intelligence"
)

GEOCODER_TIMEOUT_SECONDS = 20

GEOCODER_COUNTRY = "India"

# ============================================================
# AREA OF INTEREST (AOI)
# ============================================================

# Radius used around requested location
AOI_RADIUS_KM = 5.0

# Mean Earth radius
EARTH_RADIUS_KM = 6371.0088

# Average kilometers represented by one degree latitude
KILOMETERS_PER_DEGREE_LATITUDE = 111.32

# Used to avoid divide-by-zero during longitude calculation
MINIMUM_LONGITUDE_SCALE = 0.000001

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

OSM_FEATURE_TABLE = (
    "osm_features"
)

OSM_RTREE_TABLE = (
    "osm_features_rtree"
)

# ============================================================
# REQUIRED DATABASE TABLES
# ============================================================

REQUIRED_TABLES = {
    "osm_features",
    "osm_features_rtree",
}

# ============================================================
# REQUIRED TABLE COLUMNS
# ============================================================

REQUIRED_FEATURE_COLUMNS = {
    "feature_id",
    "osm_id",
    "osm_type",
    "feature_type",
}

REQUIRED_RTREE_COLUMNS = {
    "feature_id",
    "min_lon",
    "max_lon",
    "min_lat",
    "max_lat",
}

# ============================================================
# PROJECT FEATURE TYPES
# ============================================================

FEATURE_BUILDING = "building"

FEATURE_ROAD = "road"

FEATURE_POWER_INFRASTRUCTURE = (
    "power_infrastructure"
)

FEATURE_SUBSTATION = (
    "substation"
)

EXPECTED_FEATURE_TYPES = [

    FEATURE_BUILDING,

    FEATURE_ROAD,

    FEATURE_POWER_INFRASTRUCTURE,

    FEATURE_SUBSTATION,

]

# ============================================================
# JSON OUTPUT SECTIONS
# ============================================================

REQUIRED_JSON_SECTIONS = [

    "location",

    "aoi",

    "database",

    "feature_analysis",

    "infrastructure_indicators",

]

# ============================================================
# SQLITE QUERY
# ============================================================

AOI_FEATURE_QUERY = """
SELECT
    f.feature_id,
    f.osm_id,
    f.osm_type,
    f.feature_type,
    r.min_lon,
    r.max_lon,
    r.min_lat,
    r.max_lat

FROM osm_features_rtree AS r

JOIN osm_features AS f
    ON f.feature_id = r.feature_id

WHERE
    r.max_lon >= ?
    AND r.min_lon <= ?
    AND r.max_lat >= ?
    AND r.min_lat <= ?
"""