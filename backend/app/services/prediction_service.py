
from pathlib import Path
import joblib
from typing import Dict

from app.services.feature_engineering.feature_builder import build_feature_vector

MODEL_DIR = Path(__file__).resolve().parents[3] / "models"

SOLAR_MODEL_PATH = MODEL_DIR / "solar_model.pkl"
WIND_MODEL_PATH = MODEL_DIR / "wind_model.pkl"


class PredictionService:

    def __init__(self):
        self.solar_model = self._load(SOLAR_MODEL_PATH)
        self.wind_model = self._load(WIND_MODEL_PATH)

    @staticmethod
    def _load(path: Path):
        if not path.exists():
            return None
        return joblib.load(path)

    @staticmethod
    def _classify(score: float) -> str:
        if score >= 80:
            return "Highly Suitable"
        if score >= 60:
            return "Moderately Suitable"
        if score >= 40:
            return "Marginally Suitable"
        return "Not Suitable"

    def predict_solar(self, latitude: float, longitude: float) -> Dict:
        bundle = build_feature_vector(latitude, longitude)
        features = list(bundle["features"].values())

        if self.solar_model is None:
            score = 0.0
        else:
            score = float(self.solar_model.predict([features])[0])

        return {
            "energy_type": "solar",
            "latitude": latitude,
            "longitude": longitude,
            "score": score,
            "classification": self._classify(score),
            "raw": bundle["raw"],
            "features": bundle["features"],
        }

    def predict_wind(self, latitude: float, longitude: float) -> Dict:
        bundle = build_feature_vector(latitude, longitude)
        features = list(bundle["features"].values())

        if self.wind_model is None:
            score = 0.0
        else:
            score = float(self.wind_model.predict([features])[0])

        return {
            "energy_type": "wind",
            "latitude": latitude,
            "longitude": longitude,
            "score": score,
            "classification": self._classify(score),
            "raw": bundle["raw"],
            "features": bundle["features"],
        }


prediction_service = PredictionService()
