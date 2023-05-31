##### Downloading DMI-data #####
## Author: Bianca E. Sandvik (March 2023)

## This script imports data from DMIs API for a list of stations and parameters, merges defined 5-year periods and saves it locally
## as individual parquet files. 
## The second part of this script inserts missing values as NaNs, creates a new dataframe holding all of the imported parameters and 
## and saves the resulting dataframes as parquet files locally . 
## Note: The script is customised towards importing wind speed and wind direction from 1990-2022, but can be adjusted for other uses.



# Import packages:
import requests                     # For making web requests
import pandas as pd
import numpy as np
from DMI_API import API_key         # Import API-key from DMI_API-script
import fastparquet as parq          # For saving generated files to parquet-format
import glob                         # For searching files in current directory



### Create request string for DMIs API service:

# Create basic string fragments:
API = '&api-key=' + API_key
base_url = 'https://dmigw.govcloud.dk/v2/metObs/collections/observation'
limit = '/items?limit=300000'                      #maximum number of returned observations

## Set adjustables:

# Define list of DMI stations:
stationlist = [('06041', 'Skagen_Fyr'),('06052' ,"Thyborøn"), ('06058', "Hvide_Sande"), ('06079', "Anholt_Havn"), 
    ('06080', "Esbjerg_Lufthavn"), ('06081', "Blåvandshuk_Fyr"), ('06096', "Rømø/Juvre"), ('06104', "Billund_Lufthavn"),
    ('06108', "Kolding_Lufthavn"), ('06116', "Store_Jyndevad"), ('06119', "Kegnæs_Fyr"), ('06120', "H._C._Andersen_Airport"), 
    ('06124', "Sydfyns_Flyveplads"), ('06149', "Gedser"), ('06151', "Omø_Fyr"), ('06156', "Holbæk_Flyveplads"), ('06159', "Røsnæs_Fyr"), 
    ('06168', "Nakkehoved_Fyr"), ('06169', "Gniben"), ('06170', "Roskilde_Lufthavn"), ('06180', "Københavns_Lufthavn"), 
    ('06181', "Jægersborg"), ('06183', "Drogden_Fyr"), ('06190', "Bornholms_Lufthavn"), ('06193', "Hammer_Odde_Fyr")]

DMIstations = pd.DataFrame (stationlist, columns = ['Station_ID', 'Station_name'])       #create dataframe with list station ID and Station_name
#print (DMIstations)

st_ID = list(DMIstations['Station_ID'])     #create list of all station IDs
parameter = ['wind_speed', 'wind_dir']      #define which parameters to import
sort = '&sortorder=observed,DESC'           #sorts request with descending time

start_datetime = '1990-01-01T00:00:00Z'     #Define timespann: from UTC 01.01.1990 at midnight to UTC 31.12.1999 just before midnight
end_datetime =   '2022-12-31T23:59:59Z'

## Define 5 year periods: 
    #Note: We can´t import more than 5 years at a time without risking to exceeding the limit of returned observations.
startdatelist = ['1990-01-01T00:00:00Z', '1995-01-01T00:00:00Z', '2000-01-01T00:00:00Z', '2005-01-01T00:00:00Z', '2010-01-01T00:00:00Z', '2015-01-01T00:00:00Z', '2020-01-01T00:00:00Z']
enddatelist = ['1994-12-31T23:59:59Z', '1999-12-31T23:59:59Z', '2004-12-31T23:59:59Z', '2009-12-31T23:59:59Z', '2014-12-31T23:59:59Z', '2019-12-31T23:59:59Z', '2022-12-31T23:59:59Z']




###### Create request loop ######

wind_speed_df_count = 0                     #Create counters for generated dataframes
wind_dir_df_count = 0
datelist = []                               #Create empty list to contain date periods

