# CMPT 353 Project

## Title

Weather Conditions and Reported Vehicle Crash Patterns in Selected Lower Mainland Municipalities, 2021-2024

## Project Overview

This project examines reported vehicle crash patterns in Vancouver, Richmond, Delta, and Abbotsford from 2021 to 2024

ICBC crash data is combined with daily historical weather observations from Environment and Climate Change Canada. The weather records are aggregated to monthly measurements so they can be combined with the ICBC data by municipality, year, and month

The project also uses a separate ICBC police reported crash dataset to examine reported weather conditions, road conditions, accident types, casualty outcomes, and vehicles involved

## Research Questions

1. How did reported crash counts and casualty outcomes vary by municipality, year, month, and season from 2021 to 2024?

2. Are monthly precipitation and temperature associated with reported crash frequency?

3. Do reported crash counts differ between wetter and drier months?

4. Does the relationship between weather and crashes differ among Vancouver, Richmond, Delta, and Abbotsford?

5. In the police-reported crash dataset, how are reported weather and road conditions associated with accident type and casualty outcomes?

## Data Sources

### ICBC Reported Crashes

Contains crash information such as:

- municipality
- year and month
- crash severity
- crash configuration
- day of week and time category
- pedestrian, cyclist, motorcycle, and heavy-vehicle involvement
- total crashes
- total victims

### ICBC Police-Reported Crashes

Contains additional information such as:

- accident type
- collision type
- crash configuration
- weather
- road condition
- total casualties
- total vehicles involved
- vulnerable-road-user indicators

### Environment and Climate Change Canada

Daily weather observations from 2021 through 2024 are used from the following stations:

- Vancouver Harbour CS for Vancouver
- Vancouver International Airport (YVR) for Richmond
- Burns Bog for Delta
- Abbotsford A for Abbotsford

Important weather fields include:

- mean, minimum, and maximum temperature;
- total precipitation;
- precipitation flags and missing-value indicators

Richmond Nature Park was initially selected as the Richmond weather station. During data validation, its observations were found to become substantially incomplete in late 2023 and unavailable through 2024
Vancouver International Airport, which is located in Richmond, was therefore used consistently for Richmond for the full 2021-2024 period

## Data Processing

The `clean_data.py` script:

1. Loads the untouched raw CSV files
2. Standardizes column names, text values, and data types
3. Keeps records from 2021 through 2024 for Vancouver, Richmond, Delta, and Abbotsford
4. Keeps the fields required for the project analysis
5. Preserves valid zero precipitation values and missing weather observations
6. Rejects invalid negative precipitation and crash-count values
7. Creates crash-category fields such as casualty, pedestrian, cyclist, and motorcycle crashes
8. Aggregates daily weather observations by municipality, year, and month
9. Aggregates the main ICBC crash data to the same municipality-year-month level
10. Joins the monthly crash and weather datasets using municipality, year, and month
11. Writes the cleaned datasets to `cleaned_data/`

The final monthly ICBC, monthly weather, and combined datasets each contain 192 rows:

- 4 municipalities
- 4 years
- 12 months

This gives one row for every municipality-year-month combination

## Cleaned-Data Validation

The `audit_cleaned_data.py` script checks the generated cleaned data for:

- expected municipality, year, and month coverage
- duplicate monthly keys
- missing weather observations
- valid temperature and precipitation observation counts
- impossible or suspicious values
- consistency of the ICBC monthly aggregation
- unknown categories in the police-reported data

Weather observations are not imputed

For precipitation-dependent statistical analysis, months with less than 80% valid daily precipitation coverage are excluded. This removes one monthly observation, Vancouver in April 2021, from precipitation-based analysis

## Analysis

The `data_analysis.py` script performs the project analysis using the cleaned datasets

Techniques used include:

- descriptive statistics and grouped summaries
- annual, monthly, and seasonal crash-pattern analysis
- Pearson correlation (explained in report and code comments)
- Spearman correlation( ^^)
- multiple linear regression
- Mann-Whitney U tests comparing wetter and drier months
- Chi-square tests of independence for police-reported weather, road conditions, and accident type
- Seaborn and Matplotlib visualizations

Statistical significance is evaluated using an alpha level of 0.05. Results are interpreted as associations rather than causal relationships

Generated figures and tables are written to `data_analysis_output/`

## Requirements

The project was developed using Python 3.10

Required Python libraries:

- pandas
- numpy
- scipy
- scikit-learn
- matplotlib
- seaborn

The required libraries can be installed with:

```bash
pip install pandas numpy scipy scikit-learn matplotlib seaborn
```

## Running the Project

Run all commands from the repository root

### 1. Clean the data

```bash
python3 clean_data.py
```

No command-line arguments are required

The cleaned datasets are written to:

```text
cleaned_data/
```

The primary monthly dataset used for the weather/crash analysis is:

```text
cleaned_data/combined_monthly.csv
```

A successful cleaning run produces:

```text
Expected monthly rows: 192
ICBC monthly rows: 192
Weather monthly rows: 192
Combined monthly rows: 192
```

### 2. Audit the cleaned data

```bash
python3 audit_cleaned_data.py
```

No command-line arguments are required

This performs structural and data-quality checks on the cleaned outputs

### 3. Run the analysis

```bash
python3 data_analysis.py
```

No command-line arguments are required

Generated results are saved under:

```text
data_analysis_output/
├── figures/
└── tables/
```

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
├── data_analysis_output/
│   ├── figures/
│   └── tables/
│
├── notes/
│   ├── clean_data.md
│   └── audit_cleaned_data.md
│
├── clean_data.py
├── audit_cleaned_data.py
├── data_analysis.py
├── .gitignore
└── README.md
```

## Interpretation Notes and Limitations

The project analyzes statistical associations and does not establish baseless conclusions

Important limitations include:

- traffic volume and vehicle exposure were not available
- population differences among municipalities were not directly controlled
- road design, construction, enforcement, commuting patterns, and other factors may affect crash frequency
- raw police-reported crash counts by weather or road condition should not be interpreted as crash risk because the amount of time motorists were exposed to each condition is unknown
- some weather observations are missing, although monthly coverage was checked and low-coverage precipitation months were excluded where appropriate

The cleaned and analysis outputs are retained so that the processing and statistical results can be inspected and reproduced
