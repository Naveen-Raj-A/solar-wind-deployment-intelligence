# Field Mapping Document

This document defines the data contract between the frontend and backend APIs.
It specifies the expected fields, types, and formats for request and response payloads.

## API Endpoints

### 1. Analyze Location
**Endpoint:** `POST /deployment/analyze`
**Description:** Analyze a location for renewable energy suitability

#### Request Body
```json
{
  "location": {
    "latitude": "number (required)",
    "longitude": "number (required)",
    "district": "string (optional)",
    "address": "string (optional)"
  },
  "analysisTypes": [
    "nasa_power",
    "wind",
    "terrain", 
    "sentinel",
    "osm"
  ],
  "options": {
    "radius": "number (default: 1000)",
    "year": "number (default: current year)",
    "month": "number (1-12, optional)"
  }
}
```

#### Response Body
```json
{
  "success": "boolean",
  "data": {
    "location": {
      "latitude": "number",
      "longitude": "number",
      "district": "string",
      "address": "string"
    },
    "timestamp": "string (ISO 8601)",
    "analysis": {
      "nasa_power": {
        "solar_irradiance": "number (kWh/m²/day)",
        "temperature": "number (°C)",
        "humidity": "number (%)",
        "wind_speed": "number (m/s)",
        "cloud_cover": "number (%)",
        "solar_suitability": "number (0-100)"
      },
      "wind": {
        "mean_wind_speed": "number (m/s)",
        "max_wind_speed": "number (m/s)",
        "wind_class": "string (1-7)",
        "power_density": "number (W/m²)",
        "elevation": "number (m)",
        "wind_suitability": "number (0-100)"
      },
      "terrain": {
        "elevation": "number (m)",
        "slope": "number (degrees)",
        "aspect": "number (degrees)",
        "terrain_suitability": "number (0-100)"
      },
      "sentinel": {
        "ndvi": "number (-1 to 1)",
        "ndmi": "number (-1 to 1)",
        "vegetation_index": "number (0-100)",
        "water_bodies": "number (hectares)",
        "built_up_area": "number (hectares)"
      },
      "osm": {
        "nearest_road": "string (road type)",
        "distance_to_road": "number (meters)",
        "buildings_count": "integer",
        "accessibility_score": "number (0-100)",
        "infrastructure_density": "number (per km²)"
      }
    },
    "scores": {
      "overall": "number (0-100)",
      "solar": "number (0-100)",
      "wind": "number (0-100)",
      "combined": "number (0-100)",
      "classification": "string (Poor/Fair/Good/Excellent)",
      "recommendation": "string"
    }
  },
  "error": "string (present if success=false)"
}
```

### 2. Get Projects
**Endpoint:** `GET /projects`
**Description:** Retrieve list of projects

#### Response Body
```json
{
  "success": "boolean",
  "data": [
    {
      "id": "string (UUID)",
      "name": "string",
      "description": "string",
      "location": {
        "latitude": "number",
        "longitude": "number"
      },
      "created_at": "string (ISO 8601)",
      "updated_at": "string (ISO 8601)",
      "status": "string (active/completed/archived)",
      "analysis_count": "integer"
    }
  ],
  "error": "string (present if success=false)"
}
```

### 3. Get Sites
**Endpoint:** `GET /sites?project_id=:projectId`
**Description:** Retrieve sites for a project

#### Response Body
```json
{
  "success": "boolean",
  "data": [
    {
      "id": "string (UUID)",
      "project_id": "string (UUID)",
      "name": "string",
      "description": "string",
      "location": {
        "latitude": "number",
        "longitude": "number"
      },
      "created_at": "string (ISO 8601)",
      "status": "string (pending/analyzed/completed)",
      "latest_analysis": {
        "timestamp": "string (ISO 8601)",
        "scores": {
          "overall": "number (0-100)"
        }
      }
    }
  ],
  "error": "string (present if success=false)"
}
```

### 4. Save Deployment Recommendation
**Endpoint:** `POST /deployment/recommendation`
**Description:** Save a deployment recommendation for a site

#### Request Body
```json
{
  "site_id": "string (UUID)",
  "recommendation": {
    "technology": "string (solar/wind/hybrid)",
    "capacity": "number (MW)",
    "estimated_production": "number (MWh/year)",
    "investment_cost": "number (USD)",
    "roi_period": "number (years)",
    "confidence": "number (0-100)"
  }
}
```

#### Response Body
```json
{
  "success": "boolean",
  "data": {
    "id": "string (UUID)",
    "site_id": "string (UUID)",
    "created_at": "string (ISO 8601)"
  },
  "error": "string (present if success=false)"
}
```

## Data Types Reference

### Coordinates
- Latitude: Number between -90 and 90
- Longitude: Number between -180 and 180

### Percentages
- Values between 0 and 100 unless otherwise specified

### Scores
- All suitability scores: 0-100 scale
- Higher is better

### Timestamps
- ISO 8601 format: `YYYY-MM-DDTHH:mm:ss.sssZ`

### Units Reference
- Solar irradiance: kWh/m²/day
- Temperature: Celsius (°C)
- Wind speed: meters/second (m/s)
- Elevation: meters (m)
- Distance: meters (m) or kilometers (km)
- Area: hectares (ha) or square kilometers (km²)
- Power: watts (W), kilowatts (kW), megawatts (MW)
- Energy: watt-hours (Wh), kilowatt-hours (kWh), megawatt-hours (MWh)

## Error Response Format
All API errors follow this format:
```json
{
  "success": false,
  "error": "string (human-readable error message)",
  "error_code": "string (optional machine-readable code)",
  "details": "object (optional additional debug information)"
}
```

## Versioning
- API version is not currently versioned in the URL
- Breaking changes will be communicated via release notes
- Deprecated fields will be marked as such in this document

## Notes
1. All string fields should be substituted from this document.
2. Future versions may add additional fields - clients should ignore unknown fields.
3. Null values may be returned for optional fields when data is not available.
4. Numeric values may be returned as strings in JSON if they exceed JavaScript's safe integer range.