# Loop through all times for each station ID and both parameters requesting coresponding data from DMIs API service. 
# Concatenate/merge dataframes with same variable and station and save as individual parquet-file.
for station in st_ID:
    stationID = '&stationId=' + str(station)                    #Create call for station ID
    for p in range(len(parameter)):
        parameterId = '&parameterId=' + parameter[p]
        print(parameterId)
        for i in range(len(startdatelist)):
            datelist.append(startdatelist[i] + '/' + enddatelist[i])
            date_time = '&datetime=' + str(datelist[i])         #Returns observations between two dates. Both dates are inclusive.
            #print(date_time)
            request = base_url + limit + stationID + date_time + parameterId + API      #Create request string
            print(request)


            ## Make web request:
            r = requests.get(str(request))
            r.ok                                                     #check if response was sucessful
            #print(r)
            #print(r.headers)                                         #check content of request
            #print(r.headers['content-type'])                         #check that it is json

            resp = r.json()                                          #convert response object to dictionary

            ## Convert JSON to dataframe:
            json_norm = pd.json_normalize(resp, record_path=['features'])   #create dataframe
            #print(json_norm)

            # Format dataframe:
            json_df = json_norm.drop(['id', 'type', 'geometry.type', 'properties.created'], axis=1)   #drop columns with listed names
            json_df = json_df.rename(columns={"geometry.coordinates": "Longitude, Latitude", "properties.observed": "Time", "properties.parameterId": "Parameter", "properties.stationId": "Station_ID", "properties.value": parameter[p]})
                #Rename columns
            json_df.Time = pd.to_datetime(json_df.Time)             #Convert Time to datetime-format
            #json_df                                                 #inspect dataframe

            #Create separate dateframes for wind speed and wind direction:
            if p == 0:                                              #If parameter='wind_speed'
                if wind_speed_df_count < 1:                             #If first dataframe: 
                    wind_speed_df = json_df                                 #Rename dataframe
                    wind_speed_df_count = wind_speed_df_count + 1           #Multiply dataframe-count by one
                else:                                                   #If not first dataframe: 
                    wind_speed_df = pd.concat([json_df, wind_speed_df], ignore_index=True,sort=False)                    #Combine dataframes
            else:                                                   #If parameter='wind_dir'
                if wind_dir_df_count < 1:
                    wind_dir_df = json_df
                    wind_dir_df_count = wind_dir_df_count + 1
                else:
                    wind_dir_df = pd.concat([json_df, wind_dir_df], ignore_index=True, sort=False)                       #Combine dataframes
            

                ## Save dataframe to parquet format for each station and parameter:
                namegenerator_speed = 'wind_speed_df_' + station + '.parq.gzip'         #create dynamic names for parquet-files
                namegenerator_dir = 'wind_dir_df_' + station + '.parq.gzip'
                wind_speed_df.to_parquet(namegenerator_speed, compression='gzip')       #Create parquet-file with gzip-compression
                wind_dir_df.to_parquet(namegenerator_dir, compression='gzip')

                #parq_windspeed = pd.read_parquet(namegenerator_speed)                  #read in parquet-file as pandas DataFrame
                #parq_winddir = pd.read_parquet(namegenerator_dir)                      #read in parquet-file as pandas DataFrame

        # #Change name of generated dataframes according to station ID:
        # #for station in st_ID:
        # vars()['wind_speed_df_' + station] = wind_speed_df
        # vars()['wind_dir_df_'+ station] = wind_dir_df





##### Deal with missing values ######

# Create control datetime range:
controlTime = pd.date_range(start=start_datetime,end=end_datetime,freq='10T')       #create date range over the timeperiod with 10 min frequency
controlTime = controlTime.sort_values(ascending=False)                              #sort controlTime in descending order (matching API-order)

