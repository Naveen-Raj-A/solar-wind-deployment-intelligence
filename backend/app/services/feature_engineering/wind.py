from typing import Dict


def build_wind_features(
    wind_speed: float,
) -> Dict:
    """
    Build the wind feature vector from
    Global Wind Atlas values.
    """

    feature_vector = {
        "wind_speed": wind_speed,
    }

    return feature_vector