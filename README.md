# Solar & Wind Deployment Intelligence

> AI-assisted geospatial platform for identifying and evaluating
> suitable renewable energy deployment sites using multi-source spatial
> and climatic datasets.

## Overview

Solar & Wind Deployment Intelligence is a full-stack decision-support
platform that combines multiple public geospatial and climate datasets
into a unified analysis pipeline. It helps evaluate locations for
renewable energy deployment by analyzing climate, wind resources,
terrain, vegetation, and surrounding infrastructure.

## Features

-   NASA POWER climate analysis
-   Global Wind Atlas wind resource analysis
-   SRTM elevation and slope analysis
-   Sentinel-2 vegetation and moisture indices (NDVI/NDMI)
-   OpenStreetMap infrastructure analysis
-   Unified scoring engine
-   Detailed report generation
-   FastAPI backend
-   React + Vite frontend
-   Docker support

## Data Sources

  Source              Purpose
  ------------------- ----------------------------------
  NASA POWER          Solar and climate parameters
  Global Wind Atlas   Wind speed
  SRTM                Elevation and slope
  Sentinel-2          Vegetation and land analysis
  OpenStreetMap       Roads, buildings, infrastructure

## Technology Stack

### Backend

-   Python
-   FastAPI
-   SQLite
-   Rasterio
-   GeoPandas
-   Shapely
-   NumPy
-   Pandas

### Frontend

-   React
-   Vite
-   JavaScript
-   HTML/CSS

### DevOps

-   Docker
-   Git
-   GitHub

## Project Structure

``` text
solar-wind-deployment-intelligence/
│
├── backend/
├── engine/
│   ├── osm/
│   ├── sentinel/
│   ├── scoring.py
│   ├── report_generator.py
│   └── dataset_runner.py
├── frontend/
├── docs/
├── docker/
├── datasets/
├── README.md
├── requirements.txt
└── docker-compose.yml
```

## Analysis Pipeline

``` text
Input Location
      │
      ▼
NASA POWER
      │
      ▼
Global Wind Atlas
      │
      ▼
SRTM
      │
      ▼
Sentinel-2
      │
      ▼
OpenStreetMap
      │
      ▼
Scoring Engine
      │
      ▼
Final Report
```

## Installation

### Clone

``` bash
git clone https://github.com/Naveen-Raj-A/solar-wind-deployment-intelligence.git
cd solar-wind-deployment-intelligence
```

### Python

``` bash
pip install -r requirements.txt
```

### Frontend

``` bash
cd frontend
npm install
```

### Backend

``` bash
cd backend
pip install -r requirements.txt
```

## Running

### Backend

``` bash
uvicorn app.main:app --reload
```

### Frontend

``` bash
npm run dev
```

### Analysis Engine

``` bash
python start_engine.py
```

## Datasets

Large datasets are intentionally excluded from Git because several files
exceed GitHub's size limits.

Create the following structure before running analyses:

``` text
datasets/
    nasa_power/
    global_wind_atlas/
    sentinel/
    srtm/
    openstreetmap/
```

Typical data includes:

-   NASA POWER
-   Global Wind Atlas GeoTIFF
-   Sentinel-2 imagery
-   SRTM tiles
-   OpenStreetMap PBF extracts

## Outputs

The engine generates:

-   Climate summaries
-   Wind summaries
-   Terrain summaries
-   Vegetation summaries
-   Infrastructure summaries
-   Site suitability scores
-   JSON reports

## API

The FastAPI backend exposes endpoints for:

-   Projects
-   Sites
-   Predictions
-   Wind analysis
-   Dashboard

## Development Roadmap

-   [x] NASA POWER engine
-   [x] Wind analysis
-   [x] SRTM engine
-   [x] Sentinel engine
-   [x] OpenStreetMap engine
-   [x] Unified scoring
-   [ ] Interactive GIS visualization
-   [ ] Authentication
-   [ ] User management
-   [ ] Cloud deployment
-   [ ] ML-based suitability prediction

## License

This project is intended for educational, research, and portfolio
purposes. Update this section with your preferred open-source license if
you plan to distribute it publicly.

## Author

Developed by **Monesh**

------------------------------------------------------------------------

If you use this project in research or demonstrations, please cite the
repository and acknowledge the original public datasets used.