# Create loop for inserting missing values(NaNs) and saving all the data to a new parquet file:
for station in st_ID:
    glob_string = '*' + station + '.parq.gzip'                      #Create a dynamic string for input to search for station specific parquet-files
    dmi_st_zip = glob.glob(glob_string)                             #Find station specific parquet-files in current directory
    for i in dmi_st_zip:
        if i.startswith('wind_speed'):                              #If object in parquet-file list starts with "wind_speed":
            wind_speed_parq = pd.read_parquet(i)                        #Read and print parquet-file as wind_speed_parq
            print(wind_speed_parq)
        else:                                                       #If object in parquet-file list starts with "wind_dir":
            wind_dir_parq = pd.read_parquet(i)                          #Read and print parquet-file as wind_dir_parq
            print(wind_dir_parq)


    ## Create arrays for new dataframe containing parameters and location: 
    wind_speed_arr = []                                         #Create array to contain new wind array with missing values
    jrow = 0                                                    #Initiate counter for original time series index
    numberofnan = 0                                             #Initiate counter for NaN-values

    for row in range(len(controlTime)):
        if jrow<len(wind_speed_parq.Time) and controlTime[row] == wind_speed_parq.Time[jrow]:    #If original timeseries match control timeseries fetch wind_dir-value 
                #Additional argument jrow<len(json_df.Time) is needed to keep loop going
            wind_speed_arr.append(wind_speed_parq.wind_speed[jrow])
            jrow = jrow + 1                                     #Count index for unperturbed timeindex
        else:                                                   #If timeseries doesn´t match, insert NaN
            wind_speed_arr.append(np.nan)
            numberofnan = numberofnan + 1                       #Count index for inserted NaN
    #print(wind_speed_arr)
    print(numberofnan)


    wind_dir_arr = []                                           #Create array to contain new wind array with missing values
    jrow = 0                                                    #Initiate counter for original time series index
    numberofnan = 0                                             #Initiate counter for NaN-values

    for row in range(len(controlTime)):
        if jrow<len(wind_dir_parq.Time) and controlTime[row] == wind_dir_parq.Time[jrow]:    #If original timeseries match control timeseries fetch wind_dir-value 
                #Additional argument jrow<len(json_df.Time) is needed to keep loop going
            wind_dir_arr.append(wind_dir_parq.wind_dir[jrow])
            jrow = jrow + 1                                     #Count index for unperturbed timeindex
        else:                                                   #If timeseries doesn´t match, insert NaN
            wind_dir_arr.append(np.nan)
            numberofnan = numberofnan + 1                       #Count index for inserted NaN
    #print(wind_dir_arr)
    print(numberofnan)


    lon_lat_arr = []                                            #Create array to contain new wind array with missing values
    jrow = 0                                                    #Initiate counter for original time series index
    numberofnan = 0                                             #Initiate counter for NaN-values

    for row in range(len(controlTime)):
        if jrow<len(wind_dir_parq.Time) and controlTime[row] == wind_dir_parq.Time[jrow]:      #If original timeseries match control timeseries fetch lon_lat-value 
            lon_lat_arr.append(wind_dir_parq['Longitude, Latitude'][jrow])
            jrow = jrow + 1
        else:                                                   #If timeseries doesn´t match, insert NaN
            lon_lat_arr.append(np.nan)
            numberofnan = numberofnan + 1
    #print(lon_lat_arr)
    print(numberofnan)


    ## Create new dataframe containg the new arrays: 
    new_dict = {'Longitude, Latitude': lon_lat_arr,                         #Create dictionary
                'Time': controlTime,
                'Wind speed': wind_speed_arr,
                'Wind direction': wind_dir_arr}

    new_df = pd.DataFrame(new_dict)                                         #Create dataframe from dictionary
    #new_df

    ## Create final parquet-file: 
    namegenerator_parq_final = 'dmi_data_' + station + '.parq.gzip'         #Create dynamic naming based on station ID for final parquet-file
    new_df.to_parquet(namegenerator_parq_final, compression='gzip')         #Create station specific parquet-file

    print_parquet = pd.read_parquet(namegenerator_parq_final)
    print_parquet

print_parquet = pd.read_parquet('dmi_data_06156.parq.gzip')


# # Delete?:
# with np.printoptions(threshold=np.inf):                         #Print all values for na-array
#      print(new_df[263080:263088])