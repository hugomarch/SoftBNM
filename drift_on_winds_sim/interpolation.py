from math import floor
import datetime
import numpy as np

from formulas import altitude_from_pressure
from config import LON_INTERVAL, LAT_INTERVAL
from wind_reader import load_stored_day_wind_data

def int_to_binary_list(n, dim):
    res = []
    while n >= 1:
        res.append(n%2)
        n //= 2
    return tuple(res + [0]*(dim - len(res)))

def get_hypercube_corner_coordinates(n):
    res = []
    for k in range(2**n):
        res.append(int_to_binary_list(k, n))
    return res

def interpol_01(f, x):
    """
    la fonction f à interpoler sur l'hypercube [01]^n est représentée par un dictionnaire {[0, 1, 1] : val}
    x est le vecteur de l'hypercube dont on cherche f(x)
    """
    n = len(list(f.keys())[0])
    dim_f = len(list(f.values())[0])
    s = np.zeros(dim_f)

    for corner in get_hypercube_corner_coordinates(n):
        p = np.array(f[corner])     # f(coin)
        for k in range(n):         # coefficients de ponderation
            if corner[k]:
                p *= x[k] 
            else:
                p *= (1 - x[k])
        s += p
    return tuple(s)

def get_wind_at_coord(day_wind_data,coord):
    # find bounds and linear coef for each dimension
    bound = {}
    linear_coef = {}
    time_values = list(day_wind_data.keys())
    pressure_values = list(list(day_wind_data.values())[0].keys())
    time = coord['time']
    for t1,t2 in zip(time_values[:-1],time_values[1:]):
        if t2 > time:
            bound['time'] = (t1,t2)
            linear_coef['time'] = (time-t1).total_seconds()/(t2-t1).total_seconds()
            break
    height = coord['height']
    for p1,p2 in zip(pressure_values[:-1],pressure_values[1:]):
        h1,h2 = altitude_from_pressure(p1),altitude_from_pressure(p2)
        if h2 > height:
            bound['pressure'] = (p1,p2)
            bound['height'] = (h1,h2)
            linear_coef['height'] = (height-h1)/(h2-h1)
            break
    lon = coord['lon']
    lon1_id = floor(lon/LON_INTERVAL)
    lon2_id = (lon1_id+1)%(floor(360/LON_INTERVAL))
    bound["lon"] = (lon1_id,lon2_id)
    linear_coef["lon"] = (lon-lon1_id*LON_INTERVAL)/LON_INTERVAL
    lat = coord['lat']
    lat1_id = floor((lat+90)/LAT_INTERVAL)
    lat2_id = lat1_id + 1
    bound["lat"] = (lat1_id,lat2_id)
    linear_coef["lat"] = (lat+90-lat1_id*LAT_INTERVAL)/LAT_INTERVAL
    # find wind vector at each hypercube corner
    wind_on_corner = {}
    dimensions = ["time","height","lon","lat"]
    for corner in get_hypercube_corner_coordinates(len(dimensions)):
        labeled_corner = {dimensions[i]: corner[i] for i in range(len(corner))}
        temp = day_wind_data
        temp = temp[bound['time'][labeled_corner['time']]]
        temp = temp[bound['pressure'][labeled_corner['height']]]
        temp = temp[bound['lon'][labeled_corner['lon']]]
        wind = tuple(temp[bound['lat'][labeled_corner['lat']]])
        wind_on_corner[corner] = wind
    print(bound)
    print(wind_on_corner)
    interpoled_wind = interpol_01(wind_on_corner, [linear_coef[dim] for dim in dimensions])
    return interpoled_wind

day_wind_data = load_stored_day_wind_data()
time = datetime.datetime.strptime("07-01-1979 12:34:56","%d-%m-%Y %H:%M:%S")
height = 14798
lon = 2.245748
lat = 48.714509
coord = {'time':time,'height':height,'lon':lon,'lat':lat}
wind = get_wind_at_coord(day_wind_data,coord)
print(wind)
    

