import pygame, math
from pygame.locals import *
import datetime

from wind_reader import load_stored_day_wind_data
from interpolation import get_wind_at_coord
from config import LON_INTERVAL, LAT_INTERVAL

W, H = 1280,960
GREENWICH_X_FRAC = 0.5
MAX_SCALE = 10
AUTO_MESH_ORDER_UPDATE = False

def get_coords_after_scale(cur_coords,scale_center,cur_scale,incr_scale):
        cur_x,cur_y = cur_coords
        center_x,center_y = scale_center
        ratio = 1+incr_scale/cur_scale
        new_x = center_x + ratio * (cur_x - center_x)
        new_y = center_y + ratio * (cur_y - center_y)
        return (new_x,new_y)

def x_y_from_lon_lat(lon, lat, w, h):
    return int(((GREENWICH_X_FRAC + lon/360)%1)*w), int(h*(-lat+90)/180)

def lon_lat_from_x_y(x,y,w,h):
    return (x/w - GREENWICH_X_FRAC)%1, (-y/h+0.5)*180

def x_y_interval_of_mesh_order(w,h,lon_interval_order_0,lat_interval_order_0,mesh_order):
    """ return interval of wind mesh verticaly and horizontaly wise, in screen coordinates on the double world """
    y_mesh_interval = lat_interval_order_0 / 2**mesh_order / 180 * h
    x_mesh_interval = y_mesh_interval
    return x_mesh_interval, y_mesh_interval

def find_mesh_id_to_redraw(cur_id, new_id, max_id, frame_length):
    """ for a 1-D frame of frame_length nodes on a line, represented by their ids, 
        this function returns the nodes that have to be redrawn when the first id of the frame moves from cur_id to new_id.
        The function considers the line as a torus. 
        If the two frames do not intersect, return redraw_all = True """
    redraw_min_id, redraw_max_id = None, None
    redraw_all = False
    forward_move = (new_id - cur_id) % (max_id+1) <= (max_id+1) // 2
    if forward_move:
        if (new_id - cur_id) % (max_id+1) >= frame_length:
            redraw_all = True
        else:
            redraw_min_id = (cur_id + frame_length) % (max_id+1)
            redraw_max_id = (new_id + frame_length-1) % (max_id+1)
            if redraw_max_id < redraw_max_id:
                redraw_max_id += (max_id+1)
    if not forward_move:
        if (new_id - cur_id) % (max_id+1) <= max_id+1 - frame_length:
            redraw_all = True
        else:
            redraw_min_id = new_id
            redraw_max_id = cur_id - 1
            if redraw_max_id < redraw_max_id:
                redraw_max_id += (max_id+1)
    return redraw_all, redraw_min_id, redraw_max_id

def draw_wind_with_mesh_id(day_wind_data,time,height,double_world,w,h,x_mesh_interval,y_mesh_interval,mesh_id):
    """ draw winds on double world corresponding to the list of mesh ids given in arg """
    """ mesh id given in arg can be beyond mesh limits, function deals with that by applying % to corresponding x-y coords """

    for lon_mesh_id, lat_mesh_id in mesh_id:
        x_node,y_node = (x_mesh_interval * lon_mesh_id)%w, y_mesh_interval * lat_mesh_id
        lon,lat = lon_lat_from_x_y(x_node,y_node,w,h)
        coord = {'time':time,'height':height,'lon':lon,'lat':lat}
        wind = get_wind_at_coord(day_wind_data,coord)
        pygame.draw.line(double_world,(0,0,0),(w+x_node,y_node),(w+x_node+wind[0],y_node-wind[1]))
        pygame.draw.line(double_world,(0,0,0),(x_node,y_node),(x_node+wind[0],y_node-wind[1]))

