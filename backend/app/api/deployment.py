from fastapi import APIRouter, Query

from app.services.deployment_service import deployment_service

router = APIRouter(
    prefix="/deployment",
    tags=["Deployment"],
)


@router.get("/analyze")
def analyze(
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
    Unified Deployment Analysis

    Returns the complete deployment analysis
    used by the frontend dashboard.
    """

    return deployment_service.analyze_solar(
        latitude=latitude,
        longitude=longitude,
    )


@router.get("/solar")
def analyze_solar(
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
    Complete Solar Deployment Analysis

    Returns:
    - Prediction
    - Analysis Report
    - Deployment Optimization
    - Forecast
    - Investment Recommendation
    """

    return deployment_service.analyze_solar(
        latitude=latitude,
        longitude=longitude,
    )


@router.get("/wind")
def analyze_wind(
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
    Complete Wind Deployment Analysis

    Returns:
    - Prediction
    - Analysis Report
    - Deployment Optimization
    - Forecast
    - Investment Recommendation
    """

    return deployment_service.analyze_wind(
        latitude=latitude,
        longitude=longitude,
    )