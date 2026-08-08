import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use("Agg") # opens any plots in a new gui window

from pathlib import Path 
from scipy.stats import pearsonr, spearmanr, mannwhitneyu, chi2_contingency
from sklearn.linear_model import LinearRegression 
from sklearn.metrics import mean_squared_error, r2_score

# include file locations similar to clean_data.py and also define the 4 seasons as a list 

CLEANED_FOLDER = Path("cleaned_data")
OUTPUT_FOLDER = Path("data_analysis_output")
FIGURE_FOLDER = OUTPUT_FOLDER / "figures"
TABLE_FOLDER = OUTPUT_FOLDER / "tables"

FIGURE_FOLDER.mkdir(parents=True, exist_ok=True)
TABLE_FOLDER.mkdir(parents=True, exist_ok=True)

# made a list that directly identifies the months we have in our cleaned datasets since in clean_data.py, before joining the datasets we changed municipalities back to uppercase
MUNICIPALITIES = [
    "VANCOUVER",
    "RICHMOND",
    "DELTA",
    "ABBOTSFORD",
]

# in clean_data.py, the raw datasets used capitalized month names, and we use MONTH_NUMBERS to convert those names to numbers. 
# now we are doing the opposite and converting those numbers back to month names but shortened names 
MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

# set out a list of 
SEASON_ORDER = [
    "WINTER",
    "SPRING",
    "SUMMER",
    "FALL",
]

#---
# below are some helper functions that we would need, more would be added later
#---

# this helper function just ensures that the months names correspond to which season
def month_to_season(month):
    if month in [12, 1, 2]:
        return "WINTER"
    elif month in [3, 4, 5]:
        return "SPRING"
    elif month in [6, 7, 8]:
        return "SUMMER"
    else:
        return "FALL"

