##### DMI ERA5 plotting #####
## Author: Bianca E.Sandvik (March-Mai 2023)

## This script creates time series plots for ERA5, DMI, ERA5-DMI and wind direction along with a regression analysis for all stations listed 
## based on their individual parquet-files. 
## Autocorrelation plots can also be created.


# Import packages:
import pandas as pd
import glob                                             #For searching files in current directory
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates                       #for creating trendlines
import numpy as np                                      #for creating trendlines

import statsmodels.api as sm                            #for statistical analysis
from statsmodels.graphics import tsaplots

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

## Monthly plots:
st_name_nr = 0                                                                  #create initial counter for station names 

for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'                  #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = st_name[st_name_nr]                                          #Fetch station name
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        station_parq_monthly = pd.read_parquet(i)                               #Read and print parquet-file
        #print(station_parq_monthly)

        ## Generate wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_monthly['DMI_wind_speed'], c='cornflowerblue', label='DMI')                #plot DMI-data
        ax.plot(station_parq_monthly['ERA5_wind_speed'], c='lightcoral', linestyle='-', label='ERA5')   #plot ERA5-data
        ax.set_ylim((0, 24))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed [m/s]')
        ax.set_title("Mean monthly wind speed for station " + station + " " + station_name)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_monthly.index)                            #convert timeindex to numbers and define x-coordinate
        y1= station_parq_monthly['DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

        x2 = mdates.date2num(station_parq_monthly.index)
        y2= station_parq_monthly['ERA5_wind_speed']
        z2 = np.polyfit(x2, y2, 1)
        slope_ERA5 = np.round(z2[0],6)                                               #calculate the slope of the trendline and round it
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)     

        #plt.show()                                                                 #display plot
        #plt.savefig("monthly_wind_speed_" + station + ".png", dpi=200)              #save plot as png
        plt.close(None)


        ## Regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        # print('Regression analysis for DMI wind speed station ' + station)
        results.summary()

        fig = tsaplots.plot_acf(y1)                                                 #calculate autocorrelation
        plt.title('Autocorrelation for ' + station + " " + station_name)
        plt.show()




## Calculate difference in ERA5 and DMI wind speed:
st_name_nr = 0                                                                  #create initial counter for station names 

for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'                  #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = st_name[st_name_nr]                                          #Fetch station name
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        station_parq_monthly = pd.read_parquet(i)                               #Read and print parquet-file
        #station_parq_monthly = pd.read_parquet('DMI_ERA5_06058_monthly.parq.gzip')  
        #print(station_parq_monthly)

        ## Calculate ERA5 - DMI wind speed:
        ERA5_DMI_list = []
        for i in range(len(station_parq_monthly)):
            ERA5_DMI = station_parq_monthly['ERA5_wind_speed'][i] - station_parq_monthly['DMI_wind_speed'][i]   #calculate wind speed difference
            ERA5_DMI_list.append(ERA5_DMI)
        station_parq_monthly.insert(8, 'ERA5-DMI_wind_speed', ERA5_DMI_list)

        ## Generate ERA5-DMI wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_monthly['ERA5-DMI_wind_speed'], c='mediumpurple', label='ERA5-DMI')                #plot ERA5-DMI-data
        ax.set_ylim((-1, 16))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed difference [m/s]')
        ax.set_title("Mean monthly ERA5-DMI wind speed for station " + station + " " + station_name, fontsize=11)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_monthly.index)                            #convert timeindex to numbers and define x-coordinate
        y1= station_parq_monthly['ERA5-DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='rebeccapurple', linestyle='--', linewidth=2)     #plot trendline

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

        ## Conduct regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        #Write p-value under the trendline slope:
        ax.text(0.02, 0.94, 'p-value = ' + str(np.round(results.f_pvalue,3)), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

        #plt.show()                                                                 #display plot
        plt.savefig("monthly_ERA5-DMI_wind_speed_" + station + ".png", dpi=200)              #save plot as png
        plt.close(None)


        ## Regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        # print('Regression analysis for ERA5-DMI wind speed station ' + station)
        #results.summary()
        
        ## Plot autocorrelation plots:
        fig = tsaplots.plot_acf(y1, missing='none')
        plt.title('Autocorrelation for ' + station + " " + station_name)
        plt.show()

        fig = tsaplots.plot_pacf(y1)
        plt.title('Partial autocorrelation for ' + station + " " + station_name)
        plt.show()


        ## Generate wind direction plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_monthly['DMI_wind_dir'], c='cornflowerblue', label='DMI')                #plot DMI-data
        ax.plot(station_parq_monthly['ERA5_wind_dir'], c='lightcoral', linestyle='-', label='ERA5')   #plot ERA5-data
        ax.set_ylim((0, 360))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind direction [degrees]')
        ax.set_title("Mean monthly wind direction for station " + station + " " + station_name)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_monthly.index)                            #convert timeindex to numbers and define x-coordinate
        y1= station_parq_monthly['DMI_wind_dir']                                    #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

        x2 = mdates.date2num(station_parq_monthly.index)
        y2= station_parq_monthly['ERA5_wind_dir']
        z2 = np.polyfit(x2, y2, 1)
        slope_ERA5 = np.round(z2[0],6)                                               #calculate the slope of the trendline and round it
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes) 
        ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

        #plt.show()                                                                 #display plot
        #plt.savefig("monthly_wind_dir_" + station + ".png", dpi=200)                #save plot as png
        plt.close(None)



        



