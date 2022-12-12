import numpy as np
from datetime import datetime
from time import time
import sys

NB_OF_DATETIMES = 1000

datetimes = []
dt1 = datetime.strptime('2022-01-01 00:00:00','%Y-%m-%d %H:%M:%S')
dt2 = datetime.strptime('2022-01-01 06:00:00','%Y-%m-%d %H:%M:%S')
td = dt2 - dt1
for n in range(NB_OF_DATETIMES):
    datetimes.append(dt1 + n*td)

p_levels = [1000-50*n for n in range(20)]

def test_convert(wind_data : np.ndarray) -> dict:
    """ Transform 4D wind data arrays for (time,p level,lon,lat) in a 2D dict {datetime(datetime): {p level(number): [[wind]]} """
    print("Enriching wind data format...")
    t1 = time()
    enriched_wind_data = {}
    enriched_wind_data = {dt: {p_level: wind_data[i][j] for j,p_level in enumerate(p_levels)} for i,dt in enumerate(datetimes)}
    """
    for i,datetime in enumerate(datetimes):
        enriched_wind_data[datetime] = {}
        for j,p_level in enumerate(p_levels):
            t3 = time()
            enriched_wind_data[datetime][p_level] = wind_data[i][j]
            if i%20==0 and j%7==0:
                t4 = time()
                print(f"i={i} j={j}, {t4-t3} seconds")"""
    t2 = time()
    print(f"Data enriched in {t2-t1} seconds!\n")
    return enriched_wind_data

def display_enriched_wind_structure(enriched_data):
    print("1st D keys:")
    print(f"-{len(enriched_data.keys())} keys")
    print(f"-first keys: {list(enriched_data.keys())[:5]}")
    print("2nd D keys:")
    print(f"-{len(list(enriched_data.values())[0].keys())} keys")
    print(f"-first keys: {list(list(enriched_data.values())[0].keys())[:5]}")
    print("Values array shape:")
    print(f"{len(list(list(enriched_data.values())[0].values())[0])}x{len(list(list(enriched_data.values())[0].values())[0][0])}")


wind_data_mock = np.random.rand(NB_OF_DATETIMES,20,144,73,2)
enriched = test_convert(wind_data_mock)
display_enriched_wind_structure(enriched)