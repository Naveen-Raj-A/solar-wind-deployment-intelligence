import os
import time

import osmium


# ==================================================
# INPUT OSM FILE
# ==================================================

OSM_FILE = os.path.join(
    "datasets",
    "openstreetmap",
    "india-latest.osm.pbf",
)


# ==================================================
# OSM FEATURE INVENTORY HANDLER
# ==================================================

class OSMFeatureInventoryHandler(osmium.SimpleHandler):

    def __init__(self):

        super().__init__()

        # Required feature counters
        self.road_count = 0
        self.building_count = 0
        self.substation_count = 0
        self.power_infrastructure_count = 0

        # Total processed elements
        self.processed_nodes = 0
        self.processed_ways = 0
        self.processed_relations = 0


    # ==================================================
    # PROCESS NODES
    # ==================================================

    def node(self, node):

        self.processed_nodes += 1

        power_type = node.tags.get("power")

        if power_type == "substation":

            self.substation_count += 1

        elif power_type in {

            "line",
            "minor_line",
            "plant",
            "generator",
            "transformer",

        }:

            self.power_infrastructure_count += 1


    # ==================================================
    # PROCESS WAYS
    # ==================================================

    def way(self, way):

        self.processed_ways += 1


        # Count roads
        if "highway" in way.tags:

            self.road_count += 1


        # Count buildings
        if "building" in way.tags:

            self.building_count += 1


        # Count power infrastructure
        power_type = way.tags.get("power")


        if power_type == "substation":

            self.substation_count += 1


        elif power_type in {

            "line",
            "minor_line",
            "plant",
            "generator",
            "transformer",

        }:

            self.power_infrastructure_count += 1


    # ==================================================
    # PROCESS RELATIONS
    # ==================================================

    def relation(self, relation):

        self.processed_relations += 1


        # Count buildings represented as relations
        if "building" in relation.tags:

            self.building_count += 1


        # Count power infrastructure
        power_type = relation.tags.get("power")


        if power_type == "substation":

            self.substation_count += 1


        elif power_type in {

            "line",
            "minor_line",
            "plant",
            "generator",
            "transformer",

        }:

            self.power_infrastructure_count += 1


# ==================================================
# SCAN INDIA OSM DATASET
# ==================================================

def scan_osm_features():

    print(
        "\n===== INDIA OSM FEATURE INVENTORY ====="
    )


    # ==================================================
    # CHECK INPUT FILE
    # ==================================================

    if not os.path.exists(OSM_FILE):

        print(
            "\nERROR: India OSM PBF file not found."
        )

        print(
            "Expected File:",
            OSM_FILE,
        )

        return


    # ==================================================
    # DISPLAY FILE INFORMATION
    # ==================================================

    file_size_gb = (

        os.path.getsize(OSM_FILE)

        / (1024 ** 3)

    )


    print(
        "\nInput File:",
        OSM_FILE,
    )


    print(
        "File Size:",
        round(file_size_gb, 2),
        "GB",
    )


    print(
        "\nScanning complete India OSM dataset..."
    )


    print(
        "Counting project-required features."
    )


    print(
        "This may take approximately the same time "
        "as the validation scan."
    )


    # ==================================================
    # START TIMER
    # ==================================================

    start_time = time.time()


    # ==================================================
    # CREATE HANDLER
    # ==================================================

    handler = OSMFeatureInventoryHandler()


    try:

        # ==================================================
        # PROCESS COMPLETE PBF
        # ==================================================

        handler.apply_file(
            OSM_FILE,
            locations=False,
        )


        # ==================================================
        # CALCULATE PROCESSING TIME
        # ==================================================

        processing_time = time.time() - start_time


        total_processed = (

            handler.processed_nodes

            + handler.processed_ways

            + handler.processed_relations

        )


        # ==================================================
        # DISPLAY SCAN RESULTS
        # ==================================================

        print(
            "\n===== PROJECT FEATURE COUNTS ====="
        )


        print(
            "Roads:",
            handler.road_count,
        )


        print(
            "Buildings:",
            handler.building_count,
        )


        print(
            "Substations:",
            handler.substation_count,
        )


        print(
            "Other Power Infrastructure:",
            handler.power_infrastructure_count,
        )


        print(
            "\n===== PROCESSING INFORMATION ====="
        )


        print(
            "Nodes Processed:",
            handler.processed_nodes,
        )


        print(
            "Ways Processed:",
            handler.processed_ways,
        )


        print(
            "Relations Processed:",
            handler.processed_relations,
        )


        print(
            "Total Elements Processed:",
            total_processed,
        )


        print(
            "Processing Time:",
            round(processing_time, 2),
            "seconds",
        )


        print(
            "\n===== FEATURE INVENTORY COMPLETED SUCCESSFULLY ====="
        )


    except Exception as error:

        print(
            "\nFeature inventory failed."
        )


        print(
            "Error:",
            error,
        )


# ==================================================
# RUN PROGRAM
# ==================================================

if __name__ == "__main__":

    scan_osm_features()