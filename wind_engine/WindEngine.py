from math import ceil

from data_access.wind_data_front_service import get_wind_work_data,get_wind_metadata
from wind_engine.interpolation import get_wind_at_coord

class WindEngine:

    def load_wind_data(self,year,month):
        self.wind_data = {'year': year,'month': month,'data': get_wind_work_data(year=year,month=month)}
        self.metadata = get_wind_metadata(year=year)
    
    def make_wind_grid(self,map_area,degree_interval,time,pressure=None,height=None):
        """ Compute all winds in a 2:1 rectangle thats fits in app window (dimensions = dims_on_canvas) """
        wind_grid = []
        lon_0,lat_0 = ceil(map_area[0]/degree_interval)*degree_interval,ceil(map_area[1]/degree_interval)*degree_interval
        lon = lon_0
        while lon < map_area[1]:
            lat = lat_0
            wind_grid.append([])
            while lat < map_area[3]:
                interpol_coord = {'time':time,'pressure':pressure,'height':height,'lon':lon,'lat':lat}
                local_wind = get_wind_at_coord(self.wind_data,interpol_coord,altitude_param=('height' if height is not None else 'pressure'))
                wind_grid[-1].append(local_wind)
        return wind_grid

    def get_wind_data_degree_interval(self):
        lon_interval = self.metadata['LON Interval']
        lat_interval = self.metadata['LAT Interval']
        degree_interval = [lon_interval,lat_interval]
        return degree_interval



