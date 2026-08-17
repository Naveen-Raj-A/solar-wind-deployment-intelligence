from typing import Dict


class GlobalWindAtlasClient:
    """
    Client responsible for accessing the Global Wind Atlas dataset.
    """

    def fetch(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict:
        """
        Retrieve wind information.

        Inputs:
            - latitude
            - longitude

        Expected Output:
            Dictionary containing:
                - Wind Speed
                - Wind Direction
                - Wind Power Density

        Possible Errors:
            - Invalid coordinates
            - Dataset unavailable
            - Missing data
        """
        raise NotImplementedError(
            "Global Wind Atlas client not implemented yet."
        )