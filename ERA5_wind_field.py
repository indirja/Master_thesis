##### ERA5 mean wind field #####
## Author: Bianca E. Sandvik (May 2023)

## This script creates plots of ERA5 mean wind fields for the region over Denmark.

# Import packages:
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs                                                  #for maps
import cartopy.io.img_tiles as cimgt
from wrf import to_np                                                       #covert variables to numpy
import colormaps as cmaps                                                   #for defining colormaps
from matplotlib.lines import Line2D


## Import dataset:
ds = xr.open_dataset("ERA5_ug_vg_wind_speed_wind_dir.nc")                   #import geostrophic dataset
ds_1D = ds.mean(dim='time')                                                 #create a 1D dataframe with means

# Define variables:
ug = ds_1D.variables['ug']          
vg = ds_1D.variables['vg']
ws = ds_1D.variables['wind_speed']
lats = ds_1D.variables['lat']
lons = ds_1D.variables['lon']

ws_full = ds.variables['wind_speed']                                        #define variables for "unchanged" dataset
ug_full = ds.variables['ug']          
vg_full = ds.variables['vg']

# Compare calculation to ERA5:
de = xr.open_dataset("ERA5_10m_u-comp.wind_1990-2022.nc")                   #import datasets
dv = xr.open_dataset("ERA5_10m_v-comp.wind_1990-2022.nc")                   
de_1D = de.mean(dim='time')                                                 #create a 1D dataframes with means
dv_1D = dv.mean(dim='time')  
v10 = dv_1D.variables['v10']                                                #define variables
u10 = de_1D.variables['u10']





## Comparison test for ERA5 V_10 and ERA5 V_g (own calculation):
import pandas as pd
import netCDF4 as nc

ds_pd = nc.Dataset('ERA5_ug_vg_wind_speed_wind_dir.nc', 'r')            #Import datasets
du_pd = nc.Dataset('ERA5_10m_u-comp.wind_1990-2022.nc', 'r')
dv_pd = nc.Dataset('ERA5_10m_v-comp.wind_1990-2022.nc', 'r')

# define numbers of lon, lat and time
nlat = len(du_pd.variables['latitude'])
nlon = len(du_pd.variables['longitude'])
ntime = len(du_pd.variables['time'])
    #du_pd, dv_pd and ds_pd have the same dimensions

#Define variables:
ws_full = ds.variables['wind_speed']                                    #geostrophic wind speed
ug_full = ds.variables['ug']                                            #geostrophic ug          
vg_full = ds.variables['vg']                                            #geostrophic vg

u10_full = du_pd.variables['u10']                                            #u10
v10_full = dv_pd.variables['v10']                                            #v10

ws10 = np.zeros( (ntime,nlat,nlon) )                                    #calculate wind speed from u10 and v10
for ilat in range(nlat):
    ws10[:,:,:] = np.sqrt(u10_full[:,:,:]**2 + v10_full[:,:,:]**2)

ws_array = np.zeros( (ntime,nlat,nlon) )                                #convert netCDF geostrophic wind speed to array
for ilat in range(nlat):
    ws_array[:,:,:] = ws_full[:,:,:]


u10_ar = np.zeros( (ntime,nlat,nlon) )                                #convert netCDF u10 to array                  
for ilat in range(nlat):
    u10_ar[:,:,:] = u10_full[:,:,:]

v10_ar = np.zeros( (ntime,nlat,nlon) )                                #convert netCDF v10 to array
for ilat in range(nlat):
    v10_ar[:,:,:] = v10_full[:,:,:]



#calculate difference between geostrophic wind speed and 10m wind speed
diff = np.zeros( (ntime,nlat,nlon) )                                        
for ilat in range(nlat):
    diff = ws_array[:,:,:] - ws10[:,:,:]

diff_1D = diff.mean(0)                                                      #calculate means of difference over the time axis

# Contour plot of wind speed difference V_g-V_10 :
proj = ccrs.epsg(3857)                                                      #define projection
cmap = 'Greens'                                                               #define colourscheme for wind speed

fig = plt.figure(figsize=(10, 8))                                           #define subplot 
ax = plt.axes(projection=proj, extent=(6.9, 15.4, 54, 58))
plt.contourf(lons, lats, diff_1D, 70, cmap=cmap, transform=ccrs.PlateCarree())   #create wind speed contour
ax.coastlines()                                                             #set coastlines

ax.set_extent(extents=(6.9, 15.4, 54, 58))                                  #define plot extent

plt.colorbar(ax=ax, pad=0.05, shrink=0.85, label='Wind speed difference [m/s]')        #set colorbar
plt.title('Difference in mean wind speed 1990-2022 (' + r'$V_g - V_{10}$' + ')')
plt.show()
#plt.savefig("difference_mean_Vg-V10.png", dpi=200)                     #save map as png
plt.close()






## Create terrain plot with wind barbs:
terrain = cimgt.GoogleTiles(style='satellite')                              #import satellite image

fig = plt.figure(figsize=(10, 8))                                           #define subplot 
ax = fig.add_subplot(projection=terrain.crs, extent=(6.9, 15.4, 54, 58))        
ax.add_image(terrain, 8)                                                    #add satelite image

q_era5 = ax.quiver(to_np(lons), to_np(lats), to_np(u10), to_np(v10), scale=20, scale_units='inches', color='gold', transform=ccrs.PlateCarree())    #add wind quivers from ERA5
q = ax.quiver(to_np(lons), to_np(lats), to_np(ug), to_np(vg), scale=20, scale_units='inches', color='lightcoral', transform=ccrs.PlateCarree())    #add wind quivers

ax.set_extent(extents=(6.9, 15.4, 54, 58))                                  #define plot extent

legend_elements = [Line2D([0], [0], marker='^', color='none', label='Geostrophic wind', markerfacecolor='lightcoral', markeredgecolor='none', markersize=9),
                   Line2D([0], [0], marker='^', color='none', label='10 m wind', markerfacecolor='gold', markeredgecolor='none', markersize=9)]
legend = plt.legend(handles=legend_elements, loc="upper right", facecolor='grey', fontsize=9, labelcolor='w')

plt.title('ERA5 mean wind field 1990-2022')                                 #add title
#plt.show()
plt.savefig("ERA5_mean_wind_field_Vg_V10_arrow.png", dpi=200)                       #save map as png
plt.close(None) 




## Create plot with mean wind speed and windbarbs:
proj = ccrs.epsg(3857)                                                      #define projection
cmap = 'YlOrBr'                                                             #define colourscheme for wind speed

fig = plt.figure(figsize=(10, 8))                                           #define subplot 
ax = plt.axes(projection=proj, extent=(6.9, 15.4, 54, 58))
plt.contourf(lons, lats, ws, 70, cmap=cmap, transform=ccrs.PlateCarree())   #create wind speed contour
ax.coastlines()                                                             #set coastlines

ax.quiver(to_np(lons), to_np(lats), to_np(ug), to_np(vg), color='darkgrey', transform=ccrs.PlateCarree())    #add wind quivers
ax.set_extent(extents=(6.9, 15.4, 54, 58))                                  #define plot extent

plt.colorbar(ax=ax, pad=0.05, shrink=0.85, label='Wind speed [m/s]')        #set colorbar
plt.title('Geostrophic mean wind field 1990-2022')
#plt.show()
#plt.savefig("Geostrophic_mean_wind_field_ws_wd.png", dpi=200)                     #save map as png
plt.close()
