# CMPT 353 Project

## Title

Weather Conditions and Reported Vehicle Crash Patterns in Selected Lower Mainland Municipalities, 2021-2024

## Project Overview

This project will examine reported vehicle crash patterns in Vancouver, Richmond (YVR), Delta, and Abbotsford from 2021 to 2024
ICBC crash data will be combined with daily historical weather observations from Environment and Climate Change Canada

The weather records will be aggregated to monthly measurements so they can be joined with the ICBC data by municipality, year, and month

## Some Research Questions That May Be Answered

1. How did reported crash counts and casualty outcomes vary by municipality, year, month, and season from 2021 to 2024?

2. Are monthly precipitation and temperature associated with reported crash frequency?

3. Do crash counts or casualty outcomes differ between wetter and drier months?

4. Does the relationship between weather and crashes differ among Vancouver, Richmond, Delta, and Abbotsford?

## Data Sources

### ICBC Reported Crashes

Contains crash information such as:

- municipality;
- year and month;
- crash severity;
- crash configuration;
- day of week and time category;
- pedestrian, cyclist, motorcycle, and heavy-vehicle involvement;
- total crashes;
- total victims

### ICBC Police-Reported Crashes

Contains additional information such as:

- accident type;
- collision type;
- crash configuration;
- weather;
- road condition;
- total casualties;
- total vehicles involved;
- vulnerable-road-user indicators

### Environment and Climate Change Canada

Daily weather observations from 2021 through 2024:

- Vancouver Harbour CS for Vancouver;
- Richmond YVR (Vancouver International Airport) for Richmond;
- Burns Bog for Delta;
- Abbotsford A for Abbotsford

Important weather fields include:

- mean, minimum, and maximum temperature;
- total rain;
- total snow;
- total precipitation;
- weather-data quality and missing-value flags

## Planned Data Processing

The `clean_data.py` script will:

1. Load the untouched raw CSV files
2. Standardize column names and data types
3. Keep records from 2021 through 2024
4. Remove fields not required for the analysis
5. Convert missing-value and trace-precipitation codes
6. Examine duplicate records, missing values, and unusual observations
7. Aggregate daily weather observations by municipality, year, and month
8. Aggregate ICBC crash data to the same municipality-month level
9. Join the crash and weather datasets using municipality, year, and month
10. Write cleaned datasets for later analysis

## Planned Analysis

The project may use:

- descriptive statistics and grouped summaries;
- monthly and seasonal visualizations;
- Pearson or Spearman correlation;
- wet-versus-dry period comparisons;
- ANOVA or non-parametric group comparisons;
- linear regression, where appropriate

Statistical significance may be evaluated using an alpha level of 0.05, but conclusions will also consider effect size, patterns, and practical importance

## Repository Structure

```text
cmpt353-project/
├── raw_data/
│   ├── icbc/
│   │   ├── ICBC (new) Lower Mainland Data - RAW.csv
│   │   ├── ICBC reported crashes 2021-2024.csv
│   │   └── Lower Mainland_Full Data_RAW_deprecated.csv
│   │
│   └── weather/
│       ├── deprecated_raw_datasets/
│       │   ├── Richmond Daily Climate Data 2021 - RAW.csv
│       │   ├── Richmond Daily Climate Data 2022 - RAW.csv
│       │   ├── Richmond Daily Climate Data 2023 - RAW.csv
│       │   └── Richmond Daily Climate Data 2024 - RAW.csv
│       │
│       ├── Abbotsford Daily Climate Data 2021 - RAW.csv
│       ├── ...
│       ├── Delta Daily Climate Data 2021 - RAW.csv
│       ├── ...
│       ├── Richmond VIA Daily Climate Data 2021 - RAW.csv
│       ├── ...
│       ├── Van Daily Climate Data 2021 - RAW.csv
│       └── ...
│
├── cleaned_data/
│   ├── icbc_clean.csv
│   ├── icbc_monthly.csv
│   ├── police_crashes_clean.csv
│   ├── weather_daily_clean.csv
│   ├── weather_monthly.csv
│   └── combined_monthly.csv
│
├── notes/
│   ├── clean_data.md
│   └── audit_cleaned_data.md
│
├── clean_data.py
├── audit_cleaned_data.py
├── .gitignore
└── README.md
```
