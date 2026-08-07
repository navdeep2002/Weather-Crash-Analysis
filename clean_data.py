import pandas as pd 
from pathlib import Path
import sys 
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
  "DECEMBER": 12
}

# we created 2 helper functions for changing column names to uppercase and also determining which city a weather file represents

def clean_text_columns(data, columns):

  # using a for loop we will remove trailing spaces, and uppercase the column values to uppercase
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


# 2.) import the icbc raw datasets (lower mainland data and police reported crashes), and then clean them

icbc_columns = [ 
  "Date Of Loss Year",
  "Month Of Year",
  "Municipality Name (ifnull)",
  "Crash Severity",
  "Day Of Week",
  "Derived Crash Configuration",
  "Intersection Crash",
  "Time Category",
  "Animal Flag",
  "Cyclist Flag",
  "Heavy Veh Flag",
  "Motorcycle Flag",
  "Pedestrian Flag",
  "Total Crashes",
  "Total Victims"
]

icbc_data = pd.read_csv(ICBC_FILE, usecols = icbc_columns, low_memory=False) # low memory, if true, processed the file in chucks. I set it to false to remove any possibility of mixed type inferences (Pandas documentation)

# in the process of cleaning, I would also want to rename the columns so they are descriptive enough to know what happens and viewable in the dataframe, conventionally with underscore characters
# the left side of the (:) is what it is in the raw dataset, and the right is what I would want to rename it. applies to all columns

icbc_data = icbc_data.rename(
  columns={
    "Date Of Loss Year": "year",
    "Month Of Year": "month_name",
    "Municipality Name (ifnull)": "municipality",
    "Crash Severity": "crash_severity",
    "Day Of Week": "day_of_week",
    "Derived Crash Configuration": "crash_configuration",
    "Intersection Crash": "intersection_crash",
    "Time Category": "time_category",
    "Animal Flag": "animal_involved",
    "Cyclist Flag": "cyclist_involved",
    "Heavy Veh Flag": "heavy_vehicle_involved",
    "Motorcycle Flag": "motorcycle_involved",
    "Pedestrian Flag": "pedestrian_involved",
    "Total Crashes": "total_crashes",
    "Total Victims": "total_victims"
  }
)

icbc_text_columns = [
  "month_name",
  "municipality",
  "crash_severity",
  "day_of_week",
  "crash_configuration",
  "intersection_crash",
  "time_category",
  "animal_involved",
  "cyclist_involved",
  "heavy_vehicle_involved",
  "motorcycle_involved",
  "pedestrian_involved"
]

icbc_data = clean_text_columns(icbc_data, icbc_text_columns) # called the helper function on this to uppercase the values and remove any trailing spaces

# now that rename and uppercasing is done, we now need to convert the year, month, crash count, and victim count to numerical values to be used for analysis and testing
# when errors is set to coerce, then invalid parsing is set to NaN (pandas to_numeric() docs)

icbc_data["year"] = pd.to_numeric(icbc_data["year"], errors="coerce").astype("Int64") 
icbc_data["month"] = (icbc_data["month_name"].map(MONTH_NUMBERS).astype("Int64"))
icbc_data["total_crashes"] = pd.to_numeric(icbc_data["total_crashes"], errors="coerce")
icbc_data["total_victims"] = pd.to_numeric(icbc_data["total_victims"], errors="coerce")

icbc_data = icbc_data.drop(columns="month_name") # drop the column with name = month_name, since we created the numeric month earlier, month_name is no loner needed

# although our data is in the year range we specified at the top and the municipalities, I decided to add the code to filter for that for error handling

icbc_data = icbc_data[icbc_data["year"].isin(YEARS) & icbc_data["municipality"].isin(MUNICIPALITIES)].copy()

# in the nex step of the data cleaning process, we need to ensure that we drop any rows that does not have corresponding month, year, municipality, or crash count, as
# that is information that is needed and important

icbc_data = icbc_data.dropna(subset=["year", "month", "municipality", "total_crashes"])

# another error handling procedure would be to handle invalid counts, such as negative numbers. we need to ensure the cleaned data we use is 0 or above

