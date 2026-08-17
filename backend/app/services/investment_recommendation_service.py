from typing import Dict


class InvestmentRecommendationService:
    """
    Performs a basic financial analysis for the
    recommended renewable energy deployment.
    """

    def recommend(
        self,
        report: Dict,
        optimization: Dict,
        forecast: Dict,
    ) -> Dict:

        energy = report["site_information"]["energy_type"].lower()

        annual_energy = forecast.get(
            "annual_energy_mwh",
            0,
        )

        if energy == "solar":
            capex = 50000000
            opex = 1000000
            price = 4500

        else:
            capex = 80000000
            opex = 1500000
            price = 5500

        annual_revenue = annual_energy * price

        annual_profit = annual_revenue - opex

        if annual_profit > 0:
            payback = round(
                capex / annual_profit,
                2,
            )
        else:
            payback = None

        if payback is None:
            recommendation = "Not Financially Viable"

        elif payback <= 8:
            recommendation = "Highly Attractive"

        elif payback <= 12:
            recommendation = "Recommended"

        else:
            recommendation = "Requires Detailed Financial Assessment"

        roi = (
            round(
                (annual_profit / capex) * 100,
                2,
            )
            if annual_profit > 0
            else 0
        )

        return {

            "financial_summary": {

                "estimated_capex_inr": capex,

                "estimated_opex_inr_per_year": opex,

                "estimated_annual_revenue_inr": round(
                    annual_revenue,
                    2,
                ),

                "estimated_annual_profit_inr": round(
                    annual_profit,
                    2,
                ),

                "estimated_payback_period_years": payback,

                "estimated_roi_percent": roi,

                "investment_recommendation": recommendation,

            }

        }


investment_recommendation_service = InvestmentRecommendationService()