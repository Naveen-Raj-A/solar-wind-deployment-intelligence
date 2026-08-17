from typing import Dict

from app.services.prediction_service import prediction_service
from app.services.analysis_report_service import analysis_report_service
from app.services.deployment_optimization_service import (
    deployment_optimization_service,
)
from app.services.forecasting_service import (
    forecasting_service,
)
from app.services.investment_recommendation_service import (
    investment_recommendation_service,
)


class DeploymentService:
    """
    Coordinates the complete renewable energy deployment workflow.

    Workflow

        User Input
            ↓
        Prediction
            ↓
        Analysis Report
            ↓
        Deployment Optimization
            ↓
        Forecasting
            ↓
        Investment Recommendation
            ↓
        Return Results
    """

    def analyze_solar(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict:

        # Step 1: Site Prediction
        prediction = prediction_service.predict_solar(
            latitude,
            longitude,
        )

        # Step 2: Suitability Report
        report = analysis_report_service.build(
            prediction
        )

        # Step 3: Deployment Optimization
        optimization = deployment_optimization_service.optimize(
            report
        )

        # Step 4: Energy Forecast
        forecast = forecasting_service.forecast(
            report,
            optimization,
        )

        # Step 5: Investment Recommendation
        investment = investment_recommendation_service.recommend(
            report,
            optimization,
            forecast,
        )

        return {
            "prediction": prediction,
            "report": report,
            "optimization": optimization,
            "forecast": forecast,
            "investment": investment,
        }

    def analyze_wind(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict:

        # Step 1: Site Prediction
        prediction = prediction_service.predict_wind(
            latitude,
            longitude,
        )

        # Step 2: Suitability Report
        report = analysis_report_service.build(
            prediction
        )

        # Step 3: Deployment Optimization
        optimization = deployment_optimization_service.optimize(
            report
        )

        # Step 4: Energy Forecast
        forecast = forecasting_service.forecast(
            report,
            optimization,
        )

        # Step 5: Investment Recommendation
        investment = investment_recommendation_service.recommend(
            report,
            optimization,
            forecast,
        )

        return {
            "prediction": prediction,
            "report": report,
            "optimization": optimization,
            "forecast": forecast,
            "investment": investment,
        }


deployment_service = DeploymentService()