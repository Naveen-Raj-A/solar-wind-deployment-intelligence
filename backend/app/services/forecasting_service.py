from typing import Dict


class ForecastingService:
    """
    Forecasts the expected energy production for the
    recommended renewable energy deployment site.
    """

    def forecast(
        self,
        report: Dict,
        optimization: Dict,
    ) -> Dict:

        energy_type = report["site_information"]["energy_type"]

        if energy_type.lower() == "solar":
            return self._forecast_solar(report, optimization)

        return self._forecast_wind(report, optimization)

    # ----------------------------------------------------------

    def _forecast_solar(
        self,
        report: Dict,
        optimization: Dict,
    ) -> Dict:

        criteria = report["criteria_evaluation"]

        irradiance = criteria["solar_irradiance"]["value"] or 0
        temperature = criteria["temperature"]["value"] or 25

        capacity_factor = min(
            max((irradiance / 6.5) * 100, 10),
            30,
        )

        performance_ratio = max(
            75,
            85 - abs(temperature - 25) * 0.5,
        )

        annual_energy = round(
            irradiance * 1500,
            2,
        )

        return {
            "forecast_type": "Solar",
            "annual_energy_mwh": annual_energy,
            "capacity_factor_percent": round(
                capacity_factor,
                2,
            ),
            "performance_ratio_percent": round(
                performance_ratio,
                2,
            ),
            "summary": "Estimated annual solar energy generation.",
        }

    # ----------------------------------------------------------

    def _forecast_wind(
        self,
        report: Dict,
        optimization: Dict,
    ) -> Dict:

        criteria = report["criteria_evaluation"]

        wind_speed = criteria["wind_speed"]["value"] or 0

        capacity_factor = min(
            max((wind_speed / 8.5) * 100, 10),
            50,
        )

        annual_energy = round(
            wind_speed * 2200,
            2,
        )

        if wind_speed >= 7:
            utilization = "High"

        elif wind_speed >= 6:
            utilization = "Moderate"

        else:
            utilization = "Low"

        return {
            "forecast_type": "Wind",
            "annual_energy_mwh": annual_energy,
            "capacity_factor_percent": round(
                capacity_factor,
                2,
            ),
            "turbine_utilization": utilization,
            "summary": "Estimated annual wind energy generation.",
        }


forecasting_service = ForecastingService()