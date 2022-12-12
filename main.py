from datetime import datetime
import numpy as np
import sys

from data_access.netCDF4_reader import display_netCDF4_dataset, display_var_of_netCDF4_dataset, load_var_of_netCDF4_dataset
from data_access.wind_data_back_service import get_NOAA_NCEP_reanalysis_year_wind_data, pipeline_NOAA_NCEP_reanalysis_year
from data_access.wind_data_front_service import get_wind_work_data
from config import NETCDF4_FILES


from utils import convert_datetime_in_timestamp
    
wind_data = get_wind_work_data(year=2022,month=7)
dt = list(wind_data.keys())[0]
pmin = list(wind_data[dt].keys())[-1]
print(f"{dt} ; {pmin} : {wind_data[dt][pmin].shape}")
print(wind_data[dt][pmin][0])
