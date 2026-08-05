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