icbc_data = icbc_data[(icbc_data["total_crashes"] >=0 ) & (

  icbc_data["total_victims"].isna() | (icbc_data["total_victims"] >= 0) # isna() detects any missing values and returns a boolean. here we are checking if the count is NA or negative

)].copy()


# for specific vehicle collision categories, I would need to create the counts for those. this will primarily be done using .where() and comparisons 

icbc_data["casualty_crashes"] = icbc_data["total_crashes"].where(
    icbc_data["crash_severity"] == "CASUALTY CRASH",
    0
) # out of all crashes, crashes flagged with casualty will count as a "casualty_crashes" (such is the same logic for the bottom 3)

icbc_data["pedestrian_crashes"] = icbc_data["total_crashes"].where(
    icbc_data["pedestrian_involved"] == "YES",
    0
)

icbc_data["cyclist_crashes"] = icbc_data["total_crashes"].where(
    icbc_data["cyclist_involved"] == "YES",
    0
)

icbc_data["motorcycle_crashes"] = icbc_data["total_crashes"].where(
    icbc_data["motorcycle_involved"] == "YES",
    0
)


# 3.) now we take the main icbc data and aggregate it by month , for this we would use groupby() with agg(), and then sort the values 

icbc_monthly = (
  icbc_data.groupby(
    [
      'municipality', 
      'year', 
      'month'
    ], as_index=False
  ) 
  .agg(
    total_crashes=("total_crashes", "sum"),
    total_victims=("total_victims", "sum"),
    casualty_crashes=("casualty_crashes", "sum"),
    pedestrian_crashes=("pedestrian_crashes", "sum"),
    cyclist_crashes=("cyclist_crashes", "sum"),
    motorcycle_crashes=("motorcycle_crashes", "sum")
  )
  .sort_values(
    [
      'municipality', 
      'year', 
      'month'
    ]
  )
)


# 4.) repeat the above code process with Police-Reported ICBC Data

police_columns = [
    "Municipality",
    "Year",
    "Accident Type",
    "Collision Type",
    "Crash Configuration",
    "Cyclist Involved",
    "Hit And Run Indicator",
    "Impact With Animal",
    "Month",
    "Motorcycle Involved",
    "Pedestrian Involved",
    "Region",
    "Road Condition",
    "Weather",
    "Crash Count",
    "Total Casualty",
    "Total Vehicles Involved"
]

# read the police reported csv and store it in a pandas dataframe named police_data

police_data = pd.read_csv(
  POLICE_FILE,
  usecols=police_columns, 
  low_memory=False
)

police_data = police_data.rename(
  columns = { 
    "Municipality": "municipality",
    "Year": "year",
    "Accident Type": "accident_type",
    "Collision Type": "collision_type",
    "Crash Configuration": "crash_configuration",
    "Cyclist Involved": "cyclist_involved",
    "Hit And Run Indicator": "hit_and_run",
    "Impact With Animal": "animal_involved",
    "Month": "month_name",
    "Motorcycle Involved": "motorcycle_involved",
    "Pedestrian Involved": "pedestrian_involved",
    "Region": "region",
    "Road Condition": "road_condition",
    "Weather": "reported_weather",
    "Crash Count": "crash_count",
    "Total Casualty": "total_casualties",
    "Total Vehicles Involved": "total_vehicles"
  }
)

police_text_columns = [
  "municipality",
  "accident_type",
  "collision_type",
  "crash_configuration",
  "cyclist_involved",
  "hit_and_run",
  "animal_involved",
  "month_name",
  "motorcycle_involved",
  "pedestrian_involved",
  "region",
  "road_condition",
  "reported_weather"
]


police_data = clean_text_columns(police_data, police_text_columns)

police_data["year"] = pd.to_numeric(police_data["year"], errors="coerce").astype("Int64")
police_data["month"] = (police_data["month_name"].map(MONTH_NUMBERS).astype("Int64"))
police_data["crash_count"] = pd.to_numeric(police_data["crash_count"], errors="coerce")
police_data["total_casualties"] = pd.to_numeric(police_data["total_casualties"], errors="coerce")
police_data["total_vehicles"] = pd.to_numeric(police_data["total_vehicles"], errors="coerce")

