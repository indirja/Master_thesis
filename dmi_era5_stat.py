##### DMI ERA5 statistics #####
## Author: Bianca E.Sandvik (March 2023)

## This script imports station specific parquet files and drops lines of data based on its recorded change in latitude and longitude. 
## Whether it drops the lines before or after the station was moved can be adjusted by # or un-# certain codelines (see line 31-34).
## It then generates time series plots and conduct a regression analysis for the new time series. 


# Import packages:
import pandas as pd
import glob                                             #For searching files in current directory
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates                       #for creating trendlines
import numpy as np                                      #for creating trendlines
import statsmodels.api as sm                            #for statistical analysis

# Define list of DMI stations:
stationlist = [('06041', 'Skagen Fyr'),('06052' ,"Thyborøn"), ('06058', "Hvide Sande"), ('06079', "Anholt Havn"), 
    ('06080', "Esbjerg Lufthavn"), ('06081', "Blåvandshuk Fyr"), ('06096', "Rømø/Juvre"), ('06104', "Billund Lufthavn"),
    ('06108', "Kolding Lufthavn"), ('06116', "Store Jyndevad"), ('06119', "Kegnæs Fyr"), ('06120', "H.C.Andersen Airport"), 
    ('06124', "Sydfyns Flyveplads"), ('06149', "Gedser"), ('06151', "Omø Fyr"), ('06156', "Holbæk Flyveplads"), ('06159', "Røsnæs Fyr"), 
    ('06168', "Nakkehoved Fyr"), ('06169', "Gniben"), ('06170', "Roskilde Lufthavn"), ('06180', "Københavns Lufthavn"), 
    ('06181', "Jægersborg"), ('06183', "Drogden Fyr"), ('06190', "Bornholms Lufthavn"), ('06193', "Hammer Odde Fyr")]

DMIstations = pd.DataFrame (stationlist, columns = ['Station_ID', 'Station_name'])       #create dataframe with list station ID and Station_name
#print (DMIstations)

st_ID = list(DMIstations['Station_ID'])                                         #create list of all station IDs
st_name = list(DMIstations['Station_name'])                                     #create list of all station names

## Monthly analysis:
    ##NOTE: adjust run for two different time periods: 
        ## Before station move: comment lines 41-42 and uncomment line 59
        ## After station move:  uncomment lines 41-42 and comment line 58

st_name_nr = 0                                                                  #create initial counter for station names 

