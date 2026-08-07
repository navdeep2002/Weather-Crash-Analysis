import pandas as pd
from pathlib import Path


CLEANED_FOLDER = Path("cleaned_data")

MUNICIPALITIES = [
    "VANCOUVER",
    "RICHMOND",
    "DELTA",
    "ABBOTSFORD",
]

YEARS = [2021, 2022, 2023, 2024]

MONTHLY_KEYS = ["municipality", "year", "month"]


# ---------------------------------------------------------
# Load cleaned files
# ---------------------------------------------------------

icbc_clean = pd.read_csv(CLEANED_FOLDER / "icbc_clean.csv")
icbc_monthly = pd.read_csv(CLEANED_FOLDER / "icbc_monthly.csv")

police = pd.read_csv(
    CLEANED_FOLDER / "police_crashes_clean.csv"
)

weather_daily = pd.read_csv(
    CLEANED_FOLDER / "weather_daily_clean.csv"
)

weather_monthly = pd.read_csv(
    CLEANED_FOLDER / "weather_monthly.csv"
)

combined = pd.read_csv(
    CLEANED_FOLDER / "combined_monthly.csv"
)


# ---------------------------------------------------------
# 1. Verify complete monthly coverage
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("MONTHLY COVERAGE")
print("=" * 80)

expected = pd.MultiIndex.from_product(
    [MUNICIPALITIES, YEARS, range(1, 13)],
    names=MONTHLY_KEYS,
)

for name, df in [
    ("ICBC monthly", icbc_monthly),
    ("Weather monthly", weather_monthly),
    ("Combined monthly", combined),
]:
    actual = pd.MultiIndex.from_frame(df[MONTHLY_KEYS])

    missing = expected.difference(actual)
    extra = actual.difference(expected)

    print(f"\n{name}:")
    print(f"Rows: {len(df)}")
    print(f"Missing expected months: {len(missing)}")
    print(f"Unexpected months: {len(extra)}")
    print(
        f"Duplicate monthly keys: "
        f"{df.duplicated(MONTHLY_KEYS).sum()}"
    )


# ---------------------------------------------------------
# 2. Inspect missing monthly weather
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("MONTHS WITH MISSING WEATHER")
print("=" * 80)

weather_columns = [
    "mean_temp_c",
    "mean_max_temp_c",
    "mean_min_temp_c",
    "total_precip_mm",
]

missing_weather = weather_monthly[
    weather_monthly[weather_columns].isna().any(axis=1)
]

