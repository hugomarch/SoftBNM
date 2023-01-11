import tkinter as tk

# APP WINDOW
APP_MIN_WIDTH = 1000
APP_MIN_HEIGHT = 700
MAX_RATIO_WIDTH_HEIGHT = 2

# MAP

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