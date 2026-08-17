from typing import Dict


def build_infrastructure_features(
    distance_to_road: float,
) -> Dict:
    """
    Build infrastructure-related features
    from OpenStreetMap data.
    """

    feature_vector = {
        "distance_to_road": distance_to_road,
    }

    return feature_vector