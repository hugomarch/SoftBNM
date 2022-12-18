import tkinter as tk
from tkinter import ttk
from ctypes import windll
from PIL import Image, ImageTk

from MapCanvas import MapCanvas

def button_hit():
    print("You've indeed hit me hard bastard !")

def return_pressed(event):
    print("Return")

def enter(event):
    print("Enter")

def scale_image_on_mouse_wheel(canvas,img,event):
    "canvas widget and PIL image. mouse wheel event"
    print(f"Wheel event : {event.delta}")
    canvas.delete('all')

root = tk.Tk()
root.title("Test de TKinter")

window_min_width = 1000
window_min_height = 700
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width - window_min_width)/2)
center_y = int((screen_height - window_min_height)/2)

root.geometry(f"{window_min_width}x{window_min_height}+{center_x}+{center_y}")
root.resizable(True,True)
root.minsize(window_min_width,window_min_height)

# MAP

img_pil = Image.open('world-map.jpg')
map = MapCanvas(root,img_pil)
map.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)


# PANEL

panel = tk.Frame(root)
panel.pack(side=tk.RIGHT,fill=tk.BOTH)

title_label = ttk.Label(panel)
title_label['text'] = "Welcome in the GUI"
title_label['background'] = '#f0a050'
title_label['font'] = ('Calibri',14)
title_label['takefocus'] = True
title_label.bind('<Enter>',enter)
title_label.bind('<Return>',return_pressed)
title_label.pack(fill=tk.X, anchor=tk.CENTER)

button = ttk.Button(panel)
button['text'] = "Hit me hard"
button['command'] = button_hit
button.bind('<Return>',return_pressed)
button.pack()

canvas1 = tk.Canvas(panel)
canvas1['background'] = '#000'
cv1_width, cv1_height = int(window_min_width/5), int(window_min_height/5)
canvas1['width'] = cv1_width
canvas1['height'] = cv1_height
canvas1.pack()

canvas1.create_line(0,0,int(cv1_width/2),int(cv1_height/3),cv1_width,cv1_height,fill='#ff0',width=10)

try:
    """
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)"""
finally:
    root.mainloop()