# this function is a helper and is adapted from previous 353 exercises, instead of adding all these lines under each plot i need to save, I can just invoke this function
def save_figure(filename):
    plt.tight_layout()
    plt.savefig(
        FIGURE_FOLDER / filename,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


#---
# Load the cleaned data into this file and create some useful variables. we also need to set the data so that we use months with atleast 80% precipitation coverage for statistical analyses we perform later
#---

combined = pd.read_csv(CLEANED_FOLDER / "combined_monthly.csv")
police = pd.read_csv(CLEANED_FOLDER / "police_crashes_clean.csv")

combined["month_name"] = combined["month"].map(MONTH_NAMES)
combined["season"] = combined["month"].apply(month_to_season)
combined["season"] = pd.Categorical(
    combined["season"],
    categories=SEASON_ORDER,
    ordered=True
) # pd.Categorical is used here for taking the existing season column and using the list we made earlier to form an ordered categorical column. Categorical converts ordinary strings into a pandas categorical data type

# Number of calendar days in each month, for example if we have year = 2024 and month = 2 (feb), then it will store '29' in the days_in_month column. pandas.Period() is for time-span, unlike datetime which is for a point in time (adapted from Pandas docs)
combined["days_in_month"] = combined.apply(
    lambda row: pd.Period(
        year=int(row["year"]),
        month=int(row["month"]),
        freq="M",
    ).days_in_month,
    axis=1
) # axis=1 means we go row by row, as for the lambda, that is short for writing a function, it essentially takes one row at a time, uses that rows year and month to calculate how many days are in it

combined["temperature_coverage"] = (combined["valid_temperature_days"] / combined["days_in_month"])
combined["precipitation_coverage"] = (combined["valid_precipitation_days"] / combined["days_in_month"])

# Victims per 100 reported crashes.
combined["victims_per_100_crashes"] = (combined["total_victims"] / combined["total_crashes"] * 100)

# Only use months with at least 80% precipitation coverage
# for precipitation-dependent statistical analysis.
precip_data = combined[combined["precipitation_coverage"] >= 0.80].copy()


# Using what we have, we will now answer Question 1 for our report, see below: 
#
# Research Question 1.) How did crashes and casualty outcomes change over time? 
#---

# gather the information using grouping and aggregation, specifically the crashes and victim columns by city and year
annual_summary = (
    combined.groupby(
        ["municipality", "year"],
        as_index=False,
        observed=True
    ).agg(
        total_crashes=("total_crashes", "sum"),
        total_victims=("total_victims", "sum"),
        casualty_crashes=("casualty_crashes", "sum"),
        pedestrian_crashes=("pedestrian_crashes", "sum"),
        cyclist_crashes=("cyclist_crashes", "sum"),
        motorcycle_crashes=("motorcycle_crashes", "sum")
    )
)

annual_summary["victims_per_100_crashes"] = (annual_summary["total_victims"] / annual_summary["total_crashes"] * 100) #take the average of all victims over all crashes to then get the percentage ratio
annual_summary.to_csv(TABLE_FOLDER / "annual_summary.csv",index=False,) # output this information as CSV file


# now we will calculate the percentage change from 2021 to 2024, start by initializing an empty list for storage
change_rows = []

for municipality in MUNICIPALITIES:

    city = annual_summary[annual_summary["municipality"] == municipality]

    crashes_2021 = city.loc[city["year"] == 2021, "total_crashes"].iloc[0]
    crashes_2024 = city.loc[city["year"] == 2024, "total_crashes"].iloc[0]

    percent_change = ((crashes_2024 - crashes_2021) / crashes_2021 * 100)

    change_rows.append({
        "municipality": municipality,
        "crashes_2021": crashes_2021,
        "crashes_2024": crashes_2024,
        "percent_change_2021_2024": percent_change
    })

# set the change_rows data to annual_change so we can output it as an CSV to the table folder
annual_change = pd.DataFrame(change_rows)
annual_change.to_csv(TABLE_FOLDER / "annual_crash_change.csv", index=False)


# Output the annual crash trend figure for crashes and casualties, using seaborn's lineplot graph

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(
    data=annual_summary,
    x="year",
    y="total_crashes",
    hue="municipality",
    marker="o"
)

plt.title("Reported Crashes by Municipality, 2021-2024")
plt.xlabel("Year")
plt.ylabel("Total Reported Crashes")
plt.xticks([2021, 2022, 2023, 2024])
save_figure("annual_crashes_by_municipality.png") # invokes the save_figure helper we made 

# now we move on the rq2 which is below: 
#
# Research Question 2.) How do the crash counts vary by month's and season's?
#---

# group and aggregate the cities by month and calculate the mean of the total crashes
monthly_pattern = (
    combined.groupby(
        ["municipality", "month"],
        as_index=False,
        observed=True
    )
    ["total_crashes"].mean()
)

# 
monthly_pattern["month_name"] = (monthly_pattern["month"].map(MONTH_NAMES)) # the map function here is for pandas.series.map since it goes row by row because we selected on column (month_name)
monthly_pattern.to_csv(TABLE_FOLDER / "monthly_crash_pattern.csv", index=False) # output the results to a table csv in the mentioned folder

# plotting information below; uses seaborn lineplot (source: https://seaborn.pydata.org/generated/seaborn.lineplot.html#seaborn-lineplot)
plt.figure(figsize=(11, 6))
sns.lineplot(data=monthly_pattern, x="month", y="total_crashes", hue="municipality", marker="o")
plt.title("Average Monthly Reported Crashes by Municipality")
plt.xlabel("Month")
plt.ylabel("Average Monthly Crashes")
plt.xticks(range(1, 13), [MONTH_NAMES[i] for i in range(1, 13)]) # creates tick markers from 1-12 using a for loop, I had to search how to compress the for loop so it can be a one liner
save_figure("monthly_crash_pattern.png") # call the helper function


# Seasonal patterns aggregation and plotting below
seasonal_pattern = (
    combined.groupby(
        ["municipality", "season"],
        as_index=False,
        observed=True
    )
    ["total_crashes"].mean()
)
seasonal_pattern.to_csv(TABLE_FOLDER / "seasonal_crash_pattern.csv", index=False)

plt.figure(figsize=(10, 6))
sns.barplot(data=seasonal_pattern, x="season", y="total_crashes", hue="municipality") # source: https://seaborn.pydata.org/generated/seaborn.barplot.html#seaborn.barplot
plt.title("Average Monthly Crashes by Season")
plt.xlabel("Season")
plt.ylabel("Average Monthly Crashes")
save_figure("seasonal_crash_pattern.png")