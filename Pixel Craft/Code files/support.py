# get image from sprite sheet
import pygame
import os

def get_image_from_sheet(sprite_sheet_surf, xpos, ypos, size_tuple):

    width, height = size_tuple
    xpos *= size_tuple[0]
    ypos *= size_tuple[1]

    image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    image.blit(sprite_sheet_surf, (0, 0), (xpos, ypos, width, height))
    return image.convert_alpha()

# tells if a specific key (input to the function) is currently being pressed
def wasd_keysdown(key):
    keys = pygame.key.get_pressed()

    key = key.lower()

    match key:
        case 'a'|'left':
            return keys[pygame.K_a]
        case 's'|'down':
            return keys[pygame.K_s]
        case 'w'|'up':
            return keys[pygame.K_w]
        case 'd'|'right':
            return keys[pygame.K_d]
        case _ :
            return False
        
def list_of_image_surfaces_in_folder(path):
    surface_list = []

    for _, __, files in os.walk(path):
        for file in files:
            surface_list.append(pygame.image.load(path + file).convert_alpha())
        
    return surface_list

class Timer:

    def __init__(self, duration):

        self.start_time = 0
        self.duration = duration
        self.active = False

    def activate(self):

        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):

        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.start_time >= self.duration:
            self.deactivate()