police_data = police_data.drop(columns="month_name")

police_data = police_data[police_data["year"].isin(YEARS) & police_data["municipality"].isin(MUNICIPALITIES)].copy()

police_data = police_data.dropna(
  subset=[
    "municipality",
    "year",
    "month",
    "crash_count",
  ]
)

# I chose to leave the police reported crash dataset categories which will be useful, ungrouped, because it would get lost or jumbled up
# during the municipality, year, month, aggregation. later on when we do the analysis and apply the tests and visualization, at that point
# if the question im answering needs it to be aggregated, I can do it at that point
#___________________________________________________________________________________________________________________________________________________

# 5.) Now we will import and combine the weather data which is spanned across 4 cities and years spanning 2021-2024. cleaning next


weather_files = sorted(WEATHER_FOLDER.glob("*.csv")) # glob module finds files and directories that match the given style. kind of like regex. ???? is for the different years. I search on google, "how to import files with similar names into python code without passing them in as sys arguments"
# 'file_path.glob("*")' this is for finding all matching files, the sorts a list to weather_files variable 

if len(weather_files) != 16:
  raise ValueError(
    f"expected 16 weather CSV files, found {len(weather_files)}"
  ) # error handling, since we only have 16 weather dataset files 

weather_columns = [
  "Station Name",
  "Climate ID",
  "Date/Time",
  "Year",
  "Month",
  "Day",
  "Max Temp (°C)",
  "Min Temp (°C)",
  "Mean Temp (°C)",
  "Total Precip (mm)",
  "Total Precip Flag"
]

weather_frames = [] # declare / initialize an empty list

# use a for loop to go through the 16 CSV files to append and concatenate them: 
for weather_file in weather_files:
  city_weather = pd.read_csv(weather_file, usecols=weather_columns)

  city_weather["municipality"] = city_from_weather_filename(weather_file.name) # get the file name and then create a new dataframe column for that municipality

  weather_frames.append(city_weather) # append all the files into a single collection item

weather_data = pd.concat(weather_frames, ignore_index=True) 

weather_data = weather_data.rename(
  columns = {
    "Station Name": "station_name",
    "Climate ID": "climate_id",
    "Date/Time": "date",
    "Year": "year",
    "Month": "month",
    "Day": "day",
    "Max Temp (°C)": "max_temp_c",
    "Min Temp (°C)": "min_temp_c",
    "Mean Temp (°C)": "mean_temp_c",
    "Total Precip (mm)": "total_precip_mm",
    "Total Precip Flag": "precipitation_flag"
  }
)


# 6.) Clean the weather data which we already combined and imported

weather_data["station_name"] = (weather_data["station_name"].astype("string").str.strip().str.upper())
weather_data["precipitation_flag"] = (weather_data["precipitation_flag"]
    .astype("string")
    .str.strip()
    .str.upper()
)

weather_data["date"] = pd.to_datetime(weather_data["date"], errors="coerce") # convert the date time in the file, if the parsing is invalid, then the value is set to NaT

weather_numeric_columns = [
  "year",
  "month",
  "day",
  "max_temp_c",
  "min_temp_c",
  "mean_temp_c",
  "total_precip_mm"
]

# using the weather_numeric_columns list we have above, use a for loop to convert all the values to numerics for those columns. replace with NaN or Nat if invalid
for column in weather_numeric_columns:
  weather_data[column] = pd.to_numeric(weather_data[column], errors="coerce")

weather_data = weather_data[weather_data["year"].isin(YEARS) & weather_data["municipality"].isin(MUNICIPALITIES)].copy() #copy() makes a new separate changeable obj in a new mem location

# remove the rows with invalid date or missing join fields from the datasets
weather_data = weather_data.dropna(
  subset = [ 
    "date",
    "year",
    "month",
    "municipality"
  ]
)

# we will need to ensure that any negative precipitation values are handled as invalid, because negative precip numbers just dont exist
weather_data.loc[weather_data["total_precip_mm"] < 0, "total_precip_mm"] = pd.NA