## Yearly plots:
st_name_nr = 0                                                                  #create initial counter for station name

for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_yearly.parq.gzip'                   #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = st_name[st_name_nr]                                          #Fetch station name
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        station_parq_yearly = pd.read_parquet(i)                               #Read and print parquet-file
        #print(station_parq_monthly)

        ## Generate wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_yearly['DMI_wind_speed'], c='cornflowerblue', label='DMI')                #plot DMI-data
        ax.plot(station_parq_yearly['ERA5_wind_speed'], c='lightcoral', linestyle='-', label='ERA5')   #plot ERA5-data
        ax.set_ylim((0, 15))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed [m/s]')
        ax.set_title("Mean yearly wind speed for station " + station + " " + station_name)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_yearly.index)                            #convert timeindex to numbers and define x-coordinate
        y1 = station_parq_yearly['DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

        x2 = mdates.date2num(station_parq_yearly.index)
        y2 = station_parq_yearly['ERA5_wind_speed']
        z2 = np.polyfit(x2, y2, 1)
        slope_ERA5 = np.round(z2[0],6)
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes) 
        
        #plt.show()                                                                 #display plot
        #plt.savefig("yearly_wind_speed_" + station + ".png", dpi=200)               #save plot as png
        plt.close(None)                                                             #close open plots windows



        ## Generate wind direction plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_yearly['DMI_wind_dir'], c='cornflowerblue', label='DMI')                #plot DMI-data
        ax.plot(station_parq_yearly['ERA5_wind_dir'], c='lightcoral', linestyle='-', label='ERA5')   #plot ERA5-data
        ax.set_ylim((0, 360))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind direction [degrees]')
        ax.set_title("Mean yearly wind direction for station " + station + " " + station_name)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_yearly.index)                             #convert timeindex to numbers and define x-coordinate
        y1= station_parq_yearly['DMI_wind_dir']                                     #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

        x2 = mdates.date2num(station_parq_yearly.index)
        y2= station_parq_yearly['ERA5_wind_dir']
        z2 = np.polyfit(x2, y2, 1)
        slope_ERA5 = np.round(z2[0],6)
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

        #Write the trendline slope in the upper left corner 
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes) 

        #plt.show()                                                                 #display plot
        plt.savefig("yearly_wind_dir_" + station + ".png", dpi=200)                #save plot as png
        plt.close(None)



        ## Calculate ERA5 - DMI wind speed:
        ERA5_DMI_list = []
        for i in range(len(station_parq_yearly)):
            ERA5_DMI = station_parq_yearly['ERA5_wind_speed'][i] - station_parq_yearly['DMI_wind_speed'][i]   #calculate wind peed difference
            ERA5_DMI_list.append(ERA5_DMI)
        station_parq_yearly.insert(8, 'ERA5-DMI_wind_speed', ERA5_DMI_list)

        ## Generate ERA5-DMI wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_yearly['ERA5-DMI_wind_speed'], c='mediumpurple', label='ERA5-DMI')                #plot ERA5-DMI-data
        ax.set_ylim((-1, 16))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed difference [m/s]')
        ax.set_title("Mean yearly ERA5-DMI wind speed for station " + station + " " + station_name, fontsize=11)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_yearly.index)                            #convert timeindex to numbers and define x-coordinate
        y1= station_parq_yearly['ERA5-DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='rebeccapurple', linestyle='--', linewidth=2)     #plot trendline

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

        ## Conduct regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        #Write p-value under the trendline slope:
        ax.text(0.02, 0.94, 'p-value = ' + str(np.round(results.f_pvalue,3)), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

        #plt.show()                                                                 #display plot
        plt.savefig("yearly_ERA5-DMI_wind_speed_" + station + ".png", dpi=200)              #save plot as png
        plt.close(None)


        ## Regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        # print('Regression analysis for ERA5-DMI wind speed station ' + station)
        results.summary()

        ## Plot autocorrelation plots:
        # fig = tsaplots.plot_acf(y1, missing='none')
        # plt.title('Yearly autocorrelation for ' + station + " " + station_name)
        # plt.show()

        # fig = tsaplots.plot_pacf(y1)
        # plt.title('yearly partial autocorrelation for ' + station + " " + station_name)
        # plt.show()







### Create plots with moving date indicated:

moved_stationlist = [('06052' ,"Thyborøn", '2000-11-22T00:00:00Z'),('06168', "Nakkehoved Fyr", '2001-01-18T00:00:00Z')]

moved_DMIstations = pd.DataFrame (moved_stationlist, columns = ['Station_ID', 'Station_name', 'Moving date'])       #create dataframe with list station ID and Station_name
print(moved_DMIstations)

moved_st_ID = list(moved_DMIstations['Station_ID'])
moved_st_name = list(moved_DMIstations['Station_name'])
movingdate = list(mdates.date2num(moved_DMIstations['Moving date']))


## ERA5 and DMI data plot:

st_name_nr = 0                                                                  #create initial counter for station names 

for station in moved_st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'                  #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = moved_st_name[st_name_nr]                                    #Fetch station name
    move_date = movingdate[st_name_nr]                                          #fetch moving date
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        station_parq_monthly = pd.read_parquet(i)                               #Read and print parquet-file
        #print(station_parq_monthly)

        ## Generate wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_monthly['DMI_wind_speed'], c='cornflowerblue', label='DMI')                #plot DMI-data
        ax.plot(station_parq_monthly['ERA5_wind_speed'], c='lightcoral', linestyle='-', label='ERA5')   #plot ERA5-data
        ax.set_ylim((0, 24))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed [m/s]')
        ax.set_title("Mean monthly wind speed for station " + station + " " + station_name)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_monthly.index)                            #convert timeindex to numbers and define x-coordinate
        y1= station_parq_monthly['DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope_DMI = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='darkslateblue', linestyle='--', linewidth=2)     #plot trendline

        x2 = mdates.date2num(station_parq_monthly.index)
        y2= station_parq_monthly['ERA5_wind_speed']
        z2 = np.polyfit(x2, y2, 1)
        slope_ERA5 = np.round(z2[0],6)                                               #calculate the slope of the trendline and round it
        p2 = np.poly1d(z2)
        ax.plot(x2, p2(x2), color='crimson', linestyle='--', linewidth=2)

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope_DMI), color='darkslateblue', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.02, 0.94, 'Trendline slope = ' + str(slope_ERA5), color='crimson', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)     

        ## Add line of moving date:
        ax.vlines(move_date, ymin=-1, ymax=21.5, color='black', linestyle='dotted',linewidth=2)

        #plt.show()                                                                 #display plot
        plt.savefig("monthly_wind_speed_movedate_" + station + ".png", dpi=200)              #save plot as png
        plt.close(None)





