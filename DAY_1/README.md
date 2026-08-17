# Infosys Virtual Internship - Day 1

## Project

Solar & Wind Deployment Intelligence Platform

## Session Topic

Renewable Energy Basics and Solar Dataset Analysis

## Learning Objectives

- Understand renewable energy basics
- Understand solar, wind, and hybrid energy systems
- Learn about solar irradiance
- Learn about wind speed
- Understand capacity factor
- Understand transmission lines
- Understand substations
- Understand the electrical grid
- Learn about LCOE (Levelized Cost of Energy)
- Download and analyze a solar-related dataset

## Dataset

The dataset used for Day 1 analysis is:

`nasa_power_climate_risk_indices_190_capitals_1990_2024.csv`

The dataset contains climate and renewable energy information for 190 capital cities from 1990 to 2024.

## Dataset Size

- Total Rows: 6650
- Total Columns: 56

## Tools and Libraries Used

- Python
- Pandas
- Matplotlib
- Visual Studio Code

## Solar Features Analyzed

The following solar-related features were selected for analysis:

- `solar_total_mj`
- `solar_mean_mj`
- `solar_clear_mean_mj`
- `solar_clearness_idx`
- `solar_peak_days`
- `solar_annual_kwh_m2`

## Analysis Performed

The following dataset analysis tasks were completed:

- Loaded the CSV dataset using Pandas
- Displayed the first five rows
- Identified the number of rows and columns
- Displayed all dataset column names
- Selected solar-related features
- Performed descriptive statistical analysis
- Checked for missing values
- Calculated average solar values
- Identified the highest annual solar energy record
- Identified the lowest annual solar energy record
- Generated solar energy visualizations

## Key Findings

- The dataset contains 6650 rows and 56 columns.
- The average annual solar energy value is approximately 489.72 kWh/m².
- The `solar_clearness_idx` column contains 2090 missing values.
- The `solar_peak_days` column contains zero for all records and may require further investigation before being used for machine learning.
- The highest annual solar energy record was found for Colombo in 2016 with 1185.66 kWh/m².
- The lowest annual solar energy record was found for Reykjavik in 2018 with 213.39 kWh/m².

## Visualizations Generated

Three visualizations were created:

1. Distribution of Annual Solar Energy
2. Top 10 Cities by Average Annual Solar Energy
3. Average Annual Solar Energy Trend by Year

The generated graphs are stored inside the `outputs` folder.

## Conclusion

The Day 1 task successfully introduced renewable energy concepts and basic solar dataset analysis.

The solar-related data was explored using Python and Pandas. Statistical analysis and data visualization were performed to understand solar energy patterns across different cities and years.

This analysis provides an initial foundation for developing the Solar & Wind Deployment Intelligence Platform.

## Status

Day 1 - Completed