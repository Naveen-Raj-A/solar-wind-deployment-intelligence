# Import required libraries
import os
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

# Path of the dataset
dataset_path = "../dataset/nasa_power_climate_risk_indices_190_capitals_1990_2024.csv"

# Path where graphs will be saved
output_folder = "../outputs"


# --------------------------------------------------
# 2. CREATE OUTPUT FOLDER
# --------------------------------------------------

# Create the outputs folder if it does not exist
os.makedirs(output_folder, exist_ok=True)


# --------------------------------------------------
# 3. LOAD THE DATASET
# --------------------------------------------------

data = pd.read_csv(dataset_path)

print("\nDATASET LOADED SUCCESSFULLY!")


# --------------------------------------------------
# 4. DISPLAY FIRST 5 ROWS
# --------------------------------------------------

print("\nFIRST 5 ROWS OF THE DATASET:")

print(data.head())


# --------------------------------------------------
# 5. DISPLAY DATASET SIZE
# --------------------------------------------------

print("\nDATASET SIZE:")

print("Total Rows:", data.shape[0])

print("Total Columns:", data.shape[1])


# --------------------------------------------------
# 6. DISPLAY ALL COLUMN NAMES
# --------------------------------------------------

print("\nCOLUMN NAMES:")

for column in data.columns:
    print(column)


# --------------------------------------------------
# 7. DISPLAY DATA TYPES
# --------------------------------------------------

print("\nDATA TYPES:")

print(data.dtypes)


# --------------------------------------------------
# 8. CHECK MISSING VALUES IN COMPLETE DATASET
# --------------------------------------------------

print("\nMISSING VALUES IN COMPLETE DATASET:")

missing_values = data.isnull().sum()

print(missing_values)


# --------------------------------------------------
# 9. DISPLAY ONLY COLUMNS WITH MISSING VALUES
# --------------------------------------------------

print("\nCOLUMNS CONTAINING MISSING VALUES:")

columns_with_missing_values = missing_values[missing_values > 0]

if len(columns_with_missing_values) > 0:
    print(columns_with_missing_values)
else:
    print("No missing values found in the dataset.")


# --------------------------------------------------
# 10. IDENTIFY POTENTIALLY UNNECESSARY COLUMNS
# --------------------------------------------------

# Columns containing only one unique value do not
# provide useful variation for analysis or prediction.

constant_columns = [
    column
    for column in data.columns
    if data[column].nunique(dropna=False) <= 1
]

print("\nPOTENTIALLY UNNECESSARY CONSTANT COLUMNS:")

if constant_columns:

    for column in constant_columns:
        print(column)

else:

    print("No constant columns found.")


# --------------------------------------------------
# 11. SELECT SOLAR-RELATED COLUMNS
# --------------------------------------------------

solar_columns = [
    "solar_total_mj",
    "solar_mean_mj",
    "solar_clear_mean_mj",
    "solar_clearness_idx",
    "solar_peak_days",
    "solar_annual_kwh_m2"
]


# --------------------------------------------------
# 12. DISPLAY FIRST 5 ROWS OF SOLAR DATA
# --------------------------------------------------

print("\nFIRST 5 ROWS OF SOLAR DATA:")

print(data[solar_columns].head())


# --------------------------------------------------
# 13. SOLAR DATA STATISTICAL ANALYSIS
# --------------------------------------------------

print("\nSOLAR DATA STATISTICAL ANALYSIS:")

print(data[solar_columns].describe())


# --------------------------------------------------
# 14. CHECK MISSING VALUES IN SOLAR DATA
# --------------------------------------------------

print("\nMISSING VALUES IN SOLAR DATA:")

print(data[solar_columns].isnull().sum())


# --------------------------------------------------
# 15. DISPLAY AVERAGE SOLAR VALUES
# --------------------------------------------------

print("\nAVERAGE SOLAR VALUES:")

print(data[solar_columns].mean())


# --------------------------------------------------
# 16. FIND HIGHEST SOLAR ENERGY LOCATION
# --------------------------------------------------

highest_solar_location = data.loc[
    data["solar_annual_kwh_m2"].idxmax()
]

print("\nLOCATION WITH HIGHEST ANNUAL SOLAR ENERGY:")

print("City:", highest_solar_location["city"])

print("Year:", highest_solar_location["year"])

print(
    "Annual Solar Energy:",
    highest_solar_location["solar_annual_kwh_m2"],
    "kWh/m²"
)


# --------------------------------------------------
# 17. FIND LOWEST SOLAR ENERGY LOCATION
# --------------------------------------------------

lowest_solar_location = data.loc[
    data["solar_annual_kwh_m2"].idxmin()
]

print("\nLOCATION WITH LOWEST ANNUAL SOLAR ENERGY:")

print("City:", lowest_solar_location["city"])

print("Year:", lowest_solar_location["year"])

print(
    "Annual Solar Energy:",
    lowest_solar_location["solar_annual_kwh_m2"],
    "kWh/m²"
)


# --------------------------------------------------
# 18. GRAPH 1
# SOLAR ENERGY DISTRIBUTION
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.hist(
    data["solar_annual_kwh_m2"],
    bins=30,
    edgecolor="black"
)

plt.title("Distribution of Annual Solar Energy")

plt.xlabel("Annual Solar Energy (kWh/m²)")

plt.ylabel("Number of Records")

plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "solar_energy_distribution.png"
    )
)

plt.close()

print("\nGraph 1 saved successfully.")


# --------------------------------------------------
# 19. GRAPH 2
# TOP 10 CITIES BY AVERAGE SOLAR ENERGY
# --------------------------------------------------

city_solar_average = (
    data.groupby("city")["solar_annual_kwh_m2"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)


plt.figure(figsize=(12, 6))

city_solar_average.plot(kind="bar")

plt.title("Top 10 Cities by Average Annual Solar Energy")

plt.xlabel("City")

plt.ylabel("Average Annual Solar Energy (kWh/m²)")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "top_10_solar_cities.png"
    )
)

plt.close()

print("Graph 2 saved successfully.")


# --------------------------------------------------
# 20. GRAPH 3
# AVERAGE SOLAR ENERGY TREND BY YEAR
# --------------------------------------------------

yearly_solar_average = (
    data.groupby("year")["solar_annual_kwh_m2"]
    .mean()
)


plt.figure(figsize=(12, 6))

plt.plot(
    yearly_solar_average.index,
    yearly_solar_average.values,
    marker="o"
)

plt.title("Average Annual Solar Energy Trend")

plt.xlabel("Year")

plt.ylabel("Average Annual Solar Energy (kWh/m²)")

plt.grid()

plt.tight_layout()

plt.savefig(
    os.path.join(
        output_folder,
        "solar_energy_yearly_trend.png"
    )
)

plt.close()

print("Graph 3 saved successfully.")


# --------------------------------------------------
# 21. FINAL SUMMARY
# --------------------------------------------------

print("\nDATASET ANALYSIS COMPLETED SUCCESSFULLY!")

print(
    "The dataset was successfully explored and analyzed "
    "for solar energy potential and deployment planning."
)

print(
    "Dataset size, column names, data types, missing values, "
    "and potentially unnecessary constant columns were examined."
)

print(
    "Three visualization graphs were generated and saved "
    "inside the outputs folder."
)