from PIL import Image
import os

img = Image.open(os.path.join('GUI','world-map.jpg'))
width, height = img.size

ratio = 5
new_w, new_h = int(width/ratio), int(height/ratio)

new_img = img.resize((new_w,new_h))
new_img.show()