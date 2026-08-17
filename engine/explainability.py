"""
Model Explainability Module

Provides feature-importance based explanations for the selected
Random Forest solar-radiation model.

The model itself is loaded through engine.ml_inference.load_model(),
which is cached with lru_cache so it is loaded only once.
"""

from __future__ import annotations

from typing import Any

from engine.ml_inference import FEATURE_ORDER, load_model, validate_features


def get_feature_importance() -> list[dict[str, Any]]:
    """
    Return Random Forest feature importance in descending order.
    """
    model = load_model()

    if not hasattr(model, "feature_importances_"):
        raise RuntimeError(
            "The selected model does not expose feature_importances_."
        )

    importances = model.feature_importances_

    if len(importances) != len(FEATURE_ORDER):
        raise RuntimeError(
            "Feature-importance count does not match the training features."
        )

    results = [
        {
            "feature": feature,
            "importance": round(float(importance), 6),
            "importance_percent": round(float(importance) * 100, 2),
        }
        for feature, importance in zip(FEATURE_ORDER, importances)
    ]

    results.sort(key=lambda item: item["importance"], reverse=True)

    return results


def predict_solar_with_explanation(
    features: dict,
) -> dict[str, Any]:
    """
    Return the prediction, feature importance and a concise explanation.
    """
    validate_features(features)

    model = load_model()

    importance = get_feature_importance()

    values = [
        float(features[feature])
        for feature in FEATURE_ORDER
    ]

    prediction = float(
        model.predict([values])[0]
    )

    top_features = importance[:3]

    summary_features = ", ".join(
        item["feature"]
        for item in top_features
    )

    return {
        "prediction": round(max(0.0, prediction), 3),
        "feature_importance": importance,
        "explanation": {
            "prediction": round(max(0.0, prediction), 3),
            "most_influential_features": [
                {
                    "feature": item["feature"],
                    "importance_percent": item["importance_percent"],
                }
                for item in top_features
            ],
            "summary": (
                "The prediction is primarily influenced by "
                f"{summary_features} according to the "
                "Random Forest feature-importance scores."
            ),
        },
    }