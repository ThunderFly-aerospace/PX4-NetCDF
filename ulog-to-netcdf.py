# %% 

print("Hello World")

import xarray as xr
import numpy as np
import pandas as pd
from pyulog import ULog

# %%

# Load the ULog file
log = ULog('mc.ulg')

# %% 

print("PX4 log informations.")
print(log.msg_info_dict)

# %%

data = log.data_list
[d.name for d in data]

# %%

sensor_vehicle_gps_position_data = pd.DataFrame(log.get_dataset('vehicle_gps_position').data)

middle_index = len(sensor_vehicle_gps_position_data) // 2
epoch_utc = sensor_vehicle_gps_position_data['time_utc_usec'].iloc[middle_index] / 1e6
epoch_relative = sensor_vehicle_gps_position_data['timestamp'].iloc[middle_index]

epoch = epoch_utc - epoch_relative

sensor_vehicle_gps_position_data.drop(columns=['timestamp_sample', 'device_id',
       'vel_m_s', 'vel_n_m_s',
       'vel_e_m_s', 'vel_d_m_s', 'cog_rad', 'timestamp_time_relative',
       'heading'], inplace=True)
#print(sensor_vehicle_gps_position_data.columns)

sensor_hygrometer_data = pd.DataFrame(log.get_dataset('sensor_hygrometer').data)
#sensor_hygrometer_data['utc_timestamp'] = sensor_hygrometer_data['timestamp'].apply(lambda x: epoch + x)
sensor_hygrometer_data.drop(columns=['timestamp_sample', 'device_id'], inplace=True)

sensor_baro_data = pd.DataFrame(log.get_dataset('sensor_baro').data)
#sensor_baro_data['utc_timestamp'] = sensor_baro_data['timestamp'].apply(lambda x: epoch + x)
sensor_baro_data.drop(columns=['timestamp_sample', 'device_id', 'temperature', 'error_count'], inplace=True)


merged_data = pd.concat([sensor_vehicle_gps_position_data, 
                         sensor_hygrometer_data,
                         sensor_baro_data
                        ], axis=0)
merged_data.sort_values(by='timestamp', inplace=True)
merged_data.set_index('timestamp', inplace=True)

# %%

#print(sensor_vehicle_gps_position_data)
print(sensor_hygrometer_data)
print(sensor_baro_data)

# %%

print(merged_data)
# Perform linear extrapolation on selected columns
columns_to_extrapolate = sensor_vehicle_gps_position_data.columns
for column in columns_to_extrapolate:
    merged_data[column] = merged_data[column].interpolate(method='linear', limit_direction='both')


print(merged_data)
# %%



ds = xr.Dataset.from_dataframe(merged_data)


# Rename variables in xarray dataset to required variable names
rename_dict = {
    'latitude_deg' : 'lat',
    'longtitude_deg' : 'lon',
    'altitude_msl_m' : 'altitude',
    'temperature': 'air_temperature',
    'dew_point': 'dew_point_temperature',
    #'gpt' : 'non_coordinate_geopotential',
    'altitude_ellipsoid_m' : 'geopotential_height',
    #'wind_speed' : 'wind_speed',
    #'wind_dir' : 'wind_direction',
    'humidity' : 'relative_humidity',
    'pressure' : 'air_pressure',

}

# Rename the variables within this xarray dataframe based on the rename dictionary above
ds = ds.rename(rename_dict)


# Convert Air Temperature from Celsius to Kelvin
ds['air_temperature'] = ds['air_temperature'] + 273.15

# Convert Dew Point Temperature from Celsius to Kelvin
# ds['dew_point_temperature'] = ds['dew_point_temperature'] + 273.15


# Adding attributes to variables in the xarray dataset
ds['time'].attrs = {'units': 'seconds since 1970-01-01T00:00:00', 'long_name': 'Time', '_FillValue': float('nan'), 'processing_level': ''}
ds['lat'].attrs = {'units': 'degrees_north', 'long_name': 'Latitude', '_FillValue': float('nan'), 'processing_level': ''}
ds['lon'].attrs = {'units': 'degrees_east', 'long_name': 'Longitude', '_FillValue': float('nan'), 'processing_level': ''}
ds['altitude'].attrs = {'units': 'meters_above_sea_level', 'long_name': 'Altitude', '_FillValue': float('nan'), 'processing_level': ''}
ds['air_temperature'].attrs = {'units': 'Kelvin', 'long_name': 'Air Temperature', '_FillValue': float('nan'), 'processing_level': ''}
#ds['dew_point_temperature'].attrs = {'units': 'Kelvin', 'long_name': 'Dew Point Temperature', '_FillValue': float('nan'), 'processing_level': ''}
#ds['non_coordinate_geopotential'].attrs = {'units': 'm^2 s^-2', 'long_name': 'Non Coordinate Geopotential', '_FillValue': float('nan'), 'processing_level': ''}
#ds['geopotential_height'].attrs = {'units': 'meters', 'long_name': 'Geopotential Height', '_FillValue': float('nan'), 'processing_level': ''}
#ds['wind_speed'].attrs = {'units': 'm/s', 'long_name': 'Wind Speed', '_FillValue': float('nan'), 'processing_level': ''}
#ds['wind_direction'].attrs = {'units': 'degrees', 'long_name': 'Wind Direction', '_FillValue': float('nan'), 'processing_level': ''}
#ds['humidity_mixing_ratio'].attrs = {'units': 'kg/kg', 'long_name': 'Humidity Mixing Ratio', '_FillValue': float('nan'), 'processing_level': ''}
ds['relative_humidity'].attrs = {'units': '%', 'long_name': 'Relative Humidity', '_FillValue': float('nan'), 'processing_level': ''}
ds['air_pressure'].attrs = {'units': 'Pa', 'long_name': 'Atmospheric Pressure', '_FillValue': float('nan'), 'processing_level': ''}

# Add Global Attributes synonymous across all UASDC providers
ds.attrs['Conventions'] = "CF-1.8, WMO-CF-1.0"
ds.attrs['wmo__cf_profile'] = "FM 303-2024"
ds.attrs['featureType'] = "trajectory"

# Add Global Attributes unique to Provider
ds.attrs['platform_name'] = "ThunderFly_TF-ATMON"
ds.attrs['flight_id'] = ""
ds.attrs['site_terrain_elevation_height'] = "xxxm"
ds.attrs['processing_level'] = "raw"

# Grab Initial timestamp of observations
timestamp_dt = pd.to_datetime(ds['time'].values[0], unit='s', origin='unix')

# Format datetime object to desired format (YYYYMMDDHHMMSSZ)
formatted_timestamp = timestamp_dt.strftime('%Y%m%d%H%M%S') + 'Z'

# Save to a NetCDF file
a = "UASDC"
operator_id = "operatorID"
airframe_id = "airframeID"
ds.to_netcdf(f'?a}_{operator_id}_{airframe_id}_{formatted_timestamp}.nc')