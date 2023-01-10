import tkinter as tk

# APP WINDOW
APP_MIN_WIDTH = 1000
APP_MIN_HEIGHT = 700
MAX_RATIO_WIDTH_HEIGHT = 2

# MAP
SCALE_EXPONENT = 1.3
LEFT_LONGITUDE = -180
NB_OF_SCALES = 10

CLICKED_POINT_CROSS_HEIGHT_PROP = 0.02 # proportion of window height
CLICKED_POINT_CROSS_WIDTH = 3 # proportion of window height
CLICKED_POINT_CROSS_COLOR = "#f00" # proportion of window height

TARGET_NUMBER_OF_WIND_ARROWS_IN_LON = 30

# CONTROL PANEL
PANEL_WIDTH_FRAC = 0.2
MAX_PANEL_WIDTH = 300

# GEO INFO
NAME_FRAC = 0.4

def get_zoomed_geometry():
    """ """
    root = tk.Tk()
    root.state('zoomed')
    root.update_idletasks()
    geometry = root.winfo_geometry()
    root.destroy()
    """
    root.update_idletasks()
    root.attributes('-zoomed', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    root.update_idletasks()
    root.destroy()"""
    return geometry