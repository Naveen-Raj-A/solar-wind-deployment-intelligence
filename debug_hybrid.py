from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from test_analysis import build_mock_report

client = TestClient(app)

report = build_mock_report(
    13.0827,
    80.2707,
    6.0,
    8.0,
    2.0,
)

print("MOCK SOLAR BEFORE:", report["datasets"]["nasa_power"]["solar_resource"]["solar_radiation_kwh_m2_day"])
print("MOCK WIND BEFORE:", report["datasets"]["wind"]["wind_speed_statistics"]["mean_ms"])

with patch(
    "engine.analysis_service.build_realtime_site_report",
    return_value=report,
):
    response = client.post(
        "/analysis",
        json={
            "latitude": 13.0827,
            "longitude": 80.2707,
            "available_land_area_km2": 10,
            "used_land_area_km2": 2,
        },
    )

print("STATUS:", response.status_code)

data = response.json()

print("ML:", data.get("ml_prediction"))
print("EVALUATION:", data.get("evaluation"))
print("DEPLOYMENT:", data.get("deployment_recommendation"))
print("FEASIBILITY:", data.get("feasibility"))
