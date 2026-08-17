from typing import Dict


class OSMClient:
    """
    Client responsible for accessing OpenStreetMap data.
    """

    def fetch(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict:
        """
        Retrieve infrastructure information.

        Inputs:
            - latitude
            - longitude

        Expected Output:
            Dictionary containing:
                - Nearest Road Distance
                - Nearby Infrastructure
                - Land Use Information

        Possible Errors:
            - Invalid coordinates
            - Dataset unavailable
            - Missing data
        """
        raise NotImplementedError(
            "OSM client not implemented yet."
        )