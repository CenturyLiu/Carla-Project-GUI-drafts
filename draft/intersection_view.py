#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 19:19:58 2020

@author: shijiliu
"""


import pygame
import time
import carla

pygame.init()

pygame.display.set_caption('Intersection view')

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


class Intersection(object):
    def __init__(self, guiDisplay, map_surface, intersection_pos, intersection_direction, world_width, world_offset, display_width = display_width, display_height = display_height):
        '''
        

        Parameters
        ----------
        guiDisplay : pygame.display
            display we use for displaying everything for the gui.
        display_width : int
            width of guidisplay.
        display_height : int
            height of guidisplay.
        intersection_pos : (float,float)
            the 2d location of the center of the intersection 
        intersection_direction: (float,float)
            the 2d unit vector representing the direction the ego car will be going

        Returns
        -------
        None.

        '''
        # basic settings
        self.guiDisplay = guiDisplay
        self.map_surface = map_surface
        self.world_offset = world_offset
        self.display_width = display_width
        self.display_height = display_height
        
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
        
    def render_intersection_base(self):
        self.guiDisplay.blit(self.intersection_subsurface,self.map_pos)
        self.guiDisplay.blit(self.function_panel_surface,self.left_panel_pos)
        
    
client = carla.Client("localhost",2000)
client.set_timeout(20.0)

world = client.load_world('Town05')
carla_map = world.get_map()

world_width, world_offset = get_world_width(carla_map)

intersection_pos = (25.4,0.0)

map_surface = pygame.image.load('Town05_16140010d55cadd8d43dcbd35bb6907729a93f6b.tga')

guiDisplay = pygame.display.set_mode((display_width, display_height))
intersection_1 = Intersection(guiDisplay,map_surface,intersection_pos,(1,0),world_width,world_offset)

is_running = True
clock = pygame.time.Clock()


while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    intersection_1.render_intersection_base()
        
    pygame.display.update()
    clock.tick(15)

    