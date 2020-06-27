#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 10:43:43 2020

@author: shijiliu
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 19:19:58 2020

@author: shijiliu
"""


import pygame
import carla
import sgc
from configobj import ConfigObj

pygame.init()
pygame.display.init()
pygame.font.init()

pygame.display.set_caption('Intersection view')

# constants
display_width = 1280
display_height = 720

black = (0,0,0)
white = (255,255,255)
bright_red = (255,0,0)
red = (139,0,0)
green = (0,128,0)
bright_green = (0,255,0)
bright_blue = (0,192,255)
blue = (0,0,139)
silver = (192,192,192)

PIXELS_PER_METER = 12

# global configuration
gui_config = ConfigObj()


#-------Utils function--------#

def get_world_width(carla_map):
        waypoints = carla_map.generate_waypoints(2)
        margin = 50
        max_x = max(waypoints, key=lambda x: x.transform.location.x).transform.location.x + margin
        max_y = max(waypoints, key=lambda x: x.transform.location.y).transform.location.y + margin
        min_x = min(waypoints, key=lambda x: x.transform.location.x).transform.location.x - margin
        min_y = min(waypoints, key=lambda x: x.transform.location.y).transform.location.y - margin
        
        world_width = max(max_x - min_x, max_y - min_y)
        world_offset = (min_x, min_y)
        return world_width, world_offset


def pos_to_pixel(intersection_pos, scale = 1, pixels_per_meter = PIXELS_PER_METER, world_offset = (0,0), offset = (0,0)):
    """Converts the world coordinates to pixel coordinates"""
    x = scale * pixels_per_meter * (intersection_pos[0] - world_offset[0])
    y = scale * pixels_per_meter * (intersection_pos[1] - world_offset[1])
    return [int(x - offset[0]), int(y - offset[1])]

def world_to_pixel_width(scale, width, pixels_per_meter = PIXELS_PER_METER):
    """Converts the world units to pixel units"""
    return int(scale * pixels_per_meter * width)

def create_intersection_config(intersection_id, world_pos, big_map_pos,yaw):
    '''
    create configuration for an intersection
    
    Returns
    -------
    None.

    '''
    
    # create config for a specific intersection
    # intersection_id is a string
    gui_config[intersection_id] = {}
    gui_config[intersection_id]["world_pos"] = {}
    gui_config[intersection_id]["world_pos"]["x"] = str(world_pos[0]) # in meter
    gui_config[intersection_id]["world_pos"]["y"] = str(world_pos[1])  # in meter
    gui_config[intersection_id]["big_map_pos"] = {}
    gui_config[intersection_id]["big_map_pos"]["x"] = str(big_map_pos[0]) # in pixel
    gui_config[intersection_id]["big_map_pos"]["y"] = str(big_map_pos[1])  # in pixel
    gui_config[intersection_id]["yaw"] = str(yaw)
    
    # actors
    gui_config[intersection_id]["Vehicle"] = {}
    gui_config[intersection_id]["Traffic light"] = {}
    
    # display mode of the intersection
    gui_config[intersection_id]["display_mode"] = "Intersection" # value can be "Vehicle" or "Spawn" or "Traffic light"
    gui_config[intersection_id]["Vehicle_to_display"] = "None" # value can be uniquename of a vehicle or "None"
    gui_config[intersection_id]["display_to_remove"] = "None" # value can be "Vehicle" or "Spawn" or "Traffic light" or "Intersection"
    
    
def spawn_vehicle_config(intersection_id,vehicle_uniquename,vehicle_map_pos,vehicle_world_pos, yaw):
    gui_config[intersection_id]["Vehicle"][vehicle_uniquename] = {}
    vehicle = gui_config[intersection_id]["Vehicle"][vehicle_uniquename]
    vehicle["map_width"] = str(vehicle_map_pos[0])
    vehicle["map_height"] = str(vehicle_map_pos[1])
    vehicle["world_x"] = str(vehicle_world_pos[0])
    vehicle["world_y"] = str(vehicle_world_pos[1])
    vehicle["yaw"] = str(yaw)

def intersection_change_display_mode(intersection_id, mode):
    # mode can be only of the following string:
    # "Intersection" or "Vehicle" or "Spawn" or "Traffic light"
    # otherwise, the display mode won't be changed
    if mode in ["Intersection" , "Vehicle" , "Spawn" , "Traffic light"]:
        gui_config[intersection_id]["display_mode"] = mode
        
def intersection_remove_display(intersection_id,mode):
    # mode can be only of the following string:
    # "None" or "Intersection" or "Vehicle" or "Spawn" or "Traffic light"
    # otherwise, the display mode won't be changed
    if mode in ["None","Intersection" , "Vehicle" , "Spawn" , "Traffic light"]:
        gui_config[intersection_id]["display_to_remove"] = mode
        
        
def intersection_get_display_mode(intersection_id):
    return gui_config[intersection_id]["display_mode"]

def intersection_get_display_to_remove(intersection_id):
    return gui_config[intersection_id]["display_to_remove"]

def display_vehicle_config(intersection_id, vehicle_uniquename):
    gui_config[intersection_id]["Vehicle_to_display"] = vehicle_uniquename

#------Intersection in GUI--------#

class Intersection(object):
    def __init__(self, guiDisplay, intersection_id, map_surface, intersection_pos, intersection_yaw, world_width, world_offset, display_width = display_width, display_height = display_height):
        '''
        

        Parameters
        ----------
        guiDisplay : pygame.display
            display we use for displaying everything for the gui.
        intersection_id: str
            the uniquename of this intersection
        display_width : int
            width of guidisplay.
        display_height : int
            height of guidisplay.
        intersection_pos : (float,float)
            the 2d location of the center of the intersection 
        intersection_yaw: flaot
            the angle representing the direction the ego car will be going

        Returns
        -------
        None.

        '''
        self.intersection_id = str(intersection_id)
        
        # basic settings
        self.guiDisplay = guiDisplay
        self.map_surface = map_surface
        self.world_offset = world_offset
        self.display_width = display_width
        self.display_height = display_height
        self.world_pos = intersection_pos
        self.yaw = intersection_yaw
        # Maximum size of a Pygame surface
        width_in_pixels = (1 << 14) - 1

        # Adapt Pixels per meter to make world fit in surface
        surface_pixel_per_meter = int(width_in_pixels / world_width)
        if surface_pixel_per_meter > PIXELS_PER_METER:
            surface_pixel_per_meter = PIXELS_PER_METER
        
        self.pixel_per_meter = surface_pixel_per_meter
        
        # create the left panel for gui function, and right panel for maps
        self.left_width = int(self.display_width * 0.3) # unit: pixel
        self.left_height = int(self.display_height) # unit: pixel
        self.map_width = int(self.display_width - self.left_width) # unit: pixel
        self.map_height = int(self.display_height) # unit: pixel
        self.left_panel_pos = (0,0)
        self.map_pos = (self.left_width,0)
        
        # create panel for function panel
        self.function_panel_surface = pygame.Surface((self.left_width, self.left_height))
        self.function_panel_surface.fill(silver)
        
        # create the subsurface to get the display region of the intersection
        self.intersection_scale = 1
        self.intersection_pos = pos_to_pixel(intersection_pos, self.intersection_scale,pixels_per_meter = self.pixel_per_meter,world_offset = self.world_offset)
        
        
        self.intersection_width = world_to_pixel_width(self.intersection_scale, 75,pixels_per_meter = self.pixel_per_meter)# unit: pixel, the "75" here is the width of the 
                                                                                   # intersection, in unit of meter
        self.translation_offset = (self.intersection_pos[0] - self.intersection_width / 2 ,self.intersection_pos[1] - self.intersection_width / 2 )
        
        print(self.translation_offset)
        
        self.clipping_rect = pygame.Rect(self.translation_offset[0],
                                    self.translation_offset[1],
                                    self.intersection_width,
                                    self.intersection_width)
        
        self.intersection_subsurface = self.map_surface.subsurface(self.clipping_rect)
        self.intersection_subsurface = pygame.transform.smoothscale(self.intersection_subsurface,(int(self.map_width),int(self.map_height)))
        
        # create a dictionary for vehicles
        self.vehicle_dict = {}
        
        create_intersection_config(self.intersection_id, intersection_pos, self.intersection_pos,self.yaw)
        
        self.create_intersection_panel()
        self.create_spawn_panel()
        
    def create_spawn_panel(self):
        '''
        create the panel for spawning the actors. Here, only spawn vehicle for function demo

        '''
        self.spawn_x_text = sgc.InputBox(label = "x",pos = (50,200), label_side = "left")
        self.spawn_y_text = sgc.InputBox(label = "y", pos = (50,300), label_side = "left")
        
        self.spawn_label = None # create a label that's going to show the place the user have clicked on the map
        
        self.spawn_button = sgc.Button( label="spawn", pos=(int(self.left_width / 2) - 50, self.left_height - 100))
        self.spawn_button.config(on_click=self.spawn_in_intersection)
        
        self.interactive_mouse_button = sgc.Button(label = " Mouse", pos = (50,100))
        self.interactive_mouse_button.on_click = self.interactive_mouse_callback
        
        
    def render_spawn_panel(self):
        # the left panel are spawning settings and a unique spawn button
        
        self.spawn_x_text.add(fade=False)
        self.spawn_y_text.add(fade=False)
        
        
        self.spawn_button.add(fade=False)
        self.interactive_mouse_button.add(fade=False)
        
        if self.spawn_label != None:
            self.spawn_label.add(fade=False)
        
    def remove_spawn_page(self):
        self.spawn_x_text.remove(fade=False)
        self.spawn_x_text.text = ""
        self.spawn_y_text.remove(fade=False)
        self.spawn_y_text.text = ""
        self.spawn_button.remove(fade=False)
        self.interactive_mouse_button.remove(fade=False)
        if self.spawn_label != None:
            self.spawn_label.remove(fade=False)
            self.spawn_label = None
            
        
    def spawn_in_intersection(self):
        # call back function for spawn an actor
        # here assume vehicle is the only actor
        print("trying to spawn vehicle")
        intersection_change_display_mode(self.intersection_id, "Intersection") # after spawning actor, we view the setting of this actor
                                                                               # change display mode to "Vehicle"
        
        
        intersection_remove_display(self.intersection_id,"Spawn")
        
    def interactive_mouse_callback(self):
        # note: no collide check is applied at present
        #       it is possible that a new vehicle is chosen to be spawned at a
        #       place where a previous vehicle has been spawned
        while True:
        
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse = event.pos
                    if mouse[0] > self.left_width and self.map_height > mouse[1] > 0:
                        self.spawn_x_text.text = str(mouse[0])
                        self.spawn_y_text.text = str(mouse[1])
                        # show the position on the map
                        if self.spawn_label != None:
                            self.spawn_label.remove(fade=False)
                        
                        self.spawn_label = sgc.Label(pos =  (mouse[0],mouse[1]), text = "x: " + str(mouse[0]) + " y: " + str(mouse[1]))
                    break
                    

        
    def create_intersection_panel(self):
        self.spawn_actor_button = sgc.Button(label="spawn actor",pos=(100,300))
        self.spawn_actor_button.config(on_click = self.go_to_spawn_callback)
        
    def render_intersection_panel(self):
        # the left panel is showing the general settings for this intersection
        # with buttons leading user to "spawn actor" or "manage traffic light"
        #self.spawn_actor_button = sgc.Button(label="spawn actor",pos=(100,300))
        #self.spawn_actor_button.config(on_click = self.go_to_spawn_callback)
        self.spawn_actor_button.add(fade=False)
        
    def go_to_spawn_callback(self):
        # call back function for spawn_actor_button
        # change the display configuration of this
        # intersection to be "Spawn"
        intersection_change_display_mode(self.intersection_id, "Spawn")
        intersection_remove_display(self.intersection_id,"Intersection")
        
    def remove_intersection_page(self):
        self.spawn_actor_button.remove(fade=False)
        
        
        
        
    def render_intersection_base(self):
        self.guiDisplay.blit(self.intersection_subsurface,self.map_pos)
        self.guiDisplay.blit(self.function_panel_surface,self.left_panel_pos)
        
    
    def render_full_intersection(self):
        
        display_mode = intersection_get_display_mode(self.intersection_id)
        display_to_remove = intersection_get_display_to_remove(self.intersection_id)
        
        print("display_mode == ",display_mode)
        print("display_to_remove == ",display_to_remove)
        
        if display_to_remove == "Intersection":
            self.remove_intersection_page()
        elif display_to_remove == "Spawn":
            self.remove_spawn_page()
        
        self.render_intersection_base()
        
        
        if display_mode == "Intersection":
            self.render_intersection_panel()
        elif display_mode == "Spawn":
            self.render_spawn_panel()
            

        
    
        
    
class VehicleButton(object):
    def __init__(self, intersection_id, uniquename, img_x, img_y, map_x, map_y, yaw):
        self.button = sgc.Button(label=uniquename, pos = (img_x,img_y))
        self.map_x = map_x
        self.map_y = map_y
        self.yaw = yaw
        self.uniquename = uniquename
        self.intersection_id = intersection_id
        
    def vehicle_button_callback(self):
        display_vehicle_config(self.intersection_id, self.uniquename)




    
client = carla.Client("localhost",2000)
client.set_timeout(20.0)

world = client.load_world('Town05')
carla_map = world.get_map()

world_width, world_offset = get_world_width(carla_map)

intersection_pos = (25.4,0.0)

map_surface = pygame.image.load('Town05_16140010d55cadd8d43dcbd35bb6907729a93f6b.tga')

gui_sgc_Display = sgc.surface.Screen((display_width, display_height))#pygame.display.set_mode((display_width, display_height))



intersection_1 = Intersection(gui_sgc_Display,1,map_surface,intersection_pos,0.0,world_width,world_offset)

is_running = True
clock = pygame.time.Clock()
time = clock.tick(30)



while is_running:
    for event in pygame.event.get():
        sgc.event(event)
        if event.type == pygame.QUIT:
            is_running = False

    intersection_1.render_full_intersection()
    
    sgc.update(time)
    pygame.display.update()
    

    