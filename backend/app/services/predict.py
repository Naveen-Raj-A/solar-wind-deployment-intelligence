from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.prediction_service import prediction_service
from app.services.analysis_report_service import analysis_report_service

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)


class PredictionRequest(BaseModel):
    latitude: float
    longitude: float


@router.post("/solar")
def predict_solar(request: PredictionRequest):
    try:
        prediction = prediction_service.predict_solar(
            request.latitude,
            request.longitude,
        )

        return analysis_report_service.build(prediction)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/wind")
def predict_wind(request: PredictionRequest):
    try:
        prediction = prediction_service.predict_wind(
            request.latitude,
            request.longitude,
        )

        return analysis_report_service.build(prediction)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )