REAL DATA FORECASTING PATCH

Purpose:
Replace the claim of "forecasting tested with sample data" with a separate
real-data integration path using NASA POWER historical observations.

Files:
engine/forecasting/real_data_loader.py
engine/forecasting/real_forecasting_service.py
engine/forecasting/real_analysis_integration.py
engine/forecasting/__init__.py
engine/test_real_forecasting.py

Install:
No new package is required if requests is already installed.

Run:
python -m engine.test_real_forecasting

This test performs a real network request to NASA POWER. It is therefore
different from engine.test_forecasting.py, which remains a controlled test.

The real-data forecast is a transparent seasonal historical baseline.
It is NOT presented as a trained ML model.
