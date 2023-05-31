##### Merge DMI data with ERA5 data #####
## Author: Bianca E. Sandvik (March 2023)

## This script merges DMI data with ERA5 data for each individual station. The closest gridpoint in the ERA5 dataset is coupled to 
## the DMI data based on nearest longitude and latitude coordinates. The script takes the monthly and yearly means for each station
## and saves them to individual parquet-files with the DMI-station location.
## The output-files contain means with: time, DMI-station longitude and latitude coordinates, DMI wind speed, DMI wind direction, 
## ERA5 geostrophic wind components (ug and vg), ERA5 wind speed, and ERA5 wind direction.

# Import packages:
import netCDF4 as nc
import pandas as pd
import numpy as np
import fastparquet as parq          # For saving generated files to parquet-format
import glob                         # For searching files in current directory
import xarray as xr                 # For converting netCDF-files to dataset

# Import ERA5 datafile:
fn = '/Users/Bianca/Desktop/Thesis_data/ERA5_ug_vg_wind_speed_wind_dir.nc'
ERA5 = nc.Dataset(fn, 'r')


# Define list of DMI stations:
stationlist = [('06041', 'Skagen_Fyr'),('06052' ,"Thyborøn"), ('06058', "Hvide_Sande"), ('06079', "Anholt_Havn"), 
    ('06080', "Esbjerg_Lufthavn"), ('06081', "Blåvandshuk_Fyr"), ('06096', "Rømø/Juvre"), ('06104', "Billund_Lufthavn"),
    ('06108', "Kolding_Lufthavn"), ('06116', "Store_Jyndevad"), ('06119', "Kegnæs_Fyr"), ('06120', "H._C._Andersen_Airport"), 
    ('06124', "Sydfyns_Flyveplads"), ('06149', "Gedser"), ('06151', "Omø_Fyr"), ('06156', "Holbæk_Flyveplads"), ('06159', "Røsnæs_Fyr"), 
    ('06168', "Nakkehoved_Fyr"), ('06169', "Gniben"), ('06170', "Roskilde_Lufthavn"), ('06180', "Københavns_Lufthavn"), 
    ('06181', "Jægersborg"), ('06183', "Drogden_Fyr"), ('06190', "Bornholms_Lufthavn"), ('06193', "Hammer_Odde_Fyr")]

DMIstations = pd.DataFrame (stationlist, columns = ['Station_ID', 'Station_name'])       #create dataframe with list station ID and Station_name
#print (DMIstations)

st_ID = list(DMIstations['Station_ID'])                                 #create list of all station IDs

