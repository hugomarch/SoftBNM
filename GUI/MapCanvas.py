import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
from math import pow

import GUI.MapCanvas_config as MapCanvas_config
from GUI.MapCanvas_config import CLICKED_POINT_CROSS_HEIGHT_PROP,CLICKED_POINT_CROSS_WIDTH,CLICKED_POINT_CROSS_COLOR
from GUI.MapCanvas_config import SCALE_EXPONENT,NB_OF_SCALES,RESAMPLING_IMAGE_HEIGHT


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

def draw_meridian(image, image_left_lon, image_lon_size, meridian_lon):
    x_line = int(image.width * (meridian_lon-image_left_lon)/image_lon_size)
    im_draw = ImageDraw.Draw(image)
    line_points = [(x_line,0),(x_line,image.height)]
    im_draw.line(line_points,fill='#f00',width=2)

def concatenate_two_images(im1,im2):
    """ concatenate horizontally 2 images of same height """
    concat = Image.new('RGB',(im1.width+im2.width,im1.height))
    concat.paste(im1,(0,0))
    concat.paste(im2,(im1.width,0))
    return concat

def make_raw_image(map_def):
    image = Image.open(map_def['image_file'])
    image_left_lon = map_def['image_top_left_coords'][0]
    image_lon_size = map_def['image_lon_lat_size'][0]
    for meridian_lon in map_def['draw_meridian']:
        draw_meridian(image,image_left_lon,image_lon_size,meridian_lon)
    return image

def resample_image(raw_img):
    """ Compute an array of resampled repeated maps in increasing scale order, ending when reaches full scale """
    resampled_repeated_maps = []
    source_width, source_height = raw_img.size
    for zoom in range(NB_OF_SCALES):
        scale = pow(SCALE_EXPONENT,zoom)
        target_width, target_height = int(source_width/source_height*RESAMPLING_IMAGE_HEIGHT*scale),int(RESAMPLING_IMAGE_HEIGHT*scale)
        resampled_map = raw_img.resize((min(source_width,target_width),min(source_height,target_height)))
        resampled_repeated_maps.append(concatenate_two_images(resampled_map,resampled_map))
        if target_width > source_width or target_height > source_height:
            break
    print(f"Number of resampled maps: {len(resampled_repeated_maps)}")
    return resampled_repeated_maps

def compute_resampled_repeated_maps(map_name):
    map_def = MapCanvas_config.map_config[map_name]
    raw_img = make_raw_image(map_def)
    resampled_repeated_maps = resample_image(raw_img)
    return resampled_repeated_maps

