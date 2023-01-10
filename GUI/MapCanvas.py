import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
from math import pow

from GUI.GUI_config import CLICKED_POINT_CROSS_HEIGHT_PROP,CLICKED_POINT_CROSS_WIDTH,CLICKED_POINT_CROSS_COLOR
from GUI.GUI_config import SCALE_EXPONENT,LEFT_LONGITUDE,NB_OF_SCALES
from GUI.GUI_config import RESAMPLING_IMAGE_HEIGHT

def draw_greenwich_meridian(img, left_longitude):
    x_greenwich = int(img.width * (-left_longitude)/360)
    im_draw = ImageDraw.Draw(img)
    line_points = [(x_greenwich,0),(x_greenwich,img.height)]
    im_draw.line(line_points,fill='#f00',width=2)

def concatenate_two_images(im1,im2):
    """ concatenate horizontally 2 images of same height """
    concat = Image.new('RGB',(im1.width+im2.width,im1.height))
    concat.paste(im1,(0,0))
    concat.paste(im2,(im1.width,0))
    return concat

"""
IMPORTANT INFO TO UNDERSTAND THIS CLASS:
- It manages the movement of a virtual window over the world map, corresponding to what is currently displayed by the app.
  This virtual window actually moves on a "repeated map" consisting of a juxtaposition of two source world maps, so the user can travel on the map as on a torus.
- This virtual window can be thought as two nested windows. One has same shape than the source img of the world map, one has the shape of the app window.
  2nd must be included in the 1st. The 1st is the window of interest, because it is this window that is cut into the world map and displayed (so it overflows of app window)
  The initial size of the 1st window is the size of the source image, and is offseted to the Greenwhich meridian.
  The window position and size information only consists of the self.lon, self.lat data members for position, and self.scale for size, which is the ratio (full map size / app window size)
  Its size equivalent in term of pixels of the user screen is useful to display the image, and to convert the mouse movement from pixels to lon/lat degrees.
  This pixels equivalent can be obtained with method get_map_dims_on_canvas()
- The two variables map_area and restricted_map_area represent respectively 1st and 2nd window in lon/lat size. They are computed by method send_map_area_coords() to be sent to the business parent.
- The method convert_offset_pixel_degree() is used to convert an offset from pixel to degrees, or in the other way. Useful for map moving, window computations, and drawing of a content that is known by its lon/lat (ex: red cross)
- display_image() is called by the <Configure> event, move_map() and zoom_map()
- self.lon and self.lat are only change by the set_coordinates() -> control_coordinates() process. It is called by both move_map() and zoom_map()
- The possible map zooms is a discrete set (of size NB_OF_SCALES). To allow for better fluidity, we compute at map initialization an array of resampled repeated maps, one for each zoom level.
  The resampling factor decreases with zoom and is constant equal to 1 after a certain zoom limit. It's computed so that the height of the resulting image (with a given zoom) is a number of pixels close to RESAMPLING_IMAGE_HEIGHT
"""

