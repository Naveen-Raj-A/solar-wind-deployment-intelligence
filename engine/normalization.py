"""
Reusable score normalization utilities.

All functions return a score from 0 to 100.

Higher-is-better parameters:
    Solar irradiance
    Wind speed

Lower-is-better parameters:
    Slope
    Distance to grid
    Distance to road
"""


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Keep value inside the configured range."""
    return max(minimum, min(value, maximum))


def normalize_higher_is_better(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Normalize a value where higher values are better.

    Returns:
        0 to 100
    """

    if value is None:
        return 0.0

    if maximum <= minimum:
        raise ValueError(
            "maximum must be greater than minimum"
        )

    value = _clamp(
        float(value),
        minimum,
        maximum,
    )

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100

    return round(score, 2)


def normalize_lower_is_better(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Normalize a value where lower values are better.

    Returns:
        0 to 100
    """

    if value is None:
        return 0.0

    if maximum <= minimum:
        raise ValueError(
            "maximum must be greater than minimum"
        )

    value = _clamp(
        float(value),
        minimum,
        maximum,
    )

    score = (
        (maximum - value)
        / (maximum - minimum)
    ) * 100

    return round(score, 2)


def normalize_solar_irradiance(
    solar_irradiance: float,
) -> float:
    """
    Solar irradiance normalization.

    Unit:
        kWh/m²/day

    Configured range:
        2.0 -> 0
        7.0 -> 100
    """

    return normalize_higher_is_better(
        solar_irradiance,
        2.0,
        7.0,
    )


def normalize_wind_speed(
    wind_speed: float,
) -> float:
    """
    Wind speed normalization.

    Unit:
        m/s

    Configured range:
        2.0 -> 0
        10.0 -> 100
    """

    return normalize_higher_is_better(
        wind_speed,
        2.0,
        10.0,
    )


def normalize_slope(
    slope: float,
) -> float:
    """
    Slope normalization.

    Unit:
        degrees

    Lower slope is considered better.

    Configured range:
        0°  -> 100
        15° -> 0
    """

    return normalize_lower_is_better(
        slope,
        0.0,
        15.0,
    )


def normalize_distance_to_grid(
    distance_km: float,
) -> float:
    """
    Grid-distance normalization.

    Unit:
        km

    Lower distance is better.

    Configured range:
        0 km  -> 100
        25 km -> 0
    """

    return normalize_lower_is_better(
        distance_km,
        0.0,
        25.0,
    )


def normalize_distance_to_road(
    distance_km: float,
) -> float:
    """
    Road-distance normalization.

    Unit:
        km

    Lower distance is better.

    Configured range:
        0 km  -> 100
        10 km -> 0
    """

    return normalize_lower_is_better(
        distance_km,
        0.0,
        10.0,
    )