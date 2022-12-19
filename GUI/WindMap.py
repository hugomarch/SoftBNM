from MapCanvas import MapCanvas
import tkinter as tk

class WindMap:
    def __init__(self,business_parent=None,GUI_parent=None,image=None):
        self.business_parent = business_parent
        self.GUI_parent = GUI_parent
        self.map = MapCanvas(business_parent=self,GUI_parent=self.GUI_parent,image=image)
        # Coordinates of the maps corners, in longitude and latitute [lon_min,lat_min,lon_max,lat_max]
        self.map_area = None
        self.map.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)

    def receive_map_area_coords(self,map_area):
        self.map_area = map_area
        self.business_parent.receive_map_area_coords(map_area)

    def receive_clicked_coords(self,clicked_coords):
        self.business_parent.receive_clicked_coords(clicked_coords)
        
