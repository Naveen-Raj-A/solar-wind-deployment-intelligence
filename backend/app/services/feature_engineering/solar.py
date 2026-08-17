from typing import Dict


def build_solar_features(
    solar_irradiance: float,
    temperature: float,
    humidity: float,
) -> Dict:
    """
    Build the solar feature vector from
    NASA POWER dataset values.
    """

    feature_vector = {
        "solar_irradiance": solar_irradiance,
        "temperature": temperature,
        "humidity": humidity,
    }

    return feature_vector