import tkinter as tk
import os
from math import sqrt

from GUI.MapCanvas import MapCanvas

class WindMap:
    def __init__(self,business_parent=None,GUI_parent=None,wind_engine=None,image=None):
        self.business_parent = business_parent
        self.GUI_parent = GUI_parent
        self.wind_engine = wind_engine
        self.map = MapCanvas(business_parent=self,GUI_parent=self.GUI_parent,image=image)
        # Coordinates of the maps corners, in longitude and latitute [lon_min,lat_min,lon_max,lat_max]
        self.restricted_map_area = None
        self.map.pack(side=tk.LEFT,fill=tk.BOTH)
        self.wind_data = None

    def resize_width(self,width):
        self.map['width'] = width

    def receive_restricted_map_area_coords(self,restricted_map_area):
        self.restricted_map_area = restricted_map_area
        self.business_parent.receive_restricted_map_area_coords(restricted_map_area)

    def receive_clicked_coords(self,clicked_coords):
        self.business_parent.receive_clicked_coords(clicked_coords)

    def remove_clicked_point(self):
        self.business_parent.remove_clicked_point()

    def compute_degree_grid_interval(self,scale):
        data_interval = self.wind_engine.get_wind_data_degree_interval()[1]
        grid_size = 180/data_interval
        best_ratio_err = float('inf')
        best_interval = None
        for i in range(int(sqrt(grid_size))):
            if grid_size % i == 0:
                div1,div2 = i,grid_size//i
                for div in [d1,d2]:
                    if (ratio_err:=abs(360/scale/div/data_interval - 1)) < best_ratio_err:
                        best_ratio_err = ratio_err
                        best_interval = div*data_interval
        return best_interval

    def get_wind_grid(self,scale,map_area,time,pressure):
        degree_interval = self.compute_degree_grid_interval(scale)
        wind_grid = self.wind_engine.make_wind_grid(map_area,degree_interval,time,pressure)
        return wind_grid

    


        

        
        
