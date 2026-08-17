from typing import Dict


def build_terrain_features(
    elevation: float,
    slope: float,
) -> Dict:
    """
    Build terrain-related features from
    SRTM elevation data.
    """

    feature_vector = {
        "elevation": elevation,
        "slope": slope,
    }

    return feature_vector