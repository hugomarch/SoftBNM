import os

# Config for different map titles

map_config = {

    'World': {
        'image_file': os.path.join('resources','images','world-map.jpg'),
        'image_top_left_coords':[-180,90],
        'image_lon_lat_size':[360,180],
        'is_circular': True,
        'draw_meridian':[0]
    }

}

# Values

SCALE_EXPONENT = 1.3
NB_OF_SCALES = 10
RESAMPLING_IMAGE_HEIGHT = 1000

CLICKED_POINT_CROSS_HEIGHT_PROP = 0.02 # proportion of window height
CLICKED_POINT_CROSS_WIDTH = 3 # proportion of window height
CLICKED_POINT_CROSS_COLOR = "#f00" # proportion of window height