"""
FastAPI entry point for Solar-Wind Deployment Intelligence.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine.analysis_service import analysis_service
from engine.site_information import geocode_location


app = FastAPI(
    title="Solar-Wind Deployment Intelligence API",
    version="2.0.0",
    description=(
        "Dataset-first API for renewable-energy site analysis, "
        "deployment scoring, optimization, energy yield and finance."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    # Use either:
    #   location="Krishnagiri"
    # OR:
    #   latitude + longitude
    location: str | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    available_land_area_km2: float = Field(
        ...,
        gt=0,
    )

    used_land_area_km2: float = Field(
        default=0.0,
        ge=0,
    )

    nasa_days: int = Field(
        default=30,
        ge=1,
        le=365,
    )

    osm_radius_m: int = Field(
        default=5000,
        ge=100,
        le=50000,
    )

    sentinel_radius_m: int = Field(
        default=500,
        ge=10,
        le=5000,
    )

    sentinel_days: int = Field(
        default=30,
        ge=1,
        le=365,
    )

    require_sentinel: bool = False

    installed_capacity_mw: float | None = Field(
        default=None,
        ge=0,
    )

    capacity_factor: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    solar_capacity_factor: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    wind_capacity_factor: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    solar_capacity_share: float = Field(
        default=0.50,
        ge=0,
        le=1,
    )

    system_efficiency: float = Field(
        default=0.95,
        ge=0,
        le=1,
    )

    operational_loss: float = Field(
        default=0.05,
        ge=0,
        le=1,
    )

    electricity_tariff_inr_per_kwh: float = Field(
        default=5.0,
        ge=0,
    )

    cost_per_mw: float = Field(
        default=50_00_000.0,
        ge=0,
    )

    additional_installation_percent: float = Field(
        default=0.0,
        ge=0,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "solar-wind-deployment-intelligence",
        "pipeline": "local-dataset-first",
    }


@app.post("/analysis")
def run_analysis(
    request: AnalysisRequest,
) -> dict[str, Any]:

    if (
        request.used_land_area_km2
        > request.available_land_area_km2
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "used_land_area_km2 cannot exceed "
                "available_land_area_km2."
            ),
        )

    # ----------------------------------------------------------
    # Resolve location input
    # ----------------------------------------------------------
    if request.location and request.location.strip():
        site = geocode_location(
            request.location.strip()
        )

        if site is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Location '{request.location}' "
                    "could not be resolved in India."
                ),
            )

        latitude = site.latitude
        longitude = site.longitude
        requested_location = site.requested_location
        resolved_location = site.resolved_location
        country = site.country
        state = site.state
        source = site.source

    elif (
        request.latitude is not None
        and request.longitude is not None
    ):
        latitude = request.latitude
        longitude = request.longitude
        requested_location = "Coordinates"
        resolved_location = "Coordinates"
        country = "Unknown"
        state = "Unknown"
        source = "Manual"

    else:
        raise HTTPException(
            status_code=422,
            detail=(
                "Provide either 'location' or both "
                "'latitude' and 'longitude'."
            ),
        )

    try:
        return analysis_service.analyze(
            latitude=latitude,
            longitude=longitude,
            requested_location=requested_location,
            resolved_location=resolved_location,
            country=country,
            state=state,
            source=source,
            available_land_area_km2=(
                request.available_land_area_km2
            ),
            used_land_area_km2=(
                request.used_land_area_km2
            ),
            nasa_days=request.nasa_days,
            osm_radius_m=request.osm_radius_m,
            sentinel_radius_m=request.sentinel_radius_m,
            sentinel_days=request.sentinel_days,
            require_sentinel=request.require_sentinel,
            installed_capacity_mw=(
                request.installed_capacity_mw
            ),
            capacity_factor=request.capacity_factor,
            solar_capacity_factor=(
                request.solar_capacity_factor
            ),
            wind_capacity_factor=(
                request.wind_capacity_factor
            ),
            solar_capacity_share=(
                request.solar_capacity_share
            ),
            system_efficiency=(
                request.system_efficiency
            ),
            operational_loss=request.operational_loss,
            electricity_tariff_inr_per_kwh=(
                request.electricity_tariff_inr_per_kwh
            ),
            cost_per_mw=request.cost_per_mw,
            additional_installation_percent=(
                request.additional_installation_percent
            ),
            save_output=True,
            display_output=True,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Local dataset analysis pipeline failed: "
                f"{exc}"
            ),
        ) from exc
