##### Ageostrophic wind #####
## Author: Bianca E. Sandvik (March 2023)

## This script calculate the wind components (u_10 and v_10) for DMI station data from observational data of wind speed and wind direction
## and calculates the ageostrophic wind for each station based on data from DMI station observations and corresponding ERA5-data coupled 
## in the script "merge_dmi_data_ERA5.py".
## For each stations alpha it then creates time series plots and conduct a regression and autocorrelation analysis. 

# Import packages:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates                       #for creating trendlines
import glob                                             #For searching files in current directory
import statsmodels.api as sm                                #For statistical analysis
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

st_ID = list(DMIstations['Station_ID'])                                 #create list of all station IDs
st_name = list(DMIstations['Station_name'])                             #create list of all station IDs

st_name_nr = 0                                                          #create initial counter for station name
for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'          #Create a dynamic string for input to search for station specific parquet-files
    dmi_ERA5_zip = glob.glob(glob_string)                               #Find station specific parquet-files in current directory
    station_name = st_name[st_name_nr]                                  #Fetch station name
    st_name_nr = st_name_nr + 1                                         #Counter for station names
    for i in dmi_ERA5_zip:
        df = pd.read_parquet(i)                                         #Read and print parquet-file
        #print(df)

        # Calculate 10m wind components for the DMI station:
        md = 270 - df['DMI_wind_dir']                                   #Convert meteorological direction to math direction

        DMI_u10 = df['DMI_wind_speed']*np.cos(md)                       #Calculate u-component
        DMI_v10 = df['DMI_wind_speed']*np.sin(md)                       #Calculate v-component

        # Insert components into dataframe: 
        df.insert(2, 'DMI_u10', DMI_u10)                                #Insert u-component as column nr. 3
        df.insert(3, 'DMI_v10', DMI_v10)                                #Insert v-component as column nr. 4


        ## Calculate angle between Vg and V10: 
        alpha_list = []                                                 #define empty list to contain angle
        k = np.array([0,0,1])                                           #define the vertical unit vector
        err = 0.0001                                                    #small positive number to avoid division by zero if no wind occurs

        for i in range(len(df)):
            V10 = np.array([df['DMI_u10'][i], df['DMI_v10'][i], 0])     #define the wind vector at 10m
            Vg = np.array([df['ERA5_ug'][i], df['ERA5_vg'][i], 0])      #define the geostrophic wind vector
            #V10 = np.array([1,0,0])
            #Vg = np.array([0,1,0])
            
            V10_norm = np.sqrt(V10[0]**2 + V10[1]**2 + V10[2]**2)       #calculate the norm for V10
            Vg_norm = np.sqrt(Vg[0]**2 + Vg[1]**2 + Vg[2]**2)           #calculate the norm for Vg

            V_crossprod = np.cross(Vg,V10)                              #calclate the cross product of Vg and V10
            V_cross = V_crossprod / (Vg_norm * V10_norm + err)
            sinalpha = np.dot(k,V_cross)                                #calculate the dot product 
            alpha = np.arcsin(sinalpha)
            alpha_deg = alpha * (180/np.pi)                             #convert angle from radians to degrees
            #Vcross_abs = np.abs(Vcross)                                #take the absolute value of the dot product

            # Alt. using dot product:
            #Gives right angle size, but not angle direction.
            abdot = np.dot(Vg,V10)
            arccos= abdot / (Vg_norm * V10_norm + err)
            cos = np.arccos(arccos)
            cos_deg = cos * (180/np.pi)

            # Angle correction of original cross product formula using the result from the dot product if the angle > 90 degrees:
            if cos_deg > 90 and alpha < 0:                          #if angle is larger than 90 deg and alpha is negative      
                alpha_deg = (-1)*cos_deg                                #convert to correct angle size and direction change
            elif cos_deg > 90 and alpha > 0:                        #if angle is larger than 90 deg and alpha is positive
                alpha_deg = cos_deg                                     #correct angle size
            else:                                                   #if angle smaller than 90 deg, keep original value
                 pass

            alpha_list.append(alpha_deg)                            #insert values into list 

        df.insert(10,'alpha', alpha_list)                           #insert ageostrophic wind into dataframe as new column
        #df                                                         #print dataframe  


        # Store as parquet-file: 
        namegenerator_parq = 'ageo_' + station + '_monthly.parq.gzip'       #Create dynamic naming based on station ID for parquet-file
        df.to_parquet(namegenerator_parq, compression='gzip')               #Create station specific parquet-file

        print_parquet_month = pd.read_parquet(namegenerator_parq)           #Print
        print('Printing monthly means for station', station, ':')
        #print_parquet_month


        ## Generate angle plot:
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(df['alpha'], c='darkkhaki', label='Angle')                  #plot DMI-data
        ax.set_ylim((-190, 210))                                            #set y-axis range
        ax.set_yticks([-180,-135,-90, -45, 0,45,90,135,180])                #set y-axis ticks
        ax.set_xlabel('Time')
        ax.set_ylabel('Angle ' + r'$\alpha$')
        ax.set_title("Mean monthly " + r'$\alpha$' + " for station " + str(station) + " " + str(station_name))
        #ax.legend(loc='upper right')                                        #define legend with position

        # Create trendlines:
        x1 = mdates.date2num(df.index)                                      #convert timeindex to numbers and define x-coordinate
        y1= df['alpha']                                                     #define y-coordinate
        mask = y1.isna()                                                    #create mask for y-coordinate to avoid trendline disappearing for missing data
        z1 = np.polyfit(x1[~mask], y1[~mask], 1)                            #create least squares linear fit to coordinates
        slope = np.round(z1[0],6)                                           #calculate the slope of the trendline and round it
        p1 = np.poly1d(z1)                                                  #create linear object
        ax.plot(x1, p1(x1), color='olive', linestyle='--', linewidth=2)     #plot trendline


        ## Conduct regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()

        #Write the trendline slope in the upper left corner and p-value in upper right corner:
        ax.text(0.02, 0.98, 'Trendline slope = ' + str(slope), color='olive', style='italic',  horizontalalignment='left', verticalalignment='top', transform = ax.transAxes)
        ax.text(0.98, 0.98, 'p-value = ' + str(np.round(results.f_pvalue,3)), color='olive', style='italic',  horizontalalignment='right', verticalalignment='top', transform = ax.transAxes) 

        #plt.show()                                                          #display plot
        #plt.savefig("monthly_alpha_" + station + ".png", dpi=200)            #save plot as png
        plt.close(None)


        ## Regression analysis: 
        x = sm.add_constant(x1)
        results = sm.OLS(y1,x, missing = 'drop').fit()
        results.summary()


        ## Plot autocorrelation plots:
        fig = tsaplots.plot_acf(y1, missing='none')
        plt.title('Autocorrelation for ' + station + " " + station_name)
        plt.show()






