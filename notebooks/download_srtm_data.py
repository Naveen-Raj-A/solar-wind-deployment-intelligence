import json
import os
import time

import rasterio
import requests
from dotenv import load_dotenv
from shapely.geometry import box, shape


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("OPENTOPOGRAPHY_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENTOPOGRAPHY_API_KEY was not found in the .env file."
    )


# --------------------------------------------------
# OPENTOPOGRAPHY API CONFIGURATION
# --------------------------------------------------

API_URL = "https://portal.opentopography.org/API/globaldem"

DEM_TYPE = "SRTMGL1"

OUTPUT_FORMAT = "GTiff"


# --------------------------------------------------
# INDIA BOUNDING BOX
# --------------------------------------------------

INDIA_WEST = 68.0

INDIA_SOUTH = 6.5

INDIA_EAST = 97.5

INDIA_NORTH = 37.1


# --------------------------------------------------
# INDIA BOUNDARY FILE
# --------------------------------------------------

INDIA_BOUNDARY_PATH = os.path.join(
    "datasets",
    "boundaries",
    "geoBoundaries-IND-ADM0.geojson",
)


# --------------------------------------------------
# DOWNLOAD CONFIGURATION
# --------------------------------------------------

# Each API request will cover a 2° x 2° area
CHUNK_SIZE = 2.0

# Number of times to retry a failed download
MAX_RETRIES = 3

# Wait time before retrying
RETRY_DELAY_SECONDS = 10

# Maximum request waiting time
REQUEST_TIMEOUT_SECONDS = 600

# Small delay between successful API requests
REQUEST_DELAY_SECONDS = 2


# --------------------------------------------------
# OUTPUT DIRECTORY
# --------------------------------------------------

OUTPUT_DIRECTORY = os.path.join(
    "datasets",
    "srtm",
    "raw_tiles",
)

os.makedirs(
    OUTPUT_DIRECTORY,
    exist_ok=True,
)


# --------------------------------------------------
# LOAD INDIA BOUNDARY
# --------------------------------------------------

