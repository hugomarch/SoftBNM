import tkinter as tk

# APP WINDOW
APP_MIN_WIDTH = 1000
APP_MIN_HEIGHT = 700
MAX_RATIO_WIDTH_HEIGHT = 2

# MAP
LEFT_LONGITUDE = -180

SCALE_EXPONENT = 1.3
NB_OF_SCALES = 10
RESAMPLING_IMAGE_HEIGHT = 1000

CLICKED_POINT_CROSS_HEIGHT_PROP = 0.02 # proportion of window height
CLICKED_POINT_CROSS_WIDTH = 3 # proportion of window height
CLICKED_POINT_CROSS_COLOR = "#f00" # proportion of window height

NB_OF_DISPLAYED_WINDS_IN_MAP_AREA = 30

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