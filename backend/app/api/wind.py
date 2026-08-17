from fastapi import APIRouter, Query

from app.services.wind_service import get_wind_speed


# Create router for wind-data endpoints
router = APIRouter()


# Get wind-speed data for a geographic location
@router.get("/wind-data")
def get_wind_data(
    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Latitude of the location",
    ),
    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Longitude of the location",
    ),
):
    """
    Retrieve the wind speed at 150 m
    for the given latitude and longitude.
    """

    # Call the wind service
    result = get_wind_speed(
        latitude=latitude,
        longitude=longitude,
    )

    # Return the result
    return result