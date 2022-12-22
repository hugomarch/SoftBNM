import numpy as np
from datetime import datetime, timedelta
import pickle
import os
from time import time

from data_access.netCDF4_reader import load_var_of_netCDF4_dataset
from config import NETCDF4_FILES, WORK_DATA_DIR
from utils import convert_timestamp_in_datetime

""" This file gathers functions dedicated to load raw data and transform it into a use-ready format.
    4 levels of functions:
    - load data and collect metadata (typically for year period)
    - enrich data by transform 4D array into a 2D-dict {time: p-level: [lon][lat] wind array}
    - decompose data by day and store it in a working data dir 
    - full pipeline """

# 1. LOAD

def get_NOAA_NCEP_reanalysis_year_wind_data():
    print("Loading raw data of NOAA NCEP reanalysis...")
    t1 = time()
    uwnd_file = NETCDF4_FILES[0]
    vwnd_file = NETCDF4_FILES[1]
    uwnd_data = load_var_of_netCDF4_dataset(uwnd_file,'uwnd')
    vwnd_data = load_var_of_netCDF4_dataset(vwnd_file,'vwnd')
    year_wind_data = np.concatenate((uwnd_data,vwnd_data),axis=-1)
    metadata = {}
    times = load_var_of_netCDF4_dataset(uwnd_file,'time')
    metadata['datetimes'] = [convert_timestamp_in_datetime(timestamp) for timestamp in times]
    p_levels = list(load_var_of_netCDF4_dataset(uwnd_file,'level'))
    metadata['pressure levels'] = p_levels
    metadata['LON interval'] = 2.5
    metadata['LAT interval'] = 2.5
    t2 = time()
    print(f"Data loaded in {t2-t1} seconds !\n")
    return year_wind_data, metadata

# 2. ENRICH

def convert_wind_data_to_datetime_pressure_keys_format(wind_data : np.ndarray, metadata) -> dict:
    """ Transform 4D wind data arrays for (time,p level,lon,lat) in a 2D dict {datetime(datetime): {p level(number): [[wind]]} """
    print("Enriching wind data format...")
    t1 = time()
    enriched_wind_data = {}
    datetimes = metadata['datetimes']
    p_levels = metadata['pressure levels']
    enriched_wind_data = {dt: {p_level: wind_data[i][j] for j,p_level in enumerate(p_levels)} for i,dt in enumerate(datetimes)}
    t2 = time()
    print(f"Data enriched in {t2-t1} seconds!\n")
    return enriched_wind_data


# 3. DECOMPOSE AND STORE FOR WORK

def store_wind_data_by_month(wind_data : dict, metadata):
    """ Take as input a 2D wind data dict with datetime-pressure keys.
        Group it by month, and store each month as a single 2D wind data dict (still datetime-pressure keys). """
    print("Grouping and storing data by month...")
    t1 = time()
    # clear work data directory
    for file in os.listdir(WORK_DATA_DIR):
        if file.endswith('pickle'):
            os.remove(os.path.join(WORK_DATA_DIR,file))
    # group and store by month
    wind_by_month = {}
    for datetime, wind_at_dt in wind_data.items():
        year_month = datetime.strftime("%Y-%m")
        year = datetime.strftime("%Y")
        wind_by_month.setdefault(year_month,{})
        wind_by_month[year_month][datetime] = wind_at_dt
    with open(os.path.join(WORK_DATA_DIR,f"{year}_metadata.pickle"),'wb') as pickle_out:
            pickle.dump(metadata,pickle_out)
    for year_month, wind_of_month in wind_by_month.items():
        with open(os.path.join(WORK_DATA_DIR,f"{year_month}.pickle"),'wb') as pickle_out:
            pickle.dump(wind_by_month[year_month],pickle_out)
    t2 = time()
    print(f"Data grouped and stored by month in {t2-t1} seconds!\n")

# 4. PIPELINE

def pipeline_NOAA_NCEP_reanalysis_year():
    print("Executing full pipeline for NOAA NCEP reanalysis data...\n")
    t1 = time()
    year_wind_data, metadata = get_NOAA_NCEP_reanalysis_year_wind_data()
    enriched_wind_data = convert_wind_data_to_datetime_pressure_keys_format(year_wind_data, metadata)
    store_wind_data_by_month(enriched_wind_data, metadata)
    t2 = time()
    print(f"Full pipeline executed in {t2-t1} seconds!\n")
    