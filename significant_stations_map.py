##### DMI station map #####
## Author: Bianca E. Sandvik (May 2023)

## This script plots the significant DMI stations listed (based on ERA5-DMI wind speed and alpha) onto a map with their station ID 
## with colour indiaction for their significance level. 

# Import packages:
import pandas as pd
import numpy as np
import glob       
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


## Plot for wind speed:

# Define list of significant DMI stations:
stationlist = [('06052' ,"Thyborøn"), ('06058', "Hvide Sande"), ('06096', "Rømø/Juvre"),
    ('06124', "Sydfyns Flyveplads"),('06151', "Omø Fyr"), ('06156', "Holbæk Flyveplads"), 
    ('06168', "Nakkehoved Fyr"), ('06170', "Roskilde Lufthavn"), ('06180', "Københavns Lufthavn"), 
    ('06183', "Drogden Fyr"), ('06190', "Bornholms Lufthavn"), ('06193', "Hammer Odde Fyr")]

DMIstations = pd.DataFrame (stationlist, columns = ['Station_ID', 'Station_name'])       #create dataframe with list station ID and Station_name
#print (DMIstations)

st_ID = list(DMIstations['Station_ID'])                                 #create list of all station IDs


## Insert the last longitude and latitude position for each station into dataframe:
lon_list = []                                                           #create empty list to hold location variables
lat_list = []

for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'          #Create a dynamic string for input to search for station specific parquet-files
    dmi_ERA5_zip = glob.glob(glob_string)                               #Find station specific parquet-files in current directory
    for i in dmi_ERA5_zip:
        df = pd.read_parquet(i)                                         #Read and print parquet-file
        #print(df)

        lon_list.append(df.DMI_Lon[-1])                                 #insert final longitude position into list
        lat_list.append(df.DMI_Lat[-1])                                 #insert final longitude position into list

DMIstations.insert(2,'Longitude', lon_list)                             #insert lonitude location into dataframe as new column
DMIstations.insert(3,'Latitude', lat_list)                              #insert latitude location into dataframe as new column

sign_list = [0.01,0.05,0.05,0.1,0.1,0.1,0.01,0.05,0.05,0.01,0.05,0.1]        #create list of significance level
DMIstations.insert(4,'Significance level', sign_list)                   #insert significance level list into dataframe as new column

sign_col = []
for level in sign_list:
    if level == 0.01:
        sign_col.append('limegreen')
    elif level == 0.05:
        sign_col.append('gold')
    else:
        sign_col.append('orangered')

DMIstations.insert(5,'Sign_col', sign_col)

# sign_mark_list = ['v','^','^','v','v','^','^','^','^','^','^']          #insert column with slope direction
# DMIstations.insert(6,'Slope direction', sign_mark_list)



#DMIstations = pd.read_parquet('DMIstations.parq.gzip')

## Create new dataframes separating stations based on slope trends:
df_mark_down = DMIstations.iloc[['0','4','5']]                          #create dataframe with only downward slopes
df_mark_down.reset_index(inplace=True, drop=True)                       #reset index

not_mark_down = list(range(0,len(DMIstations),1))                       #create list for indexes
for i in sorted([0,4,5], reverse = True):                               #identifiy and remove entries that match the indexes with downward slopes
    del not_mark_down[i]
for i in range(len(not_mark_down)):                                     #convert list of numbers to list of strings
    not_mark_down[i] = str(not_mark_down[i])

df_mark_up = DMIstations.iloc[not_mark_down]                            #create dataframe with only upward slopes
df_mark_up.reset_index(inplace=True, drop=True)                         #reset index

        

# Create map for wind speed:
terrain = cimgt.GoogleTiles(style='satellite')                              #import satellite image

fig = plt.figure(figsize=(10, 8))                                           #define subplot 
ax = fig.add_subplot(projection=terrain.crs, extent=(6.9, 15.4, 54, 58))        
ax.add_image(terrain, 8)                                                    #add satelite image

