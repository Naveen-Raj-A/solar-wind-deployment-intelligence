from __future__ import annotations

import argparse
import math
import os
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests

from engine.ml_integration import apply_ml_prediction


NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
)

OPEN_METEO_ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)

OPEN_METEO_CURRENT_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

OPEN_METEO_ELEVATION_URL = (
    "https://api.open-meteo.com/v1/elevation"
)

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

CDSE_TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

CDSE_STATISTICS_URL = (
    "https://sh.dataspace.copernicus.eu/statistics/v1"
)

HTTP_HEADERS = {
    "User-Agent": (
        "SolarWindDeploymentIntelligence/1.0 "
        "(renewable-energy-site-analysis)"
    ),
    "Accept": "application/json",
}


def _get_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    timeout: int = 90,
) -> dict[str, Any]:

    response = requests.get(
        url,
        params=params,
        headers=HTTP_HEADERS,
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


def _is_valid_number(value: Any) -> bool:
    """
    Reject API missing-data sentinels such as -999.
    """

    try:
        numeric = float(value)

        if not math.isfinite(numeric):
            return False

        if numeric == -999:
            return False

        if numeric < 0:
            return False

        return True

    except (TypeError, ValueError):
        return False


def _mean(values: list[float]) -> float:
    if not values:
        raise RuntimeError(
            "No valid numeric values were available."
        )

    return round(
        sum(values) / len(values),
        3,
    )


# ------------------------------------------------------------------
# NASA POWER
# ------------------------------------------------------------------

def _fetch_nasa_power_raw(
    latitude: float,
    longitude: float,
    days: int,
) -> dict[str, Any]:

    # NASA POWER can lag behind the current date.
    # Use yesterday as the end date rather than requesting today's
    # incomplete record.
    end_date = date.today() - timedelta(days=1)

    start_date = end_date - timedelta(
        days=max(1, days) - 1
    )

    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,WS10M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON",
        "time-standard": "UTC",
    }

    return _get_json(
        NASA_POWER_URL,
        params=params,
    )


def _extract_nasa_values(
    payload: dict[str, Any],
) -> tuple[list[float], list[float]]:

    parameter_data = (
        payload
        .get("properties", {})
        .get("parameter", {})
    )

    solar_values = [
        float(value)
        for value in parameter_data.get(
            "ALLSKY_SFC_SW_DWN",
            {},
        ).values()
        if _is_valid_number(value)
    ]

    wind_values = [
        float(value)
        for value in parameter_data.get(
            "WS10M",
            {},
        ).values()
        if _is_valid_number(value)
    ]

    return solar_values, wind_values


# ------------------------------------------------------------------
# Open-Meteo fallback
# ------------------------------------------------------------------

def _fetch_open_meteo_resource_history(
    latitude: float,
    longitude: float,
    days: int,
) -> dict[str, Any]:

    end_date = date.today() - timedelta(days=1)

    start_date = end_date - timedelta(
        days=max(1, days) - 1
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": (
            "shortwave_radiation_sum,"
            "wind_speed_10m_mean"
        ),
        "wind_speed_unit": "ms",
        "timezone": "UTC",
    }

    payload = _get_json(
        OPEN_METEO_ARCHIVE_URL,
        params=params,
    )

    daily = payload.get("daily", {})

    solar_values = [
        float(value)
        for value in daily.get(
            "shortwave_radiation_sum",
            [],
        )
        if _is_valid_number(value)
    ]

    wind_values = [
        float(value)
        for value in daily.get(
            "wind_speed_10m_mean",
            [],
        )
        if _is_valid_number(value)
    ]

    if not solar_values:
        raise RuntimeError(
            "Open-Meteo returned no valid solar resource values."
        )

    if not wind_values:
        raise RuntimeError(
            "Open-Meteo returned no valid wind resource values."
        )

    return {
        "source": "Open-Meteo Historical API",
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "solar_resource": {
            "solar_radiation_kwh_m2_day": round(
                _mean(solar_values) / 1000.0,
                3,
            ),
            "sample_count": len(solar_values),
        },
        "wind_speed_statistics": {
            "mean_ms": _mean(wind_values),
            "current_period_max_ms": round(
                max(wind_values),
                3,
            ),
            "sample_count": len(wind_values),
        },
    }


