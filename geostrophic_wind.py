##### Geostropic wind calculation #####
## Author: Bianca E. Sandvik (March 2023)

## This file calculates the geostrophic wind components (ug and vg), wind speed and wind direction from a netCDF-file containing 
## geopotential. A new netCDF-file called "ERA5_ug_vg_wind_speed_wind_dir.nc" is created where the calculated wind parameters are 
## stored. 


# Importing packages:
import netCDF4 as nc
import numpy as np
import metpy.calc as mpcalc
import metpy.units as mpunits


### Calculate wind parameters:

# Define original dataset:
fn = '/Users/Bianca/Desktop/Thesis_data/ERA5_geopotential_1000hPa_1990-2022.nc'
geopot_file = nc.Dataset(fn, 'r')

print(geopot_file.variables.keys())                    #check variables in dataset


# Initial definitions:
lat = geopot_file.variables['latitude'][:]             #store latitude data into a variable
lon = geopot_file.variables['longitude'][:]            #store longitude data into a variable
geopotential = geopot_file.variables['z']              #define geopotential variable


# Calculate coriolis parameter: 
rad_earth = 6360000                                    # define Earth´s radius, unit: m
lon_degree_grid = (lon[-1]-lon[0])/(len(lon)-1)        # define gridsize ,      unit: degrees
lat_degree_grid = (lat[-1]-lat[0])/(len(lat)-1)             # NB! latitude is defined from higher to lower
delta_theta = (-lat_degree_grid*2*np.pi)/180           # unit: radians
delta_lambda = (lon_degree_grid*2*np.pi)/180           # unit: radians


nlat = len(lat)                                        #number of latitudes
nlon = len(lon)                                        #number of longitudes
ntime = len(geopotential)                              #number of timesteps

f = np.zeros( (ntime,nlat,nlon) )                      #Create empty 3D-arrays to contain variables created in loop
coeffu = np.zeros( (ntime, nlat,nlon) )
coeffv = np.zeros( (ntime, nlat,nlon) )
ug = np.zeros( (ntime,nlat,nlon) )
vg = np.zeros( (ntime,nlat,nlon) )
wind_speed = np.zeros( (ntime,nlat,nlon) )
wind_dir = np.zeros( (ntime,nlat,nlon) )
wind_dir1 = np.zeros( (ntime,nlat,nlon) )
wind_dir2 = np.zeros( (ntime,nlat,nlon) )


# Create loop that itterates through each gridcell by latitude index
for ilat in range(nlat):                            #set parameters that are time invariant
   latmid = ((lat[0]+(float(ilat+1)*lat_degree_grid))*np.pi)/180					#latitude in middle of calculation, unit: radians
   f[:,ilat,:] = 2*7.292*10**(-5)*np.sin(latmid)				                    #Coriolis-parameter
   coeffu[:,ilat,:] = - 1/(f[:,ilat,:] * rad_earth * delta_theta)                    #coefficient for u-component
   coeffv[:,ilat,:] =   1/(f[:,ilat,:] * np.cos(latmid) * rad_earth * delta_lambda)	#coefficient for v-component

   #print('Latitude = ',latmid*180/np.pi,'  f = ', f[0,ilat,0],'  coeffu = ',coeffu[0,ilat,0],)#'  coeffv = ',coeffv[0,ilat])
        #NOTE: latmid goes up to lat=53.5

   ug[:,1:nlat-1,1:nlon-1] = coeffu[:,0:nlat-2, 1:nlon-1] * (geopotential[:,0:nlat-2,1:nlon-1] - geopotential[:,2:nlat,1:nlon-1])
   vg[:,1:nlat-1,1:nlon-1] = coeffv[:,0:nlat-2, 1:nlon-1] * (geopotential[:,1:nlat-1,2:nlon] - geopotential[:,1:nlat-1,0:nlon-2])
        ##loops trough all indexes and calculate ug and vg except edges
        ##latitude index for coeffu and coeffv needs to be cut 2 from end due to its original calculation starts at lat[1]
   wind_speed[:,1:nlat-1,1:nlon-1] = np.sqrt(ug[:,1:nlat-1,1:nlon-1]**2 + vg[:,1:nlat-1,1:nlon-1]**2)
   #wind_dir1[:,1:nlat-1,1:nlon-1] = (np.arctan2(vg[:,1:nlat-1,1:nlon-1], ug[:,1:nlat-1,1:nlon-1])) * (180 / np.pi)
          ## Should work, but doesn´t?
   wind_dir2[:,1:nlat-1,1:nlon-1] = mpcalc.wind_direction(ug[:,1:nlat-1,1:nlon-1]*mpunits.units('m/s'), vg[:,1:nlat-1,1:nlon-1]*mpunits.units('m/s'), convention='from')
          ##Use metpy-library to calculate wind direction. Metpy requires units to be defined for used variables. 
   #print('ug =',ug[:,1:nlat-1,1:nlon-1])
   #print('vg =',vg[:,1:nlat-1,1:nlon-1])
   #print('wind speed =',wind_speed[:,1:nlat-1,1:nlon-1])
   #print('wind dir1 =',wind_dir1[:,1:nlat-1,1:nlon-1])
   print('wind dir2 =',wind_dir2[:,1:nlat-1,1:nlon-1])



