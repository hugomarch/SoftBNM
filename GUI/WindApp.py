import tkinter as tk
from tkinter import ttk
from ctypes import windll
from PIL import Image, ImageTk

from WindMap import WindMap
from ControlPanel import ControlPanel

from config import APP_MIN_WIDTH, APP_MIN_HEIGHT, PANEL_WIDTH_FRAC, MAX_PANEL_WIDTH

class WindApp:
    def __init__(self):
        self.init_tkinter_root()
        map_background = Image.open('world-map.jpg')
        self.map = WindMap(business_parent=self,GUI_parent=self.root,image=map_background)
        self.panel = ControlPanel(business_parent=self,GUI_parent=self.root)
        # WindMap is not a widget, it packs its own canvas
        self.panel.pack(side=tk.RIGHT,fill=tk.BOTH)
        self.root.bind('<Configure>',self.on_resize)
        try:
            """ If blurry visual
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)"""
        finally:
            self.root.mainloop()

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

    def on_resize(self,event):
        app_width,app_height= self.root.winfo_width(),self.root.winfo_height()
        if app_width > 1.7 * app_height:
            app_width = int(1.7 * app_height)
            x,y = self.root.winfo_x(),self.root.winfo_y()
            self.root.geometry(f"{app_width}x{app_height}+{x}+{y}")
        panel_width = min(PANEL_WIDTH_FRAC * app_width, MAX_PANEL_WIDTH)
        self.panel['width'] = panel_width

    def receive_map_area_coords(self,map_area):
        self.panel.receive_map_area_coords(map_area)

    def receive_clicked_coords(self,clicked_coords):
        self.panel.receive_clicked_coords(clicked_coords)

