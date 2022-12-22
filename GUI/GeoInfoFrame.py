import tkinter as tk
from tkinter import ttk

from GUI.GUI_config import NAME_FRAC

class GeoInfoFrame(tk.Frame):
    def __init__(self,GUI_parent=None,business_parent=None):
        self.GUI_parent = GUI_parent
        tk.Frame.__init__(self,self.GUI_parent,background='#999')
        self.coords = {'Top-left': [None,None],'Bottom-right': [None,None],'Clicked':[None,None]}
        self.labels = {'Top-left': None,'Bottom-right': None,'Clicked': None}
        self.make_labels()
        self.bind('<Configure>',self.on_resize)

    def make_labels(self):
        self.columnconfigure(1,weight=4)
        self.columnconfigure(2,weight=3)
        self.columnconfigure(3,weight=3)
        for i,name in enumerate(self.labels.keys()):
            self.labels[name] = []
            for j in range(3):
                label = ttk.Label(self,text=(name if j==0 else "---"),background='#999')
                self.labels[name].append(label)
                label.grid(row=i,column=j,sticky=(tk.W if j==0 else tk.E))

    def on_resize(self,event):
        """ resize label when panel get resized """
        if list(self.labels.values())[0]: # Check that labels have been initialized
            geo_info_width = self.winfo_width()
            for label_group in self.labels.values():
                for i,label in enumerate(label_group):
                    label['width'] = geo_info_width * (NAME_FRAC if i==0 else (1-NAME_FRAC)/2)

    def change_coords(self,name,coords):
        self.coords[name] = coords
        lon,lat = coords[0],coords[1]
        if lon is not None and lat is not None:
            lon,lat = round(coords[0],1),round(coords[1],1)
            lon,lat = f"{lon}°",f"{lat}°"
        else:
            lon,lat='---','---'
        self.labels[name][1]['text'] = lon
        self.labels[name][2]['text'] = lat
        
    def receive_map_area_coords(self,area):
        self.change_coords('Top-left',area[0],area[2])
        self.change_coords('Bottom-right',area[1],area[3])

    def receive_clicked_coords(self,coords):
        self.change_coords('Clicked',coords[0],coords[1])

    def remove_clicked_point(self):
        self.change_coords('Clicked',[None,None])

    

    