from app.services.feature_engineering.feature_builder import build_feature_vector

features = build_feature_vector(
    solar_irradiance=5.8,
    temperature=29,
    humidity=68,
    wind_speed=7.1,
    elevation=126,
    slope=3,
    distance_to_road=480,
)

print("Generated Feature Vector:")
print(features)