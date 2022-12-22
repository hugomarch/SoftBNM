import pickle
import os

from config import WORK_DATA_DIR, get_month_wind_data_pickle_file, get_year_metadata_pickle_file

def get_wind_work_data(year=2022,month=1):
    """ Return one month of wind work data """
    fn = get_month_wind_data_pickle_file(year,month)
    with open(fn,'rb') as pickle_in:
        wind_data = pickle.load(pickle_in)
    return wind_data

def get_wind_metadata(year=2022):
    """ Return wind metadata of a given year """
    fn = get_year_metadata_pickle_file(year)
    with open(fn,'rb') as pickle_in:
        wind_data = pickle.load(pickle_in)
    return wind_data