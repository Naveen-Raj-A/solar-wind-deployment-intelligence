"""
Energy Yield Estimation Service

Provides reusable annual energy-yield estimates for solar, wind and
hybrid renewable deployments.

The calculations are planning-level estimates, not detailed bankable
energy assessments. They explicitly account for installed capacity,
capacity factor, system efficiency and operational losses.
"""

from __future__ import annotations

from typing import Any

HOURS_PER_YEAR = 8760.0

# Planning defaults. They are intentionally configurable rather than
# hidden inside the calculation functions.
DEFAULT_SYSTEM_EFFICIENCY = 0.95
DEFAULT_OPERATIONAL_LOSS = 0.05
DEFAULT_SOLAR_CAPACITY_FACTOR = 0.20
DEFAULT_WIND_CAPACITY_FACTOR = 0.35


def _validate_fraction(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1.")
    return value


def _validate_positive(value: float, name: str) -> float:
    value = float(value)
    if value < 0.0:
        raise ValueError(f"{name} cannot be negative.")
    return value


def _effective_performance_factor(
    system_efficiency: float,
    operational_loss: float,
) -> float:
    """Combine efficiency and operational loss without double counting."""
    efficiency = _validate_fraction(
        system_efficiency,
        "system_efficiency",
    )
    loss = _validate_fraction(
        operational_loss,
        "operational_loss",
    )
    return efficiency * (1.0 - loss)


def estimate_annual_energy(
    installed_capacity_mw: float,
    capacity_factor: float,
    system_efficiency: float = DEFAULT_SYSTEM_EFFICIENCY,
    operational_loss: float = DEFAULT_OPERATIONAL_LOSS,
) -> float:
    """
    Estimate annual generation in MWh.

    Formula:
        Energy = Capacity(MW) * 8760 * CapacityFactor
                 * SystemEfficiency * (1 - OperationalLoss)
    """
    capacity = _validate_positive(
        installed_capacity_mw,
        "installed_capacity_mw",
    )
    cf = _validate_fraction(capacity_factor, "capacity_factor")
    performance = _effective_performance_factor(
        system_efficiency,
        operational_loss,
    )

    return round(
        capacity * HOURS_PER_YEAR * cf * performance,
        2,
    )


def estimate_solar_energy_yield(
    installed_capacity_mw: float,
    solar_irradiance_kwh_m2_day: float | None = None,
    capacity_factor: float | None = None,
    system_efficiency: float = DEFAULT_SYSTEM_EFFICIENCY,
    operational_loss: float = DEFAULT_OPERATIONAL_LOSS,
) -> dict[str, Any]:
    """
    Estimate annual solar generation.

    If capacity_factor is omitted, it is estimated from daily solar
    irradiation using:

        solar_CF = daily irradiation / 24

    This is a planning approximation; a detailed PV model should use
    module temperature, tilt, azimuth, inverter clipping, shading and
    time-series irradiance.
    """
    if solar_irradiance_kwh_m2_day is not None:
        irradiance = _validate_positive(
            solar_irradiance_kwh_m2_day,
            "solar_irradiance_kwh_m2_day",
        )
    else:
        irradiance = None

    if capacity_factor is None:
        if irradiance is None:
            capacity_factor = DEFAULT_SOLAR_CAPACITY_FACTOR
        else:
            capacity_factor = min(1.0, irradiance / 24.0)

    energy_mwh = estimate_annual_energy(
        installed_capacity_mw=installed_capacity_mw,
        capacity_factor=capacity_factor,
        system_efficiency=system_efficiency,
        operational_loss=operational_loss,
    )

    return {
        "technology": "SOLAR",
        "installed_capacity_mw": round(float(installed_capacity_mw), 2),
        "solar_irradiance_kwh_m2_day": (
            round(irradiance, 4) if irradiance is not None else None
        ),
        "capacity_factor": round(float(capacity_factor), 4),
        "system_efficiency": round(float(system_efficiency), 4),
        "operational_loss": round(float(operational_loss), 4),
        "annual_energy_mwh": energy_mwh,
        "annual_energy_gwh": round(energy_mwh / 1000.0, 4),
    }


def estimate_wind_energy_yield(
    installed_capacity_mw: float,
    wind_speed_ms: float | None = None,
    capacity_factor: float | None = None,
    system_efficiency: float = DEFAULT_SYSTEM_EFFICIENCY,
    operational_loss: float = DEFAULT_OPERATIONAL_LOSS,
) -> dict[str, Any]:
    """
    Estimate annual wind generation.

    A supplied capacity factor is preferred because wind generation
    normally requires a turbine power curve and wind-speed distribution.
    When it is absent, a configurable planning proxy is used rather than
    treating mean wind speed as directly proportional to generation.
    """
    if wind_speed_ms is not None:
        wind_speed = _validate_positive(wind_speed_ms, "wind_speed_ms")
    else:
        wind_speed = None

    if capacity_factor is None:
        if wind_speed is None:
            capacity_factor = DEFAULT_WIND_CAPACITY_FACTOR
        else:
            # Conservative planning proxy. It is deliberately capped and
            # should be replaced by a turbine power-curve model for bankable work.
            capacity_factor = min(0.60, max(0.05, (wind_speed - 3.0) / 18.0))

    energy_mwh = estimate_annual_energy(
        installed_capacity_mw=installed_capacity_mw,
        capacity_factor=capacity_factor,
        system_efficiency=system_efficiency,
        operational_loss=operational_loss,
    )

    return {
        "technology": "WIND",
        "installed_capacity_mw": round(float(installed_capacity_mw), 2),
        "wind_speed_ms": round(wind_speed, 4) if wind_speed is not None else None,
        "capacity_factor": round(float(capacity_factor), 4),
        "system_efficiency": round(float(system_efficiency), 4),
        "operational_loss": round(float(operational_loss), 4),
        "annual_energy_mwh": energy_mwh,
        "annual_energy_gwh": round(energy_mwh / 1000.0, 4),
    }


def estimate_hybrid_energy_yield(
    installed_capacity_mw: float,
    solar_irradiance_kwh_m2_day: float | None = None,
    wind_speed_ms: float | None = None,
    solar_capacity_factor: float | None = None,
    wind_capacity_factor: float | None = None,
    solar_capacity_share: float = 0.50,
    system_efficiency: float = DEFAULT_SYSTEM_EFFICIENCY,
    operational_loss: float = DEFAULT_OPERATIONAL_LOSS,
) -> dict[str, Any]:
    """Estimate annual generation for a solar/wind hybrid plant."""
    share = _validate_fraction(
        solar_capacity_share,
        "solar_capacity_share",
    )

    total_capacity = _validate_positive(
        installed_capacity_mw,
        "installed_capacity_mw",
    )

    solar_capacity = total_capacity * share
    wind_capacity = total_capacity * (1.0 - share)

    solar = estimate_solar_energy_yield(
        installed_capacity_mw=solar_capacity,
        solar_irradiance_kwh_m2_day=solar_irradiance_kwh_m2_day,
        capacity_factor=solar_capacity_factor,
        system_efficiency=system_efficiency,
        operational_loss=operational_loss,
    )

    wind = estimate_wind_energy_yield(
        installed_capacity_mw=wind_capacity,
        wind_speed_ms=wind_speed_ms,
        capacity_factor=wind_capacity_factor,
        system_efficiency=system_efficiency,
        operational_loss=operational_loss,
    )

    annual_energy_mwh = round(
        solar["annual_energy_mwh"] + wind["annual_energy_mwh"],
        2,
    )

    return {
        "technology": "HYBRID",
        "installed_capacity_mw": round(total_capacity, 2),
        "solar_capacity_mw": round(solar_capacity, 2),
        "wind_capacity_mw": round(wind_capacity, 2),
        "solar_capacity_share": round(share, 4),
        "wind_capacity_share": round(1.0 - share, 4),
        "solar": solar,
        "wind": wind,
        "annual_energy_mwh": annual_energy_mwh,
        "annual_energy_gwh": round(annual_energy_mwh / 1000.0, 4),
    }


def estimate_energy_yield(
    technology: str,
    installed_capacity_mw: float,
    *,
    solar_irradiance_kwh_m2_day: float | None = None,
    wind_speed_ms: float | None = None,
    capacity_factor: float | None = None,
    solar_capacity_factor: float | None = None,
    wind_capacity_factor: float | None = None,
    solar_capacity_share: float = 0.50,
    system_efficiency: float = DEFAULT_SYSTEM_EFFICIENCY,
    operational_loss: float = DEFAULT_OPERATIONAL_LOSS,
) -> dict[str, Any]:
    """Dispatch to the appropriate technology-specific estimator."""
    technology = technology.upper().strip()

    if technology == "SOLAR":
        return estimate_solar_energy_yield(
            installed_capacity_mw,
            solar_irradiance_kwh_m2_day,
            capacity_factor,
            system_efficiency,
            operational_loss,
        )

    if technology == "WIND":
        return estimate_wind_energy_yield(
            installed_capacity_mw,
            wind_speed_ms,
            capacity_factor,
            system_efficiency,
            operational_loss,
        )

    if technology == "HYBRID":
        # A single capacity factor can be used as a common fallback
        # when technology-specific factors are not supplied.
        if solar_capacity_factor is None:
            solar_capacity_factor = capacity_factor
        if wind_capacity_factor is None:
            wind_capacity_factor = capacity_factor

        return estimate_hybrid_energy_yield(
            installed_capacity_mw,
            solar_irradiance_kwh_m2_day,
            wind_speed_ms,
            solar_capacity_factor,
            wind_capacity_factor,
            solar_capacity_share,
            system_efficiency,
            operational_loss,
        )

    raise ValueError("technology must be SOLAR, WIND, or HYBRID")
