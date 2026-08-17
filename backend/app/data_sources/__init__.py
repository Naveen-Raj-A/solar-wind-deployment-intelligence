from typing import Dict


class NasaPowerClient:
    """
    Client responsible for accessing the NASA POWER dataset.
    """

    def fetch(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict:
        """
        Retrieve NASA POWER data.

        Inputs:
            - latitude
            - longitude

        Expected Output:
            Dictionary containing NASA POWER weather data.

        Possible Errors:
            - Invalid coordinates
            - Network/API failure
            - Missing data
        """
        raise NotImplementedError("NASA POWER client not implemented yet.")