import os
import time
import requests
import osmium


# ==================================================
# CONFIGURATION
# ==================================================

OSM_FILE = os.path.join(
    "datasets",
    "openstreetmap",
    "india-latest.osm.pbf",
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

SEARCH_OFFSET = 0.05

POWER_TYPES = {
    "line",
    "minor_line",
    "plant",
    "generator",
    "transformer",
}


# ==================================================
# GEOCODE LOCATION NAME
# ==================================================

def get_location_coordinates(location_name):

    print("\nSearching location...")

    params = {
        "q": f"{location_name}, India",
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "in",
    }

    headers = {
        "User-Agent":
        "solar-wind-deployment-intelligence/1.0"
    }

    try:

        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        results = response.json()

        if not results:

            print("\nERROR: Location not found in India.")

            return None

        location = results[0]

        latitude = float(location["lat"])

        longitude = float(location["lon"])

        display_name = location["display_name"]

        return (
            display_name,
            latitude,
            longitude,
        )

    except requests.RequestException as error:

        print(
            "\nGeocoding request failed:",
            error,
        )

        return None


# ==================================================
# LOCAL OSM HANDLER
# ==================================================

class LocalOSMQueryHandler(osmium.SimpleHandler):

    def __init__(
        self,
        south,
        west,
        north,
        east,
    ):

        super().__init__()

        self.south = south
        self.west = west
        self.north = north
        self.east = east

        self.roads = 0
        self.buildings = 0
        self.substations = 0
        self.power_infrastructure = 0


    # ==================================================
    # CHECK COORDINATES
    # ==================================================

    def is_inside_bounds(
        self,
        latitude,
        longitude,
    ):

        return (
            self.south
            <= latitude
            <= self.north

            and

            self.west
            <= longitude
            <= self.east
        )


    # ==================================================
    # PROCESS NODES
    # ==================================================

    def node(self, node):

        if not node.location.valid():

            return

        latitude = node.location.lat
        longitude = node.location.lon

        if not self.is_inside_bounds(
            latitude,
            longitude,
        ):

            return

        power_type = node.tags.get("power")

        if power_type == "substation":

            self.substations += 1

        elif power_type in POWER_TYPES:

            self.power_infrastructure += 1


    # ==================================================
    # PROCESS WAYS
    # ==================================================

    def way(self, way):

        inside_search_area = False

        for node_reference in way.nodes:

            if not node_reference.location.valid():

                continue

            latitude = node_reference.location.lat
            longitude = node_reference.location.lon

            if self.is_inside_bounds(
                latitude,
                longitude,
            ):

                inside_search_area = True

                break

        if not inside_search_area:

            return


        if "highway" in way.tags:

            self.roads += 1


        if "building" in way.tags:

            self.buildings += 1


        power_type = way.tags.get("power")


        if power_type == "substation":

            self.substations += 1


        elif power_type in POWER_TYPES:

            self.power_infrastructure += 1


# ==================================================
# RUN LOCATION TEST
# ==================================================

def test_location():

    print(
        "\n===== DYNAMIC INDIA OSM LOCATION TEST ====="
    )


    # ==================================================
    # CHECK INDIA DATASET
    # ==================================================

    if not os.path.exists(OSM_FILE):

        print(
            "\nERROR: India OSM dataset not found."
        )

        print(
            "Expected File:",
            OSM_FILE,
        )

        return


    # ==================================================
    # GET USER INPUT
    # ==================================================

    location_name = input(
        "\nEnter location in India: "
    ).strip()


    if not location_name:

        print(
            "\nERROR: Location cannot be empty."
        )

        return


    # ==================================================
    # GEOCODE LOCATION
    # ==================================================

    location_result = get_location_coordinates(
        location_name
    )


    if location_result is None:

        return


    display_name, latitude, longitude = (
        location_result
    )


    print(
        "\n===== LOCATION FOUND ====="
    )


    print(
        "Location:",
        display_name,
    )


    print(
        "Latitude:",
        latitude,
    )


    print(
        "Longitude:",
        longitude,
    )


    # ==================================================
    # CREATE SEARCH BOUNDS
    # ==================================================

    south = latitude - SEARCH_OFFSET

    north = latitude + SEARCH_OFFSET

    west = longitude - SEARCH_OFFSET

    east = longitude + SEARCH_OFFSET


    print(
        "\n===== SEARCH BOUNDS ====="
    )


    print(
        "South:",
        south,
    )


    print(
        "North:",
        north,
    )


    print(
        "West:",
        west,
    )


    print(
        "East:",
        east,
    )


    # ==================================================
    # PROCESS LOCAL INDIA PBF
    # ==================================================

    print(
        "\nSearching India OSM dataset..."
    )


    print(
        "This test may take several minutes."
    )


    start_time = time.time()


    handler = LocalOSMQueryHandler(
        south,
        west,
        north,
        east,
    )


    try:

        handler.apply_file(
            OSM_FILE,
            locations=True,
            idx="flex_mem",
        )


        processing_time = (
            time.time() - start_time
        )


        # ==================================================
        # DISPLAY RESULTS
        # ==================================================

        print(
            "\n===== OSM LOCATION RESULTS ====="
        )


        print(
            "Location:",
            display_name,
        )


        print(
            "\nRoads:",
            handler.roads,
        )


        print(
            "Buildings:",
            handler.buildings,
        )


        print(
            "Substations:",
            handler.substations,
        )


        print(
            "Other Power Infrastructure:",
            handler.power_infrastructure,
        )


        print(
            "\nProcessing Time:",
            round(processing_time, 2),
            "seconds",
        )


        print(
            "\n===== TEST COMPLETED SUCCESSFULLY ====="
        )


    except Exception as error:

        print(
            "\nLocal OSM query test failed."
        )


        print(
            "Error:",
            error,
        )


# ==================================================
# RUN PROGRAM
# ==================================================

if __name__ == "__main__":

    test_location()