from MapCanvas import MapCanvas

class WindMapCanvas:
    def __init__(self,GUI_parent,img_):
        self.map = MapCanvas(self,img_)
        # Coordinates of the maps corners, in longitude and latitute [lon_min,lat_min,lon_max,lat_max]
        self.area = None
        
