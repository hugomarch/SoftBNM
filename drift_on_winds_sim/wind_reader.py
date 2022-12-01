from math import ceil, floor
import datetime
from time import time
import pickle

from config import TIMESTAMP_MIN, DATE_MIN, PRESSURE_LEVELS, DAY_WIND_DATA_FILE, LON_INTERVAL, LAT_INTERVAL
from con import create_connection
from formulas import altitude_from_pressure

def get_wind_data(con, timestamp = 1569072):
    """retourne toute les données de vents pour un timestamp"""
    print(f"Starting to read data for timestamp = {timestamp}")
    wind_data = {p_level: [[[0, 0] for _ in range(73)] for _ in range(144)] for p_level in PRESSURE_LEVELS}
    request_u = "select level, lon, lat, u from uwind where t="+str(timestamp)
    request_v = "select level, lon, lat, v from vwind where t="+str(timestamp)
    requests = [request_u,request_v]
    cur = con.cursor()
    for i in range(2):
        cur.execute(requests[i])
        counter = 0
        t0 = time()
        end = False
        while not end:
            x = cur.fetchone()
            counter += 1
            if counter%10000 == 0:
                print(f"{counter}: avg time of {(time()-t0)/10000*1000}ms by row")
                t0 = time()
            if x is None:
                end = True
            else:
                p = x[0]
                lon = int(x[1]/LON_INTERVAL)
                lat = int((x[2]+90)/LAT_INTERVAL)
                wind_coord = x[3]
                wind_data[p][lon][lat][i] = wind_coord
    return wind_data

def convert_wind_data_p_to_z(wind_data):
    """ take a wind_data and convert all pressure keys in altitude """
    wind_data = {altitude_from_pressure(p):x for p,x in wind_data.items()}
    return wind_data

def get_day_wind_data(con, day, convert_p_to_z = False, store_data = False):
    """ return a dictionary of wind arrays with corresponding hours as keys. Hours are < 0 (resp >= 24) for the latest wind array of the previous day (resp earliest wind array of next day) """
    # find datetime of latest wind data of the previous day and corresponding timestamp
    day_wind_data = {}
    h_minus_1 = day - datetime.timedelta(hours=1)
    seconds_since_hour_min = (h_minus_1 - DATE_MIN).total_seconds()
    first_timestamp = floor(seconds_since_hour_min/(3600*6))*6 + TIMESTAMP_MIN
    first_datetime = DATE_MIN + datetime.timedelta(hours = first_timestamp - TIMESTAMP_MIN)
    for data_index in range(7):
        timestamp_ = first_timestamp + 6*data_index
        wind_data = get_wind_data(con, timestamp=timestamp_)
        if convert_p_to_z:
            wind_data = convert_wind_data_p_to_z(wind_data)
        day_wind_data[first_datetime + datetime.timedelta(hours = data_index*6)] = wind_data
    if store_data:
        with open(DAY_WIND_DATA_FILE,'wb') as pickle_out:
            pickle.dump(day_wind_data,pickle_out)
        print("Wind day data successfully stored.")
    return day_wind_data

def load_stored_day_wind_data():
    with open(DAY_WIND_DATA_FILE,'rb') as pickle_in:
        day_wind_data = pickle.load(pickle_in)
    return day_wind_data

con = create_connection()
day = datetime.datetime.strptime("07-01-1979","%d-%m-%Y")
#get_day_wind_data(con,day,store_data = True)
#wind_data = load_stored_day_wind_data()

