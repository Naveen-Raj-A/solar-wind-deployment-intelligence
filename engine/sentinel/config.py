"""
Sentinel-2 Configuration
Solar & Wind Deployment Intelligence
"""

import os

# ============================================================
# STAC CONFIGURATION
# ============================================================

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

SENTINEL_COLLECTION = "sentinel-2-l2a"

# ============================================================
# SEARCH PARAMETERS
# ============================================================

SEARCH_OFFSET = 0.05

MAX_CLOUD_COVER = 20

DATE_RANGE = "2025-01-01/2026-12-31"

MAX_RESULTS = 20

# ============================================================
# REQUIRED SENTINEL ASSETS
# ============================================================

REQUIRED_ASSETS = [
    "B04",      # Red
    "B08",      # Near Infrared
    "B11",      # Short Wave Infrared
    "SCL",      # Scene Classification Layer
]

# ============================================================
# OUTPUT DIRECTORIES
# ============================================================

DATASET_DIRECTORY = os.path.join(
    "datasets",
    "sentinel",
)

RAW_DIRECTORY = os.path.join(
    DATASET_DIRECTORY,
    "raw",
)

PROCESSED_DIRECTORY = os.path.join(
    DATASET_DIRECTORY,
    "processed",
)

REPORT_DIRECTORY = os.path.join(
    DATASET_DIRECTORY,
    "reports",
)

# Create folders automatically

os.makedirs(RAW_DIRECTORY, exist_ok=True)
os.makedirs(PROCESSED_DIRECTORY, exist_ok=True)
os.makedirs(REPORT_DIRECTORY, exist_ok=True)