## The clean_data.py now outputs the correct cleaned versions that we needed. the output is below:

Expected monthly rows: 192
ICBC monthly rows: 192
Weather monthly rows: 192
Combined monthly rows: 192

Cleaning complete.
Clean ICBC rows: 309,750
Clean police-reported rows: 12,230
Clean weather rows: 5,844
Files saved in: cleaned_data

there were some bugs such as:

- raw data for delta climate for 2021 was accidentally downloaded as a 2026 dataset, and had only half the years data
- our helper functions were somehow wrongfully indented, that was also fixed
- apparently for the richmond nature park station, 2023 data for the last 2 months, and all of 2024, had the weather data missing,
  therefore, I needed to use the YVR airport weather station for richmond. using YVR station was feasible because it's only 7km away from 
  the richmond nature park station data I was using initially. 
  * I have replaced those initial datasets with the newer YVR ones. the old ones were put into a subfolder under weather called "deprecated_raw_datasets"

  

