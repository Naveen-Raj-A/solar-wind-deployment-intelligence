"""
Unified Test Runner

Purpose:
    Run the original local-dataset analysis workflow from one command and,
    after dataset scoring, calculate deployment, energy-yield and financial
    values.

Run:
    python test_runner.py

Input:
    - District/location name
    - OR latitude/longitude

The existing dataset modules remain unchanged.
"""

from __future__ import annotations

from engine.input_handler import get_site_information
from engine.dataset_runner import run_all_datasets
from engine.report_generator import generate_report
from engine.scoring import calculate_deployment_score
from engine.optimization import optimize_site
from engine.feasibility import evaluate_hard_constraints
from engine.energy_yield import estimate_energy_yield
from engine.financial_analysis import calculate_financial_analysis


# ==============================================================
# DEFAULT FINANCIAL ASSUMPTIONS
# ==============================================================

ELECTRICITY_TARIFF_INR_PER_KWH = 5.0
COST_PER_MW = 5_000_000.0
ADDITIONAL_INSTALLATION_PERCENT = 0.0

SYSTEM_EFFICIENCY = 0.95
OPERATIONAL_LOSS = 0.05


def extract_annual_energy_kwh(energy_yield: dict) -> float:
    """Extract annual generation in kWh from the energy-yield result."""

    for key in (
        "annual_energy_yield_kwh",
        "annual_energy_kwh",
        "estimated_annual_energy_kwh",
    ):
        value = energy_yield.get(key)
        if value is not None:
            return float(value)

    for key in (
        "annual_energy_yield_mwh",
        "annual_energy_mwh",
        "estimated_annual_energy_mwh",
    ):
        value = energy_yield.get(key)
        if value is not None:
            return float(value) * 1000.0

    solar = energy_yield.get("solar", {})
    wind = energy_yield.get("wind", {})

    solar_kwh = 0.0
    wind_kwh = 0.0

    if isinstance(solar, dict):
        solar_kwh = float(
            solar.get(
                "annual_energy_yield_kwh",
                solar.get("annual_energy_kwh", 0.0),
            )
        )

    if isinstance(wind, dict):
        wind_kwh = float(
            wind.get(
                "annual_energy_yield_kwh",
                wind.get("annual_energy_kwh", 0.0),
            )
        )

    if solar_kwh > 0 or wind_kwh > 0:
        return solar_kwh + wind_kwh

    raise ValueError(
        "Annual energy value was not found in the energy-yield result."
    )


def run_financial_stage(
    site,
    report,
    scoring,
    *,
    available_land_area_km2: float = 5.0,
):
    """
    Run deployment -> feasibility -> energy yield -> financial analysis.

    Land area is passed explicitly because SiteInformation does not
    allow arbitrary attributes.
    """

    site_information = {
        **report["site_information"],
        "available_land_area_km2": available_land_area_km2,
        "used_land_area_km2": 0.0,
    }

    evaluated_site = {
        **scoring,
        "site_information": site_information,
        "datasets": report["datasets"],
        "land_area_km2": available_land_area_km2,
        "used_land_area_km2": 0.0,
    }

    deployment = optimize_site(evaluated_site)

    capacity_mw = float(
        deployment["recommended_capacity_mw"]
    )

    feasibility = evaluate_hard_constraints(
        evaluated_site,
        recommended_capacity_mw=capacity_mw,
    )

    if feasibility["feasibility_status"] != "FEASIBLE":
        print("\nFINANCIAL ANALYSIS SKIPPED")
        print("Reason: Technical feasibility check failed.")
        return None

    nasa = report["datasets"].get("nasa_power", {})
    solar_resource = nasa.get("solar_resource", {})

    wind = report["datasets"].get("wind", {})
    wind_statistics = wind.get("wind_speed_statistics", {})

    technology = deployment["recommended_technology"]

    energy_yield = estimate_energy_yield(
        technology,
        capacity_mw,
        solar_irradiance_kwh_m2_day=solar_resource.get(
            "solar_radiation_kwh_m2_day"
        ),
        wind_speed_ms=wind_statistics.get("mean_ms"),
        system_efficiency=SYSTEM_EFFICIENCY,
        operational_loss=OPERATIONAL_LOSS,
    )

    annual_energy_kwh = extract_annual_energy_kwh(
        energy_yield
    )

    financial = calculate_financial_analysis(
        annual_energy_yield_kwh=annual_energy_kwh,
        installed_capacity_mw=capacity_mw,
        electricity_tariff_inr_per_kwh=(
            ELECTRICITY_TARIFF_INR_PER_KWH
        ),
        cost_per_mw=COST_PER_MW,
        additional_installation_percent=(
            ADDITIONAL_INSTALLATION_PERCENT
        ),
    )

    print("\n====================================")
    print("ENERGY & FINANCIAL ANALYSIS")
    print("====================================")

    print(
        f"Recommended Technology : "
        f"{technology}"
    )

    print(
        f"Installed Capacity     : "
        f"{capacity_mw:.2f} MW"
    )

    print(
        f"Annual Energy Yield    : "
        f"{annual_energy_kwh:,.2f} kWh"
    )

    print(
        f"Electricity Tariff     : "
        f"₹{ELECTRICITY_TARIFF_INR_PER_KWH:,.2f}/kWh"
    )

    print(
        f"Estimated Annual Revenue: "
        f"₹{financial['estimated_annual_revenue']:,.2f}"
    )

    print(
        f"Estimated Project Cost : "
        f"₹{financial['estimated_project_cost']:,.2f}"
    )

    print(
        f"Payback Period         : "
        f"{financial['payback_period_years']:.2f} years"
    )

    print(
        f"ROI                    : "
        f"{financial['roi_percent']:.2f}%"
    )

    print("------------------------------------")
    print(
        f"Suitability Score      : "
        f"{scoring['normalized_score']:.2f} / 100"
    )
    print(
        f"Recommendation         : "
        f"{scoring['recommendation']}"
    )

    return {
        "deployment": deployment,
        "technical_feasibility": feasibility,
        "energy_yield": energy_yield,
        "financial_analysis": financial,
    }


