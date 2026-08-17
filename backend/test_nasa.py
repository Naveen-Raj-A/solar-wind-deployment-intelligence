from app.services.nasa_power_service import (
    get_nasa_power_features,
)

result = get_nasa_power_features(
    10.7905,
    78.7047,
)

print(result)