def fetch_nasa_power(
    latitude: float,
    longitude: float,
    days: int = 30,
) -> dict[str, Any]:

    try:

        payload = _fetch_nasa_power_raw(
            latitude,
            longitude,
            days,
        )

        solar_values, wind_values = (
            _extract_nasa_values(payload)
        )

        if solar_values and wind_values:

            end_date = date.today() - timedelta(days=1)
            start_date = end_date - timedelta(
                days=max(1, days) - 1
            )

            return {
                "source": "NASA POWER",
                "source_status": "SUCCESS",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "solar_resource": {
                    "solar_radiation_kwh_m2_day": _mean(
                        solar_values
                    ),
                    "sample_count": len(solar_values),
                },
                "wind_speed_statistics": {
                    "mean_ms": _mean(wind_values),
                    "current_period_max_ms": round(
                        max(wind_values),
                        3,
                    ),
                    "sample_count": len(wind_values),
                },
            }

        raise RuntimeError(
            "NASA POWER returned no valid resource values."
        )

    except Exception as nasa_error:

        fallback = _fetch_open_meteo_resource_history(
            latitude,
            longitude,
            days,
        )

        fallback["source_status"] = (
            "FALLBACK_AFTER_NASA_POWER_FAILURE"
        )

        fallback["primary_source_error"] = str(
            nasa_error
        )

        return fallback


# ------------------------------------------------------------------
# CURRENT CONDITIONS
# ------------------------------------------------------------------

def fetch_current_conditions(
    latitude: float,
    longitude: float,
) -> dict[str, Any]:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "wind_speed_10m,"
            "wind_direction_10m,"
            "shortwave_radiation"
        ),
        "wind_speed_unit": "ms",
        "timezone": "UTC",
    }

    payload = _get_json(
        OPEN_METEO_CURRENT_URL,
        params=params,
    )

    return {
        "source": "Open-Meteo",
        "status": "success",
        "current": payload.get(
            "current",
            {},
        ),
        "current_units": payload.get(
            "current_units",
            {},
        ),
    }


# ------------------------------------------------------------------
# ELEVATION + SLOPE
# ------------------------------------------------------------------

def _meters_per_degree(
    latitude: float,
) -> tuple[float, float]:

    lat_rad = math.radians(latitude)

    meters_per_lat = (
        111132.92
        - 559.82 * math.cos(2 * lat_rad)
        + 1.175 * math.cos(4 * lat_rad)
    )

    meters_per_lon = (
        111412.84 * math.cos(lat_rad)
        - 93.5 * math.cos(3 * lat_rad)
    )

    return meters_per_lat, meters_per_lon


def fetch_elevation_grid(
    latitude: float,
    longitude: float,
    spacing_m: float = 90.0,
) -> dict[str, Any]:

    meters_lat, meters_lon = _meters_per_degree(
        latitude
    )

    delta_lat = spacing_m / meters_lat
    delta_lon = spacing_m / meters_lon

    points = []

    for row in (-1, 0, 1):
        for col in (-1, 0, 1):

            points.append(
                (
                    latitude + row * delta_lat,
                    longitude + col * delta_lon,
                )
            )

    latitudes = [
        point[0]
        for point in points
    ]

    longitudes = [
        point[1]
        for point in points
    ]

    payload = _get_json(
        OPEN_METEO_ELEVATION_URL,
        params={
            "latitude": ",".join(
                str(value)
                for value in latitudes
            ),
            "longitude": ",".join(
                str(value)
                for value in longitudes
            ),
        },
    )

    elevations = payload.get(
        "elevation",
        [],
    )

    valid_elevations = [
        float(value)
        for value in elevations
        if _is_valid_number(value)
    ]

    if len(valid_elevations) != 9:
        raise RuntimeError(
            "Elevation API did not return a complete 3x3 grid."
        )

    center = valid_elevations[4]

    north = valid_elevations[1]
    south = valid_elevations[7]
    west = valid_elevations[3]
    east = valid_elevations[5]

    dz_dy = (
        north - south
    ) / (
        2.0 * spacing_m
    )

    dz_dx = (
        east - west
    ) / (
        2.0 * spacing_m
    )

    slope_degrees = math.degrees(
        math.atan(
            math.sqrt(
                dz_dx ** 2
                + dz_dy ** 2
            )
        )
    )

    return {
        "source": "Open-Meteo Elevation API",
        "elevation_m": round(
            center,
            2,
        ),
        "slope_statistics": {
            "mean_degrees": round(
                slope_degrees,
                3,
            ),
        },
    }


