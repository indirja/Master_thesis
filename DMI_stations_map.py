##### DMI station map #####
## Author: Bianca E. Sandvik (April 2023)

## This script plots all DMI stations listed onto a map with their station ID. 
## Locations are extracted from each stations individual parquet-file.


# Import packages:
import pandas as pd
import numpy as np
import glob       
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

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




distance = np.round(100*0.56,0)                                             #calculation of correct map scale

# Create map:
fig, ax = plt.subplots(figsize=[10, 8])
m = Basemap(llcrnrlon=6.9,llcrnrlat=54,urcrnrlon=15.4,urcrnrlat=58,
            epsg=3857, lat_1=54, lat_2=58, lat_0=56, lon_0=8.5,
            resolution='f')                                                 #define map projection and area
m.arcgisimage(xpixels=1000)                                                 #define mapimage
# m.drawcoastlines(color='grey')                                              #draw coastlines and countries
# m.drawcountries()
# m.drawmapboundary(fill_color='#99ffff')                                     #define mapboundary colour
# m.fillcontinents(color='#cc9966',lake_color='#99ffff')                      #define colour of land and ocean
lats = DMIstations.Latitude                                                 #define positions of DMI stations
lons = DMIstations.Longitude
x, y = m(lons,lats)
for i,txt in enumerate(DMIstations.Station_ID):
    ax.annotate(txt, (x[i], y[i]), xytext=(1,1), textcoords='offset points', size=8, fontweight='medium', style='italic', color='lightgray')
    plt.scatter(x, y, 10, marker='o', color='crimson')
        #Create scatter of station locations with station ID attached to the upper right corner
m.drawmapscale(lon=7.5,lat=54.3,lon0=8.5,lat0=56,length=100, fontsize=8, fontcolor='lightgray')                        #set scale bar
ax.text(55659.74539663678, 28459.542818231508, distance, size=8, color='lightgray', backgroundcolor='#19414f')     #overwrite scale number with correct distance
plt.title('DMI station locations')                                                              #set title
#plt.show()

plt.savefig("DMI_station_locations_terrain.png", dpi=200)                           #save map as png
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
#m.arcgisimage(xpixels=1000)                                                 #define mapimage
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