def load_india_boundary():
    """
    Load the India ADM0 boundary from GeoJSON.
    """

    with open(
        INDIA_BOUNDARY_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        geojson_data = json.load(file)


    india_boundary = shape(
        geojson_data["features"][0]["geometry"]
    )


    # Check whether the boundary is valid
    if not india_boundary.is_valid:

        raise ValueError(
            "India boundary geometry is invalid."
        )


    return india_boundary


# --------------------------------------------------
# GENERATE INDIA-INTERSECTING CHUNKS
# --------------------------------------------------

def generate_chunks():
    """
    Divide the India bounding rectangle into
    2° x 2° chunks.

    Keep only chunks that intersect the actual
    India ADM0 boundary.
    """

    chunks = []

    india_boundary = load_india_boundary()


    latitude = INDIA_SOUTH


    while latitude < INDIA_NORTH:

        south = latitude

        north = min(
            latitude + CHUNK_SIZE,
            INDIA_NORTH,
        )


        longitude = INDIA_WEST


        while longitude < INDIA_EAST:

            west = longitude

            east = min(
                longitude + CHUNK_SIZE,
                INDIA_EAST,
            )


            # Create a rectangular polygon
            # for the current chunk
            chunk_geometry = box(
                west,
                south,
                east,
                north,
            )


            # Keep the chunk only if it intersects
            # the actual India boundary
            if india_boundary.intersects(
                chunk_geometry
            ):

                chunks.append(
                    (
                        south,
                        north,
                        west,
                        east,
                    )
                )


            longitude += CHUNK_SIZE


        latitude += CHUNK_SIZE


    return chunks


# --------------------------------------------------
# VALIDATE GEOTIFF
# --------------------------------------------------

def validate_geotiff(file_path):
    """
    Check whether a downloaded file is a valid
    and readable GeoTIFF.
    """

    try:

        with rasterio.open(file_path) as dataset:

            if dataset.count < 1:

                return False


            if dataset.width <= 0:

                return False


            if dataset.height <= 0:

                return False


        return True


    except rasterio.errors.RasterioIOError:

        return False


# --------------------------------------------------
# CREATE FILE NAME
# --------------------------------------------------

def create_file_name(
    south,
    north,
    west,
    east,
):
    """
    Create a unique file name for each chunk.
    """

    file_name = (
        f"srtm_"
        f"S{south:.1f}_"
        f"N{north:.1f}_"
        f"W{west:.1f}_"
        f"E{east:.1f}.tif"
    )


    return file_name


# --------------------------------------------------
# DOWNLOAD ONE SRTM CHUNK
# --------------------------------------------------

def download_chunk(
    chunk_number,
    total_chunks,
    south,
    north,
    west,
    east,
):
    """
    Download one SRTM chunk from OpenTopography.
    """


    file_name = create_file_name(
        south=south,
        north=north,
        west=west,
        east=east,
    )


    output_path = os.path.join(
        OUTPUT_DIRECTORY,
        file_name,
    )


    print("\n----------------------------------------")

    print(
        f"Chunk {chunk_number}/{total_chunks}"
    )

    print(
        f"Bounds: "
        f"South={south}, "
        f"North={north}, "
        f"West={west}, "
        f"East={east}"
    )


    # --------------------------------------------------
    # SKIP EXISTING VALID FILE
    # --------------------------------------------------

    if os.path.exists(output_path):

        if validate_geotiff(output_path):

            print(
                "Status: Already downloaded. Skipping."
            )

            return True


        else:

            print(
                "Status: Existing file is invalid."
            )

            print(
                "Deleting invalid file and downloading again."
            )

            os.remove(output_path)


    # --------------------------------------------------
    # API PARAMETERS
    # --------------------------------------------------

    params = {

        "demtype": DEM_TYPE,

        "south": south,

        "north": north,

        "west": west,

        "east": east,

        "outputFormat": OUTPUT_FORMAT,

        "API_Key": API_KEY,
    }


    # --------------------------------------------------
    # DOWNLOAD WITH RETRIES
    # --------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        print(
            f"Download attempt "
            f"{attempt}/{MAX_RETRIES}"
        )


        try:

            response = requests.get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )


            # --------------------------------------------------
            # HANDLE HTTP ERROR
            # --------------------------------------------------

            if response.status_code != 200:

                print(
                    "HTTP Error:",
                    response.status_code,
                )


                print(
                    "Server Response:",
                    response.text[:500],
                )


            # --------------------------------------------------
            # HANDLE SUCCESSFUL RESPONSE
            # --------------------------------------------------

            else:

                with open(
                    output_path,
                    "wb",
                ) as file:

                    file.write(
                        response.content
                    )


                # Validate the downloaded file
                if validate_geotiff(output_path):

                    file_size_mb = (
                        os.path.getsize(output_path)
                        / (1024 * 1024)
                    )


                    print(
                        "Status: Download successful."
                    )


                    print(
                        "File Name:",
                        file_name,
                    )


                    print(
                        "File Size:",
                        round(file_size_mb, 2),
                        "MB",
                    )


                    return True


                # Download completed but file is invalid
                print(
                    "Status: Downloaded file "
                    "is not a valid GeoTIFF."
                )


                if os.path.exists(output_path):

                    os.remove(output_path)


        # --------------------------------------------------
        # HANDLE NETWORK ERRORS
        # --------------------------------------------------

        except requests.RequestException as error:

            print(
                "Request Error:",
                error,
            )


        # --------------------------------------------------
        # WAIT BEFORE RETRY
        # --------------------------------------------------

        if attempt < MAX_RETRIES:

            print(
                f"Waiting "
                f"{RETRY_DELAY_SECONDS} seconds "
                f"before retry..."
            )


            time.sleep(
                RETRY_DELAY_SECONDS
            )


    print(
        "Status: Download failed."
    )


    return False


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print(
        "\n===== INDIA SRTM DOWNLOAD ====="
    )


    print(
        "DEM Product:",
        DEM_TYPE,
    )


    print(
        "Resolution: Approximately 30 m"
    )


    print(
        "Chunk Size:",
        CHUNK_SIZE,
        "degrees",
    )


    print(
        "Loading India boundary..."
    )


    # --------------------------------------------------
    # GENERATE FILTERED CHUNKS
    # --------------------------------------------------

    chunks = generate_chunks()


    total_chunks = len(chunks)


    print(
        "\nIndia-intersecting chunks:",
        total_chunks,
    )


    # --------------------------------------------------
    # DOWNLOAD COUNTERS
    # --------------------------------------------------

    successful_downloads = 0

    failed_downloads = 0


    # --------------------------------------------------
    # DOWNLOAD EACH CHUNK
    # --------------------------------------------------

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        south, north, west, east = chunk


        success = download_chunk(

            chunk_number=index,

            total_chunks=total_chunks,

            south=south,

            north=north,

            west=west,

            east=east,
        )


        if success:

            successful_downloads += 1


        else:

            failed_downloads += 1


        # --------------------------------------------------
        # DISPLAY PROGRESS
        # --------------------------------------------------

        print(
            f"Progress: "
            f"{index}/{total_chunks}"
        )


        print(
            f"Successful: "
            f"{successful_downloads}"
        )


        print(
            f"Failed: "
            f"{failed_downloads}"
        )


        # Small delay between API requests
        time.sleep(
            REQUEST_DELAY_SECONDS
        )


    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    print(
        "\n===== DOWNLOAD SUMMARY ====="
    )


    print(
        "Total India Chunks:",
        total_chunks,
    )


    print(
        "Successful Downloads:",
        successful_downloads,
    )


    print(
        "Failed Downloads:",
        failed_downloads,
    )


    print(
        "\n===== DOWNLOAD PROCESS COMPLETED ====="
    )


# --------------------------------------------------
# RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    main()