# ------------------------------------------------------------------
# OPENSTREETMAP
# ------------------------------------------------------------------

def _overpass_query(
    latitude: float,
    longitude: float,
    radius_m: int,
) -> str:

    return f"""
[out:json][timeout:90];

(
  way["highway"](around:{radius_m},{latitude},{longitude});
  node["power"](around:{radius_m},{latitude},{longitude});
  way["power"](around:{radius_m},{latitude},{longitude});
  relation["power"](around:{radius_m},{latitude},{longitude});
  node["building"](around:{radius_m},{latitude},{longitude});
  way["building"](around:{radius_m},{latitude},{longitude});
  relation["building"](around:{radius_m},{latitude},{longitude});
);

out center tags;
"""


def _haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:

    radius = 6371.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(
        lat2 - lat1
    )

    dl = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return (
        2
        * radius
        * math.asin(
            math.sqrt(a)
        )
    )


def _element_coordinates(
    element: dict[str, Any],
) -> tuple[float, float] | None:

    if (
        "lat" in element
        and "lon" in element
    ):

        return (
            float(element["lat"]),
            float(element["lon"]),
        )

    center = element.get(
        "center"
    )

    if center:

        return (
            float(center["lat"]),
            float(center["lon"]),
        )

    return None


def fetch_osm_infrastructure(
    latitude: float,
    longitude: float,
    radius_m: int = 5000,
) -> dict[str, Any]:

    query = _overpass_query(
        latitude,
        longitude,
        radius_m,
    )

    last_error: Exception | None = None

    for overpass_url in OVERPASS_URLS:

        try:

            response = requests.post(
                overpass_url,
                data={
                    "data": query,
                },
                headers={
                    **HTTP_HEADERS,
                    "Content-Type": (
                        "application/x-www-form-urlencoded"
                    ),
                },
                timeout=120,
            )

            response.raise_for_status()

            payload = response.json()

            elements = payload.get(
                "elements",
                [],
            )

            road_distances = []
            power_distances = []
            substation_distances = []

            building_count = 0

            for element in elements:

                tags = element.get(
                    "tags",
                    {},
                )

                coordinates = _element_coordinates(
                    element
                )

                if coordinates is None:
                    continue

                element_lat, element_lon = coordinates

                distance = _haversine_km(
                    latitude,
                    longitude,
                    element_lat,
                    element_lon,
                )

                highway = tags.get(
                    "highway"
                )

                if highway:
                    road_distances.append(
                        distance
                    )

                power = tags.get(
                    "power"
                )

                if power:

                    power_distances.append(
                        distance
                    )

                    if power == "substation":
                        substation_distances.append(
                            distance
                        )

                if "building" in tags:
                    building_count += 1

            return {
                "source": (
                    "OpenStreetMap Overpass API"
                ),
                "status": "success",
                "overpass_server": overpass_url,
                "infrastructure_indicators": {
                    "nearest_road_distance_km": (
                        round(
                            min(road_distances),
                            3,
                        )
                        if road_distances
                        else None
                    ),
                    "nearest_power_infrastructure_distance_km": (
                        round(
                            min(power_distances),
                            3,
                        )
                        if power_distances
                        else None
                    ),
                    "nearest_substation_distance_km": (
                        round(
                            min(substation_distances),
                            3,
                        )
                        if substation_distances
                        else None
                    ),
                },
                "feature_analysis": {
                    "building": {
                        "count": building_count,
                    },
                },
            }

        except Exception as exc:

            last_error = exc

    raise RuntimeError(
        "All configured Overpass servers failed. "
        f"Last error: {last_error}"
    )


# ------------------------------------------------------------------
# SENTINEL-2
# ------------------------------------------------------------------

def _sentinel_geometry(
    latitude: float,
    longitude: float,
    radius_m: int,
) -> dict[str, Any]:

    meters_lat, meters_lon = _meters_per_degree(
        latitude
    )

    delta_lat = radius_m / meters_lat
    delta_lon = radius_m / meters_lon

    return {
        "type": "Polygon",
        "coordinates": [[
            [
                longitude - delta_lon,
                latitude - delta_lat,
            ],
            [
                longitude + delta_lon,
                latitude - delta_lat,
            ],
            [
                longitude + delta_lon,
                latitude + delta_lat,
            ],
            [
                longitude - delta_lon,
                latitude + delta_lat,
            ],
            [
                longitude - delta_lon,
                latitude - delta_lat,
            ],
        ]],
    }