for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'                  #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = st_name[st_name_nr]                                          #Fetch station name
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        # if i == 'DMI_ERA5_06116_monthly.parq.gzip':                             #jump over itteration for station 06116
        #    continue
           #Needed for run for NEW location since station has no values for new location yet

        station_parq_monthly = pd.read_parquet(i)                               #Read and print parquet-file

        ## Plot and regression for timeframe of unchanged station location:        
        counter = 0                                                             #create counter for number of rows containing original location
        for row in range(len(station_parq_monthly)):
            if station_parq_monthly.DMI_Lon[row] == station_parq_monthly.DMI_Lon[0] and station_parq_monthly.DMI_Lat[row] == station_parq_monthly.DMI_Lat[0]:
                counter = counter + 1
                #If longitude or latitude match the original location, increase row counter
            else:
                pass

        # Drop all rows in dataframe with data for original or last location 
        #unmoved_st = station_parq_monthly.drop(station_parq_monthly.index[:counter+1])          #drop rows with old location
        unmoved_st = station_parq_monthly.drop(station_parq_monthly.index[counter:])            #drop rows with new location
            #NOTE: one month excluded from both due to potential transition values.
        
        if len(unmoved_st) == 0:                        #jump over itteration if new dataframe is empty
            continue
       
        ## Generate wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(unmoved_st['DMI_wind_speed'], c='cornflowerblue', label='DMI')                  #plot DMI-data
        ax.plot(unmoved_st['ERA5_wind_speed'], c='lightcoral', linestyle='-', label='ERA5')     #plot ERA5-data
        ax.set_ylim((0, 24))                                                                    #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed [m/s]')
        ax.set_title("Mean monthly wind speed for station " + station + " " + station_name)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(unmoved_st.index)                            #convert timeindex to numbers and define x-coordinate
        y1= unmoved_st['DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

        x2 = mdates.date2num(unmoved_st.index)
        y2= unmoved_st['ERA5_wind_speed']
        z2 = np.polyfit(x2, y2, 1)
        slope_ERA5 = np.round(z2[0],6)                                               #calculate the slope of the trendline and round it
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)     

        #plt.show()                                                                   #display plot
        #plt.savefig("monthly_wind_speed_" + station + "before/after.png", dpi=200)              #save plot as png
        plt.close(None)


        ## Regression analysis: 
        # x = sm.add_constant(x1)
        # results = sm.OLS(y1,x, missing = 'drop').fit()
        # # print('Regression analysis for DMI wind speed station ' + station)
        # results.summary()




        ## Calculate ERA5 - DMI wind speed:
        ERA5_DMI_list = []
        for i in range(len(unmoved_st)):
            ERA5_DMI = unmoved_st['ERA5_wind_speed'][i] - unmoved_st['DMI_wind_speed'][i]   #calculate wind peed difference
            ERA5_DMI_list.append(ERA5_DMI)
        unmoved_st.insert(8, 'ERA5-DMI_wind_speed', ERA5_DMI_list)

        ## Generate ERA5-DMI wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(unmoved_st['ERA5-DMI_wind_speed'], c='mediumpurple', label='ERA5-DMI')                #plot ERA5-DMI-data
        ax.set_ylim((-1, 16))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed difference [m/s]')
        ax.set_title("Mean monthly ERA5-DMI wind speed for station " + station + " " + station_name, fontsize=11)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(unmoved_st.index)                            #convert timeindex to numbers and define x-coordinate
        y1= unmoved_st['ERA5-DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='rebeccapurple', linestyle='--', linewidth=2)     #plot trendline

        ## Conduct regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'p-value = ' + str(np.round(results.f_pvalue,3)), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        plt.show()                                                                 #display plot
        #plt.savefig("monthly_ERA5-DMI_wind_speed_" + station + "before/after.png", dpi=200)              #save plot as png
        #plt.close(None)


        ## Regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        #print('Regression analysis for ERA5-DMI wind speed station ' + station)
        results.summary()





## Special analysis for station 06183 Drogden_Fyr:
## Height changed between 2019-01-15T13:34:47Z and 2022-04-04T12:41:04Z

station_parq_monthly = pd.read_parquet('DMI_ERA5_06183_monthly.parq.gzip')

# Plot and regression for timeframe of unchanged station location:
counter = 0                                                             #create counter for number of rows containing previous location
for row in range(len(station_parq_monthly)):
    if str(station_parq_monthly.index[row])[0:4] < '2019':
        counter = counter + 1
        #If longitude or latitude do not match the final location increase row counter
    else:
        pass

unmoved_st = station_parq_monthly.drop(station_parq_monthly.index[counter:len(station_parq_monthly)])       #drop all rows in dataframe with data for previous location   



## Generate wind speed plot:
fig, ax = plt.subplots(layout='constrained')
ax.plot(unmoved_st['DMI_wind_speed'], c='cornflowerblue', label='DMI')                #plot DMI-data
ax.plot(unmoved_st['ERA5_wind_speed'], c='lightcoral', linestyle='-', label='ERA5')   #plot ERA5-data
ax.set_ylim((0, 24))                                                        #set y-axis range
ax.set_xlabel('Time')
ax.set_ylabel('Wind speed [m/s]')
ax.set_title("Mean monthly wind speed for station " + station + " " + station_name)
ax.legend(loc='upper right')                                                #define legend with position

# Create trendlines:
x1 = mdates.date2num(unmoved_st.index)                            #convert timeindex to numbers and define x-coordinate
y1= unmoved_st['DMI_wind_speed']                                  #define y-coordinate
mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
p1 = np.poly1d(z1)                                                          #create linear object
ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

x2 = mdates.date2num(unmoved_st.index)
y2= unmoved_st['ERA5_wind_speed']
z2 = np.polyfit(x2, y2, 1)
slope_ERA5 = np.round(z2[0],6)                                               #calculate the slope of the trendline and round it
p2 = np.poly1d(z2)
ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

#Write the trendline slope in the upper left corner
ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)     

#plt.show()                                                                   #display plot
#plt.savefig("monthly_wind_speed_" + station + ".png", dpi=200)              #save plot as png
plt.close(None)


