"""
Financial Analysis Engine

Independent financial calculations for renewable energy projects.

This module does not depend on:
    - Machine learning
    - Technical feasibility
    - Energy-yield implementation
    - FastAPI

All functions are reusable and can be called independently.
"""

from __future__ import annotations

from typing import Any


# ================================================================
# DEFAULT CONFIGURATION
# ================================================================

DEFAULT_COST_PER_MW = 50_00_000.0
DEFAULT_ADDITIONAL_INSTALLATION_PERCENT = 0.0
DEFAULT_ELECTRICITY_TARIFF_INR_PER_KWH = 5.0


# ================================================================
# VALIDATION
# ================================================================

def _validate_non_negative(
    value: float,
    name: str,
) -> float:

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{name} must be a valid number."
        )

    if numeric_value < 0:
        raise ValueError(
            f"{name} cannot be negative."
        )

    return numeric_value


# ================================================================
# ANNUAL REVENUE
# ================================================================

def calculate_annual_revenue(
    annual_energy_yield_kwh: float,
    electricity_tariff_inr_per_kwh: float,
) -> float:
    """
    Calculate estimated annual electricity revenue.

    Formula:

        Annual Revenue
        = Annual Energy Yield (kWh)
          × Electricity Tariff (₹/kWh)
    """

    energy = _validate_non_negative(
        annual_energy_yield_kwh,
        "annual_energy_yield_kwh",
    )

    tariff = _validate_non_negative(
        electricity_tariff_inr_per_kwh,
        "electricity_tariff_inr_per_kwh",
    )

    revenue = energy * tariff

    return round(revenue, 2)


# ================================================================
# PROJECT COST
# ================================================================

def calculate_project_cost(
    installed_capacity_mw: float,
    cost_per_mw: float = DEFAULT_COST_PER_MW,
    additional_installation_percent: float = (
        DEFAULT_ADDITIONAL_INSTALLATION_PERCENT
    ),
) -> float:
    """
    Estimate total project installation cost.

    Formula:

        Base Cost
        = Installed Capacity × Cost per MW

        Total Cost
        = Base Cost ×
          (1 + Additional Installation % / 100)
    """

    capacity = _validate_non_negative(
        installed_capacity_mw,
        "installed_capacity_mw",
    )

    cost = _validate_non_negative(
        cost_per_mw,
        "cost_per_mw",
    )

    additional_percent = _validate_non_negative(
        additional_installation_percent,
        "additional_installation_percent",
    )

    base_cost = capacity * cost

    total_cost = (
        base_cost
        * (1.0 + additional_percent / 100.0)
    )

    return round(total_cost, 2)


# ================================================================
# PAYBACK PERIOD
# ================================================================

def calculate_payback_period(
    total_project_cost: float,
    annual_revenue: float,
) -> float | None:
    """
    Estimate simple project payback period in years.

    Formula:

        Payback Period
        = Total Project Cost / Annual Revenue

    Returns None when annual revenue is zero.

    Negative revenue is rejected because it cannot represent
    a valid annual revenue stream for this calculation.
    """

    project_cost = _validate_non_negative(
        total_project_cost,
        "total_project_cost",
    )

    try:
        revenue = float(annual_revenue)
    except (TypeError, ValueError):
        raise ValueError(
            "annual_revenue must be a valid number."
        )

    if revenue < 0:
        raise ValueError(
            "annual_revenue cannot be negative."
        )

    if revenue == 0:
        return None

    if project_cost == 0:
        return 0.0

    payback = project_cost / revenue

    return round(payback, 2)


# ================================================================
# ROI
# ================================================================

def calculate_roi(
    total_project_cost: float,
    annual_revenue: float,
) -> float:
    """
    Calculate annual Return on Investment.

    Formula:

        ROI (%)
        = (Annual Revenue / Total Project Cost) × 100

    Returns 0 when project cost is zero.
    """

    project_cost = _validate_non_negative(
        total_project_cost,
        "total_project_cost",
    )

    try:
        revenue = float(annual_revenue)
    except (TypeError, ValueError):
        raise ValueError(
            "annual_revenue must be a valid number."
        )

    if revenue < 0:
        raise ValueError(
            "annual_revenue cannot be negative."
        )

    if project_cost == 0:
        return 0.0

    roi = (
        revenue
        / project_cost
        * 100.0
    )

    return round(roi, 2)


# ================================================================
# COMPLETE FINANCIAL ANALYSIS
# ================================================================

def calculate_financial_analysis(
    annual_energy_yield_kwh: float,
    installed_capacity_mw: float,
    electricity_tariff_inr_per_kwh: float = (
        DEFAULT_ELECTRICITY_TARIFF_INR_PER_KWH
    ),
    cost_per_mw: float = DEFAULT_COST_PER_MW,
    additional_installation_percent: float = (
        DEFAULT_ADDITIONAL_INSTALLATION_PERCENT
    ),
) -> dict[str, Any]:
    """
    Execute the complete financial analysis.

    Returns:
        annual_energy_yield_kwh
        electricity_tariff_inr_per_kwh
        installed_capacity_mw
        cost_per_mw
        additional_installation_percent
        estimated_annual_revenue
        estimated_project_cost
        payback_period_years
        roi_percent
    """

    annual_energy = _validate_non_negative(
        annual_energy_yield_kwh,
        "annual_energy_yield_kwh",
    )

    capacity = _validate_non_negative(
        installed_capacity_mw,
        "installed_capacity_mw",
    )

    revenue = calculate_annual_revenue(
        annual_energy_yield_kwh=annual_energy,
        electricity_tariff_inr_per_kwh=(
            electricity_tariff_inr_per_kwh
        ),
    )

    project_cost = calculate_project_cost(
        installed_capacity_mw=capacity,
        cost_per_mw=cost_per_mw,
        additional_installation_percent=(
            additional_installation_percent
        ),
    )

    payback = calculate_payback_period(
        total_project_cost=project_cost,
        annual_revenue=revenue,
    )

    roi = calculate_roi(
        total_project_cost=project_cost,
        annual_revenue=revenue,
    )

    return {
        "annual_energy_yield_kwh": round(
            annual_energy,
            2,
        ),

        "installed_capacity_mw": round(
            capacity,
            2,
        ),

        "electricity_tariff_inr_per_kwh": round(
            float(electricity_tariff_inr_per_kwh),
            4,
        ),

        "cost_per_mw": round(
            float(cost_per_mw),
            2,
        ),

        "additional_installation_percent": round(
            float(additional_installation_percent),
            2,
        ),

        "estimated_annual_revenue": revenue,

        "estimated_project_cost": project_cost,

        "payback_period_years": payback,

        "roi_percent": roi,
    }