print(
    missing_weather[
        MONTHLY_KEYS
        + weather_columns
        + [
            "measurable_precip_days",
            "freezing_days",
            "valid_temperature_days",
            "valid_precipitation_days",
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 3. Check weather observation coverage
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("WEATHER OBSERVATION COVERAGE")
print("=" * 80)

coverage = weather_monthly.copy()

coverage["days_in_month"] = coverage.apply(
    lambda row: pd.Period(
        year=int(row["year"]),
        month=int(row["month"]),
        freq="M",
    ).days_in_month,
    axis=1,
)

coverage["temperature_coverage"] = (
    coverage["valid_temperature_days"]
    / coverage["days_in_month"]
)

coverage["precipitation_coverage"] = (
    coverage["valid_precipitation_days"]
    / coverage["days_in_month"]
)

print("\nMinimum valid days by municipality:")

print(
    coverage.groupby("municipality")[
        [
            "valid_temperature_days",
            "valid_precipitation_days",
        ]
    ].min()
)

print("\nMonths with less than 80% temperature coverage:")

low_temperature = coverage[
    coverage["temperature_coverage"] < 0.80
]

print(
    low_temperature[
        MONTHLY_KEYS
        + [
            "valid_temperature_days",
            "days_in_month",
            "temperature_coverage",
        ]
    ].to_string(index=False)
)

print("\nMonths with less than 80% precipitation coverage:")

low_precipitation = coverage[
    coverage["precipitation_coverage"] < 0.80
]

print(
    low_precipitation[
        MONTHLY_KEYS
        + [
            "valid_precipitation_days",
            "days_in_month",
            "precipitation_coverage",
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 4. Check for potentially misleading zero indicators
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("ZERO-OBSERVATION WEATHER CHECK")
print("=" * 80)

no_precip_data = weather_monthly[
    weather_monthly["valid_precipitation_days"] == 0
]

print("\nMonths with zero valid precipitation observations:")
print(
    no_precip_data[
        MONTHLY_KEYS
        + [
            "total_precip_mm",
            "measurable_precip_days",
            "valid_precipitation_days",
        ]
    ].to_string(index=False)
)

no_temp_data = weather_monthly[
    weather_monthly["valid_temperature_days"] == 0
]

print("\nMonths with zero valid temperature observations:")
print(
    no_temp_data[
        MONTHLY_KEYS
        + [
            "mean_temp_c",
            "freezing_days",
            "valid_temperature_days",
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 5. Summary statistics
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("MONTHLY SUMMARY STATISTICS")
print("=" * 80)

summary_columns = [
    "total_crashes",
    "total_victims",
    "casualty_crashes",
    "pedestrian_crashes",
    "cyclist_crashes",
    "motorcycle_crashes",
    "mean_temp_c",
    "mean_max_temp_c",
    "mean_min_temp_c",
    "total_precip_mm",
    "measurable_precip_days",
    "freezing_days",
]

print(
    combined[summary_columns]
    .describe()
    .T[
        [
            "count",
            "mean",
            "std",
            "min",
            "25%",
            "50%",
            "75%",
            "max",
        ]
    ]
)


# ---------------------------------------------------------
# 6. Impossible-value checks
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("IMPOSSIBLE / SUSPICIOUS VALUE CHECKS")
print("=" * 80)

checks = {
    "Negative crashes":
        (combined["total_crashes"] < 0),

    "Negative victims":
        (combined["total_victims"] < 0),

    "Casualty crashes greater than total crashes":
        (
            combined["casualty_crashes"]
            > combined["total_crashes"]
        ),

    "Pedestrian crashes greater than total crashes":
        (
            combined["pedestrian_crashes"]
            > combined["total_crashes"]
        ),

    "Cyclist crashes greater than total crashes":
        (
            combined["cyclist_crashes"]
            > combined["total_crashes"]
        ),

    "Motorcycle crashes greater than total crashes":
        (
            combined["motorcycle_crashes"]
            > combined["total_crashes"]
        ),

    "Negative precipitation":
        (combined["total_precip_mm"] < 0),

    "Wet days greater than valid precipitation days":
        (
            combined["measurable_precip_days"]
            > combined["valid_precipitation_days"]
        ),

    "Freezing days greater than valid temperature days":
        (
            combined["freezing_days"]
            > combined["valid_temperature_days"]
        ),
}

for description, condition in checks.items():
    print(f"{description}: {condition.sum()}")


# ---------------------------------------------------------
# 7. Exact duplicate rows
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("EXACT DUPLICATE ROW CHECK")
print("=" * 80)

for name, df in [
    ("ICBC clean", icbc_clean),
    ("Police crashes", police),
    ("Weather daily", weather_daily),
]:
    print(
        f"{name}: {df.duplicated().sum()} "
        "exact duplicate rows"
    )


# ---------------------------------------------------------
# 8. Verify ICBC monthly aggregation
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("ICBC MONTHLY AGGREGATION CHECK")
print("=" * 80)

crash_columns = [
    "total_crashes",
    "total_victims",
    "casualty_crashes",
    "pedestrian_crashes",
    "cyclist_crashes",
    "motorcycle_crashes",
]

recalculated = (
    icbc_clean
    .groupby(MONTHLY_KEYS, as_index=False)[crash_columns]
    .sum()
)

comparison = icbc_monthly.merge(
    recalculated,
    on=MONTHLY_KEYS,
    suffixes=("_saved", "_recalculated"),
)

differences = 0

for column in crash_columns:
    differences += (
        comparison[f"{column}_saved"]
        != comparison[f"{column}_recalculated"]
    ).sum()

print(
    "Differences between saved monthly totals "
    f"and recalculated totals: {differences}"
)

print("\nCrash totals by municipality and year:")

print(
    icbc_monthly
    .groupby(["municipality", "year"])[
        ["total_crashes", "total_victims"]
    ]
    .sum()
)


# ---------------------------------------------------------
# 9. Police UNKNOWN-category audit
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("POLICE UNKNOWN CATEGORY CHECK")
print("=" * 80)

categorical_columns = police.select_dtypes(
    include="object"
).columns

for column in categorical_columns:
    values = police[column].astype("string")

    unknown_count = (
        values
        .str.contains("UNKNOWN", case=False, na=False)
        .sum()
    )

    if unknown_count > 0:
        percentage = unknown_count / len(police) * 100

        print(
            f"{column}: {unknown_count} "
            f"({percentage:.2f}%)"
        )


print("\nReported weather categories:")
print(police["reported_weather"].value_counts())

print("\nRoad condition categories:")
print(police["road_condition"].value_counts())


print("\nAudit complete.")