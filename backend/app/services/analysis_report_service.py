from typing import Dict, List


class AnalysisReportService:
    """
    Builds a detailed suitability report from the prediction result.
    """

    @staticmethod
    def _status(value, minimum):
        if value is None:
            return "Unknown"
        return "Pass" if value >= minimum else "Fail"

    @staticmethod
    def _remarks(features: Dict, classification: str) -> List[str]:
        remarks = []

        solar = features.get("solar_irradiance")
        wind = features.get("wind_speed")
        slope = features.get("slope")

        if solar is not None:
            if solar >= 5:
                remarks.append("High solar resource available.")
            else:
                remarks.append("Solar resource is below the preferred threshold.")

        if wind is not None:
            if wind >= 6:
                remarks.append("Good wind potential.")
            else:
                remarks.append("Wind potential is limited.")

        if slope is not None:
            if slope <= 10:
                remarks.append("Terrain is suitable for installation.")
            else:
                remarks.append("Terrain is relatively steep.")

        remarks.append(f"Overall classification: {classification}")

        return remarks

    @classmethod
    def build(cls, prediction: Dict) -> Dict:

        features = prediction.get("features", {})

        return {
            "site_information": {
                "latitude": prediction["latitude"],
                "longitude": prediction["longitude"],
                "energy_type": prediction["energy_type"],
            },

            "overall_score": round(prediction["score"], 2),

            "recommendation": prediction["classification"],

            "criteria_evaluation": {

                "solar_irradiance": {
                    "value": features.get("solar_irradiance"),
                    "status": cls._status(
                        features.get("solar_irradiance"),
                        5,
                    ),
                },

                "wind_speed": {
                    "value": features.get("wind_speed"),
                    "status": cls._status(
                        features.get("wind_speed"),
                        6,
                    ),
                },

                "slope": {
                    "value": features.get("slope"),
                    "status": (
                        "Pass"
                        if features.get("slope") is not None
                        and features.get("slope") <= 10
                        else "Fail"
                    ),
                },

                "temperature": {
                    "value": features.get("temperature"),
                },

                "humidity": {
                    "value": features.get("humidity"),
                },

                "elevation": {
                    "value": features.get("elevation"),
                },

            },

            "constraints": {
                "protected_area": False,
                "water_body": False,
            },

            "remarks": cls._remarks(
                features,
                prediction["classification"],
            ),

            "raw_dataset": prediction.get("raw"),
        }


analysis_report_service = AnalysisReportService()