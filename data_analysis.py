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

# regression for research question 3 and 4, predictors: monthly precip, monthly mean temp, municipality, year
def run_regression(data, target): # data = DF to analyze, target = outcome to predict
    regression_data = data[
        [
            target, 
            "total_precip_mm",
            "mean_temp_c", 
            "municipality",
            "year"
        ]
    ].dropna() # creates a smaller DF that contains only the variables we need for the regress. dropna() removes rows which contain missing values in any of the stated columns

    # convert the municipality and year categories into dummy variables because reression requires numerical inputs, but municipality and year are categorical 
    X = pd.get_dummies( # get_dummies converts those categories into numeric dummy variables which are assigned some number
        regression_data[
            [
                "total_precip_mm",
                "mean_temp_c",
                "municipality",
                "year"
            ]
        ],
        columns=["municipality", "year"],
        drop_first=True, # avoids making any redundant dummy vars
        dtype=float # dummy var numbers are turned into floating points
    )

    y = regression_data[target] # either total_crashes or total_victims

    model = LinearRegression() # creates the empty LR model
    model.fit(X, y) # LR starts, the model will look at the observations and will then estimate the coef's

    predictions = model.predict(X) # predict outcome for every row

    result = pd.DataFrame({"predictor": X.columns, "coefficient": model.coef_}) # creates a DF table that contains each prediction variable and regress coef
    result.loc[len(result)] = ["INTERCEPT", model.intercept_] # adds the models intercept into the results table, here the intercept is predicted outcome when all prediction vars are 0

    r_squared = r2_score(y, predictions) # calculates r_squared // tells us how much of the variation in the outcome is explained by the model
    rmse = np.sqrt(mean_squared_error(y, predictions)) # take the square root of the actual values vs the predicted values which gives us the "Root Mean Squared Error" saved into rmse

    return result, r_squared, rmse, len(regression_data) # return the results


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

#---
# rq3 and rq4 are both related to one another and contain statistical tests. the plots used here are: lmplot and catplot (using violinplot as the categorical distribution "kind='violin'")
# for the statistical tests, we use mann-whitney-u on all the cities in a for loop, pvalue tests (Pearson (better suitable for categorical data that is numerical) and Spearman)
#   * according to some research, Pearson tests is for finding if there is a linear relationship between two numerical datasets (in our case, crash_counts vs precipitation)
#     and spearman tests is for finding a monotonic relationship (aka. 2 variables are connected and move in the same direction), between them (in our case, as precipitation increases, do crash counts increase or decrease, even if the pattern is not 100% linear)
#   * ** the idea to use pearson and spearman was something that was suggested by Generative AI **
# Linear regression will also be used here multiple times, for model crash_counts using (precip, temp, city, and year). A helper is created to run the regression, instead of duplicating code multiple times

# Research Questions (3)(4).) Are precipitation and temperature associated with crash frequency, and does this differ by each municipality? 
#                             Do wetter months have different crash counts versus drier months? 
#---

correlation_rows = [] # initialize empty list

for municipality in MUNICIPALITIES:

    city_all = combined[combined["municipality"] == municipality]
    city_precip = precip_data[precip_data["municipality"] == municipality]

    # Here we use pearson testing to find a linear relationship between total precipitation and total crashes (explained above the RQ's above)
    precip_r, precip_p = pearsonr(city_precip["total_precip_mm"], city_precip["total_crashes"])
    temp_r, temp_p = pearsonr(city_all["mean_temp_c"], city_all["total_crashes"])

    # Here we use Spearman testing to find a monotonic relationship between the data to see if the both increase, decrease, or go separate ways 
    precip_spearman, precip_spearman_p = spearmanr(city_precip["total_precip_mm"], city_precip["total_crashes"])
    temp_spearman, temp_spearman_p = spearmanr(city_all["mean_temp_c"], city_all["total_crashes"])

    correlation_rows.append({
        "municipality": municipality,
        "precipitation_pearson_r": precip_r,
        "precipitation_pearson_p": precip_p,
        "precipitation_spearman_r": precip_spearman,
        "precipitation_spearman_p": precip_spearman_p,
        "temperature_pearson_r": temp_r,
        "temperature_pearson_p": temp_p,
        "temperature_spearman_r": temp_spearman,
        "temperature_spearman_p": temp_spearman_p
    })

# create a dataframe to store all the results into "correlations" to output it to a csv. both pearson and spearman were used as correlation testing because we were finding relations between data variables 
correlations = pd.DataFrame(correlation_rows)
correlations.to_csv(TABLE_FOLDER / "municipality_correlations.csv", index=False)

# Precipitation vs crashes plots using lmplot is below. most of the code was gotten from the seabron docs website (source: https://seaborn.pydata.org/generated/seaborn.lmplot.html#seaborn.lmplot)

