from typing import Dict, List


class DeploymentOptimizationService:
    """
    Provides engineering recommendations for deploying
    renewable energy infrastructure based on the
    analyzed site suitability report.
    """

    def optimize(self, report: Dict) -> Dict:
        score = report.get("overall_score", 0)

        site = report.get("site_information", {})
        criteria = report.get("criteria_evaluation", {})
        constraints = report.get("constraints", {})

        strategy = self._deployment_strategy(
            score,
            site.get("energy_type"),
        )

        engineering = self._engineering_configuration(
            site,
            criteria,
        )

        land = self._land_assessment(criteria)

        risk = self._risk_assessment(
            criteria,
            constraints,
        )

        recommendations = self._recommendations(
            site,
            criteria,
            strategy,
            risk,
        )

        return {
            "deployment_strategy": strategy,
            "engineering_configuration": engineering,
            "land_assessment": land,
            "risk_assessment": risk,
            "recommendations": recommendations,
        }

    # --------------------------------------------------

    def _deployment_strategy(
        self,
        score: float,
        energy_type: str,
    ) -> Dict:

        if score >= 85:
            status = "Highly Recommended"
            priority = "High"

        elif score >= 70:
            status = "Recommended"
            priority = "Medium"

        elif score >= 55:
            status = "Conditionally Recommended"
            priority = "Low"

        else:
            status = "Not Recommended"
            priority = "Very Low"

        return {
            "deployment_status": status,
            "priority": priority,
            "recommended_energy": energy_type,
        }

    # --------------------------------------------------

    def _engineering_configuration(
        self,
        site: Dict,
        criteria: Dict,
    ) -> Dict:

        latitude = abs(site.get("latitude", 0))

        solar = criteria.get("solar_irradiance", {}).get("value")
        wind = criteria.get("wind_speed", {}).get("value")

        configuration = {
            "panel_tilt": None,
            "panel_orientation": None,
            "row_spacing": None,
            "hub_height": None,
            "turbine_spacing": None,
        }

        if solar is not None:
            configuration["panel_tilt"] = round(latitude, 1)
            configuration["panel_orientation"] = "South"
            configuration["row_spacing"] = "4.5 m"

        if wind is not None:

            if wind >= 7:
                configuration["hub_height"] = "120 m"

            elif wind >= 6:
                configuration["hub_height"] = "100 m"

            else:
                configuration["hub_height"] = "Not Recommended"

            configuration["turbine_spacing"] = "7D × 5D"

        return configuration

    # --------------------------------------------------

    def _land_assessment(
        self,
        criteria: Dict,
    ) -> Dict:

        slope = criteria.get("slope", {}).get("value")

        if slope is None:
            terrain = "Unknown"

        elif slope <= 5:
            terrain = "Excellent"

        elif slope <= 10:
            terrain = "Good"

        elif slope <= 15:
            terrain = "Moderate"

        else:
            terrain = "Challenging"

        if terrain in ["Excellent", "Good"]:
            complexity = "Low"

        elif terrain == "Moderate":
            complexity = "Medium"

        else:
            complexity = "High"

        return {
            "terrain": terrain,
            "installation_complexity": complexity,
        }

    # --------------------------------------------------

    def _risk_assessment(
        self,
        criteria: Dict,
        constraints: Dict,
    ) -> Dict:

        slope = criteria.get("slope", {}).get("value", 0)

        terrain_risk = "Low"

        if slope > 15:
            terrain_risk = "High"

        elif slope > 10:
            terrain_risk = "Medium"

        climate_risk = "Low"

        if criteria.get("solar_irradiance", {}).get("status") == "Fail":
            climate_risk = "Medium"

        if criteria.get("wind_speed", {}).get("status") == "Fail":
            climate_risk = "Medium"

        return {
            "terrain_risk": terrain_risk,
            "climate_risk": climate_risk,
            "protected_area": constraints.get("protected_area"),
            "water_body": constraints.get("water_body"),
        }

    # --------------------------------------------------

    def _recommendations(
        self,
        site: Dict,
        criteria: Dict,
        strategy: Dict,
        risk: Dict,
    ) -> List[str]:

        recommendations = []

        if criteria["solar_irradiance"]["status"] == "Pass":
            recommendations.append(
                "Suitable solar resource for utility-scale deployment."
            )

        if criteria["wind_speed"]["status"] == "Pass":
            recommendations.append(
                "Wind resource supports commercial turbine installation."
            )

        if criteria["slope"]["status"] == "Pass":
            recommendations.append(
                "Terrain is appropriate for construction activities."
            )

        if risk["terrain_risk"] != "Low":
            recommendations.append(
                "Detailed geotechnical investigation is recommended."
            )

        if strategy["deployment_status"] == "Highly Recommended":
            recommendations.append(
                "Proceed with detailed engineering design."
            )

        elif strategy["deployment_status"] == "Recommended":
            recommendations.append(
                "Proceed after detailed feasibility assessment."
            )

        else:
            recommendations.append(
                "Additional site investigation is advised."
            )

        return recommendations


deployment_optimization_service = DeploymentOptimizationService()