## Regression analysis: 
x = sm.add_constant(x1)
results = sm.OLS(y1,x, missing = 'drop').fit()
print('Regression analysis for DMI wind speed station ' + station)
results.summary()




## Calculate ERA5 - DMI wind speed:
ERA5_DMI_list = []
for i in range(len(unmoved_st)):
    ERA5_DMI = unmoved_st['ERA5_wind_speed'][i] - unmoved_st['DMI_wind_speed'][i]   #calculate wind peed difference
    ERA5_DMI_list.append(ERA5_DMI)
unmoved_st.insert(8, 'ERA5-DMI_wind_speed', ERA5_DMI_list)

## Generate ERA5-DMI wind speed plot:
fig, ax = plt.subplots(layout='constrained')
ax.plot(unmoved_st['ERA5-DMI_wind_speed'], c='mediumpurple', label='ERA5-DMI')                #plot ERA5-DMI-data
ax.set_ylim((-1, 16))                                                        #set y-axis range
ax.set_xlabel('Time')
ax.set_ylabel('Wind speed difference [m/s]')
ax.set_title("Mean monthly ERA5-DMI wind speed for station " + station + " " + station_name, fontsize=11)
ax.legend(loc='upper right')                                                #define legend with position

# Create trendlines:
x1 = mdates.date2num(unmoved_st.index)                            #convert timeindex to numbers and define x-coordinate
y1= unmoved_st['ERA5-DMI_wind_speed']                                  #define y-coordinate
mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
slope = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
p1 = np.poly1d(z1)                                                          #create linear object
ax.plot(x1, p1(x1), color='rebeccapurple', linestyle='--', linewidth=2)     #plot trendline

#Write the trendline slope in the upper left corner
ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

plt.show()                                                                 #display plot
#plt.savefig("monthly_ERA5-DMI_wind_speed_" + station + ".png", dpi=200)              #save plot as png
plt.close(None)


## Regression analysis: 
x = sm.add_constant(x1)
results = sm.OLS(y1,x, missing = 'drop').fit()
results.summary()




## Analysis for alpha:
st_name_nr = 0                                                                  #create initial counter for station names 

for station in st_ID:
    glob_string = 'ageo_' + station + '_monthly.parq.gzip'                      #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = st_name[st_name_nr]                                          #Fetch station name
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        if i == 'ageo_06116_monthly.parq.gzip':                             #jump over itteration for station 06116
           continue
           #NOTE: Needed for run for NEW location since station has no values for new location yet

        station_parq_monthly = pd.read_parquet(i)                               #Read and print parquet-file
        #station_parq_monthly = pd.read_parquet('ageo_06080_monthly.parq.gzip')

        ## Plot and regression for timeframe of unchanged station location:        
        counter = 0                                                             #create counter for number of rows containing original location
        for row in range(len(station_parq_monthly)):
            if station_parq_monthly.DMI_Lon[row] == station_parq_monthly.DMI_Lon[0] and station_parq_monthly.DMI_Lat[row] == station_parq_monthly.DMI_Lat[0]:
                counter = counter + 1
                #If longitude or latitude match the original location, increase row counter
            else:
                pass

        # Drop all rows in dataframe with data for original or last location 
        unmoved_st = station_parq_monthly.drop(station_parq_monthly.index[:counter+1])          #drop rows with old location
        #unmoved_st = station_parq_monthly.drop(station_parq_monthly.index[counter:])            #drop rows with new location
            #NOTE: one month excluded from both due to potential transition values.
        
        if len(unmoved_st) == 0:                        #jump over itteration if new dataframe is empty
            continue
       
        ## Generate angle plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(unmoved_st['alpha'], c='darkkhaki', label='Angle')                #plot DMI-data
        #ax.set_ylim((-0.1, 15))                                             #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Angle ' + r'$\alpha$')
        ax.set_title("Mean monthly " + r'$\alpha$' + " for station " + str(station) + " " + str(station_name))
        #ax.legend(loc='upper right')                                        #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(unmoved_st.index)                                      #convert timeindex to numbers and define x-coordinate
        y1= unmoved_st['alpha']                                                     #define y-coordinate
        mask = y1.isna()                                                    #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                            #create least squares linear fit to coordinates
        slope = np.round(z1[0],6)                                           #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                  #create linear object
        ax.plot(x1, p1(x1), color='olive', linestyle='--', linewidth=2)     #plot trendline
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='olive', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
                
        plt.show()                                                          #display plot
        #plt.savefig("monthly_alpha_" + station + ".png", dpi=200)            #save plot as png
        #plt.close(None)


        ## Regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        results.summary()







        

