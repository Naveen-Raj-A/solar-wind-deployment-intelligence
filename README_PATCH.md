# Dataset-first pipeline patch

Replace:

- `engine/analysis_service.py`
- your FastAPI `main.py`

The new API accepts either:

```json
{
  "location": "Krishnagiri",
  "available_land_area_km2": 5
}
```

or:

```json
{
  "latitude": 12.5152,
  "longitude": 78.0094,
  "available_land_area_km2": 5
}
```

The service now calls:

`engine.dataset_runner.run_all_datasets()`

instead of `engine.realtime_pipeline.build_realtime_site_report()`.

The dataset runner executes NASA POWER, Global Wind Atlas, SRTM,
Sentinel-2 and OpenStreetMap using the shared `SiteInformation` object.

Outputs are written to:

`reports/<location>/deployment_report.json`

and, when the PDF generator is available:

`reports/<location>/deployment_report.pdf`.

## Important

Make sure the active `engine/dataset_runner.py` is the 5-dataset version
that imports:

- `notebooks.analyze_nasa_power_data`
- `notebooks.analyze_wind_data`
- `notebooks.analyze_srtm_data`
- `engine.sentinel`
- `engine.osm.analyzer`

The runner's `run_all_datasets()` function is the expected integration point.
