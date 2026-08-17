import os
import sqlite3
import time

import osmium


# ============================================================
# CONFIGURATION
# ============================================================

OSM_FILE = os.path.join(
    "datasets",
    "openstreetmap",
    "india-latest.osm.pbf",
)

OUTPUT_DIRECTORY = os.path.join(
    "datasets",
    "openstreetmap",
    "processed",
)

DATABASE_FILE = os.path.join(
    OUTPUT_DIRECTORY,
    "india_osm_spatial.db",
)

POWER_TYPES = {
    "line",
    "minor_line",
    "plant",
    "generator",
    "transformer",
}

BATCH_SIZE = 50_000

# Show progress after every 5 million OSM elements
PROGRESS_INTERVAL = 5_000_000


# ============================================================
# OSM SPATIAL DATABASE BUILDER
# ============================================================

class OSMSpatialDatabaseBuilder(osmium.SimpleHandler):

    def __init__(self, connection):

        super().__init__()

        self.connection = connection
        self.cursor = connection.cursor()

        # Feature counts
        self.road_count = 0
        self.building_count = 0
        self.substation_count = 0
        self.power_infrastructure_count = 0

        # OSM element counts
        self.node_count = 0
        self.way_count = 0
        self.relation_count = 0

        # Other counters
        self.skipped_features = 0
        self.total_indexed_features = 0

        # SQLite batches
        self.pending_features = []
        self.pending_rtree = []

        # Internal feature ID
        self.next_feature_id = 1

        # Timing
        self.start_time = time.time()

        # Next progress update
        self.next_progress_update = PROGRESS_INTERVAL


    # ========================================================
    # GET TOTAL PROCESSED ELEMENTS
    # ========================================================

    def get_total_processed_elements(self):

        return (
            self.node_count
            + self.way_count
            + self.relation_count
        )


    # ========================================================
    # GET DATABASE SIZE
    # ========================================================

    def get_database_size_gb(self):

        try:

            if os.path.exists(DATABASE_FILE):

                return (
                    os.path.getsize(DATABASE_FILE)
                    / (1024 ** 3)
                )

        except OSError:

            pass

        return 0.0


    # ========================================================
    # DISPLAY LIVE PROGRESS
    # ========================================================

    def display_progress(self):

        total_processed = (
            self.get_total_processed_elements()
        )

        if total_processed < self.next_progress_update:

            return


        elapsed_seconds = (
            time.time() - self.start_time
        )

        elapsed_minutes = (
            elapsed_seconds / 60
        )

        database_size_gb = (
            self.get_database_size_gb()
        )


        print(
            "\n===== LIVE PROGRESS UPDATE =====",
            flush=True,
        )

        print(
            "OSM Elements Processed:",
            f"{total_processed:,}",
            flush=True,
        )

        print(
            "Nodes Processed:",
            f"{self.node_count:,}",
            flush=True,
        )

        print(
            "Ways Processed:",
            f"{self.way_count:,}",
            flush=True,
        )

        print(
            "Relations Processed:",
            f"{self.relation_count:,}",
            flush=True,
        )

        print(
            "\nFeatures Indexed:",
            f"{self.total_indexed_features:,}",
            flush=True,
        )

        print(
            "Roads:",
            f"{self.road_count:,}",
            flush=True,
        )

        print(
            "Buildings:",
            f"{self.building_count:,}",
            flush=True,
        )

        print(
            "Substations:",
            f"{self.substation_count:,}",
            flush=True,
        )

        print(
            "Other Power Infrastructure:",
            f"{self.power_infrastructure_count:,}",
            flush=True,
        )

        print(
            "Skipped Features:",
            f"{self.skipped_features:,}",
            flush=True,
        )

        print(
            "\nElapsed Time:",
            round(elapsed_minutes, 2),
            "minutes",
            flush=True,
        )

        print(
            "Current Database Size:",
            round(database_size_gb, 2),
            "GB",
            flush=True,
        )

        print(
            "================================",
            flush=True,
        )


        while (
            self.next_progress_update
            <= total_processed
        ):

            self.next_progress_update += (
                PROGRESS_INTERVAL
            )


    # ========================================================
    # ADD FEATURE
    # ========================================================

    def add_feature(
        self,
        osm_id,
        osm_type,
        feature_type,
        min_lon,
        max_lon,
        min_lat,
        max_lat,
    ):

        feature_id = self.next_feature_id

        self.next_feature_id += 1


        self.pending_features.append(
            (
                feature_id,
                osm_id,
                osm_type,
                feature_type,
            )
        )


        self.pending_rtree.append(
            (
                feature_id,
                min_lon,
                max_lon,
                min_lat,
                max_lat,
            )
        )


        self.total_indexed_features += 1


        if (
            len(self.pending_features)
            >= BATCH_SIZE
        ):

            self.flush_batch()


    # ========================================================
    # WRITE BATCH TO SQLITE
    # ========================================================

    def flush_batch(self):

        if not self.pending_features:

            return


        self.cursor.executemany(
            """
            INSERT INTO osm_features
            (
                feature_id,
                osm_id,
                osm_type,
                feature_type
            )
            VALUES (?, ?, ?, ?)
            """,
            self.pending_features,
        )


        self.cursor.executemany(
            """
            INSERT INTO osm_features_rtree
            (
                feature_id,
                min_lon,
                max_lon,
                min_lat,
                max_lat
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            self.pending_rtree,
        )


        self.connection.commit()


        self.pending_features.clear()

        self.pending_rtree.clear()


    # ========================================================
    # GET WAY BOUNDING BOX
    # ========================================================

    def get_way_bounds(self, way):

        min_lon = None
        max_lon = None

        min_lat = None
        max_lat = None


        for node_reference in way.nodes:

            if not node_reference.location.valid():

                continue


            longitude = (
                node_reference.location.lon
            )

            latitude = (
                node_reference.location.lat
            )


            if min_lon is None:

                min_lon = longitude
                max_lon = longitude

                min_lat = latitude
                max_lat = latitude

            else:

                min_lon = min(
                    min_lon,
                    longitude,
                )

                max_lon = max(
                    max_lon,
                    longitude,
                )

                min_lat = min(
                    min_lat,
                    latitude,
                )

                max_lat = max(
                    max_lat,
                    latitude,
                )


        if min_lon is None:

            return None


        return (
            min_lon,
            max_lon,
            min_lat,
            max_lat,
        )


    # ========================================================
    # PROCESS NODE
    # ========================================================

    def node(self, node):

        self.node_count += 1


        power_type = node.tags.get(
            "power"
        )


        if power_type is not None:

            if not node.location.valid():

                self.skipped_features += 1

            else:

                longitude = node.location.lon

                latitude = node.location.lat


                if power_type == "substation":

                    self.substation_count += 1


                    self.add_feature(
                        node.id,
                        "node",
                        "substation",
                        longitude,
                        longitude,
                        latitude,
                        latitude,
                    )


                elif power_type in POWER_TYPES:

                    self.power_infrastructure_count += 1


                    self.add_feature(
                        node.id,
                        "node",
                        "power_infrastructure",
                        longitude,
                        longitude,
                        latitude,
                        latitude,
                    )


        self.display_progress()


    # ========================================================
    # PROCESS WAY
    # ========================================================

    def way(self, way):

        self.way_count += 1


        is_road = (
            "highway" in way.tags
        )

        is_building = (
            "building" in way.tags
        )

        power_type = way.tags.get(
            "power"
        )

        is_substation = (
            power_type == "substation"
        )

        is_other_power = (
            power_type in POWER_TYPES
        )


        if (
            is_road
            or is_building
            or is_substation
            or is_other_power
        ):

            bounds = self.get_way_bounds(
                way
            )


            if bounds is None:

                self.skipped_features += 1

            else:

                (
                    min_lon,
                    max_lon,
                    min_lat,
                    max_lat,

                ) = bounds


                if is_road:

                    self.road_count += 1


                    self.add_feature(
                        way.id,
                        "way",
                        "road",
                        min_lon,
                        max_lon,
                        min_lat,
                        max_lat,
                    )


                if is_building:

                    self.building_count += 1


                    self.add_feature(
                        way.id,
                        "way",
                        "building",
                        min_lon,
                        max_lon,
                        min_lat,
                        max_lat,
                    )


                if is_substation:

                    self.substation_count += 1


                    self.add_feature(
                        way.id,
                        "way",
                        "substation",
                        min_lon,
                        max_lon,
                        min_lat,
                        max_lat,
                    )


                elif is_other_power:

                    self.power_infrastructure_count += 1


                    self.add_feature(
                        way.id,
                        "way",
                        "power_infrastructure",
                        min_lon,
                        max_lon,
                        min_lat,
                        max_lat,
                    )


        self.display_progress()


    # ========================================================
    # PROCESS RELATION
    # ========================================================

    def relation(self, relation):

        self.relation_count += 1

        # Relations are counted for progress.
        #
        # They are not spatially indexed in this
        # prototype because resolving complete
        # multipolygon relation geometry requires
        # additional processing.

        self.display_progress()


    # ========================================================
    # FINAL STATISTICS
    # ========================================================

    def print_final_statistics(self):

        processing_time_seconds = (
            time.time() - self.start_time
        )

        processing_time_minutes = (
            processing_time_seconds / 60
        )


        print(
            "\n===== FINAL DATABASE STATISTICS ====="
        )


        print(
            "\nOSM Elements Processed:",
            f"{self.get_total_processed_elements():,}",
        )


        print(
            "Nodes:",
            f"{self.node_count:,}",
        )


        print(
            "Ways:",
            f"{self.way_count:,}",
        )


        print(
            "Relations:",
            f"{self.relation_count:,}",
        )


        print(
            "\n===== INDEXED FEATURES ====="
        )


        print(
            "Roads:",
            f"{self.road_count:,}",
        )


        print(
            "Buildings:",
            f"{self.building_count:,}",
        )


        print(
            "Substations:",
            f"{self.substation_count:,}",
        )


        print(
            "Other Power Infrastructure:",
            f"{self.power_infrastructure_count:,}",
        )


        print(
            "\nTotal Indexed Features:",
            f"{self.total_indexed_features:,}",
        )


        print(
            "Skipped Features:",
            f"{self.skipped_features:,}",
        )


        print(
            "\nTotal Processing Time:",
            round(
                processing_time_minutes,
                2,
            ),
            "minutes",
        )


# ============================================================
# CREATE SQLITE DATABASE
# ============================================================

def create_database(connection):

    cursor = connection.cursor()


    cursor.execute(
        """
        CREATE TABLE osm_features
        (
            feature_id INTEGER PRIMARY KEY,
            osm_id INTEGER NOT NULL,
            osm_type TEXT NOT NULL,
            feature_type TEXT NOT NULL
        )
        """
    )


    cursor.execute(
        """
        CREATE VIRTUAL TABLE osm_features_rtree
        USING rtree
        (
            feature_id,
            min_lon,
            max_lon,
            min_lat,
            max_lat
        )
        """
    )


    cursor.execute(
        """
        CREATE INDEX idx_feature_type
        ON osm_features(feature_type)
        """
    )


    connection.commit()


# ============================================================
# BUILD INDIA OSM SPATIAL DATABASE
# ============================================================

def build_osm_spatial_database():

    print(
        "\n===== INDIA OSM SPATIAL DATABASE BUILDER ====="
    )


    # ========================================================
    # CHECK INPUT FILE
    # ========================================================

    if not os.path.exists(OSM_FILE):

        print(
            "\nERROR: India OSM PBF file not found."
        )

        print(
            "Expected File:",
            OSM_FILE,
        )

        return


    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    os.makedirs(
        OUTPUT_DIRECTORY,
        exist_ok=True,
    )


    # ========================================================
    # REMOVE OLD DATABASE
    # ========================================================

    if os.path.exists(DATABASE_FILE):

        print(
            "\nRemoving old database:"
        )

        print(
            DATABASE_FILE
        )


        os.remove(
            DATABASE_FILE
        )


    # ========================================================
    # DISPLAY INFORMATION
    # ========================================================

    input_size_gb = (

        os.path.getsize(OSM_FILE)

        / (1024 ** 3)

    )


    print(
        "\nInput File:",
        OSM_FILE,
    )


    print(
        "Input Size:",
        round(input_size_gb, 2),
        "GB",
    )


    print(
        "\nOutput Database:",
        DATABASE_FILE,
    )


    print(
        "\nProgress Interval:",
        f"{PROGRESS_INTERVAL:,}",
        "OSM elements",
    )


    print(
        "SQLite Batch Size:",
        f"{BATCH_SIZE:,}",
        "features",
    )


    print(
        "\nStarting one-time preprocessing..."
    )


    # ========================================================
    # CONNECT DATABASE
    # ========================================================

    connection = sqlite3.connect(
        DATABASE_FILE
    )


    try:

        # ====================================================
        # SQLITE PERFORMANCE SETTINGS
        # ====================================================

        connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        connection.execute(
            "PRAGMA synchronous = NORMAL"
        )

        connection.execute(
            "PRAGMA temp_store = MEMORY"
        )


        # ====================================================
        # CREATE DATABASE TABLES
        # ====================================================

        create_database(
            connection
        )


        # ====================================================
        # CREATE OSM HANDLER
        # ====================================================

        handler = OSMSpatialDatabaseBuilder(
            connection
        )


        # ====================================================
        # PROCESS INDIA PBF
        # ====================================================

        handler.apply_file(
            OSM_FILE,
            locations=True,
            idx="flex_mem",
        )


        # ====================================================
        # SAVE FINAL BATCH
        # ====================================================

        handler.flush_batch()


        # ====================================================
        # OPTIMIZE SQLITE DATABASE
        # ====================================================

        print(
            "\nOptimizing SQLite database..."
        )


        connection.execute(
            "ANALYZE"
        )


        connection.commit()


        # ====================================================
        # FINAL RESULTS
        # ====================================================

        handler.print_final_statistics()


        database_size_gb = (

            os.path.getsize(DATABASE_FILE)

            / (1024 ** 3)

        )


        print(
            "\nDatabase File:",
            DATABASE_FILE,
        )


        print(
            "Final Database Size:",
            round(database_size_gb, 2),
            "GB",
        )


        print(
            "\n===== SPATIAL DATABASE BUILD COMPLETED SUCCESSFULLY ====="
        )


    except KeyboardInterrupt:

        print(
            "\n\n===== PROCESS INTERRUPTED ====="
        )


        print(
            "The database build was stopped."
        )


        print(
            "Do not use the incomplete database."
        )


    except Exception as error:

        print(
            "\n===== DATABASE BUILD FAILED ====="
        )


        print(
            "Error:",
            error,
        )


    finally:

        connection.close()


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    build_osm_spatial_database()