class MapCanvas(tk.Canvas):
    def __init__(self,business_parent=None,GUI_parent=None):
        tk.Canvas.__init__(self,GUI_parent,borderwidth=3)
        self['background'] = '#000'
        self.business_parent = business_parent
        self.cur_map = 'World'
        self.focus_set()
        self.init_state()
        self.init_image()
        # Events
        self.bind('<MouseWheel>',self.zoom_map)
        self.bind('<Configure>',self.display_image)
        self.bind('<Configure>',self.send_map_area_coords,add='+')
        self.bind('<1>', self.remember_mouse_pos)
        self.bind('<2>', self.remove_clicked_point)
        self.bind('<B1-Motion>', self.move_map)
        self.bind('<3>', self.click_point)
        self.bind('<KeyPress-w>', self.change_map)
        self.bind('<KeyPress-f>', self.change_map)

    def init_state(self):
        # zoom state
        self.zoom = 0
        self.scale = pow(SCALE_EXPONENT,self.zoom)
        # Remember state at last click for dragging
        self.mouse_memory_x = None
        self.mouse_memory_y = None
        self.lon_memory = None
        self.lat_memory = None
        # Clicked point
        self.clicked_lon = None
        self.clicked_lat = None

    def init_image(self):
        # resampled repeated maps arrays
        self.resampled_repeated_maps = compute_resampled_repeated_maps(self.cur_map)
        self.cur_img = None # ad hoc variable to store currently displayed image
        self.image_top_left_coords = MapCanvas_config.map_config[self.cur_map]['image_top_left_coords']
        self.image_lon_lat_size = MapCanvas_config.map_config[self.cur_map]['image_lon_lat_size']
        self.is_planisphere = MapCanvas_config.map_config[self.cur_map]['is_planisphere']
        self.set_coordinates(self.image_top_left_coords[0],self.image_top_left_coords[1])
        self.display_image(None)

    def change_map(self,event):
        new_map = None
        if event.keysym == 'w':
            new_map = 'World'
        elif event.keysym == 'f':
            new_map = 'France'
        if new_map != self.cur_map:
            self.cur_map = new_map
            self.init_image()
            self.init_state()

    def send_map_area_coords(self,event):
        lon_size, lat_size = tuple(self.image_lon_lat_size)
        map_area = [self.lon,self.lat,self.lon+lon_size/self.scale,self.lat-lat_size/self.scale]
        restricted_map_area_lon_width = self.convert_offset_pixel_degree(self.winfo_width(),data_source='pixel',axis='lon')
        restricted_map_area = [self.lon,self.lat,(self.lon+restricted_map_area_lon_width)%360,self.lat-lat_size/self.scale]
        self.business_parent.receive_map_area_coords(map_area,restricted_map_area)

    def set_coordinates(self,lon,lat):
        lon,lat = self.control_coordinates(lon,lat)
        self.lon = lon
        self.lat = lat
        self.send_map_area_coords(None)

    def control_coordinates(self,lon,lat):
        """ ensure that coordinates do not cross limits """
        lon_size, lat_size = tuple(self.image_lon_lat_size)
        # control longitude
        if self.is_planisphere:
            lon = lon % 360
        else:
            left_lon = self.image_top_left_coords[0]
            max_lon_offset = (1-1/self.scale)*lat_size
            # convert longitude in relative to left
            rel_lon = (lon-left_lon)%360 
            if rel_lon > max_lon_offset:
                if 360-rel_lon > rel_lon-max_lon_offset:
                    rel_lon = max_lon_offset
                else:
                    rel_lon = 0
            # back to normal lon
            lon = (rel_lon+left_lon)%360
        # control latitude
        max_lat = self.image_top_left_coords[1]
        min_lat = min(max_lat,max_lat-(1-1/self.scale)*lat_size)
        lat = min(max_lat,max(min_lat,lat))
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
        repeated_map_width, repeated_map_height = self.resampled_repeated_maps[0].size
        source_image_ratio = repeated_map_width/2/repeated_map_height
        return int(self.winfo_height()*source_image_ratio), self.winfo_height()

    def convert_offset_pixel_degree(self,offset,data_source='pixel',axis='lon'):
        lon_size, lat_size = tuple(self.image_lon_lat_size)
        total_degrees = lon_size/self.scale if axis=='lon' else lat_size/self.scale
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
        lon_size, lat_size = tuple(self.image_lon_lat_size)
        max_lat = self.image_top_left_coords[1]
        # lon-lat coordinates of cropped zone of map
        lon_crop_limit = [self.lon,self.lon+lon_size/self.scale]
        left_lon = MapCanvas_config.map_config[self.cur_map]['image_top_left_coords'][0]
        rel_lon_crop_limit = [(lon_crop_limit[0]-left_lon)%360, (lon_crop_limit[0]-left_lon)%360+lon_crop_limit[1]-lon_crop_limit[0]]
        if not self.is_planisphere:
            rel_lon_crop_limit[-1] = min(rel_lon_crop_limit[-1],lon_size)
        lat_crop_limit = [self.lat,self.lat-lat_size/self.scale]
        # crop area on repeated map
        x_crop_limit = [x*source_width/lon_size for x in rel_lon_crop_limit]
        y_crop_limit = [(max_lat-y) * source_height/lat_size for y in lat_crop_limit]
        crop_area = (x_crop_limit[0],y_crop_limit[0],x_crop_limit[1],y_crop_limit[1])
        cropped_source = repeated_map.crop(crop_area)
        self.cur_img = ImageTk.PhotoImage(cropped_source.resize(dims_on_canvas))
        self.delete('all')
        self.create_image(0,0,anchor=tk.NW,image=self.cur_img)
        if self.clicked_lon is not None:
            self.draw_clicked_point_cross()