precip_plot = sns.lmplot(
    data=precip_data,
    x="total_precip_mm",
    y="total_crashes",
    col="municipality",
    col_wrap=2,
    height=4,
    scatter_kws={"alpha": 0.7}
)
precip_plot.set_axis_labels("Monthly Precipitation (mm)", "Reported Crashes")
precip_plot.fig.suptitle("Monthly Precipitation vs Reported Crashes", y=1.03)
precip_plot.savefig(FIGURE_FOLDER / "precipitation_vs_crashes.png", dpi=300, bbox_inches="tight")
plt.close()


# Temperature vs crashes plots using lmplot as well 

temp_plot = sns.lmplot(
    data=combined,
    x="mean_temp_c",
    y="total_crashes",
    col="municipality",
    col_wrap=2,
    height=4,
    scatter_kws={"alpha": 0.7},
)
temp_plot.set_axis_labels("Monthly Mean Temperature (°C)", "Reported Crashes")
temp_plot.fig.suptitle("Monthly Mean Temperature vs Reported Crashes", y=1.03)
temp_plot.savefig(FIGURE_FOLDER / "temperature_vs_crashes.png", dpi=300, bbox_inches="tight")
plt.close()

# now we will need to run 2 linear regressions (explained below). Both LR use the following model: (Model = precipitation + temperature + municipality + year)
#
#   * LR1 (total_crashes) --> we want to figure out how the "Model" is associated with the number of reported crashes
#   * LR2 (total_victims) --> we want to figure out how the "Model" is associated with the number of crash victims
#
# the regression helper will then return 4 things which are
#   * crash_regression = contains the model coefficients
#   * crash_r2 = R squared, variation in crashes
#   * crash_rmse (root mean squared error) = prediction error
#   * crash_n = #observations used in regress
#
# Essentially what im trying to do is: fit the same weather model 2 times (explaining crash freq and explain victim totals), and then saving the coef's of each to compare how predictors relate to both outcomes

crash_regression, crash_r2, crash_rmse, crash_n = (run_regression(precip_data, "total_crashes"))
crash_regression.to_csv(TABLE_FOLDER / "crash_regression_coefficients.csv", index=False)

victim_regression, victim_r2, victim_rmse, victim_n = (run_regression(precip_data, "total_victims"))
victim_regression.to_csv(TABLE_FOLDER / "victim_regression_coefficients.csv", index=False)

#---
# run the mannwhitneyu tests on all cities using a for loop to figure out RQ4 which was "Do wetter months have different crash counts than drier months?". output the result in a catplot using violinplot
#---

# declare the empty lists to store the test results and cit wet/dry data 
mann_whitney_rows = []
wet_dry_data = []

for municipality in MUNICIPALITIES:

    city = precip_data[precip_data["municipality"] == municipality].copy() # sift through the cities
    median_precipitation = city["total_precip_mm"].median() # calculate the median precipitation  of the cities (middle value)
    city["precipitation_group"] = np.where(city["total_precip_mm"] >= median_precipitation, "WET", "DRY") # created a new column called "precipitation_group" where we label each month as wet or dry, relative to the city's median precip

    wet = city.loc[city["precipitation_group"] == "WET", "total_crashes"] # extracts the crash counts for the wet and dry month groups
    dry = city.loc[city["precipitation_group"] == "DRY", "total_crashes"]

    statistic, p_value = mannwhitneyu(wet, dry, alternative="two-sided") # compare the wet month and fry month crash counts to see if the two groups differ in any way (aka 2 sided test). mannwhintey was useful because we are comparing 2 groups

    # builds a dictionary which contains each city's results, and appends it to the list we declared above "mann_whitney_rows = []"
    mann_whitney_rows.append({
        "municipality": municipality,
        "median_precipitation_mm": median_precipitation,
        "wet_months": len(wet),
        "dry_months": len(dry),
        "wet_mean_crashes": wet.mean(),
        "dry_mean_crashes": dry.mean(),
        "mann_whitney_u": statistic,
        "p_value": p_value
    })

    wet_dry_data.append(city) # keep the labeled city data so all the cities can be plotted together


mann_whitney_results = pd.DataFrame(mann_whitney_rows) # convert the test summaries into a pandas DF table and save it to TABLE_FOLDER
mann_whitney_results.to_csv(TABLE_FOLDER / "mann_whitney_wet_vs_dry.csv", index=False)

wet_dry_data = pd.concat(wet_dry_data, ignore_index=True) # combine all the city-level wet/dry data into one dataframe so we can plot it in the next step

# Violin plot is used to describe the data returned by the mannwhitneyu stat codes as a visual comparison 

wet_dry_plot = sns.catplot(
    data=wet_dry_data,
    x="precipitation_group",
    y="total_crashes",
    col="municipality",
    col_wrap=2,
    kind="violin",
    order=["DRY", "WET"],
    inner="box",
    height=4
)
wet_dry_plot.set_axis_labels("Month Classification", "Reported Crashes")
wet_dry_plot.fig.suptitle("Crash Distributions in Drier and Wetter Months", y=1.03)
wet_dry_plot.savefig(FIGURE_FOLDER / "wet_vs_dry_violin.png", dpi=300, bbox_inches="tight")
plt.close()