## ERA5-DMI plot:

st_name_nr = 0                                                                  #create initial counter for station names 

for station in moved_st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'                  #Create a dynamic string for input to search for station specific parquet-files
    station_zip = glob.glob(glob_string)                                        #Find station specific parquet-files in current directory
    station_name = moved_st_name[st_name_nr]                                    #Fetch station name
    move_date = movingdate[st_name_nr]                                          #fetch moving date
    st_name_nr = st_name_nr + 1                                                 #Counter for station names
    #print(station_name)
    for i in station_zip:
        station_parq_monthly = pd.read_parquet(i)                               #Read and print parquet-file

        ## Calculate ERA5 - DMI wind speed:
        ERA5_DMI_list = []
        for i in range(len(station_parq_monthly)):
            ERA5_DMI = station_parq_monthly['ERA5_wind_speed'][i] - station_parq_monthly['DMI_wind_speed'][i]   #calculate wind speed difference
            ERA5_DMI_list.append(ERA5_DMI)
        station_parq_monthly.insert(8, 'ERA5-DMI_wind_speed', ERA5_DMI_list)

        ## Generate ERA5-DMI wind speed plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(station_parq_monthly['ERA5-DMI_wind_speed'], c='mediumpurple', label='ERA5-DMI')                #plot ERA5-DMI-data
        ax.set_ylim((-1, 16))                                                        #set y-axis range
        ax.set_xlabel('Time')
        ax.set_ylabel('Wind speed difference [m/s]')
        ax.set_title("Mean monthly ERA5-DMI wind speed for station " + station + " " + station_name, fontsize=11)
        ax.legend(loc='upper right')                                                #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(station_parq_monthly.index)                            #convert timeindex to numbers and define x-coordinate
        y1= station_parq_monthly['ERA5-DMI_wind_speed']                                  #define y-coordinate
        mask = y1.isna()                                                            #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                                    #create least squares linear fit to coordinates
        slope = np.round(z1[0],6)                                               #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                          #create linear object
        ax.plot(x1, p1(x1), color='rebeccapurple', linestyle='--', linewidth=2)     #plot trendline

        #Write the trendline slope in the upper left corner
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

        ## Conduct regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        #Write p-value under the trendline slope:
        ax.text(0.02, 0.94, 'p-value = ' + str(np.round(results.f_pvalue,3)), color='rebeccapurple', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)

        ## Add line of moving date:
        ax.vlines(move_date, ymin=-1, ymax=14, color='black', linestyle='dotted',linewidth=2)

        #plt.show()                                                                 #display plot
        plt.savefig("monthly_ERA5-DMI_wind_speed_movedate_" + station + ".png", dpi=200)              #save plot as png
        plt.close(None)
