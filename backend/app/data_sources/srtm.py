from typing import Dict


class SRTMClient:
    """
    Client responsible for accessing SRTM elevation data.
    """

    def fetch(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict:
        """
        Retrieve terrain information.

        Inputs:
            - latitude
            - longitude

        Expected Output:
            Dictionary containing:
                - Elevation
                - Slope

        Possible Errors:
            - Invalid coordinates
            - Missing raster
            - Processing failure
        """
        raise NotImplementedError(
            "SRTM client not implemented yet."
        )