x_down, y_down = df_mark_down.Longitude, df_mark_down.Latitude              #define placement of station markers
x_up, y_up = df_mark_up.Longitude, df_mark_up.Latitude
# Insert station number and markers with colour indicating the significance level and marker indicationg the slope direction:
for i,txt in enumerate(df_mark_down.Station_ID):
    ax.annotate(txt, (x_down[i], y_down[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray', transform=ccrs.Geodetic())
    plt.scatter(x_down, y_down, 15, marker='v', color=df_mark_down.Sign_col, transform=ccrs.Geodetic())
for i,txt in enumerate(df_mark_up.Station_ID):
    ax.annotate(txt, (x_up[i], y_up[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray', transform=ccrs.Geodetic())
    plt.scatter(x_up, y_up, 15, marker='^', color=df_mark_up.Sign_col, transform=ccrs.Geodetic())

ax.set_extent(extents=(6.9, 15.4, 54, 58))                                  #define plot extent

# Create custom legend:
legend_elements = [Line2D([0], [0], marker='^', color='none', label='<0.01', markerfacecolor='limegreen', markeredgecolor='none', markersize=10),
                   Line2D([0], [0], marker='^', color='none', label='<0.05', markerfacecolor='gold', markeredgecolor='none', markersize=10),
                   Line2D([0], [0], marker='^', color='none', label='<0.10', markerfacecolor='orangered', markeredgecolor='none', markersize=10)]
legend = ax.legend(handles=legend_elements, loc="upper right", title='Significance level', facecolor='lightgray') 
plt.title('Significant DMI station locations for ERA5-DMI wind speed') 

#plt.show()
plt.savefig("significant_station_locations_wind_speed.png", dpi=200)                           #save map as png
plt.close(None)         






## Plot for alpha:

# Define list of significant DMI stations:
stationlist = [('06080' ,"Esbjerg Lufthavn"), ('06081', "Blåvandshuk Fyr"), ('06096', "Rømø/Juvre"),
    ('06124', "Sydfyns Flyveplads"), ('06156', "Holbæk Flyveplads"), ('06170', "Roskilde Lufthavn"),
    ('06183', "Drogden Fyr")]

DMIstations = pd.DataFrame (stationlist, columns = ['Station_ID', 'Station_name'])       #create dataframe with list station ID and Station_name
#print (DMIstations)

st_ID = list(DMIstations['Station_ID'])                                 #create list of all station IDs


## Insert the last longitude and latitude position for each station into dataframe:
lon_list = []                                                           #create empty list to hold location variables
lat_list = []

for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'          #Create a dynamic string for input to search for station specific parquet-files
    dmi_ERA5_zip = glob.glob(glob_string)                               #Find station specific parquet-files in current directory
    for i in dmi_ERA5_zip:
        df = pd.read_parquet(i)                                         #Read and print parquet-file
        #print(df)

        lon_list.append(df.DMI_Lon[-1])                                 #insert final longitude position into list
        lat_list.append(df.DMI_Lat[-1])                                 #insert final longitude position into list

DMIstations.insert(2,'Longitude', lon_list)                             #insert lonitude location into dataframe as new column
DMIstations.insert(3,'Latitude', lat_list)                              #insert latitude location into dataframe as new column

sign_list = [0.1,0.1,0.05,0.1,0.05,0.05,0.05]        #create list of significance level
DMIstations.insert(4,'Significance level', sign_list)                   #insert significance level list into dataframe as new column

sign_col = []
for level in sign_list:
    if level == 0.01:
        sign_col.append('limegreen')
    elif level == 0.05:
        sign_col.append('gold')
    else:
        sign_col.append('orangered')

DMIstations.insert(5,'Sign_col', sign_col)

# sign_mark_list = ['v','^','^','v','v','^','^','^','^','^','^']          #insert column with slope direction
# DMIstations.insert(6,'Slope direction', sign_mark_list)



## Create new dataframes separating stations based on slope trends:
df_mark_down = DMIstations.iloc[['1','2','3','6']]                          #create dataframe with only downward slopes
df_mark_down.reset_index(inplace=True, drop=True)                       #reset index

not_mark_down = list(range(0,len(DMIstations),1))                       #create list for indexes
for i in sorted([1,2,3,6], reverse = True):                               #identifiy and remove entries that match the indexes with downward slopes
    del not_mark_down[i]
for i in range(len(not_mark_down)):                                     #convert list of numbers to list of strings
    not_mark_down[i] = str(not_mark_down[i])

df_mark_up = DMIstations.iloc[not_mark_down]                            #create dataframe with only upward slopes
df_mark_up.reset_index(inplace=True, drop=True)                         #reset index


# Create map for alpha:
terrain = cimgt.GoogleTiles(style='satellite')                              #import satellite image

fig = plt.figure(figsize=(10, 8))                                           #define subplot 
ax = fig.add_subplot(projection=terrain.crs, extent=(6.9, 15.4, 54, 58))        
ax.add_image(terrain, 8)                                                    #add satelite image

x_down, y_down = df_mark_down.Longitude, df_mark_down.Latitude              #define placement of station markers
x_up, y_up = df_mark_up.Longitude, df_mark_up.Latitude
# Insert station number and markers with colour indicating the significance level and marker indicationg the slope direction:
for i,txt in enumerate(df_mark_down.Station_ID):
    ax.annotate(txt, (x_down[i], y_down[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray', transform=ccrs.Geodetic())
    plt.scatter(x_down, y_down, 15, marker='v', color=df_mark_down.Sign_col, transform=ccrs.Geodetic())
for i,txt in enumerate(df_mark_up.Station_ID):
    ax.annotate(txt, (x_up[i], y_up[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray', transform=ccrs.Geodetic())
    plt.scatter(x_up, y_up, 15, marker='^', color=df_mark_up.Sign_col, transform=ccrs.Geodetic())

ax.set_extent(extents=(6.9, 15.4, 54, 58))                                  #define plot extent

# Create custom legend:
legend_elements = [Line2D([0], [0], marker='^', color='none', label='<0.01', markerfacecolor='limegreen', markeredgecolor='none', markersize=10),
                   Line2D([0], [0], marker='^', color='none', label='<0.05', markerfacecolor='gold', markeredgecolor='none', markersize=10),
                   Line2D([0], [0], marker='^', color='none', label='<0.10', markerfacecolor='orangered', markeredgecolor='none', markersize=10)]
legend = ax.legend(handles=legend_elements, loc="upper right", title='Significance level', facecolor='lightgray') 
plt.title('Significant DMI station locations for ' + r'$\alpha$') 

#plt.show()
plt.savefig("significant_station_locations_alpha.png", dpi=200)                           #save map as png
plt.close(None)  

