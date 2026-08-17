"""
OpenStreetMap Database Module

This module handles all interactions with the
SQLite spatial database.

Responsibilities
----------------
• Connect to SQLite database
• Validate database structure
• Execute spatial queries
• Close database connection

No analysis logic belongs here.
"""

import sqlite3

from .config import (
    DATABASE_PATH,
    REQUIRED_TABLES,
    REQUIRED_FEATURE_COLUMNS,
    REQUIRED_RTREE_COLUMNS,
    AOI_FEATURE_QUERY,
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database():
    """
    Connect to the OSM spatial database.

    Returns
    -------
    sqlite3.Connection
    """

    return sqlite3.connect(DATABASE_PATH)


# ============================================================
# CLOSE DATABASE
# ============================================================

def close_database(connection):
    """
    Close database connection safely.
    """

    if connection is not None:
        connection.close()


# ============================================================
# VALIDATE DATABASE STRUCTURE
# ============================================================

def validate_database_structure(connection):
    """
    Verify the required tables and columns exist.

    Returns
    -------
    (bool, list)
    """

    table_records = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """
    ).fetchall()

    available_tables = {
        record[0]
        for record in table_records
    }

    missing_tables = (
        REQUIRED_TABLES
        - available_tables
    )

    if missing_tables:
        return (
            False,
            sorted(missing_tables),
        )

    feature_columns = connection.execute(
        """
        PRAGMA table_info(osm_features)
        """
    ).fetchall()

    feature_column_names = {
        record[1]
        for record in feature_columns
    }

    missing_feature_columns = (
        REQUIRED_FEATURE_COLUMNS
        - feature_column_names
    )

    if missing_feature_columns:
        return (
            False,
            sorted(missing_feature_columns),
        )

    rtree_columns = connection.execute(
        """
        PRAGMA table_info(osm_features_rtree)
        """
    ).fetchall()

    rtree_column_names = {
        record[1]
        for record in rtree_columns
    }

    missing_rtree_columns = (
        REQUIRED_RTREE_COLUMNS
        - rtree_column_names
    )

    if missing_rtree_columns:
        return (
            False,
            sorted(missing_rtree_columns),
        )

    return (
        True,
        [],
    )


# ============================================================
# QUERY AOI FEATURES
# ============================================================

def query_aoi_features(
    connection,
    bounds,
):
    """
    Query all OSM features intersecting
    the AOI bounding box.

    Parameters
    ----------
    connection : sqlite3.Connection

    bounds : dict

    Returns
    -------
    list
    """

    records = connection.execute(
        AOI_FEATURE_QUERY,
        (
            bounds["west"],
            bounds["east"],
            bounds["south"],
            bounds["north"],
        ),
    ).fetchall()

    return records


# ============================================================
# DATABASE INFORMATION
# ============================================================

def get_database_size_gb():
    """
    Return database size in GB.
    """

    if not DATABASE_PATH.exists():
        return 0.0

    return (
        DATABASE_PATH.stat().st_size
        /
        (1024 ** 3)
    )


# ============================================================
# DATABASE EXISTS
# ============================================================

def database_exists():
    """
    Check database exists.
    """

    return DATABASE_PATH.exists()