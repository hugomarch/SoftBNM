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

    def __init__(self,parent,img_):
        """ use PIL img for init """
        tk.Canvas.__init__(self,parent)
        self['background'] = '#000'
        draw_greenwich_meridian(img_,self.LEFT_LONGITUDE)
        self.source_img = img_
        self.repeated_map = concatenate_two_images(img_,img_)
        self.img = None
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
        self.pack()

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
        return pixels * pix_to_degree

    def control_coordinates(self):
        """ ensure that coordinates do not cross limits """
        min_lat = min(90,90-(1-1/self.scale)*180)
        self.lon = (self.lon - self.LEFT_LONGITUDE) % 360 + self.LEFT_LONGITUDE
        self.lat = min(90,max(min_lat,self.lat))

    def move_map(self,event):
        x_pixel_offset = -(event.x-self.mouse_memory_x)
        y_pixel_offset = -(event.y-self.mouse_memory_y)
        lon_offset = self.convert_pixel_offset_in_degree(x_pixel_offset,axis='lon')
        lat_offset = self.convert_pixel_offset_in_degree(y_pixel_offset,axis='lat')
        min_lat = min(90,90-(1-1/self.scale)*180)
        self.lon += lon_offset
        self.lat += lat_offset
        self.control_coordinates()
        self.display_image(None)

    def zoom_map(self,event):
        if event and event.delta > 0 and self.zoom < self.NB_OF_SCALES-1:
            self.zoom += 1
        elif event and event.delta < 0 and self.zoom > 0:
            self.zoom -= 1
        previous_scale = self.scale
        self.scale = pow(self.SCALE_EXPONENT,self.zoom)
        # zoom with mouse pos as center
        zoom_center_lon = self.lon + self.convert_pixel_offset_in_degree(event.x,axis='lon')
        zoom_center_lat = self.lat + self.convert_pixel_offset_in_degree(event.y,axis='lat')
        self.lon = zoom_center_lon + (previous_scale/self.scale)*(self.lon - zoom_center_lon)
        self.lat = zoom_center_lat + (previous_scale/self.scale)*(self.lat - zoom_center_lat)
        self.control_coordinates()
        self.display_image(None)

    def display_image(self,event):
        source_width, source_height = self.source_img.size
        #dims of image displayed on canvas (indepently of zoom)
        on_canvas_width, on_canvas_height = int(self.winfo_height() / source_height * source_width), self.winfo_height()
        on_canvas_dims = (on_canvas_width,on_canvas_height)
        #dims of cropped zone of map
        lon_crop_limit = [self.lon,self.lon+360/self.scale]
        lat_crop_limit = [self.lat,self.lat-180/self.scale]
        x_crop_limit = [(x-self.LEFT_LONGITUDE) * source_width/360 for x in lon_crop_limit]
        y_crop_limit = [(90-y) * source_height/180 for y in lat_crop_limit]
        crop_area = (x_crop_limit[0],y_crop_limit[0],x_crop_limit[1],y_crop_limit[1])
        cropped_source = self.repeated_map.crop(crop_area)
        self.img = ImageTk.PhotoImage(cropped_source.resize(on_canvas_dims))
        self.delete('all')
        self.create_image(0,0,anchor=tk.NW,image=self.img)