def fetch_sentinel_statistics(
    latitude: float,
    longitude: float,
    radius_m: int = 500,
    days: int = 30,
) -> dict[str, Any]:

    client_id = os.getenv(
        "CDSE_CLIENT_ID"
    )

    client_secret = os.getenv(
        "CDSE_CLIENT_SECRET"
    )

    if not client_id or not client_secret:
        raise RuntimeError(
            "Sentinel is not configured. "
            "Set CDSE_CLIENT_ID and CDSE_CLIENT_SECRET."
        )

    token_response = requests.post(
        CDSE_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={
            "Content-Type": (
                "application/x-www-form-urlencoded"
            ),
        },
        timeout=60,
    )

    token_response.raise_for_status()

    access_token = token_response.json().get(
        "access_token"
    )

    if not access_token:
        raise RuntimeError(
            "Copernicus token response did not contain access_token."
        )

    end_date = date.today()
    start_date = end_date - timedelta(
        days=max(1, days) - 1
    )

    geometry = _sentinel_geometry(
        latitude,
        longitude,
        radius_m,
    )

    payload = {
        "input": {
            "bounds": {
                "geometry": geometry,
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": (
                                start_date.isoformat()
                                + "T00:00:00Z"
                            ),
                            "to": (
                                end_date.isoformat()
                                + "T23:59:59Z"
                            ),
                        },
                        "maxCloudCoverage": 80,
                    },
                }
            ],
        },
        "aggregation": {
            "timeRange": {
                "from": (
                    start_date.isoformat()
                    + "T00:00:00Z"
                ),
                "to": (
                    end_date.isoformat()
                    + "T23:59:59Z"
                ),
            },
            "aggregationInterval": {
                "of": "P1D"
            },
            "evalscript": (
                "//VERSION=3\n"
                "function setup(){return {"
                "input:["
                "\"B04\",\"B08\",\"B11\",\"dataMask\""
                "],"
                "output:["
                "{\"id\":\"ndvi\",\"bands\":1,\"sampleType\":\"FLOAT32\"},"
                "{\"id\":\"ndmi\",\"bands\":1,\"sampleType\":\"FLOAT32\"},"
                "{\"id\":\"valid\",\"bands\":1,\"sampleType\":\"FLOAT32\"}"
                "]};}\n"
                "function evaluatePixel(s){"
                "let ndvi=(s.B08-s.B04)/(s.B08+s.B04);"
                "let ndmi=(s.B08-s.B11)/(s.B08+s.B11);"
                "return {"
                "ndvi:[ndvi],"
                "ndmi:[ndmi],"
                "valid:[s.dataMask]"
                "};}"
            ),
        },
    }

    response = requests.post(
        CDSE_STATISTICS_URL,
        json=payload,
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    data = result.get(
        "data",
        [],
    )

    ndvi_values = []
    ndmi_values = []
    valid_values = []

    for item in data:

        outputs = item.get(
            "outputs",
            {}
        )

        ndvi = outputs.get(
            "ndvi",
            {}
        ).get(
            "bands",
            [{}],
        )[0].get(
            "stats",
            {},
        ).get(
            "mean"
        )

        ndmi = outputs.get(
            "ndmi",
            {}
        ).get(
            "bands",
            [{}],
        )[0].get(
            "stats",
            {},
        ).get(
            "mean"
        )

        valid = outputs.get(
            "valid",
            {}
        ).get(
            "bands",
            [{}],
        )[0].get(
            "stats",
            {},
        ).get(
            "mean"
        )

        if _is_valid_number(ndvi):
            ndvi_values.append(
                float(ndvi)
            )

        if _is_valid_number(ndmi):
            ndmi_values.append(
                float(ndmi)
            )

        if _is_valid_number(valid):
            valid_values.append(
                float(valid) * 100.0
            )

    if not ndvi_values or not ndmi_values:
        raise RuntimeError(
            "Sentinel returned no valid NDVI/NDMI statistics."
        )

    return {
        "source": "Copernicus Sentinel-2 L2A",
        "status": "success",
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "ndvi_statistics": {
            "mean": round(
                _mean(ndvi_values),
                4,
            ),
        },
        "ndmi_statistics": {
            "mean": round(
                _mean(ndmi_values),
                4,
            ),
        },
        "valid_percentage": round(
            _mean(valid_values)
            if valid_values
            else 0.0,
            2,
        ),
    }


# ------------------------------------------------------------------
# CONSOLIDATED REAL-TIME SITE REPORT
# ------------------------------------------------------------------

def build_realtime_site_report(
    latitude: float,
    longitude: float,
    available_land_area_km2: float,
    used_land_area_km2: float = 0.0,
    *,
    nasa_days: int = 30,
    osm_radius_m: int = 5000,
    sentinel_radius_m: int = 500,
    sentinel_days: int = 30,
    require_sentinel: bool = False,
) -> dict[str, Any]:

    if not -90 <= latitude <= 90:
        raise ValueError(
            "latitude must be between -90 and 90."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "longitude must be between -180 and 180."
        )

    if available_land_area_km2 <= 0:
        raise ValueError(
            "available_land_area_km2 must be greater than zero."
        )

    if used_land_area_km2 < 0:
        raise ValueError(
            "used_land_area_km2 cannot be negative."
        )

    if used_land_area_km2 > available_land_area_km2:
        raise ValueError(
            "used_land_area_km2 cannot exceed available_land_area_km2."
        )

    nasa = fetch_nasa_power(
        latitude,
        longitude,
        days=nasa_days,
    )

    current_conditions = fetch_current_conditions(
        latitude,
        longitude,
    )

    terrain = fetch_elevation_grid(
        latitude,
        longitude,
    )

    osm = fetch_osm_infrastructure(
        latitude,
        longitude,
        radius_m=osm_radius_m,
    )

    sentinel_status = "NOT_CONFIGURED"

    try:

        sentinel = fetch_sentinel_statistics(
            latitude,
            longitude,
            radius_m=sentinel_radius_m,
            days=sentinel_days,
        )

        sentinel_status = "SUCCESS"

    except Exception as exc:

        if require_sentinel:
            raise

        sentinel = {
            "source": "Copernicus Sentinel-2 L2A",
            "status": "unavailable",
            "error": str(exc),
        }

        if (
            "not configured"
            not in str(exc).lower()
        ):
            sentinel_status = "UNAVAILABLE"
        else:
            sentinel_status = "NOT_CONFIGURED"

    reserve_percent = (
        (
            available_land_area_km2
            - used_land_area_km2
        )
        / available_land_area_km2
        * 100.0
    )

    report = {
        "site_information": {
            "requested_location": (
                f"{latitude:.6f}, {longitude:.6f}"
            ),
            "latitude": latitude,
            "longitude": longitude,
            "available_land_area_km2": (
                available_land_area_km2
            ),
            "used_land_area_km2": (
                used_land_area_km2
            ),
            "land_reserve_percent": round(
                max(
                    0.0,
                    reserve_percent,
                ),
                2,
            ),
        },

        "datasets": {
            "nasa_power": nasa,

            "wind": {
                "source": nasa[
                    "source"
                ],
                "source_status": nasa.get(
                    "source_status"
                ),
                "wind_speed_statistics": nasa[
                    "wind_speed_statistics"
                ],
            },

            "srtm": terrain,

            "osm": osm,

            "sentinel": sentinel,
        },

        "current_conditions": (
            current_conditions
        ),

        "runtime_metadata": {
            "fetched_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),

            "solar_resource_source": nasa[
                "source"
            ],

            "wind_resource_source": nasa[
                "source"
            ],

            "sentinel_status": sentinel_status,
        },
    }

    # --------------------------------------------------------------
    # MACHINE LEARNING INFERENCE
    # --------------------------------------------------------------
    # The ML module loads the persisted Random Forest model once,
    # validates the required features, and adds the prediction to
    # the consolidated live-data report.
    report = apply_ml_prediction(report)

    return report


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Live Solar-Wind site evaluation"
        )
    )

    parser.add_argument(
        "--latitude",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--longitude",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--land-area-km2",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--used-land-area-km2",
        type=float,
        default=0.0,
    )

    parser.add_argument(
        "--nasa-days",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--osm-radius-m",
        type=int,
        default=5000,
    )

    args = parser.parse_args()

    import json

    report = build_realtime_site_report(
        latitude=args.latitude,
        longitude=args.longitude,
        available_land_area_km2=(
            args.land_area_km2
        ),
        used_land_area_km2=(
            args.used_land_area_km2
        ),
        nasa_days=args.nasa_days,
        osm_radius_m=args.osm_radius_m,
    )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
