##### DMI station map #####
## Author: Bianca E. Sandvik (May 2023)

## This script plots the significant DMI stations listed (based on ERA5-DMI wind speed) onto a map with their station ID with colour 
## indiaction for their significance level. 

# Import packages:
import pandas as pd
import numpy as np
import glob       
import pandas as pd
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
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



# Create map with Basemap:
distance = np.round(100*0.56,0)                                             #calculation of correct map scale

fig, ax = plt.subplots(figsize=[10, 8])
legend_elements = [Line2D([0], [0], marker='o', color='#D5D7D2', label='<0.01', markerfacecolor='limegreen', markersize=10),
                   Line2D([0], [0], marker='o', color='#D5D7D2', label='<0.05', markerfacecolor='gold', markersize=10),
                   Line2D([0], [0], marker='o', color='#D5D7D2', label='<0.10', markerfacecolor='orangered', markersize=10)]
ax.legend(handles=legend_elements)                                         #create custom legend
m = Basemap(llcrnrlon=6.9,llcrnrlat=54,urcrnrlon=15.4,urcrnrlat=58,
            epsg=3857, lat_1=54, lat_2=58, lat_0=56, lon_0=8.5,
            resolution='f')                                                 #define map projection and area
m.arcgisimage(xpixels=1000)                                                 #define mapimage
# m.drawcoastlines(color='grey')                                              #draw coastlines and countries
# m.drawcountries()
# m.drawmapboundary(fill_color='#99ffff')                                     #define mapboundary colour
# m.fillcontinents(color='#cc9966',lake_color='#99ffff')                      #define colour of land and ocean
# lats = DMIstations.Latitude                                                 #define positions of DMI stations
# lons = DMIstations.Longitude
# x, y = m(lons,lats)
x_down, y_down = m(df_mark_down.Longitude, df_mark_down.Latitude)
x_up, y_up = m(df_mark_up.Longitude, df_mark_up.Latitude)
for i,txt in enumerate(df_mark_down.Station_ID):
    ax.annotate(txt, (x_down[i], y_down[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray')
    plt.scatter(x_down, y_down, 10, marker='v', color=df_mark_down.Sign_col)
for i,txt in enumerate(df_mark_up.Station_ID):
    ax.annotate(txt, (x_up[i], y_up[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray')
    plt.scatter(x_up, y_up, 10, marker='^', color=df_mark_up.Sign_col)
#for i,txt in enumerate(DMIstations.Station_ID):
    #ax.annotate(txt, (x[i], y[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray')
    #plt.scatter(x, y, 10, marker='o', color=sign_col)
        #Create scatter of station locations with station ID attached to the upper right corner
m.drawmapscale(lon=7.5,lat=54.3,lon0=8.5,lat0=56,length=100, fontsize=8, fontcolor='lightgray')                    #set scale bar
ax.text(55659.74539663678, 28459.542818231508, distance, size=8, color='lightgray', backgroundcolor='#19414f')     #overwrite scale number with correct distance
plt.title('Significant DMI station locations')                                                              #set title
#plt.show()

#plt.savefig("significant_station_locations_terrain.png", dpi=200)                           #save map as png
plt.close(None)         


## With cartopy:
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

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










### Map of positional changes:

from matplotlib.lines import Line2D

lon_list_start = []                                                     #create empty list to hold location variables
lat_list_start = []
lon_list_end = []                                              
lat_list_end = []

for station in st_ID:
    glob_string = 'DMI_ERA5_' + station + '_monthly.parq.gzip'          #Create a dynamic string for input to search for station specific parquet-files
    dmi_ERA5_zip = glob.glob(glob_string)                               #Find station specific parquet-files in current directory
    for i in dmi_ERA5_zip:
        df = pd.read_parquet(i)                                         #Read and print parquet-file
        #print(df)

        lon_list_start.append(df.DMI_Lon[0])                            #insert start longitude position into list
        lat_list_start.append(df.DMI_Lat[0])                            #insert start latitude position into list
        lon_list_end.append(df.DMI_Lon[-1])                             #insert final longitude position into list
        lat_list_end.append(df.DMI_Lat[-1])                             #insert final latitude position into list

DMIstations.insert(2,'Lon_start', lon_list_start)                       #insert location into dataframe as new column
DMIstations.insert(3,'Lat_start', lat_list_start)     
DMIstations.insert(4,'Lon_end', lon_list_end) 
DMIstations.insert(5,'Lat_end', lat_list_end)  


# Create map:
fig, ax = plt.subplots(figsize=[10, 8])
legend_elements = [Line2D([0], [0], marker='o', color='w', label='Start location', markerfacecolor='crimson', markersize=10),
                   Line2D([0], [0], marker='o', color='w', label='End location', markerfacecolor='darkslateblue', markersize=10)]
plt.legend(handles=legend_elements)                                         #create custom legend
m = Basemap(llcrnrlon=6.9,llcrnrlat=54,urcrnrlon=15.4,urcrnrlat=58,
            epsg=3857, lat_1=54, lat_2=58, lat_0=56, lon_0=8.5,
            resolution='f')                                                 #define map projection and area
m.drawcoastlines(color='grey')                                              #draw coastlines and countries
m.drawcountries()
m.drawmapboundary(fill_color='#99ffff')                                     #define mapboundary colour
m.fillcontinents(color='#cc9966',lake_color='#99ffff')                      #define colour of land and ocean
lats = DMIstations.Lat_start                                                #define starting positions of DMI stations
lons = DMIstations.Lon_start
x1, y1 = m(lons,lats)
plt.scatter(x1, y1, 15, marker='o', color='crimson')
    #Create scatter of station locations with station ID attached to the upper right corner
late = DMIstations.Lat_end                                                  #define end positions of DMI stations
lone = DMIstations.Lon_end
x2, y2 = m(lone,late)
plt.scatter(x2, y2, 15, marker='o', color='darkslateblue')
    #Create scatter of station locations with station ID attached to the upper right corner
m.drawmapscale(lon=7.5,lat=54.3,lon0=8,lat0=54.1,length=50, fontsize=8)    #add scale bar
plt.title('DMI station locations')                                          #set title
plt.show()









