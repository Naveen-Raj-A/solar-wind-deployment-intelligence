"""
=========================================================
pdf_tables.py
---------------------------------------------------------
Reusable Report Tables

Solar Wind Deployment Intelligence
=========================================================
"""

from reportlab.platypus import Table

from engine.report_styles import TABLE_STYLE, SUMMARY_TABLE_STYLE


# =========================================================
# Generic Two Column Table
# =========================================================

def build_key_value_table(title, rows):
    """
    rows example:

    [
        ("Latitude",11.23),
        ("Longitude",78.44),
        ...
    ]
    """

    data = [["Parameter", "Value"]]

    data.extend(rows)

    table = Table(
        data,
        colWidths=[220, 260]
    )

    table.setStyle(TABLE_STYLE)

    return table


# =========================================================
# Generic Summary Table
# =========================================================

def build_summary_table(headers, rows):
    """
    Generic summary table.
    """

    data = [headers]

    data.extend(rows)

    table = Table(data)

    table.setStyle(SUMMARY_TABLE_STYLE)

    return table


# =========================================================
# Site Information
# =========================================================

def build_site_information_table(site):

    rows = [

        ("Requested Location",
         site.get("requested_location", "N/A")),

        ("Resolved Location",
         site.get("resolved_location", "N/A")),

        ("State",
         site.get("state", "N/A")),

        ("Country",
         site.get("country", "N/A")),

        ("Latitude",
         site.get("latitude", "N/A")),

        ("Longitude",
         site.get("longitude", "N/A")),

        ("Source",
         site.get("source", "N/A"))

    ]

    return build_key_value_table(
        "Site Information",
        rows
    )


# =========================================================
# NASA POWER
# =========================================================

def build_nasa_table(nasa):

    rows = [

        ("Solar Radiation",
         nasa.get("solar_radiation", "N/A")),

        ("Temperature",
         nasa.get("temperature", "N/A")),

        ("Humidity",
         nasa.get("humidity", "N/A")),

        ("Wind Speed 10m",
         nasa.get("wind_speed_10m", "N/A")),

        ("Wind Speed 50m",
         nasa.get("wind_speed_50m", "N/A")),

        ("Solar Class",
         nasa.get("solar_resource_class", "N/A"))

    ]

    return build_key_value_table(
        "NASA POWER",
        rows
    )


# =========================================================
# WIND
# =========================================================

def build_wind_table(wind):

    rows = [

        ("Mean Wind Speed",
         wind.get("mean_wind_speed", "N/A")),

        ("Maximum Wind Speed",
         wind.get("max_wind_speed", "N/A")),

        ("Wind Class",
         wind.get("wind_class", "N/A"))

    ]

    return build_key_value_table(
        "Wind",
        rows
    )


# =========================================================
# SRTM
# =========================================================

def build_srtm_table(srtm):

    rows = [

        ("Mean Elevation",
         srtm.get("mean_elevation", "N/A")),

        ("Mean Slope",
         srtm.get("mean_slope", "N/A")),

        ("Terrain Suitability",
         srtm.get("terrain_suitability", "N/A"))

    ]

    return build_key_value_table(
        "SRTM",
        rows
    )


# =========================================================
# Sentinel
# =========================================================

def build_sentinel_table(sentinel):

    rows = [

        ("NDVI",
         sentinel.get("ndvi_mean", "N/A")),

        ("NDMI",
         sentinel.get("ndmi_mean", "N/A")),

        ("Valid Pixels %",
         sentinel.get("valid_pixels_percentage", "N/A"))

    ]

    return build_key_value_table(
        "Sentinel",
        rows
    )


# =========================================================
# OSM
# =========================================================

def build_osm_table(osm):

    rows = []

    for key, value in osm.items():

        rows.append(
            (
                key.replace("_", " ").title(),
                value
            )
        )

    return build_key_value_table(
        "OpenStreetMap",
        rows
    )


# =========================================================
# Deployment Assessment
# =========================================================

def build_score_table(score):

    data = [

        ["Dataset", "Score", "Weight"],

        [
            "Solar",
            f"{score['solar_score']:.2f}",
            score["weights"]["solar"]
        ],

        [
            "Wind",
            f"{score['wind_score']:.2f}",
            score["weights"]["wind"]
        ],

        [
            "Terrain",
            f"{score['terrain_score']:.2f}",
            score["weights"]["terrain"]
        ],

        [
            "Sentinel",
            f"{score['sentinel_score']:.2f}",
            score["weights"]["sentinel"]
        ],

        [
            "OSM",
            f"{score['osm_score']:.2f}",
            score["weights"]["osm"]
        ],

        [
            "Overall",
            f"{score['overall_score']:.2f}",
            "100"
        ]

    ]

    table = Table(
        data,
        colWidths=[180, 120, 120]
    )

    table.setStyle(SUMMARY_TABLE_STYLE)

    return table