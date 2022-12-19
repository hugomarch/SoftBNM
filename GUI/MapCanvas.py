import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
from math import pow

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

class MapCanvas(tk.Canvas):
    SCALE_EXPONENT = 1.3
    NB_OF_SCALES = 10
    LEFT_LONGITUDE = -180 # longitude of map left side

    def __init__(self,business_parent=None,GUI_parent=None,image=None):
        """ use PIL img for init """
        tk.Canvas.__init__(self,GUI_parent)
        self.business_parent = business_parent
        self['background'] = '#000'
        draw_greenwich_meridian(image,self.LEFT_LONGITUDE)
        self.source_img = image
        self.repeated_map = concatenate_two_images(image,image)
        self.cur_img = None
        self.zoom = 0
        self.scale = pow(self.SCALE_EXPONENT,self.zoom)
        # Coordinated of top left corner of area cut in the full map (its size depend on zoom state).
        # Longitude origin is at world map left side, and latitude origin is at world top side (INVERSED)
        self.lon = 0
        self.lat = 90
        # Remember state at last click for dragging
        self.mouse_memory_x = None
        self.mouse_memory_y = None
        self.lon_memory = None
        self.lat_memory = None
        # Display image for first time
        self.display_image(None)
        # Events
        self.bind('<MouseWheel>',self.zoom_map)
        self.bind('<Configure>',self.display_image)
        self.bind('<1>', self.remember_mouse_pos)
        self.bind('<B1-Motion>', self.move_map)
        self.bind('<3>', self.on_right_click)

    def set_coordinates(self,lon,lat):
        lon,lat = self.control_coordinates(lon,lat)
        self.lon = lon
        self.lat = lat
        map_area_lon_width = self.convert_pixel_offset_in_degree(self.winfo_width(),axis='lon')
        map_area = [self.lon,self.lat,(self.lon+map_area_lon_width)%360,self.lat-180/self.scale]
        self.business_parent.receive_map_area_coords(map_area)

    def control_coordinates(self,lon,lat):
        """ ensure that coordinates do not cross limits """
        min_lat = min(90,90-(1-1/self.scale)*180)
        lon = (lon - self.LEFT_LONGITUDE) % 360 + self.LEFT_LONGITUDE
        lat = min(90,max(min_lat,lat))
        return lon,lat

    def on_right_click(self,event):
        # Identify clicked point
        clicked_lon = self.lon + self.convert_pixel_offset_in_degree(event.x,axis='lon')
        clicked_lat = self.lat + self.convert_pixel_offset_in_degree(event.y,axis='lat')
        # Send coords
        self.business_parent.receive_clicked_coords([clicked_lon,clicked_lat])

    def remember_mouse_pos(self,event):
        self.mouse_memory_x = event.x
        self.mouse_memory_y = event.y
        self.lon_memory = self.lon
        self.lat_memory = self.lat

    def get_map_dims_on_canvas(self):
        source_width, source_height = self.source_img.size
        return int(self.winfo_height() / source_height * source_width), self.winfo_height()

    def convert_pixel_offset_in_degree(self,pixels,axis='lon'):
        total_degrees = 360 if axis=='lon' else 180
        dims_on_canvas = self.get_map_dims_on_canvas()
        total_pixels = dims_on_canvas[0] if axis == 'lon' else dims_on_canvas[1]
        pix_to_degree = (total_degrees/self.scale)/total_pixels * (1 if axis == 'lon' else -1)
        """ DEBUG
        if axis == 'lon':
            print(f"Pixels: {pixels}; Prop: {dims_on_canvas[0]}; Degrees: {pixels * pix_to_degree}")"""
        return pixels * pix_to_degree

    def move_map(self,event):
        # Compute offset
        x_pixel_offset = event.x - self.mouse_memory_x
        y_pixel_offset = event.y - self.mouse_memory_y
        lon_offset = self.convert_pixel_offset_in_degree(x_pixel_offset,axis='lon')
        lat_offset = self.convert_pixel_offset_in_degree(y_pixel_offset,axis='lat')
        # Set new coordinates
        new_lon = self.lon_memory - lon_offset
        new_lat = self.lat_memory - lat_offset
        self.set_coordinates(new_lon,new_lat)
        # Display
        self.display_image(None)

    def zoom_map(self,event):
        # Identify zoom center
        zoom_center_lon = self.lon + self.convert_pixel_offset_in_degree(event.x,axis='lon')
        zoom_center_lat = self.lat + self.convert_pixel_offset_in_degree(event.y,axis='lat')
        # Change scale
        if event and event.delta > 0 and self.zoom < self.NB_OF_SCALES-1:
            self.zoom += 1
        elif event and event.delta < 0 and self.zoom > 0:
            self.zoom -= 1
        previous_scale = self.scale
        self.scale = pow(self.SCALE_EXPONENT,self.zoom)
        # Set new coordinates
        new_lon = zoom_center_lon + (previous_scale/self.scale)*(self.lon - zoom_center_lon)
        new_lat = zoom_center_lat + (previous_scale/self.scale)*(self.lat - zoom_center_lat)
        self.set_coordinates(new_lon,new_lat)
        self.display_image(None)

    def display_image(self,event):
        dims_on_canvas = self.get_map_dims_on_canvas()
        source_width, source_height = self.source_img.width, self.source_img.height
        # lon-lat coordinates of cropped zone of map
        lon_crop_limit = [self.lon,self.lon+360/self.scale]
        lat_crop_limit = [self.lat,self.lat-180/self.scale]
        # crop area on repeated map
        x_crop_limit = [(x-self.LEFT_LONGITUDE) * source_width/360 for x in lon_crop_limit]
        y_crop_limit = [(90-y) * source_height/180 for y in lat_crop_limit]
        crop_area = (x_crop_limit[0],y_crop_limit[0],x_crop_limit[1],y_crop_limit[1])
        cropped_source = self.repeated_map.crop(crop_area)
        self.cur_img = ImageTk.PhotoImage(cropped_source.resize(dims_on_canvas))
        self.delete('all')
        self.create_image(0,0,anchor=tk.NW,image=self.cur_img)
