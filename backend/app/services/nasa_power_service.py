from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

NASA_POWER_DATASET = (
    BASE_DIR
    / "datasets"
    / "nasa_power"
    / "raw"
    / "nasa_power_india_climatology.csv"
)

_dataframe = None


def load_dataset():
    global _dataframe

    if _dataframe is None:
        _dataframe = pd.read_csv(NASA_POWER_DATASET)

    return _dataframe


def get_nasa_power_features(
    latitude: float,
    longitude: float,
):
    """
    Returns the nearest NASA POWER
    feature vector.
    """

    dataframe = load_dataset().copy()

    dataframe["distance"] = (
        (dataframe["latitude"] - latitude) ** 2
        +
        (dataframe["longitude"] - longitude) ** 2
    )

    nearest = dataframe.loc[
        dataframe["distance"].idxmin()
    ]

    return {
        "success": True,
        "solar_irradiance": float(
            nearest["solar_radiation_kwh_m2_day"]
        ),
        "temperature": float(
            nearest["temperature_mean_c"]
        ),
        "humidity": float(
            nearest["relative_humidity_pct"]
        ),
    }