"""
Test Script for OpenStreetMap Engine

This script verifies that the OSM analysis engine
works correctly before integrating it into the
complete Solar & Wind Deployment Intelligence
pipeline.
"""

from pprint import pprint

from engine.osm.analyzer import analyze_location


def main():
    """
    Run a simple OSM analysis.
    """

    location = "Chennai"

    print("=" * 60)
    print("OPENSTREETMAP ENGINE TEST")
    print("=" * 60)
    print(f"Location : {location}")
    print()

    try:

        result = analyze_location(location)

        print("\nAnalysis Completed Successfully.\n")

        pprint(result)

    except Exception as error:

        print("\nOSM ENGINE FAILED\n")

        print(type(error).__name__)
        print(error)

        raise


if __name__ == "__main__":
    main()