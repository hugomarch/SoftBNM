import tkinter as tk
from tkinter import ttk

from GUI.GUI_config import NAME_FRAC

class GeoInfoFrame(tk.Frame):
    def __init__(self,GUI_parent=None,business_parent=None):
        self.GUI_parent = GUI_parent
        tk.Frame.__init__(self,self.GUI_parent)
        self.coords = {'Top-left': [None,None],'Bottom-right': [None,None],'Clicked':[None,None]}
        self.coord_frames = {'Top-left': None,'Bottom-right': None,'Clicked': None}
        self.labels = {'Top-left': None,'Bottom-right': None,'Clicked': None}
        self.make_widgets()
        self.bind('<Configure>',self.on_resize)

    def make_one_coord_frame(self,name):
        coord_frame = tk.Frame(self)
        labels = []
        for i in range(3):
            label = ttk.Label(coord_frame,text=(name if i==0 else ""),background='#999')
            labels.append(label)
            label.pack(side=tk.LEFT,fill=tk.Y,expand=(i>0))
        return coord_frame,labels

    def make_widgets(self):
        for name in self.coord_frames.keys():
            coord_frame, labels = self.make_one_coord_frame(name)
            self.coord_frames[name] = coord_frame
            self.labels[name] = labels
            coord_frame.pack(side=tk.TOP,fill=tk.BOTH)

    def on_resize(self,event):
        """ resize label when panel get resized """
        if list(self.labels.values())[0]: # Check that labels have been initialized
            geo_info_width = self.winfo_width()
            for label_group in self.labels.values():
                for i,label in enumerate(label_group):
                    label['width'] = geo_info_width * (NAME_FRAC if i==0 else (1-NAME_FRAC)/2)

    def change_coords(self,name,coords):
        self.coords[name] = coords
        lon,lat = round(coords[0],1),round(coords[1],1)
        self.labels[name][0]['text'] = name
        self.labels[name][1]['text'] = f"{lon}°"
        self.labels[name][2]['text'] = f"{lat}°"
        
    def receive_map_area_coords(self,area):
        self.change_coords('Top-left',area[0],area[2])
        self.change_coords('Bottom-right',area[1],area[3])

    def receive_clicked_coords(self,coords):
        self.change_coords('Clicked',coords[0],coords[1])

    

    