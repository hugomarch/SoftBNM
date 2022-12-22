import tkinter as tk
import os
from math import sqrt
from datetime import datetime

from GUI.MapCanvas import MapCanvas

class WindMap:
    def __init__(self,business_parent=None,GUI_parent=None,wind_engine=None,image=None):
        self.business_parent = business_parent
        self.GUI_parent = GUI_parent
        self.wind_engine = wind_engine
        self.map = MapCanvas(business_parent=self,GUI_parent=self.GUI_parent,image=image)
        self.map.pack(side=tk.LEFT,fill=tk.BOTH)
        # Map business info (should have ideally in fact been entirely processed here, no logic and display only in MapCanvas)
        self.restricted_map_area = None
        self.map_area = [0,-90,360,90]
        self.scale = 1
        self.time = datetime.strptime('2022-01-01 10:00:00','%Y-%m-%d %H:%M:%S')
        self.pressure = 500
        self.wind_grid = None
        self.wind_grid_limits = None
        
    def resize_width(self,width):
        self.map['width'] = width

    def receive_map_area_coords(self,map_area,restricted_map_area):
        self.map_area = map_area
        self.restricted_map_area = restricted_map_area
        self.business_parent.receive_restricted_map_area_coords(restricted_map_area)

    def receive_clicked_coords(self,clicked_coords):
        self.business_parent.receive_clicked_coords(clicked_coords)

    def remove_clicked_point(self):
        self.business_parent.remove_clicked_point()

    def compute_degree_grid_interval(self):
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

    def update_grid_limits(self):
        return

    def get_wind_grid(self):
        self.degree_interval = self.compute_degree_grid_interval(scale)
        wind_grid = self.wind_engine.make_wind_grid(self.map_area,self.degree_interval,self.time,pressure=self.pressure)
        return wind_grid

    


        

        
        
