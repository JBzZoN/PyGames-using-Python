import pygame

# screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500

# tile size
TILE_WIDTH = 16
TILE_HEIGHT = 16

# size of sprites
pixel_size = {'player':(48, 48)}

# level of sprites, add to same level if you want y level camera
level = {'ground':0,'water':10, 'dirt': 25,'water_soil': 30, 'small_seed': 40,'log':45, 'player':50, 'apple': 55, 'hit_box':100}

# log cut tree settings
cut_tree_offset = {'small_tree':(4, 16),\
                   'big_tree':(10, 20)}

# level of zoom
ZOOM_MAX = 2
ZOOM_MIN = 1

# inventory
inventory = {'apple':0,
             'log':0,
             'corn':0,
             'tomato':0,
             'corn_seed':5,
             'tomato_seed':1,}

# apples
apples = {'big_tree': {'loc1':(0,(5, 5)), 'loc2':(0,(12, 2)), 'loc3':(0,(18, 7)), 'loc4':(0,(5, 12)), 'loc5':(0,(14, 14))},
          'small_tree': {'loc1':(0,(3, 2)), 'loc2':(0,(3, 10))}} # add co-ordinate tuples instead of these strings


inventory_order = ['apple',
                   'log',
                   'corn',
                   'tomato',
                   'corn_seed',
                   'tomato_seed',]

# sky colour
MAX_COLOUR_SKY = 255
RAIN_COLOUR_SKY = 200
MIN_COLOUR_SKY = 120