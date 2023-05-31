# Master_thesis

This repository includes all of the Python scripts used for the master thesis "Impact of Wind Turbines on Local and Regional Winds Across Denmark" by Bianca E. Sandvik delivered 31. May 2023. 


 Most of the scripts build heavliy on each other and should be run in the following order:

1. Data collection and data processing
   - geostrophic_wind.py       
   - template_dmi_download_superloop.py
2. Merging of datasets
   - merge_dmi_data_ERA5.py  
3. Calculation of alpha
   - ageostrophic_wind.py
4. Generation of plots
   - dmi_era5_plotting.py
   - DMI_stations_map.py
   - significant_stations_map.py
   - era5_wind_field.py
5. Statistical analysis and plots for parts of the time series (before and after move for stations)
   - dmi_era5_stat.py