for station in st_ID:
    glob_string = 'dmi_data_' + station + '.parq.gzip'                  #Create a dynamic string for input to search for station specific parquet-files
    dmi_ERA5_zip = glob.glob(glob_string)                                   #Find station specific parquet-files in current directory
    for i in dmi_ERA5_zip:
        DMI_parq = pd.read_parquet(i)                                   #Read and print parquet-file
        #print(DMI_parq)

        # Define longitude and lattude coordinates for DMI data:
        DMI_parq['Longitude, Latitude'].bfill(inplace=True)             #backward fill lon-/lat-values where None-values are present
        DMI_parq['Longitude, Latitude'].ffill(inplace=True)             #forward fill lon-/lat-values where None-values are present
            #Filling of missing location values are necessary to avoid TypeError.
        lon_dmi = DMI_parq['Longitude, Latitude'][0][0]                                             #starting position
        lat_dmi = DMI_parq['Longitude, Latitude'][0][1]
        lon_dmi_end = DMI_parq['Longitude, Latitude'][len(DMI_parq['Longitude, Latitude'])-1][0]    #ending position
        lat_dmi_end = DMI_parq['Longitude, Latitude'][len(DMI_parq['Longitude, Latitude'])-1][1]

        # Convert ERA5 data as xarray and select data from ERA5 that has the nearest location to the DMI data:
        ERA5_xr = xr.open_dataset('ERA5_ug_vg_wind_speed_wind_dir.nc') 
        ERA5_st = ERA5_xr.sel(lon=lon_dmi, lat=lat_dmi, method="nearest")                #select ERA5-data based on DMI station´s first location
        ERA5_st_end = ERA5_xr.sel(lon=lon_dmi_end, lat=lat_dmi_end, method="nearest")    #select ERA5-data based on DMI station´s final location

        #Control if a change in location changes the "corresponding" ERA5 grid 
        if ERA5_st == ERA5_st_end:                                            
            print('Corresponding ERA5 grid location is unchanged for station:', station)
        else: 
            print('WARNING! Corresponding ERA5 grid location is changed for station:', station)
            break

        # Convert xarray to pandas DataFrame and sort by descending time:
        ERA5_st_pd = ERA5_st.to_pandas().sort_values('time', ascending=False)

        ## Create monthly and yearly means for ERA5 station data:
        ERA5_st_monthly = ERA5_st_pd.resample('M').mean()               #create monthly means of all variables
        ERA5_st_yearly = ERA5_st_pd.resample('Y').mean()                #create monthly means of all variables
        #era_month = ERA5_st_pd[0:744].mean()                               #control for last month and year
        #era_yr = ERA5_st_pd[0:8760].mean()

        ## Create monthly and yearly means for DMI station data:
        DMI_parq.set_index('Time', inplace=True)                        #set time as index
        DMI_parq.index = pd.to_datetime(DMI_parq.index)                 #convert time to datetime

        # Create lists to hold separate longitude and latitude variables from DMI station data:
            #This is necessary to keep the location when we take the mean.
        lon_list = []
        for i in range(len(DMI_parq['Longitude, Latitude'])):
            longitude = DMI_parq['Longitude, Latitude'][i][0]           #Append the 1st entry in the lon/lat-list
            lon_list.append(longitude) 

        lat_list = []
        for i in range(len(DMI_parq['Longitude, Latitude'])):
            latitude = DMI_parq['Longitude, Latitude'][i][1]           #Append the 2nd entry in the lon/lat-list
            lat_list.append(latitude) 

        # Create new columns containing our new longitude and latitude lists:
        DMI_parq.insert(1, 'DMI_Lon', lon_list)
        DMI_parq.insert(2, 'DMI_Lat', lat_list)

        DMI_parq = DMI_parq.rename(columns={"Wind speed": "DMI_wind_speed", "Wind direction": "DMI_wind_dir"})   #rename columns

        # Create DMI datasets with means:
        dmi_st_monthly = DMI_parq.resample('M').mean()              #create monthly means of all variables
        dmi_st_yearly = DMI_parq.resample('Y').mean()               #create yearly means of all variables
        #dmi_month = DMI_parq[0:4464].mean()                            #control for last month and year
        #dmi_yr = DMI_parq[0:52560].mean()


        ### Insert ERA5-variables into new columns in the DMI datasets and store as parquet-files:
        ## Monthly:
        dmi_st_monthly['ERA5_ug'] = list(ERA5_st_monthly['ug'])
        dmi_st_monthly['ERA5_vg'] = list(ERA5_st_monthly['vg'])
        dmi_st_monthly['ERA5_wind_speed'] = list(ERA5_st_monthly['wind_speed'])
        dmi_st_monthly['ERA5_wind_dir'] = list(ERA5_st_monthly['wind_dir'])

        # Store as parquet-file: 
        namegenerator_parq = 'DMI_ERA5_' + station + '_monthly.parq.gzip'       #Create dynamic naming based on station ID for parquet-file
        dmi_st_monthly.to_parquet(namegenerator_parq, compression='gzip')       #Create station specific parquet-file

        print_parquet_month = pd.read_parquet(namegenerator_parq)               #Print
        print('Printing monthly means for station', station, ':')
        print_parquet_month


        ## Yearly:
        dmi_st_yearly['ERA5_ug'] = list(ERA5_st_yearly['ug'])
        dmi_st_yearly['ERA5_vg'] = list(ERA5_st_yearly['vg'])
        dmi_st_yearly['ERA5_wind_speed'] = list(ERA5_st_yearly['wind_speed'])
        dmi_st_yearly['ERA5_wind_dir'] = list(ERA5_st_yearly['wind_dir'])
        
        # Store as parquet-file: 
        namegenerator_parq = 'DMI_ERA5_' + station + '_yearly.parq.gzip'        #Create dynamic naming based on station ID for parquet-file
        dmi_st_yearly.to_parquet(namegenerator_parq, compression='gzip')        #Create station specific parquet-file

        print_parquet_year = pd.read_parquet(namegenerator_parq)                #Print
        print('Printing yearly means for station', station, ':')
        print_parquet_year