# Keep the missing measurements as missing rather than imputing them, anything that is above 0 is going to be converted to int64
weather_data["measurable_precip_day"] = (weather_data["total_precip_mm"] > 0).astype("Int64")
weather_data.loc[weather_data["total_precip_mm"].isna(), "measurable_precip_day"] = pd.NA

weather_data["freezing_day"] = (weather_data["min_temp_c"] < 0).astype("Int64") # freezing day would be considered with a number less than 0 degrees celsius
weather_data.loc[weather_data["min_temp_c"].isna(), "freezing_day"] = pd.NA


# 6.) aggregate the weather data by months. the weather data has the mean max and min temps, total precips, and then freezing temp data

# group the data and then aggregate them and apply mean functions on them, sum the precipitation across all days for each month, and then count the number of days
# where the temperature and precipitation was valid. then sort the  values by the stated column labels

weather_monthly = (
    weather_data.groupby(["municipality", "year", "month"], as_index=False)
    .agg(
        mean_temp_c=("mean_temp_c", "mean"),
        mean_max_temp_c=("max_temp_c", "mean"),
        mean_min_temp_c=("min_temp_c", "mean"),
        total_precip_mm=("total_precip_mm", lambda values: values.sum(min_count=1)), # the reason i needed to use lambda here was because for each city-year-month group, it sums the values in the total_precip_mm 
        # the lambda is the equvalent of defining a function , in our case it would take the variable values, and then return the sum of all values in values
        # min_count=1 is needed because it will only sum values that are minimum 1 milimetre and anything less than that is considered NaN which wouldn't be counted. replacing it with zero but incur a bias in the data which I dont need or want to deal with
      
        measurable_precip_days=("measurable_precip_day", "sum"),
        freezing_days=("freezing_day", "sum"),
        valid_temperature_days=("mean_temp_c", "count"),
        valid_precipitation_days=("total_precip_mm", "count")
    )
    .sort_values(["municipality", "year", "month"])
)


# 7.) join the monthly icbc datasets and the weather datasets before exporting them in the last step

combined_monthly = icbc_monthly.merge(weather_monthly, on=["municipality", "year", "month"], how="inner") #join the two datasets
combined_monthly = combined_monthly.sort_values(["municipality", "year", "month"])

expected_months = (len(MUNICIPALITIES) * len(YEARS) * 12) #this should produce 192 months

# Confirm that every expected municipality-month was joined
if len(combined_monthly) != expected_months:
  raise ValueError(
    f"Expected {expected_months} combined monthly rows, "
    f"but found {len(combined_monthly)}."
  )

# test print statement

print(f"Expected monthly rows: {expected_months}")
print(f"ICBC monthly rows: {len(icbc_monthly)}")
print(f"Weather monthly rows: {len(weather_monthly)}")
print(f"Combined monthly rows: {len(combined_monthly)}")


# 8.) this is the last step in the cleaning data pipeline where we would now export the cleaned data to new folders (much of this code is adapted from lectures and exercises)

CLEANED_FOLDER.mkdir(exist_ok=True) # make a directory file in our project folder called "cleaned_data"

icbc_data.to_csv(CLEANED_FOLDER / "icbc_clean.csv", index=False)

icbc_monthly.to_csv(CLEANED_FOLDER / "icbc_monthly.csv", index=False)

police_data.to_csv(CLEANED_FOLDER / "police_crashes_clean.csv", index=False)

weather_data.to_csv(CLEANED_FOLDER / "weather_daily_clean.csv", index=False)

weather_monthly.to_csv(CLEANED_FOLDER / "weather_monthly.csv", index=False)

combined_monthly.to_csv(CLEANED_FOLDER / "combined_monthly.csv", index=False)

# test print statements 

print("\nCleaning complete.")
print(f"Clean ICBC rows: {len(icbc_data):,}")
print(f"Clean police-reported rows: {len(police_data):,}")
print(f"Clean weather rows: {len(weather_data):,}")
print(f"Files saved in: {CLEANED_FOLDER}")