def main():

    # ----------------------------------------------------------
    # 1. LOCATION INPUT
    # ----------------------------------------------------------

    site = get_site_information()

    # ----------------------------------------------------------
    # 2. RUN ORIGINAL FIVE DATASET PIPELINE
    # ----------------------------------------------------------

    results = run_all_datasets(
        site=site,
        save_output=True,
        display_output=True,
    )

    # ----------------------------------------------------------
    # 3. GENERATE UNIFIED DATASET REPORT
    # ----------------------------------------------------------

    report = generate_report(
        site=site,
        dataset_results=results,
        save_output=True,
        display_output=True,
    )

    # ----------------------------------------------------------
    # 4. CALCULATE SUITABILITY SCORE
    # ----------------------------------------------------------

    score = calculate_deployment_score(report)

    print("\n====================================")
    print("DEPLOYMENT SUITABILITY SCORE")
    print("====================================")

    weights = score["weights"]

    print(
        f"Solar Score      : "
        f"{score['solar_score']:.2f} / {weights['solar']}"
    )

    print(
        f"Wind Score       : "
        f"{score['wind_score']:.2f} / {weights['wind']}"
    )

    print(
        f"Terrain Score    : "
        f"{score['terrain_score']:.2f} / {weights['terrain']}"
    )

    print(
        f"Sentinel Score   : "
        f"{score['sentinel_score']:.2f} / {weights['sentinel']}"
    )

    print(
        f"OSM Score        : "
        f"{score['osm_score']:.2f} / {weights['osm']}"
    )

    print("------------------------------------")

    print(
        f"Overall Score    : "
        f"{score['overall_score']:.2f} / 100"
    )

    print(
        f"Normalized Score : "
        f"{score['normalized_score']:.2f} / 100"
    )

    print("------------------------------------")

    print(
        f"Recommendation   : "
        f"{score['recommendation']}"
    )

    # ----------------------------------------------------------
    # 5. ENERGY + FINANCIAL ANALYSIS
    # ----------------------------------------------------------

    # SiteInformation uses slots and does not allow arbitrary
    # attributes. Land area is therefore passed explicitly.
    available_land_area_km2 = 5.0

    financial_result = run_financial_stage(
        site,
        report,
        score,
        available_land_area_km2=available_land_area_km2,
    )

    # ----------------------------------------------------------
    # 6. FINAL SUMMARY
    # ----------------------------------------------------------

    print("\n====================================")
    print("PIPELINE COMPLETED")
    print("====================================")

    if financial_result:

        financial = financial_result["financial_analysis"]
        deployment = financial_result["deployment"]

        print(
            f"Technology           : "
            f"{deployment['recommended_technology']}"
        )

        print(
            f"Capacity             : "
            f"{deployment['recommended_capacity_mw']:.2f} MW"
        )

        print(
            f"Annual Revenue       : "
            f"₹{financial['estimated_annual_revenue']:,.2f}"
        )

        print(
            f"Project Cost         : "
            f"₹{financial['estimated_project_cost']:,.2f}"
        )

        print(
            f"Payback Period       : "
            f"{financial['payback_period_years']:.2f} years"
        )

        print(
            f"ROI                  : "
            f"{financial['roi_percent']:.2f}%"
        )

        print(
            f"Suitability Score    : "
            f"{score['normalized_score']:.2f}/100"
        )


if __name__ == "__main__":
    main()