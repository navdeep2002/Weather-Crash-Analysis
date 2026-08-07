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