### Create a new netCDF-file for storing new variables with their new dimensions: 

# Create new arrays to contain new variables without empty edges:
ug_inner = ug[:,1:nlat-1,1:nlon-1]
vg_inner = vg[:,1:nlat-1,1:nlon-1]
wind_dir_inner = wind_dir2[:,1:nlat-1,1:nlon-1]
wind_speed_inner = wind_speed[:,1:nlat-1,1:nlon-1]

lat_inner = lat[1:-1]                                       #Create latitude array
lon_inner = lon[1:-1]                                       #Create longitude array
time_inner = geopot_file.variables['time'][:]               #Define time array as original netCDF-file

# Create dictionaries with attributes for each variable:
time_attr_dict = {'standard_name': 'time', 'long_name': 'time', 'units': 'hours since 1900-01-01 00:00:00.0', 'calendar': 'gregorian', 'axis': 'T'}
lon_attr_dict = {'standard_name': 'longitude', 'long_name': 'longitude', 'units': 'degrees_east', 'axis': 'X'}
lat_attr_dict = {'standard_name': 'latitude', 'long_name': 'latitude', 'units': 'degrees_north', 'axis': 'Y'}
ug_attr_dict = {'standard_name': 'ug', 'long_name': 'geostrophic_wind_u_component', 'units': 'm/s'}
vg_attr_dict = {'standard_name': 'vg', 'long_name': 'geostrophic_wind_v_component', 'units': 'm/s'}
wind_speed_attr_dict = {'standard_name': 'wind_speed', 'long_name': 'wind_speed', 'units': 'm/s'}
wind_dir_attr_dict = {'standard_name': 'wind_dir', 'long_name': 'wind_direction', 'units': 'degrees'}

## Create new netCDF4-file:
netCDF_new = nc.Dataset('ERA5_ug_vg_wind_speed_wind_dir.nc','w');
netCDF_new.createDimension('lon', len(lon_inner));               #Create longitude, latitude and time dimensions
netCDF_new.createDimension('lat', len(lat_inner));
netCDF_new.createDimension('time', ntime);
# Create netCDF-variables with attribute list and values from previously created arrays:
lonvar = netCDF_new.createVariable('lon','float32',('lon')); lonvar.setncatts(lon_attr_dict); lonvar[:] = lon_inner;
latvar = netCDF_new.createVariable('lat','float32',('lat')); latvar.setncatts(lat_attr_dict); latvar[:] = lat_inner;
timevar = netCDF_new.createVariable('time','int32',('time')); timevar.setncatts(time_attr_dict); timevar[:] = time_inner;
ugvar = netCDF_new.createVariable('ug','float32',('time','lat','lon')); ugvar.setncatts(ug_attr_dict); ugvar[:] = ug_inner;
vgvar = netCDF_new.createVariable('vg','float32',('time','lat','lon')); vgvar.setncatts(vg_attr_dict); vgvar[:] = vg_inner;
wind_speed_var = netCDF_new.createVariable('wind_speed','float32',('time','lat','lon')); wind_speed_var.setncatts(wind_speed_attr_dict); wind_speed_var[:] = wind_speed_inner;
wind_dir_var = netCDF_new.createVariable('wind_dir','float32',('time','lat','lon')); wind_dir_var.setncatts(wind_dir_attr_dict); wind_dir_var[:] = wind_dir_inner;
netCDF_new.close();

# Print new netCDF:
new_netCDF = nc.Dataset('ERA5_ug_vg_wind_speed_wind_dir.nc', 'r')












