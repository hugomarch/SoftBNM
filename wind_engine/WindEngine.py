from math import ceil, floor

from data_access.wind_data_front_service import get_wind_work_data,get_wind_metadata
from wind_engine.interpolation import get_wind_at_coord
from wind_engine.config import DECIMALS_OF_WIND_TABLE_KEYS

class WindEngine:

    def load_wind_data(self,year,month):
        self.wind_data = {'year': year,'month': month,'data': get_wind_work_data(year=year,month=month)}
        self.metadata = get_wind_metadata(year=year)

    def get_wind_data_degree_interval(self):
        lon_interval = self.metadata['LON Interval']
        lat_interval = self.metadata['LAT Interval']
        degree_interval = [lon_interval,lat_interval]
        return degree_interval
    
    def make_wind_table(self,map_area,lon_0,lat_0,degree_interval,time,pressure=None,height=None):
        """ Compute all winds in a 2:1 rectangle thats fits in app window, represented by map_area (longitude upper limit may be > 360) 
            Return a wind table as a dict with (lon,lat) couples as keys and wind as values. lon are given % 360 in keys
            lon_0 and lat_0 are the coordinates of the point chosen as the origin of the wind grid """
        # wind grid limits expressed as integers corresponding to coordinates on the wind grid
        wind_grid_limits = [0,0,floor((map_area[2]-lon_0)/degree_interval),floor((lat_0-map_area[3])/degree_interval)]
        wind_table = {}
        for i in range(wind_grid_limits[0],wind_grid_limits[2]+1):
            for j in range(wind_grid_limits[1],wind_grid_limits[3]+1):
                lon = round(lon_0 + i*degree_interval,DECIMALS_OF_WIND_TABLE_KEYS)
                lat = round(lat_0 - j*degree_interval,DECIMALS_OF_WIND_TABLE_KEYS)
                interpol_coord = {'time':time,'pressure':pressure,'height':height,'lon':lon,'lat':lat}
                params = {altitude_param:('height' if height is not None else 'pressure'),lon_interval:self.metadata['LON Interval'],lat_interval:self.metadata['LAT Interval']}
                wind_table[(lon,lat)] = get_wind_at_coord(self.wind_data,interpol_coord,**params)
        return wind_table,wind_grid_limits

    def compute_single_wind(self,lon,lat,time,pressure=None,height=None):
        interpol_coord = {'time':time,'pressure':pressure,'height':height,'lon':lon,'lat':lat}
        params = {altitude_param:('height' if height is not None else 'pressure'),lon_interval:self.metadata['LON Interval'],lat_interval:self.metadata['LAT Interval']}
        wind = get_wind_at_coord(self.wind_data,interpol_coord,**params)
        return wind



