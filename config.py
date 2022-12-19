import os

RAW_DATA_DIR = os.path.join('data','raw')
WORK_DATA_DIR = os.path.join('data','work')
NETCDF4_FILES = (os.path.join(RAW_DATA_DIR,'uwnd.2022.nc'),os.path.join(RAW_DATA_DIR,'vwnd.2022.nc'))

def get_month_wind_data_pickle_file(year,month):
    month_str = ('0'+str(month))[-2:]
    fn = os.path.join(WORK_DATA_DIR,f"{year}-{month_str}.pickle")
    return fn