import tkinter as tk
from tkinter import ttk

from GeoInfoFrame import GeoInfoFrame
from config import APP_MIN_WIDTH, APP_MIN_HEIGHT

def button_hit():
    print("You've indeed hit me hard bastard !")

def return_pressed(event):
    print("Return")

def enter(event):
    print("Enter")

class ControlPanel(tk.Frame):
    def __init__(self,business_parent=None,GUI_parent=None):
        self.business_parent = business_parent
        self.GUI_parent = GUI_parent
        tk.Frame.__init__(self,self.GUI_parent)
        self.bullshit_fill()
        self.geo_info = GeoInfoFrame(business_parent=self,GUI_parent=self)
        self.geo_info.pack(side=tk.TOP,fill=tk.BOTH)

    def receive_map_area_coords(self,area):
        self.geo_info.change_coords('Top-left',area[:2])
        self.geo_info.change_coords('Bottom-right',area[-2:])

    def receive_clicked_coords(self,clicked_coords):
        self.geo_info.change_coords('Clicked',clicked_coords)

    def bullshit_fill(self):
        title_label = ttk.Label(self)
        title_label['text'] = "Welcome in the GUI"
        title_label['background'] = '#f0a050'
        title_label['font'] = ('Calibri',14)
        title_label['takefocus'] = True
        title_label.bind('<Enter>',enter)
        title_label.bind('<Return>',return_pressed)
        title_label.pack(fill=tk.X, anchor=tk.CENTER)
        self.title_label = title_label

        button = ttk.Button(self)
        button['text'] = "Hit me hard"
        button['command'] = button_hit
        button.bind('<Return>',return_pressed)
        button.pack()
        self.button = button

        canvas1 = tk.Canvas(self)
        canvas1['background'] = '#000'
        cv1_width, cv1_height = int(APP_MIN_WIDTH/5), int(APP_MIN_HEIGHT/5)
        canvas1['width'] = cv1_width
        canvas1['height'] = cv1_height
        canvas1.pack()
        self.canvas1 = canvas1

        canvas1.create_line(0,0,int(cv1_width/2),int(cv1_height/3),cv1_width,cv1_height,fill='#ff0',width=10)
