"""
Unified Analysis Service
------------------------
Dataset-first orchestration for Solar-Wind Deployment Intelligence.

Flow:
    SiteInformation
        -> local dataset_runner (NASA POWER, Wind Atlas, SRTM,
           Sentinel-2, OpenStreetMap)
        -> unified dataset report
        -> scoring
        -> deployment optimization
        -> technical feasibility
        -> annual energy yield
        -> financial analysis
        -> final recommendation
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from engine.dataset_runner import run_all_datasets
from engine.site_information import (
    SiteInformation,
    create_site_information_from_coordinates,
)
from engine.scoring import calculate_deployment_score
from engine.optimization import optimize_site
from engine.feasibility import evaluate_hard_constraints
from engine.energy_yield import estimate_energy_yield
from engine.financial_analysis import calculate_financial_analysis

try:
    from engine.pdf_report_generator import generate_pdf_report
except Exception:
    generate_pdf_report = None


PROJECT_NAME = "Solar Wind Deployment Intelligence"
REPORTS_DIRECTORY = Path("reports")


def build_realtime_site_report(
    *,
    latitude: float,
    longitude: float,
    available_land_area_km2: float,
    used_land_area_km2: float = 0.0,
    nasa_days: int = 30,
    osm_radius_m: int = 5000,
    sentinel_radius_m: int = 500,
    sentinel_days: int = 30,
    require_sentinel: bool = False,
    requested_location: str | None = None,
    resolved_location: str | None = None,
    country: str | None = None,
    state: str | None = None,
    source: str = "Manual",
    save_output: bool = True,
    display_output: bool = True,
) -> dict[str, Any]:
    """Build the unified site report from the local dataset engine.

    The function name is retained for compatibility with the analysis
    validation tests. It does not call an external realtime API: all resource
    data comes from the project's local dataset_runner.
    """
    site = create_site_information_from_coordinates(
        latitude=float(latitude),
        longitude=float(longitude),
    )

    site = SiteInformation(
        requested_location=(
            requested_location.strip()
            if requested_location
            else site.requested_location
        ),
        resolved_location=(
            resolved_location
            if resolved_location
            else site.resolved_location
        ),
        latitude=site.latitude,
        longitude=site.longitude,
        country=country if country else site.country,
        state=state if state else site.state,
        source=source,
    )

    dataset_results = run_all_datasets(
        site=site,
        save_output=save_output,
        display_output=display_output,
    )

    land_reserve_percent = round(
        max(0.0, available_land_area_km2 - used_land_area_km2)
        / available_land_area_km2
        * 100.0,
        2,
    )

    return {
        "project": PROJECT_NAME,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "site_information": {
            "requested_location": site.requested_location,
            "resolved_location": site.resolved_location,
            "latitude": site.latitude,
            "longitude": site.longitude,
            "country": site.country,
            "state": site.state,
            "source": site.source,
            "available_land_area_km2": available_land_area_km2,
            "used_land_area_km2": used_land_area_km2,
            "land_reserve_percent": land_reserve_percent,
        },
        "datasets": dataset_results,
        "runtime_metadata": {
            "data_source": "local_dataset_runner",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "sentinel_status": (
                "SUCCESS"
                if isinstance(dataset_results.get("sentinel"), dict)
                and dataset_results["sentinel"].get("status") != "failed"
                else "FAILED"
            ),
        },
    }


class AnalysisService:
    """Orchestrate the complete local-dataset deployment workflow."""

    def analyze(
        self,
        *,
        latitude: float,
        longitude: float,
        available_land_area_km2: float,
        used_land_area_km2: float = 0.0,
        nasa_days: int = 30,
        osm_radius_m: int = 5000,
        sentinel_radius_m: int = 500,
        sentinel_days: int = 30,
        require_sentinel: bool = False,
        installed_capacity_mw: float | None = None,
        capacity_factor: float | None = None,
        solar_capacity_factor: float | None = None,
        wind_capacity_factor: float | None = None,
        solar_capacity_share: float = 0.50,
        system_efficiency: float = 0.95,
        operational_loss: float = 0.05,
        electricity_tariff_inr_per_kwh: float = 5.0,
        cost_per_mw: float = 50_00_000.0,
        additional_installation_percent: float = 0.0,
        requested_location: str | None = None,
        resolved_location: str | None = None,
        country: str | None = None,
        state: str | None = None,
        source: str = "Manual",
        save_output: bool = True,
        display_output: bool = True,
    ) -> dict[str, Any]:
        self._validate_inputs(
            latitude=latitude,
            longitude=longitude,
            available_land_area_km2=available_land_area_km2,
            used_land_area_km2=used_land_area_km2,
            nasa_days=nasa_days,
            osm_radius_m=osm_radius_m,
            sentinel_radius_m=sentinel_radius_m,
            sentinel_days=sentinel_days,
            installed_capacity_mw=installed_capacity_mw,
            capacity_factor=capacity_factor,
            solar_capacity_factor=solar_capacity_factor,
            wind_capacity_factor=wind_capacity_factor,
            solar_capacity_share=solar_capacity_share,
            system_efficiency=system_efficiency,
            operational_loss=operational_loss,
            electricity_tariff_inr_per_kwh=electricity_tariff_inr_per_kwh,
            cost_per_mw=cost_per_mw,
            additional_installation_percent=additional_installation_percent,
        )

        # Coordinates are already resolved by main.py.  Preserve a supplied
        # location name for report paths and OSM analysis.
        site = create_site_information_from_coordinates(
            latitude=float(latitude),
            longitude=float(longitude),
        )

        site = SiteInformation(
            requested_location=(
                requested_location.strip()
                if requested_location
                else site.requested_location
            ),
            resolved_location=(
                resolved_location
                if resolved_location
                else site.resolved_location
            ),
            latitude=site.latitude,
            longitude=site.longitude,
            country=country if country else site.country,
            state=state if state else site.state,
            source=source,
        )

        if display_output:
            print("\n======================================")
            print("DATASET-FIRST ANALYSIS PIPELINE")
            print("======================================")
            print("Location:", site.requested_location)
            print("Latitude:", site.latitude)
            print("Longitude:", site.longitude)

        # ----------------------------------------------------------
        # STEP 1 — RETRIEVE THE UNIFIED SITE REPORT
        # ----------------------------------------------------------
        site_report = build_realtime_site_report(
            latitude=latitude,
            longitude=longitude,
            available_land_area_km2=available_land_area_km2,
            used_land_area_km2=used_land_area_km2,
            nasa_days=nasa_days,
            osm_radius_m=osm_radius_m,
            sentinel_radius_m=sentinel_radius_m,
            sentinel_days=sentinel_days,
            require_sentinel=require_sentinel,
            requested_location=requested_location,
            resolved_location=resolved_location,
            country=country,
            state=state,
            source=source,
            save_output=save_output,
            display_output=display_output,
        )

        if not isinstance(site_report, dict):
            raise RuntimeError("Site report must be a dictionary.")

        dataset_results = site_report.get("datasets", {})
        if not isinstance(dataset_results, dict):
            raise RuntimeError("Site report contains invalid dataset results.")

        self._validate_core_dataset_results(
            dataset_results,
            require_sentinel=require_sentinel,
        )

        # Keep the resolved site information from the report when available.
        report_site_information = site_report.get("site_information", {})
        if not isinstance(report_site_information, dict):
            report_site_information = {}

        dataset_report = {
            "project": site_report.get("project", PROJECT_NAME),
            "generated_at": site_report.get(
                "generated_at",
                datetime.now().isoformat(timespec="seconds"),
            ),
            "site_information": {
                **report_site_information,
                "requested_location": report_site_information.get(
                    "requested_location", site.requested_location
                ),
                "resolved_location": report_site_information.get(
                    "resolved_location", site.resolved_location
                ),
                "latitude": report_site_information.get(
                    "latitude", site.latitude
                ),
                "longitude": report_site_information.get(
                    "longitude", site.longitude
                ),
                "country": report_site_information.get(
                    "country", site.country
                ),
                "state": report_site_information.get(
                    "state", site.state
                ),
                "source": report_site_information.get(
                    "source", site.source
                ),
                "available_land_area_km2": available_land_area_km2,
                "used_land_area_km2": used_land_area_km2,
                "land_reserve_percent": round(
                    max(
                        0.0,
                        available_land_area_km2 - used_land_area_km2,
                    )
                    / available_land_area_km2
                    * 100.0,
                    2,
                ),
            },
            "datasets": dataset_results,
        }

        # ----------------------------------------------------------
        # STEP 3 — SCORE THE ACTUAL LOCAL DATASET RESULTS
        # ----------------------------------------------------------
        scoring = calculate_deployment_score(dataset_report)

        evaluated_site = {
            **scoring,
            "site_information": dataset_report["site_information"],
            "datasets": dataset_results,
            "land_area_km2": available_land_area_km2,
            "used_land_area_km2": used_land_area_km2,
            "runtime_metadata": {
                "data_source": "local_dataset_runner",
                "generated_at": dataset_report["generated_at"],
            },
        }

        # ----------------------------------------------------------
        # STEP 4 — OPTIMIZE DEPLOYMENT
        # ----------------------------------------------------------
        deployment_plan = optimize_site(evaluated_site)

        capacity_for_yield = (
            float(installed_capacity_mw)
            if installed_capacity_mw is not None
            else float(deployment_plan["recommended_capacity_mw"])
        )

        # ----------------------------------------------------------
        # STEP 5 — TECHNICAL FEASIBILITY
        # ----------------------------------------------------------
        feasibility = evaluate_hard_constraints(
            evaluated_site,
            recommended_capacity_mw=capacity_for_yield,
        )

        # ----------------------------------------------------------
        # STEP 5A — NORMALIZE FEASIBILITY DETAILS FOR THE API
        # ----------------------------------------------------------
        # Keep the original feasibility-engine response intact, but expose
        # a predictable structure that the frontend/API can consume without
        # having to understand the internal constraint implementation.
        passed_constraints = feasibility.get("passed_constraints", [])
        failed_constraints = feasibility.get("failed_constraints", [])

        if not isinstance(passed_constraints, list):
            passed_constraints = []
        if not isinstance(failed_constraints, list):
            failed_constraints = []

        failure_reasons = [
            {
                "name": item.get("name", "unknown"),
                "status": item.get("status", "FAIL"),
                "message": item.get(
                    "message",
                    "Technical feasibility constraint failed.",
                ),
            }
            for item in failed_constraints
            if isinstance(item, dict)
        ]

        feasibility["passed_constraints"] = passed_constraints
        feasibility["failed_constraints"] = failed_constraints
        feasibility["failure_reasons"] = failure_reasons
        feasibility["hard_constraints_passed"] = len(passed_constraints)
        feasibility["hard_constraints_failed"] = len(failed_constraints)
        feasibility["is_feasible"] = (
            feasibility.get("feasibility_status") == "FEASIBLE"
            and len(failed_constraints) == 0
        )
        feasibility["constraint_summary"] = (
            "All mandatory technical constraints passed."
            if not failure_reasons
            else " | ".join(
                f"{item['name']}: {item['message']}"
                for item in failure_reasons
            )
        )

        # ----------------------------------------------------------
        # BUILD A STABLE, FRONTEND-FRIENDLY FEASIBILITY SUMMARY
        # ----------------------------------------------------------
        # Keep the complete constraint objects, but also expose the exact
        # failure reason at the top level.  This is important because the
        # frontend must never have to infer why a site became NOT_FEASIBLE.
        failed_constraints = feasibility.get("failed_constraints", [])
        passed_constraints = feasibility.get("passed_constraints", [])

        if not isinstance(failed_constraints, list):
            failed_constraints = []
        if not isinstance(passed_constraints, list):
            passed_constraints = []

        feasibility["passed_constraints"] = passed_constraints
        feasibility["failed_constraints"] = failed_constraints
        feasibility["hard_constraints_passed"] = len(passed_constraints)
        feasibility["hard_constraints_failed"] = len(failed_constraints)
        feasibility["failure_reasons"] = [
            {
                "name": item.get("name", "unknown"),
                "status": item.get("status", "FAIL"),
                "message": item.get(
                    "message",
                    "Technical feasibility constraint failed.",
                ),
            }
            for item in failed_constraints
            if isinstance(item, dict)
        ]
        feasibility["constraint_summary"] = (
            "All mandatory technical constraints passed."
            if not failed_constraints
            else "One or more mandatory technical constraints failed: "
            + " | ".join(
                str(item.get("message", "Constraint failed."))
                for item in failed_constraints
                if isinstance(item, dict)
            )
        )

        if display_output:
            print("\n===== TECHNICAL FEASIBILITY DETAILS =====")
            print("Status:", feasibility.get("feasibility_status"))
            print("Score:", feasibility.get("feasibility_score"))
            print(
                "Passed constraints:",
                feasibility.get("hard_constraints_passed"),
            )
            print(
                "Failed constraints:",
                feasibility.get("hard_constraints_failed"),
            )

            print("\nPASSED CONSTRAINTS:")
            for item in passed_constraints:
                print(
                    f"  [PASS] {item.get('name', 'unknown')}: "
                    f"{item.get('message', '')}"
                )

            print("\nFAILED CONSTRAINTS:")
            for item in failed_constraints:
                print(
                    f"  [FAIL] {item.get('name', 'unknown')}: "
                    f"{item.get('message', '')}"
                )

            print(
                "\nFeasibility Summary:",
                feasibility.get("constraint_summary"),
            )
            print("==========================================\n")

        # ----------------------------------------------------------
        # STEP 6 — ENERGY YIELD
        # ----------------------------------------------------------
        energy_yield = None

        if feasibility["feasibility_status"] == "FEASIBLE":
            nasa = dataset_results.get("nasa_power", {})
            solar_features = nasa.get("solar_resource", {})

            wind = dataset_results.get("wind", {})
            wind_features = wind.get("wind_speed_statistics", {})

            energy_yield = estimate_energy_yield(
                deployment_plan["recommended_technology"],
                capacity_for_yield,
                solar_irradiance_kwh_m2_day=solar_features.get(
                    "solar_radiation_kwh_m2_day"
                ),
                wind_speed_ms=wind_features.get("mean_ms"),
                capacity_factor=capacity_factor,
                solar_capacity_factor=solar_capacity_factor,
                wind_capacity_factor=wind_capacity_factor,
                solar_capacity_share=solar_capacity_share,
                system_efficiency=system_efficiency,
                operational_loss=operational_loss,
            )

        # ----------------------------------------------------------
        # STEP 7 — FINANCIAL ANALYSIS
        # ----------------------------------------------------------
        financial_analysis = None

        if energy_yield is not None:
            annual_energy_yield_kwh = self._extract_annual_energy_kwh(
                energy_yield
            )

            financial_analysis = calculate_financial_analysis(
                annual_energy_yield_kwh=annual_energy_yield_kwh,
                installed_capacity_mw=capacity_for_yield,
                electricity_tariff_inr_per_kwh=(
                    electricity_tariff_inr_per_kwh
                ),
                cost_per_mw=cost_per_mw,
                additional_installation_percent=(
                    additional_installation_percent
                ),
            )

        # ----------------------------------------------------------
        # STEP 8 — SAVE UNIFIED REPORT
        # ----------------------------------------------------------
        report = {
            "site": {
                "latitude": site.latitude,
                "longitude": site.longitude,
                "available_land_area_km2": available_land_area_km2,
                "used_land_area_km2": used_land_area_km2,
                "land_reserve_percent": dataset_report["site_information"].get(
                    "land_reserve_percent",
                    0.0,
                ),
            },
            **dataset_report,
            "deployment_assessment": scoring,
            "technical_feasibility": feasibility,
            # Convenience fields for API/frontend consumers. These duplicate
            # the normalized feasibility information intentionally so the UI
            # does not have to know the internal engine structure.
            "feasibility_status": feasibility.get("feasibility_status"),
            "feasibility_score": feasibility.get("feasibility_score"),
            "passed_constraints": feasibility.get("passed_constraints", []),
            "failed_constraints": feasibility.get("failed_constraints", []),
            "failure_reasons": feasibility.get("failure_reasons", []),
            "constraint_summary": feasibility.get("constraint_summary", ""),
            "deployment_recommendation": deployment_plan,
            "energy_yield": energy_yield,
            "financial_analysis": financial_analysis,
            "pipeline": {
                "data_source": "LOCAL_DATASET_ENGINE",
                "steps": [
                    "site_details_received",
                    "local_nasa_power_analysis",
                    "local_global_wind_atlas_analysis",
                    "local_srtm_analysis",
                    "local_sentinel_analysis",
                    "local_openstreetmap_analysis",
                    "deployment_score_calculated",
                    "deployment_optimized",
                    "technical_feasibility_validated",
                    "annual_energy_yield_estimated",
                    "financial_analysis_completed",
                    "final_response_generated",
                ],
                "completed": True,
            },
            "status": "success",
        }

        report = self._json_safe(report)

        report_directory = (
            REPORTS_DIRECTORY
            / self._safe_location_name(site.requested_location)
        )

        if save_output:
            report_directory.mkdir(parents=True, exist_ok=True)

            report_json_path = (
                report_directory / "deployment_report.json"
            )

            with report_json_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    report,
                    file,
                    indent=4,
                    ensure_ascii=False,
                    allow_nan=False,
                )

            if generate_pdf_report is not None:
                try:
                    generate_pdf_report(
                        report,
                        report_directory,
                    )
                except Exception as error:
                    if display_output:
                        print(
                            "PDF report warning:",
                            error,
                        )

            report["runtime_metadata"] = {
                "report_json": str(report_json_path),
                "report_directory": str(report_directory),
                "pdf_report": str(
                    report_directory / "deployment_report.pdf"
                )
                if (
                    report_directory
                    / "deployment_report.pdf"
                ).exists()
                else None,
            }

        if display_output:
            print("\n======================================")
            print("FINAL DEPLOYMENT RESULT")
            print("======================================")
            print(
                "Overall Score:",
                scoring.get("overall_score"),
                "/ 100",
            )
            print(
                "Normalized Score:",
                scoring.get("normalized_score"),
                "/ 100",
            )
            print(
                "Recommendation:",
                scoring.get("recommendation"),
            )
            print(
                "Recommended Technology:",
                deployment_plan.get(
                    "recommended_technology"
                ),
            )
            print(
                "Recommended Capacity:",
                deployment_plan.get(
                    "recommended_capacity_mw"
                ),
                "MW",
            )

            # Always print the exact technical failure, if any.
            # This is deliberately based on the feasibility engine result;
            # nothing is inferred or fabricated here.
            print("Technical Feasibility:", feasibility.get("feasibility_status"))
            print(
                "Constraints Passed:",
                len(feasibility.get("passed_constraints", [])),
            )
            print(
                "Constraints Failed:",
                len(feasibility.get("failed_constraints", [])),
            )

            if feasibility.get("failed_constraints"):
                print("FAILED CONSTRAINTS:")
                for failure in feasibility["failed_constraints"]:
                    if isinstance(failure, dict):
                        print(
                            f"  [FAIL] {failure.get('name', 'unknown')}: "
                            f"{failure.get('message', 'No failure message provided.')}"
                        )
            else:
                print("FAILED CONSTRAINTS: None")

        return report

    @staticmethod
    def _validate_core_dataset_results(
        dataset_results: dict[str, Any],
        *,
        require_sentinel: bool,
    ) -> None:
        required = (
            "nasa_power",
            "wind",
            "srtm",
        )

        failures = []

        for name in required:
            result = dataset_results.get(name)

            if not isinstance(result, dict):
                failures.append(
                    f"{name}: no result returned"
                )
                continue

            if result.get("status") == "failed":
                failures.append(
                    f"{name}: {result.get('error', 'unknown error')}"
                )

        sentinel = dataset_results.get("sentinel")

        if require_sentinel and (
            not isinstance(sentinel, dict)
            or sentinel.get("status") == "failed"
        ):
            failures.append(
                "sentinel: Sentinel-2 analysis failed"
            )

        if failures:
            raise RuntimeError(
                "Required local dataset analysis failed: "
                + " | ".join(failures)
            )

    @staticmethod
    def _safe_location_name(value: str) -> str:
        safe = "".join(
            char if char.isalnum() else "_"
            for char in str(value).strip().lower()
        )

        while "__" in safe:
            safe = safe.replace("__", "_")

        return safe.strip("_") or "site"

    @staticmethod
    def _extract_annual_energy_kwh(
        energy_yield: dict[str, Any],
    ) -> float:
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

        total = 0.0

        for technology in ("solar", "wind"):
            component = energy_yield.get(technology, {})
            if isinstance(component, dict):
                total += float(
                    component.get(
                        "annual_energy_yield_kwh",
                        component.get(
                            "annual_energy_kwh",
                            0.0,
                        ),
                    )
                )

        if total > 0:
            return total

        raise ValueError(
            "Energy-yield response does not contain "
            "a recognized annual energy value."
        )

    @classmethod
    def _json_safe(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                str(key): cls._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                cls._json_safe(item)
                for item in value
            ]

        try:
            import numpy as np

            if isinstance(value, np.ndarray):
                return cls._json_safe(
                    value.tolist()
                )

            if isinstance(value, np.bool_):
                return bool(value)

            if isinstance(value, np.integer):
                return int(value)

            if isinstance(value, np.floating):
                if np.isnan(value) or np.isinf(value):
                    return None
                return float(value)
        except ImportError:
            pass

        if isinstance(value, float):
            if value != value:
                return None
            if value in (float("inf"), float("-inf")):
                return None

        return value

    @staticmethod
    def _validate_inputs(
        *,
        latitude: float,
        longitude: float,
        available_land_area_km2: float,
        used_land_area_km2: float,
        nasa_days: int,
        osm_radius_m: int,
        sentinel_radius_m: int,
        sentinel_days: int,
        installed_capacity_mw: float | None,
        capacity_factor: float | None,
        solar_capacity_factor: float | None,
        wind_capacity_factor: float | None,
        solar_capacity_share: float,
        system_efficiency: float,
        operational_loss: float,
        electricity_tariff_inr_per_kwh: float,
        cost_per_mw: float,
        additional_installation_percent: float,
    ) -> None:
        if not -90.0 <= latitude <= 90.0:
            raise ValueError(
                "latitude must be between -90 and 90."
            )

        if not -180.0 <= longitude <= 180.0:
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
                "used_land_area_km2 cannot exceed "
                "available_land_area_km2."
            )

        if not 1 <= nasa_days <= 365:
            raise ValueError(
                "nasa_days must be between 1 and 365."
            )

        if not 100 <= osm_radius_m <= 50000:
            raise ValueError(
                "osm_radius_m must be between 100 and 50000."
            )

        if not 10 <= sentinel_radius_m <= 5000:
            raise ValueError(
                "sentinel_radius_m must be between 10 and 5000."
            )

        if not 1 <= sentinel_days <= 365:
            raise ValueError(
                "sentinel_days must be between 1 and 365."
            )

        if (
            installed_capacity_mw is not None
            and installed_capacity_mw < 0
        ):
            raise ValueError(
                "installed_capacity_mw cannot be negative."
            )

        for name, value in (
            ("capacity_factor", capacity_factor),
            ("solar_capacity_factor", solar_capacity_factor),
            ("wind_capacity_factor", wind_capacity_factor),
        ):
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0 and 1."
                )

        if not 0.0 <= solar_capacity_share <= 1.0:
            raise ValueError(
                "solar_capacity_share must be between 0 and 1."
            )

        if not 0.0 <= system_efficiency <= 1.0:
            raise ValueError(
                "system_efficiency must be between 0 and 1."
            )

        if not 0.0 <= operational_loss <= 1.0:
            raise ValueError(
                "operational_loss must be between 0 and 1."
            )

        if electricity_tariff_inr_per_kwh < 0:
            raise ValueError(
                "electricity_tariff_inr_per_kwh cannot be negative."
            )

        if cost_per_mw < 0:
            raise ValueError(
                "cost_per_mw cannot be negative."
            )

        if additional_installation_percent < 0:
            raise ValueError(
                "additional_installation_percent cannot be negative."
            )


analysis_service = AnalysisService()