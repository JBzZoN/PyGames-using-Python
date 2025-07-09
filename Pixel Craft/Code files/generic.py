import pygame
from settings import *
from support import *

class Generic(pygame.sprite.Sprite):

    # hit box only if one of the specified tiles
    def __init__(self, image_surf, sprite_type, groups, pos, zpos, wd = None, hg = None, loc_on_map = None, id = None):
        super().__init__(groups)
        self.z = zpos
        self.image = image_surf
        self.sprite_type = sprite_type

        if image_surf:
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.center_of_rect = self.rect.center
        else:   ### FOR GENERICS WHICH DOESNT NEED IMAGES ###
            self.rect = pygame.Rect(0, 0, wd, hg)
            self.rect.topleft = pos
            self.center_of_rect = self.rect.center

        # collision
        if sprite_type == 'top_hit_box':
            self.hit_box = self.rect.inflate(0, -self.rect.height*0.9)
            self.hit_box.top = self.rect.top
        elif sprite_type == 'bottom_hit_box':
            self.hit_box = self.rect.inflate(0, -self.rect.height*0.9)
            self.hit_box.bottom = self.rect.bottom
        elif sprite_type == 'right_hit_box':
            self.hit_box = self.rect.inflate(-self.rect.width*0.9, 0)
            self.hit_box.right = self.rect.right
        elif sprite_type == 'left_hit_box':
            self.hit_box = self.rect.inflate(-self.rect.width*0.9, 0)
            self.hit_box.left = self.rect.left
        elif sprite_type == 'dirt':
            self.watered = 0
            self.seeded = 0
            self.loc_on_map = loc_on_map
        elif sprite_type == 'seed_soil':
            self.seed_age = 0
            self.seed_type = None
            self.loc_on_map = loc_on_map
            self.hit_box = self.rect.inflate(0, -self.image.get_width()*0.9)
            self.hit_box.bottom = self.rect.bottom - 3
        elif sprite_type in ['big_tree', 'small_tree', 'rock_flower', 'cut_big_tree', 'cut_small_tree']:
            self.hit_box = self.rect.inflate(-self.image.get_width()*0.5, -self.image.get_height()*0.9)
            self.hit_box.bottom = self.rect.bottom - 5
            self.hit_box.centerx = self.rect.centerx
            self.center_of_hitbox = self.hit_box.center
            self.apples = 0
            self.id = id
        elif sprite_type == "bed":
            topleft = self.rect.topleft
            self.rect.inflate_ip(16, 0)
            self.rect.topleft = topleft
            self.center_of_rect = self.rect.center
        elif sprite_type == "apple":
            self.id = id
            self.loc_on_map = loc_on_map
            ...

        if sprite_type in ['left_hit_box', 'right_hit_box', 'bottom_hit_box', 'top_hit_box', 'seed_soil']:
            self.center_of_hitbox = self.hit_box.center

# a update sprite
class Water(Generic):

    def __init__(self, image_surfs, groups, pos):

        super().__init__(image_surf=image_surfs[0],
                         sprite_type='water', 
                         groups=groups,
                         pos=pos,
                         zpos=level['water'])
        
        self.water_surfs = image_surfs
        self.water_index = 0
        self.animation_speed = 5
        
    def update(self, dt):

        self.water_index += self.animation_speed*dt
        if self.water_index >= len(self.water_surfs):
            self.water_index = 0

        self.image = self.water_surfs[int(self.water_index)]

# a update sprite
class Dragon(Generic):

    def __init__(self, image_surfs, groups, pos):

        super().__init__(image_surf=image_surfs[0],
                         sprite_type='dragon', 
                         groups=groups,
                         pos=pos,
                         zpos=level['player'])
        
        self.dragon_surfs = image_surfs
        self.dragon_index = 0
        self.animation_speed = 5

        self.hit_box = self.rect.inflate(0, -self.rect.height*0.9)
        self.hit_box.bottom = self.rect.bottom
        self.center_of_hitbox = self.hit_box.center

    def update(self, dt):

        self.dragon_index += self.animation_speed*dt
        if self.dragon_index >= len(self.dragon_surfs):
            self.dragon_index = 0

        self.image = self.dragon_surfs[int(self.dragon_index)]