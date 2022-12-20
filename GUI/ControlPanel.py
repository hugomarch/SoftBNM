import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
import os

from GUI.GeoInfoFrame import GeoInfoFrame
from GUI.GUI_config import APP_MIN_WIDTH, APP_MIN_HEIGHT

def button_hit():
    print("You've indeed hit me hard bastard !")

def return_pressed(event):
    print("Return")

def enter(event):
    print("Enter in the panel")

class ControlPanel(tk.Frame):
    def __init__(self,business_parent=None,GUI_parent=None):
        self.business_parent = business_parent
        self.GUI_parent = GUI_parent
        tk.Frame.__init__(self,self.GUI_parent,borderwidth=3)
        self.bullshit_header()
        self.logo = tk.Canvas(self)
        self.logo_img = None
        self.logo.pack(side=tk.TOP)
        self.geo_info = GeoInfoFrame(business_parent=self,GUI_parent=self)
        self.geo_info.pack(side=tk.TOP,fill=tk.BOTH)
        self.bind('<Configure>',self.on_resize)

    def receive_map_area_coords(self,area):
        self.geo_info.change_coords('Top-left',area[:2])
        self.geo_info.change_coords('Bottom-right',area[-2:])

    def receive_clicked_coords(self,clicked_coords):
        self.geo_info.change_coords('Clicked',clicked_coords)

    def on_resize(self,event):
        self.size_logo()
        
    def size_logo(self):
        panel_width = self.winfo_width()
        source_img = Image.open(os.path.join('GUI','logo.png'))
        logo_width, logo_height = panel_width, int(source_img.height/source_img.width * panel_width)
        self.logo_img = ImageTk.PhotoImage(source_img.resize((logo_width,logo_height)))
        self.logo['width'] = logo_width
        self.logo['height'] = logo_height
        self.logo.create_image(0,0,anchor=tk.NW,image=self.logo_img)

    def bullshit_header(self):
        title_label = ttk.Label(self)
        title_label['text'] = "Welcome in the GUI"
        title_label['background'] = '#f0a050'
        title_label['font'] = ('Calibri',14)
        title_label['takefocus'] = True
        title_label.bind('<Return>',return_pressed)
        title_label.pack(fill=tk.X, anchor=tk.CENTER)
        self.title_label = title_label

        button = ttk.Button(self)
        button['text'] = "Hit me hard"
        button['command'] = button_hit
        button.bind('<Return>',return_pressed)
        button.pack()
        self.button = button