def main():
    #loading the winds
    #conn = create_connection("wind.db")
    #wind = get_wind(conn)
     
    # initialize the pygame module
    pygame.init()
    pygame.key.set_repeat(10)
     
    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((W, H))

    ###########################
    # CONSTANTS

    # load planisphere on which winds will be drawn
    # join two side by side (horizontaly) is enough to deal with world limits
    world = pygame.image.load("world-map.jpg")
    world_width, world_height = world.get_size()
    pygame.draw.line(world, (0, 0, 255), x_y_from_lon_lat(0, 90, world_width, world_height), x_y_from_lon_lat(0, -90, world_width, world_height))
    double_world = pygame.Surface((2*world_width, world_height))
    double_world.blit(world, (0,0))
    double_world.blit(world, (world_width,0))

    dscale = 0.01
    min_scale,max_scale = H/world_height,MAX_SCALE

    day_wind_data = load_stored_day_wind_data()

    time = datetime.datetime.strptime("07-01-1979 12:34:56","%d-%m-%Y %H:%M:%S")
    height = 14798

    nb_of_mesh_node_in_wind_window_lat = math.floor(180/LAT_INTERVAL) + 1
    nb_of_mesh_node_in_wind_window_lon = math.floor(nb_of_mesh_node_in_wind_window_lat / H * W)

    #############################
    # VARIABLES

    # copy of the double world that will be reset at each wind scale change
    double_world_copy = double_world.copy()

    # position of main world (positive x-coord) relatively to screen
    x, y = 0, 0
    mesh_order = None
    screen_lon_mesh_id, screen_lat_mesh_id = 0,0
    scale = 1
    drag = False
    update_scale = False

    # define a variable to control the main loop
    running = True

    
    # main loop
    while running:
        incr_scale = 0
        update_scale = False
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                # move map
                if event.key == K_LEFT:
                    x += 1
                if event.key == K_RIGHT:
                    x -= 1
                if event.key == K_UP:
                    y += 1
                if event.key == K_DOWN:
                    y -= 1
                if event.key == K_u:
                    update_scale = True
                 # scale map
                if event.key == K_PLUS or event.key == K_KP_PLUS:
                    incr_scale = dscale*scale
                if event.key == K_MINUS or event.key == K_KP_MINUS:
                    incr_scale = -dscale*scale
                elif event.type == pygame.MOUSEWHEEL:
                    scroll = event.y
                    incr_scale = scroll*dscale*scale
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:            
                    drag = True
                    mouse_x, mouse_y = event.pos
                    offset_x = x - mouse_x
                    offset_y = y - mouse_y
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:            
                    drag = False
            elif event.type == pygame.MOUSEMOTION:
                if drag:
                    mouse_x, mouse_y = event.pos
                    x = mouse_x + offset_x
                    y = mouse_y + offset_y

        # apply scale
        mouse_x,mouse_y = pygame.mouse.get_pos()
        new_scale = max(min_scale,min(scale+incr_scale,max_scale))
        x,y = get_coords_after_scale((x,y),(mouse_x,mouse_y),scale,new_scale-scale)
        scale = new_scale
           
        # x is the coord of the first world with positive x-coord
        # screen cannot go beyond the world
        x %= (world_width*scale)
        y = max(-world_height*scale+H, min(y, 0))

        # coord of screen in double_world
        x_screen = world_width - x/scale
        y_screen = -y/scale

        # MESH LOGIC
        if AUTO_MESH_ORDER_UPDATE or update_scale or mesh_order is None:
            new_mesh_order = math.floor(math.log(world_height/H*scale)/math.log(2))
        else:
            new_mesh_order = mesh_order
        x_mesh_interval,y_mesh_interval = x_y_interval_of_mesh_order(world_width,world_height,LON_INTERVAL,LAT_INTERVAL,new_mesh_order)
        max_lon_mesh_id = int(world_width/x_mesh_interval) - 1
        max_lat_mesh_id = int(world_width/x_mesh_interval) - 1
        new_screen_lon_mesh_id = min(math.floor(x_screen / x_mesh_interval),max_lon_mesh_id)
        new_screen_lat_mesh_id = min(math.floor(y_screen / y_mesh_interval),max_lat_mesh_id)
        # decide which part of the mesh has to be redrawn
        redraw_all = False
        redraw_min_lon_id, redraw_max_lon_id = None, None
        redraw_min_lat_id, redraw_max_lat_id = None, None
        if new_mesh_order != mesh_order:
            redraw_all = True
        else:
            if new_screen_lon_mesh_id != screen_lon_mesh_id:
                print(f"lon: {screen_lon_mesh_id} -> {new_screen_lon_mesh_id}")
                redraw_all, redraw_min_lon_id, redraw_max_lon_id = find_mesh_id_to_redraw(screen_lon_mesh_id,new_screen_lon_mesh_id,max_lon_mesh_id,nb_of_mesh_node_in_wind_window_lon)
                print(redraw_all, redraw_min_lon_id, redraw_max_lon_id)
                print(f"{x_screen} {new_screen_lon_mesh_id*x_mesh_interval}")
            if new_screen_lat_mesh_id != screen_lat_mesh_id:
                redraw_all, redraw_min_lat_id, redraw_max_lat_id = find_mesh_id_to_redraw(screen_lat_mesh_id,new_screen_lat_mesh_id,max_lat_mesh_id,nb_of_mesh_node_in_wind_window_lat)
                print(f"lat: {screen_lat_mesh_id} -> {new_screen_lat_mesh_id}")
                print(redraw_all, redraw_min_lat_id, redraw_max_lat_id)
                print(f"{y_screen} {new_screen_lat_mesh_id*y_mesh_interval}")
        # create a list of ids of nodes that have to be redrawn
        mesh_id = []
        if redraw_all:
            print(world_height, H/scale, world_height/H*scale)
            print(f"{mesh_order} -> {new_mesh_order}, {y_mesh_interval*(nb_of_mesh_node_in_wind_window_lat-1)}, {H/scale}")
            print(f"wind frame has {nb_of_mesh_node_in_wind_window_lon} nodes in lon among {max_lon_mesh_id+1} nodes")
            double_world_copy = double_world.copy()
            for di in range(nb_of_mesh_node_in_wind_window_lon):
                for dj in range(nb_of_mesh_node_in_wind_window_lat):
                    node_mesh_id = (new_screen_lon_mesh_id + di, new_screen_lat_mesh_id + dj)
                    mesh_id.append(node_mesh_id)
        else:
            if redraw_min_lon_id is not None:
                for lon_mesh_id in range(redraw_min_lon_id, redraw_max_lon_id+1):
                    for dj in range(nb_of_mesh_node_in_wind_window_lat):
                        lat_mesh_id = new_screen_lat_mesh_id + dj
                        node_mesh_id = ((lon_mesh_id)%(max_lon_mesh_id+1), lat_mesh_id)
                        mesh_id.append(node_mesh_id)
            if redraw_min_lat_id is not None:
                for di in range(nb_of_mesh_node_in_wind_window_lon):
                    for lat_mesh_id in range(redraw_min_lat_id, redraw_max_lat_id+1):
                        lon_mesh_id = new_screen_lon_mesh_id + di
                        node_mesh_id = (lon_mesh_id, (lat_mesh_id)%(max_lat_mesh_id+1))
                        mesh_id.append(node_mesh_id)
        # draw nodes in mesh_id 
        draw_wind_with_mesh_id(day_wind_data,time,height,double_world_copy,world_width,world_height,x_mesh_interval,y_mesh_interval,mesh_id)
        # update before looping
        mesh_order = new_mesh_order
        screen_lon_mesh_id, screen_lat_mesh_id = new_screen_lon_mesh_id, new_screen_lat_mesh_id
        
        screen_cut = double_world_copy.subsurface((x_screen,y_screen), (int(W/scale),int(H/scale)))
        screen_cut = pygame.transform.scale(screen_cut, (W,H))
        
        #render
        #screen.blit(world, (x, y))
        #screen.blit(world, (x - world.get_width(), y))
        #pygame.draw.circle(screen, (0,0,0), (x, y), 10)
        #pygame.draw.circle(screen, (255,0,0), (x - world.get_width(), y), 10)

        screen.blit(screen_cut, (0,0))

        #step = 100 ??
        


        pygame.display.flip()
     
     
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
