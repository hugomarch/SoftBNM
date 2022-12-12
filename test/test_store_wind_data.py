import numpy as np
from datetime import datetime
from time import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_access.wind_data_back_service import convert_wind_data_to_datetime_pressure_keys_format, store_wind_data_by_month

NB_OF_DATETIMES = 1000

datetimes = []
dt1 = datetime.strptime('2022-01-01 00:00:00','%Y-%m-%d %H:%M:%S')
dt2 = datetime.strptime('2022-01-01 06:00:00','%Y-%m-%d %H:%M:%S')
td = dt2 - dt1
for n in range(NB_OF_DATETIMES):
    datetimes.append(dt1 + n*td)

p_levels = [1000-50*n for n in range(20)]

wind_data_mock = np.random.rand(NB_OF_DATETIMES,20,144,73,2)
metadata_mock = {'datetimes': datetimes, 'pressure levels': p_levels, 'LON interval': 2.5, 'LAT interval': 2.5}
enriched_wind_data_mock = convert_wind_data_to_datetime_pressure_keys_format(wind_data_mock,metadata_mock)

store_wind_data_by_month(enriched_wind_data_mock, metadata_mock)

