import pickle
import os

from config import WORK_DATA_DIR

def get_wind_work_data(year=2022,month=1):
    """ Return one month of wind work data """
    month_str = ('0'+str(month))[-2:]
    fn = os.path.join(WORK_DATA_DIR,f"{year}-{month_str}.pickle")
    with open(fn,'rb') as pickle_in:
        wind_data = pickle.load(pickle_in)
    return wind_data