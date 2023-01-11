import tkinter as tk
import os
from math import sqrt, floor, ceil
from datetime import datetime

from GUI.MapCanvas import MapCanvas
from wind_engine.config import DECIMALS_OF_WIND_TABLE_KEYS
from GUI.GUI_config import NB_OF_DISPLAYED_WINDS_IN_MAP_AREA

class WindMap:
    def __init__(self,business_parent=None,GUI_parent=None,wind_engine=None):
        self.business_parent = business_parent
        self.GUI_parent = GUI_parent
        self.wind_engine = wind_engine
        self.map = MapCanvas(business_parent=self,GUI_parent=self.GUI_parent)
        self.map.pack(side=tk.LEFT,fill=tk.BOTH)
        # Map business info (should have ideally in fact been entirely processed here, no logic and display only in MapCanvas)
        self.restricted_map_area = None
        self.map_area = [0,-90,360,90] # coords can be > 360 here
        self.scale = 1
        self.time = datetime.strptime('2022-01-01 10:00:00','%Y-%m-%d %H:%M:%S')
        self.pressure = 500

        self.wind_table = None
        self.wind_table_lon_0 = None # Origin of the wind grid
        self.wind_table_lat_0 = None
        self.wind_table_deg_interval = None 
        self.wind_grid_limits = None # Expressed in integers corresponding to grid coordinates
        
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
        
    def get_new_wind_table(self):
        """ create a new wind table corresponding to a grid that fits map area and whose top-left corner is at coords 1/2,1/2 (*degree_interval) from the screen top-left
            Called at init or when the map is zoomed """
        self.wind_table_deg_interval = 360/self.scale/(NB_OF_DISPLAYED_WINDS_IN_MAP_AREA) #divide by N and not N-1 for margins (1/2 _ (N-1) _ 1/2)
        self.wind_table_lon_0 = self.map_area[0] + self.wind_table_deg_interval/2
        self.wind_table_lat_0 = self.map_area[1] + self.wind_table_deg_interval/2
        self.wind_table, self.wind_grid_limits = self.wind_engine.make_wind_table(self,self.map_area,lon_0,lat_0,self.wind_table_deg_interval,self.time,pressure=self.pressure,height=None)

    def update_wind_table(self):
        """ add and delete winds that are no more in map area because of map move """
        # Coords of the map area corners
        lon_1,lat_1,lon_2,lat_2 = self.map_area[0],self.map_area[1],self.map_area[2],self.map_area[3]
        lon_0,lat_0 = self.wind_table_lon_0,self.wind_table_lat_0
        interval = self.wind_table_deg_interval
        cur_limits = self.wind_grid_limits
        # Find points where winds need to be added or removed as grid coordinates
        new_limits = [ceil((lon_1-lon_0)/interval),ceil((lat_0-lat_1)/interval),floor((lon_2-lon_0)/interval),floor((lat_0-lat_2)/interval)]
        cur_cols, new_cols = set(list(range(cur_limits[0],cur_limits[2]))), set(list(range(new_limits[0],new_limits[2])))
        cols_to_add, cols_to_rm = new_cols.difference(cur_cols), cur_cols.difference(new_cols)
        cur_rows, new_rows = set(list(range(cur_limits[1],cur_limits[3]))), set(list(range(new_limits[1],new_limits[3])))
        rows_to_add, rows_to_rm = new_rows.difference(cur_rows), cur_rows.difference(new_rows)
        col_row_to_add = set(  [(col_to_add,j) for col_to_add in cols_to_add for j in range(new_limits[1],new_limits[3]+1)]
                             + [(i,row_to_add) for row_to_add in rows_to_add for i in range(new_limits[0],new_limits[2]+1)]  )
        col_row_to_rm = set(  [(col_to_rm,j) for col_to_rm in cols_to_rm for j in range(cur_limits[1],cur_limits[3]+1)]
                             + [(i,row_to_rm) for row_to_rm in rows_to_rm for i in range(cur_limits[0],cur_limits[2]+1)]  )
        for i,j in col_row_to_add:
            lon, lat = lon_0 + i*interval, lat_0 - j*interval
        