st_name_nr = 0  

## Yearly plots:
for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_yearly.parq.gzip'                  #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = st_name[st_name_nr]                                          #Fetch station name
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        if i == 'DMI_ERA5_06116_yearly.parq.gzip':                             #jump over itteration for station 06116
           continue
           #Needed for run for NEW location since station has no values for new location yet

        station_parq_yearly = pd.read_parquet(i)                               #Read and print parquet-file
        #station_parq_monthly = pd.read_parquet('DMI_ERA5_06116_yearly.parq.gzip')

        ## Plot and regression for timeframe of unchanged station location:        
        counter = 0                                                             #create counter for number of rows containing original location
        for row in range(len(station_parq_yearly)):
            if station_parq_yearly.DMI_Lon[row] == station_parq_yearly.DMI_Lon[0] and station_parq_yearly.DMI_Lat[row] == station_parq_yearly.DMI_Lat[0]:
                counter = counter + 1
                #If longitude or latitude match the original location, increase row counter
            else:
                pass

        # Drop all rows in dataframe with data for original or last location 
        unmoved_st = station_parq_yearly.drop(station_parq_yearly.index[:counter+1])          #drop rows with old location
        #unmoved_st = station_parq_yearly.drop(station_parq_yearly.index[counter:])            #drop rows with new location
            #NOTE: one month excluded from both due to potential transition values.
        
        if len(unmoved_st) == 0:                        #jump over itteration if new dataframe is empty
            continue
       
        ## Generate wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(unmoved_st['DMI_wind_speed'], c='cornflowerblue', label='DMI')                  #plot DMI-data
        ax.plot(unmoved_st['ERA5_wind_speed'], c='lightcoral', linestyle='-', label='ERA5')     #plot ERA5-data
        ax.set_ylim((0, 24))                                                                    #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed [m/s]')
        ax.set_title("Mean yearly wind speed for station " + station + " " + station_name)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(unmoved_st.index)                            #convert timeindex to numbers and define x-coordinate
        y1= unmoved_st['DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

        x2 = mdates.date2num(unmoved_st.index)
        y2= unmoved_st['ERA5_wind_speed']
        z2 = np.polyfit(x2, y2, 1)
        slope_ERA5 = np.round(z2[0],6)                                               #calculate the slope of the trendline and round it
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)     

        #plt.show()                                                                   #display plot
        #plt.savefig("yearly_wind_speed_" + station + ".png", dpi=200)              #save plot as png
        plt.close(None)


        ## Regression analysis: 
        # x = sm.add_constant(x1)
        # results = sm.OLS(y1,x, missing = 'drop').fit()
        # print('Regression analysis for DMI wind speed station ' + station)
        # results.summary()




        ## Calculate ERA5 - DMI wind speed:
        ERA5_DMI_list = []
        for i in range(len(unmoved_st)):
            ERA5_DMI = unmoved_st['ERA5_wind_speed'][i] - unmoved_st['DMI_wind_speed'][i]   #calculate wind speed difference
            ERA5_DMI_list.append(ERA5_DMI)
        unmoved_st.insert(8, 'ERA5-DMI_wind_speed', ERA5_DMI_list)

        ## Generate ERA5-DMI wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(unmoved_st['ERA5-DMI_wind_speed'], c='mediumpurple', label='ERA5-DMI')                #plot ERA5-DMI-data
        ax.set_ylim((-1, 16))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed difference [m/s]')
        ax.set_title("Mean yearly ERA5-DMI wind speed for station " + station + " " + station_name, fontsize=11)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(unmoved_st.index)                            #convert timeindex to numbers and define x-coordinate
        y1= unmoved_st['ERA5-DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='rebeccapurple', linestyle='--', linewidth=2)     #plot trendline

        ## Conduct regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'p-value = ' + str(np.round(results.f_pvalue,3)), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        plt.show()                                                                 #display plot
        #plt.savefig("yearly_ERA5-DMI_wind_speed_" + station + ".png", dpi=200)              #save plot as png
        #plt.close(None)


        ## Regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        #print('Regression analysis for ERA5-DMI wind speed station ' + station)
        results.summary()







