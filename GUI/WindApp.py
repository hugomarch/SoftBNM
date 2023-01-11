import tkinter as tk
from tkinter import ttk
from ctypes import windll
import os

from wind_engine.WindEngine import WindEngine
from GUI.WindMap import WindMap
from GUI.ControlPanel import ControlPanel
from GUI.GUI_config import APP_MIN_WIDTH, APP_MIN_HEIGHT, PANEL_WIDTH_FRAC, MAX_PANEL_WIDTH, MAX_RATIO_WIDTH_HEIGHT, get_zoomed_geometry

class WindApp:
    def __init__(self):
        self.init_tkinter_root()
        self.panel = ControlPanel(business_parent=self,GUI_parent=self.root)
        self.wind_engine = WindEngine()
        self.map = WindMap(business_parent=self,GUI_parent=self.root,wind_engine=self.wind_engine)
        # WindMap is not a widget, it packs its own canvas
        self.panel.pack(side=tk.RIGHT,fill=tk.BOTH)
        self.root.bind('<Configure>',self.on_resize)
        #self.root.bind('<KeyPress-i>',self.echo_app_info)
        try:
            """ If blurry visual
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)"""
        finally:
            self.root.mainloop()

    def echo_app_info(self,event):
        print(f"{self.map.map.winfo_width()} + {self.panel.winfo_width()} = {self.map.map.winfo_width()+self.panel.winfo_width()}")
        print(f"root width: {self.root.winfo_width()}")
        print(f"Full screen: {self.root.wm_state()=='zoomed'}")
        print('\n')

    def init_tkinter_root(self):
        self.root = tk.Tk()
        self.root.title("Wind App")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - APP_MIN_WIDTH)/2)
        center_y = int((screen_height - APP_MIN_HEIGHT)/2)
        self.root.geometry(f"{APP_MIN_WIDTH}x{APP_MIN_HEIGHT}+{center_x}+{center_y}")
        self.root.resizable(True,True)
        self.root.minsize(APP_MIN_WIDTH,APP_MIN_HEIGHT)
        self.root.maxsize(MAX_RATIO_WIDTH_HEIGHT*screen_height,screen_height)

    def on_resize(self,event):
        app_width,app_height= self.root.winfo_width(),self.root.winfo_height()
        full_screen = (self.root.wm_state()=='zoomed')
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        full_screen = (self.root.wm_state()=='zoomed')
        if not full_screen and app_width > MAX_RATIO_WIDTH_HEIGHT* app_height:
            app_width = int(MAX_RATIO_WIDTH_HEIGHT * app_height)
            x,y = self.root.winfo_x(),self.root.winfo_y()
            self.root.geometry(f"{app_width}x{app_height}+{x}+{y}")
        panel_width = min(PANEL_WIDTH_FRAC * app_width, MAX_PANEL_WIDTH)
        map_width = app_width - panel_width
        self.panel.resize_width(panel_width)
        self.map.resize_width(map_width)

    def receive_restricted_map_area_coords(self,restricted_map_area):
        self.panel.receive_restricted_map_area_coords(restricted_map_area)

    def receive_clicked_coords(self,clicked_coords):
        self.panel.receive_clicked_coords(clicked_coords)

    def remove_clicked_point(self):
        self.panel.remove_clicked_point()

