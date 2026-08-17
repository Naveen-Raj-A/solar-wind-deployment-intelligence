import rasterio


# Path to the Global Wind Atlas GeoTIFF dataset
file_path = "datasets/global_wind_atlas/IND_wind-speed_150m.tif"


# Open the GeoTIFF file
with rasterio.open(file_path) as dataset:

    print("\n===== GLOBAL WIND ATLAS DATASET INFORMATION =====")

    # Display basic dataset information
    print("File Name:", dataset.name)
    print("File Format:", dataset.driver)
    print("CRS:", dataset.crs)
    print("Width:", dataset.width)
    print("Height:", dataset.height)
    print("Number of Bands:", dataset.count)
    print("Data Type:", dataset.dtypes[0])
    print("NoData Value:", dataset.nodata)
    print("Geographic Bounds:", dataset.bounds)
    print("Resolution:", dataset.res)


    # Read the first raster band
    # masked=True ignores NoData values during analysis
    wind_data = dataset.read(1, masked=True)


    # Calculate total, valid, and NoData cells
    total_cells = wind_data.size

    valid_cells = wind_data.count()

    nodata_cells = total_cells - valid_cells


    print("\n===== CELL INFORMATION =====")

    print("Total Cells:", total_cells)

    print("Valid Wind Data Cells:", valid_cells)

    print("NoData Cells:", nodata_cells)


    print("\n===== WIND SPEED STATISTICS =====")

    # Calculate wind-speed statistics
    # NoData values are automatically ignored
    print(
        "Minimum Wind Speed:",
        wind_data.min(),
        "m/s"
    )

    print(
        "Maximum Wind Speed:",
        wind_data.max(),
        "m/s"
    )

    print(
        "Average Wind Speed:",
        wind_data.mean(),
        "m/s"
    )


    print("\n===== ANALYSIS COMPLETED SUCCESSFULLY =====")