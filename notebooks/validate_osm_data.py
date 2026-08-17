import os
import time

import osmium


# --------------------------------------------------
# INDIA OSM DATASET
# --------------------------------------------------

OSM_FILE = os.path.join(
    "datasets",
    "openstreetmap",
    "india-latest.osm.pbf",
)


# --------------------------------------------------
# VALIDATION HANDLER
# --------------------------------------------------

class OSMValidationHandler(osmium.SimpleHandler):

    def __init__(self):

        super().__init__()

        self.node_count = 0
        self.way_count = 0
        self.relation_count = 0


    # Count OSM nodes
    def node(self, node):

        self.node_count += 1


    # Count OSM ways
    def way(self, way):

        self.way_count += 1


    # Count OSM relations
    def relation(self, relation):

        self.relation_count += 1


# --------------------------------------------------
# VALIDATE DATASET
# --------------------------------------------------

def validate_osm_dataset():

    print("\n===== INDIA OSM DATASET VALIDATION =====")


    # Check whether file exists
    if not os.path.exists(OSM_FILE):

        print("\nERROR: OSM file not found.")

        print("Expected File:", OSM_FILE)

        return


    # Get file size
    file_size_bytes = os.path.getsize(OSM_FILE)

    file_size_gb = file_size_bytes / (1024 ** 3)


    print("\nFile:", OSM_FILE)

    print("File Size:", round(file_size_gb, 2), "GB")

    print("\nReading complete OSM PBF file...")

    print("This may take several minutes.")


    # Start timer
    start_time = time.time()


    # Create handler
    handler = OSMValidationHandler()


    try:

        # Read complete PBF file
        handler.apply_file(
            OSM_FILE,
            locations=False,
        )


        # Calculate processing time
        end_time = time.time()

        processing_time = end_time - start_time


        print(
            "\n===== OSM ELEMENT COUNTS ====="
        )


        print(
            "Nodes:",
            handler.node_count,
        )


        print(
            "Ways:",
            handler.way_count,
        )


        print(
            "Relations:",
            handler.relation_count,
        )


        total_elements = (

            handler.node_count

            + handler.way_count

            + handler.relation_count

        )


        print(
            "\nTotal OSM Elements:",
            total_elements,
        )


        print(
            "Processing Time:",
            round(processing_time, 2),
            "seconds",
        )


        print(
            "\nOSM PBF validation completed successfully."
        )


        print(
            "\n===== VALIDATION COMPLETED ====="
        )


    except Exception as error:

        print(
            "\nOSM PBF validation failed."
        )


        print(
            "Error:",
            error,
        )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    validate_osm_dataset()