class MapCanvas(tk.Canvas):
    def __init__(self,business_parent=None,GUI_parent=None,image=None):
        """ use PIL img for init """
        tk.Canvas.__init__(self,GUI_parent,borderwidth=3)
        self.business_parent = business_parent
        self['background'] = '#000'
        self.init_image_data(image)
        self.zoom = 0
        self.scale = pow(SCALE_EXPONENT,self.zoom)
        # Coordinated of top left corner of area cut in the full map (its size depend on zoom state).
        # Longitude origin is at world map left side, and latitude origin is at world top side (INVERSED)
        self.set_coordinates(0,0)
        # Remember state at last click for dragging
        self.mouse_memory_x = None
        self.mouse_memory_y = None
        self.lon_memory = None
        self.lat_memory = None
        self.clicked_lon = None
        self.clicked_lat = None
        # Display image for first time
        self.display_image(None)
        # Events
        self.bind('<MouseWheel>',self.zoom_map)
        self.bind('<Configure>',self.display_image)
        self.bind('<Configure>',self.send_map_area_coords,add='+')
        self.bind('<1>', self.remember_mouse_pos)
        self.bind('<2>', self.remove_clicked_point)
        self.bind('<B1-Motion>', self.move_map)
        self.bind('<3>', self.click_point)

    def init_image_data(self,image):
        draw_greenwich_meridian(image,LEFT_LONGITUDE)
        self.source_img = image
        #self.repeated_map = concatenate_two_images(image,image)
        self.cur_img = None
        # Compute an array of resampled repeated maps in increasing scale order, ending when reaches full scale
        self.resampled_repeated_maps = []
        source_width, source_height = self.source_img.size
        for zoom in range(NB_OF_SCALES):
            scale = pow(SCALE_EXPONENT,zoom)
            target_width, target_height = int(source_width/source_height*RESAMPLING_IMAGE_HEIGHT*scale),int(RESAMPLING_IMAGE_HEIGHT*scale)
            resampled_map = self.source_img.resize((min(source_width,target_width),min(source_height,target_height)))
            self.resampled_repeated_maps.append(concatenate_two_images(resampled_map,resampled_map))
            if target_width > source_width or target_height > source_height:
                break
        print(f"Number of resampled maps: {len(self.resampled_repeated_maps)}")

    def send_map_area_coords(self,event):
        map_area = [self.lon,self.lat,self.lon+360/self.scale,self.lat-180/self.scale]
        restricted_map_area_lon_width = self.convert_offset_pixel_degree(self.winfo_width(),data_source='pixel',axis='lon')
        restricted_map_area = [self.lon,self.lat,(self.lon+restricted_map_area_lon_width)%360,self.lat-180/self.scale]
        self.business_parent.receive_map_area_coords(map_area,restricted_map_area)

    def set_coordinates(self,lon,lat):
        lon,lat = self.control_coordinates(lon,lat)
        self.lon = lon
        self.lat = lat
        self.send_map_area_coords(None)

    def control_coordinates(self,lon,lat):
        """ ensure that coordinates do not cross limits """
        min_lat = min(90,90-(1-1/self.scale)*180)
        lon = lon % 360
        lat = min(90,max(min_lat,lat))
        return lon,lat

    def click_point(self,event):
        # Identify clicked point
        self.clicked_lon = (self.lon + self.convert_offset_pixel_degree(event.x,data_source='pixel',axis='lon'))%360
        self.clicked_lat = self.lat + self.convert_offset_pixel_degree(event.y,data_source='pixel',axis='lat')
        # Send coords
        self.business_parent.receive_clicked_coords([self.clicked_lon,self.clicked_lat])
        self.display_image(None)

    def remove_clicked_point(self,event):
        self.business_parent.remove_clicked_point()
        self.clicked_lon = None
        self.clicked_lat = None
        self.display_image(None)

    def remember_mouse_pos(self,event):
        self.mouse_memory_x = event.x
        self.mouse_memory_y = event.y
        self.lon_memory = self.lon
        self.lat_memory = self.lat

    def get_map_dims_on_canvas(self):
        source_width, source_height = self.source_img.size
        return int(self.winfo_height() / source_height * source_width), self.winfo_height()

    def convert_offset_pixel_degree(self,offset,data_source='pixel',axis='lon'):
        total_degrees = 360/self.scale if axis=='lon' else 180/self.scale
        dims_on_canvas = self.get_map_dims_on_canvas()
        total_pixels = dims_on_canvas[0] if axis == 'lon' else dims_on_canvas[1]
        conv_ratio = total_degrees/total_pixels * (1 if axis == 'lon' else -1)
        if data_source == 'degree':
            conv_ratio = 1/conv_ratio
        """ DEBUG
        if axis == 'lon':
            print(f"Pixels: {pixels}; Prop: {dims_on_canvas[0]}; Degrees: {pixels * pix_to_degree}")"""
        return offset*conv_ratio

    def move_map(self,event):
        # Compute offset
        x_pixel_offset = event.x - self.mouse_memory_x
        y_pixel_offset = event.y - self.mouse_memory_y
        lon_offset = self.convert_offset_pixel_degree(x_pixel_offset,data_source='pixel',axis='lon')
        lat_offset = self.convert_offset_pixel_degree(y_pixel_offset,data_source='pixel',axis='lat')
        # Set new coordinates
        new_lon = self.lon_memory - lon_offset
        new_lat = self.lat_memory - lat_offset
        self.set_coordinates(new_lon,new_lat)
        # Display
        self.display_image(None)

    def zoom_map(self,event):
        # Identify zoom center
        zoom_center_lon = self.lon + self.convert_offset_pixel_degree(event.x,data_source='pixel',axis='lon')
        zoom_center_lat = self.lat + self.convert_offset_pixel_degree(event.y,data_source='pixel',axis='lat')
        # Change scale
        if event and event.delta > 0 and self.zoom < NB_OF_SCALES-1:
            self.zoom += 1
        elif event and event.delta < 0 and self.zoom > 0:
            self.zoom -= 1
        previous_scale = self.scale
        self.scale = pow(SCALE_EXPONENT,self.zoom)
        # Set new coordinates
        new_lon = zoom_center_lon + (previous_scale/self.scale)*(self.lon - zoom_center_lon)
        new_lat = zoom_center_lat + (previous_scale/self.scale)*(self.lat - zoom_center_lat)
        self.set_coordinates(new_lon,new_lat)
        self.display_image(None)

    def draw_clicked_point_cross(self):
        dims_on_canvas = self.get_map_dims_on_canvas()
        x = self.convert_offset_pixel_degree((self.clicked_lon-self.lon)%360,data_source='degree',axis='lon')
        y = self.convert_offset_pixel_degree(self.clicked_lat-self.lat,data_source='degree',axis='lat')
        if x<dims_on_canvas[0] and y>=0 and y<dims_on_canvas[1]:
            cross_size = int(dims_on_canvas[1]*CLICKED_POINT_CROSS_HEIGHT_PROP//2)
            self.create_line(x-cross_size,y-cross_size,x+cross_size,y+cross_size,fill=CLICKED_POINT_CROSS_COLOR,width=CLICKED_POINT_CROSS_WIDTH)
            self.create_line(x-cross_size,y+cross_size,x+cross_size,y-cross_size,fill=CLICKED_POINT_CROSS_COLOR,width=CLICKED_POINT_CROSS_WIDTH)

    def display_image(self,event):
        dims_on_canvas = self.get_map_dims_on_canvas()
        # Choose the resampled repeated map corresponding to scale
        repeated_map = self.resampled_repeated_maps[min(self.zoom,len(self.resampled_repeated_maps)-1)]
        source_width, source_height = repeated_map.width//2, repeated_map.height
        # lon-lat coordinates of cropped zone of map
        lon_crop_limit = [self.lon,self.lon+360/self.scale]
        lat_crop_limit = [self.lat,self.lat-180/self.scale]
        # crop area on repeated map
        lon_crop_limit_reworked = [(lon_crop_limit[0]-LEFT_LONGITUDE)%360, (lon_crop_limit[0]-LEFT_LONGITUDE)%360+lon_crop_limit[1]-lon_crop_limit[0]]
        x_crop_limit = [x*source_width/360 for x in lon_crop_limit_reworked]
        y_crop_limit = [(90-y) * source_height/180 for y in lat_crop_limit]
        crop_area = (x_crop_limit[0],y_crop_limit[0],x_crop_limit[1],y_crop_limit[1])
        cropped_source = repeated_map.crop(crop_area)
        self.cur_img = ImageTk.PhotoImage(cropped_source.resize(dims_on_canvas))
        self.delete('all')
        self.create_image(0,0,anchor=tk.NW,image=self.cur_img)
        if self.clicked_lon is not None:
            self.draw_clicked_point_cross()
