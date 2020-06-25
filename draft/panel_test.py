#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 20:51:03 2020

@author: shijiliu
"""


import pygame
import time

pygame.init()

pygame.display.set_caption('Hello Button')

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


class GuiPanel(object):
    def __init__(self, display_width, display_height):
        self.clock = pygame.time.Clock()
        
        # create the base of the panel
        self.display_width = display_width
        self.display_height = display_height
        self.guiDisplay = pygame.display.set_mode((display_width, display_height))
        self.guiDisplay.fill(white)
        
        # create the left panel for gui function, and right panel for maps
        self.left_width = self.display_width * 0.3
        self.left_height = self.display_height
        self.map_width = self.display_width - self.left_width
        self.map_height = self.display_height
        
        self.left_pos = (0,0)
        self.map_pos = (self.left_width,0)
        
        self.function_panel_surface = pygame.Surface((self.left_width, self.left_height))
        self.map_surface = pygame.Surface((self.map_width,self.map_height))
        
        self.function_panel_surface.set_alpha(100)
        self.function_panel_surface.fill(silver)
        
        self.map_surface.fill(white)
        
    def render_gui_panel_base(self):
        self.guiDisplay.blit(self.function_panel_surface,self.left_pos)
        self.guiDisplay.blit(self.map_surface,self.map_pos)
        

is_running = True
gui_panel = GuiPanel(display_width, display_height)
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    gui_panel.render_gui_panel_base()
        
    pygame.display.update()
    gui_panel.clock.tick(15)