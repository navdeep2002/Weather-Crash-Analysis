import pandas as pd 
from pathlib import Path
assert sys.version_info >= (3, 8) # just to make sure the TA or professor, or any other professional has the minimum python requirements

# 1.) we will first globally declare our file locations and the constants we will be using for cleaning our data 

RAW_DATA = Path("raw_data")
ICBC_FOLDER = RAW_DATA/"icbc"
WEATHER_FOLDER = RAW_DATA/"weather"
CLEANED_FOLDER = Path("cleaned_data")

ICBC_FILE = ICBC_FOLDER/"ICBC (new) Lower Mainland Data - RAW.csv"
POLICE_FILE = ICBC_FOLDER/"ICBC reported crashes 2021-2024.csv"

# The years we would be basing our report on is from 2021 to 2024

YEARS = [2021, 2022, 2023, 2024]

# we will be looking at 4 municipalities in the lower mainland

MUNICIPALITIES = ["VANCOUVER", "RICHMOND", "DELTA", "ABBOTSFORD"]

# we will create a sort of hash table (key:value) pair thing for the months because our datasets have the months by number and not by name

MONTH_NUMBERS = {
  "JANUARY": 1, 
  "FEBRUARY": 2,
  "MARCH": 3,
  "APRIL": 4,
  "MAY": 5,
  "JUNE": 6,
  "JULY": 7,
  "AUGUST": 8,
  "SEPTEMBER": 9,
  "OCTOBER": 10,
  "NOVEMBER": 11,
  "DECEMBER": 12,
}

# we created 2 helper functions for changing column names to uppercase and also determining which city a weather file represents

def clean_text_columns(data, columns):

  # using a for loop we will remove trailing spaces, and rename the column names to uppercase
  # we will not remove any missing values because even missing values can affect the bias of data, as taught in lectures

  for column in columns:
    data[column] = (data[column].astype("string").str.strip().str.upper())

    return data


def city_from_weather_filename(filename):

  # we will determine which municipality the weather file represents using some if statements
  # I decided to make this a separate helper function in order to not clutter up the code, if I hadn't
  # I included the space after city names just because the raw data set filenames have a space after the city name

  if filename.startswith("Van "):

    return "VANCOUVER"

    if filename.startswith("Richmond "):

      return "RICHMOND"

    if filename.startswith("Delta "):

      return "DELTA"

    if filename.startswith("Abbotsford "):

      return "ABBOTSFORD"

    raise ValueError(f"Unknown weather filename: {filename}") # this is basically the else clause but for a ValueError for error handling

