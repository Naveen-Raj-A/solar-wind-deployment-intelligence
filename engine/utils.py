"""
Common utility functions.
"""


def create_safe_location_name(name: str) -> str:
    """
    Convert a location name into a filesystem-safe folder name.

    Examples
    --------
    "Tiruvannamalai" -> "tiruvannamalai"
    "New York City" -> "new_york_city"
    "Los-Angeles" -> "los_angeles"
    """

    safe = ""

    for c in name.lower():
        if c.isalnum():
            safe += c
        elif c in (" ", "-", "_"):
            safe += "_"

    return safe.strip("_")