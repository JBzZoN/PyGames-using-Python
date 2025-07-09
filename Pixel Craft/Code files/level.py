from settings import *
from player import Player
import pygame, math
from generic import Generic, Water, Dragon
from pytmx.util_pygame import load_pygame
from overlay import Overlay, Rain, Rain_spots
from support import *
from random import randint, choice

class Level:
    def __init__(self):

        # screens
        self.screen = pygame.display.get_surface()
        self.world_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA).convert_alpha()

        # sprite groups
        self.display_sprites = CameraGroup(self.world_screen)
        self.collide_sprites = pygame.sprite.Group()
        self.move_along_only_sprites = pygame.sprite.Group()
        self.not_farmable_group = pygame.sprite.Group()
        self.apple_group = pygame.sprite.Group()
        self.apple_tree = pygame.sprite.Group()

        # image_surfs
        self.trees = {'big_tree': 0, 'small_tree': 0}

        # initialising Overlay
        self.overlay = Overlay() # help button, inventory, 

        # using pytmx
        tmx_data = load_pygame("../Graphics/tiled/tmx/world.tmx")

        # get marker from tmx file to get the starting point
        obj_layer = tmx_data.get_layer_by_name("shapes")
        for obj in obj_layer:
            if obj.name == "marker":
                self.marker = (obj.x, obj.y)

            elif obj.name == "bed":
                self.bed = obj.image # gives surface
                self.bed_xy = (obj.x, obj.y)
            
            elif obj.name == "dragon":
                self.dragon_loc = (obj.x, obj.y)

        bed_x, bed_y = self.bed_xy
        bed_sprite = Generic(
            image_surf=self.bed,
            sprite_type="bed",
            groups=[self.move_along_only_sprites],
            pos=(bed_x, bed_y) - (pygame.math.Vector2(self.marker) - pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)),
            zpos=level["hit_box"],
        )

        # not farmable sprites
        self.not_farmable_matrix = [[0 for col in range(100)] for row in range(100)]
        for x, y, surf in tmx_data.get_layer_by_name("not_farmable").tiles():
            Generic(
                image_surf=surf.convert_alpha(),
                groups=[self.not_farmable_group, self.move_along_only_sprites],
                sprite_type='not_farmable',
                pos=(x*TILE_WIDTH, y*TILE_HEIGHT) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker),
                zpos=None,
            )
            self.not_farmable_matrix[y][x] = 1


        # dragon
        dragon_surfs = []
        dragon_sheet_surf = pygame.image.load('../Graphics/other_images/beast.png')
        for index in range(4):
            dragon_surfs.append(get_image_from_sheet(dragon_sheet_surf, index, 0, (79, 69)))
        
        self.dragon = Dragon(image_surfs = dragon_surfs,
                      groups = [self.display_sprites, self.collide_sprites, self.move_along_only_sprites],
                      pos = self.dragon_loc + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker) - pygame.math.Vector2(34, 50))


        # player sprite
        player_sheet = pygame.image.load("../Graphics/other_images/player.png").convert_alpha()
        self.player = Player(
            start_pos = self.marker,
            group=self.display_sprites,
            image_sheet=player_sheet,
            sprite_type="player",
            z=level["player"],
            collide_sprites=self.collide_sprites,
            overlay = self.overlay,
            not_farmable_matrix=self.not_farmable_matrix,
            movement_group=self.move_along_only_sprites,
            bed = bed_sprite,
            dragon = self.dragon,
            apple_group= self.apple_group,
            apple_tree_group= self.apple_tree,
        )
        # back ground image
        self.bg_surf = pygame.image.load("../Graphics/other_images/world.png").convert()
        Generic(
            image_surf=self.bg_surf,
            sprite_type="ground",
            groups=[self.display_sprites],
            # top left position
            pos=pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker),
            zpos=level["ground"],
        )

        # water sprites
        # create water blocks in tiled to get x and y
        water_surfs = []

        water_sheet_surf = pygame.image.load('../Graphics/other_images/water.png')
        for index in range(4):
            water_surfs.append(get_image_from_sheet(water_sheet_surf, index, 0, (16, 16)))

        for x, y, surf in tmx_data.get_layer_by_name("water").tiles():
            Water(
                image_surfs=water_surfs,
                groups=[self.display_sprites],
                pos=(x*TILE_WIDTH, y*TILE_HEIGHT) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker),
            )

        # trees - apples
        self.apple_surf = pygame.image.load('../Graphics/other_images/apple.png')
        obj_layer = tmx_data.get_layer_by_name("tree_stones")
        for obj in obj_layer:
            if obj.name == 'rock_flower':
                loc = (obj.x, obj.y) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker);
                Generic(
                image_surf=obj.image.convert_alpha(),
                sprite_type="rock_flower",
                groups=[self.display_sprites, self.collide_sprites, self.move_along_only_sprites],
                pos=loc,
                zpos=level["player"],
                )
            elif obj.name == "big_tree":
                if not self.trees['big_tree']:
                    self.trees['big_tree'] = obj.image.convert_alpha()
                tree_loc = (obj.x, obj.y) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker);
                a = Generic(
                image_surf=obj.image.convert_alpha(),
                sprite_type="big_tree",
                groups=[self.display_sprites, self.collide_sprites, self.move_along_only_sprites, self.apple_tree],
                pos=tree_loc,
                zpos=level["player"],
                id = (obj.x, obj.y),
                )

                if randint(0, 2) == 1:
                    k = str(choice([1, 2, 3, 4, 5]))
                    Generic(
                    image_surf=self.apple_surf,
                    sprite_type="apple",
                    groups=[self.display_sprites, self.apple_group],
                    pos=tree_loc+apples['big_tree']['loc'+ k][1],
                    zpos=level["apple"],
                    loc_on_map=int(k),
                    id = (obj.x, obj.y)
                    )
                    a.apples = 1
            elif obj.name == "small_tree":
                if not self.trees['small_tree']:
                    self.trees['small_tree'] = obj.image.convert_alpha()
                tree_loc = (obj.x, obj.y) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker) 
                a = Generic(
                image_surf=obj.image.convert_alpha(),
                sprite_type="small_tree",
                groups=[self.display_sprites, self.collide_sprites, self.move_along_only_sprites, self.apple_tree],
                pos=tree_loc,
                zpos=level["player"],
                id = (obj.x, obj.y),
                )

                if randint(0, 2) == 1:
                    k = str(choice([1, 2]))
                    Generic(
                    image_surf=self.apple_surf,
                    sprite_type="apple",
                    groups=[self.display_sprites, self.apple_group],
                    pos=tree_loc+apples['small_tree']['loc' + k][1],
                    zpos=level["apple"],
                    loc_on_map=int(k),
                    id = (obj.x, obj.y),
                    )
                    a.apples = 1
                
        
        # hitbox sprites

        # top_hit_box
        for x, y, surf in tmx_data.get_layer_by_name("top_hit_box").tiles():
            Generic(
                image_surf=None,
                sprite_type="top_hit_box",
                groups=[self.collide_sprites],
                pos=(x*TILE_WIDTH, y*TILE_HEIGHT) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker),
                zpos=level["hit_box"],
                wd=TILE_WIDTH,
                hg=TILE_HEIGHT,
            )
        # bottom_hit_box
        for x, y, surf in tmx_data.get_layer_by_name("bottom_hit_box").tiles():
            Generic(
                image_surf=None,
                sprite_type="bottom_hit_box",
                groups=[self.collide_sprites],
                pos=(x*TILE_WIDTH, y*TILE_HEIGHT) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker),
                zpos=level["hit_box"],
                wd=TILE_WIDTH,
                hg=TILE_HEIGHT,
            )
        # left_hit_box
        for x, y, surf in tmx_data.get_layer_by_name("left_hit_box").tiles():
            Generic(
                image_surf=None,
                sprite_type="left_hit_box",
                groups=[self.collide_sprites],
                pos=(x*TILE_WIDTH, y*TILE_HEIGHT) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker),
                zpos=level["hit_box"],
                wd=TILE_WIDTH,
                hg=TILE_HEIGHT,
            )
        # right_hit_box
        for x, y, surf in tmx_data.get_layer_by_name("right_hit_box").tiles():
            Generic(
                image_surf=None,
                sprite_type="right_hit_box",
                groups=[self.collide_sprites],
                pos=(x*TILE_WIDTH, y*TILE_HEIGHT) + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker),
                zpos=level["hit_box"],
                wd=TILE_WIDTH,
                hg=TILE_HEIGHT,
            )
        # rain drops
        self.rain = []
        for _ in range(300):
            self.rain.append(Rain(self.player))
        self.rain_spots = []
        for _ in range(50):
            self.rain_spots.append(Rain_spots(self.player))

    # only function in game loop in this entire file
    def run(self, dt, zoom):

        ##### IMP ######
        # Think of pos as the place where the sprite should be placed when the offset is 0 #

        self.screen.fill("black")

        offset = self.player.pos_in_display - self.player.start_pos

        self.display_sprites.custom_draw(offset, dt)

        if not self.overlay.box_is_displayed: # to prevent motion and animation when box of overlay is displayed
            self.display_sprites.update(dt)

        self.display_sprites.zoom(zoom)

        # debug
        # pygame.draw.rect(self.screen, 'red', self.player.rect, width=1)
        # pygame.draw.rect(self.screen, 'black', tree.rect, width=1)

        for sprite in self.collide_sprites.sprites():
            sprite.hit_box.center = sprite.center_of_hitbox - offset
            # debug use zoom = 1
            # pygame.draw.rect(self.screen, 'blue', sprite.hit_box, width=1)

        for sprite in self.move_along_only_sprites:
            sprite.rect.center = sprite.center_of_rect - offset
            # debug
            # pygame.draw.rect(surface=self.screen, color='red', rect=sprite.rect, width=2)

        # for next day
        if self.display_sprites.next_day():
            for cut_tree in self.player.cut_trees:
                tree_loc = cut_tree.id + pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - pygame.math.Vector2(self.marker) 
                a = Generic(
                image_surf=self.trees[cut_tree.sprite_type.replace("cut_", '')],
                sprite_type=cut_tree.sprite_type.replace("cut_", ''),
                groups=[self.display_sprites, self.collide_sprites, self.move_along_only_sprites, self.apple_tree],
                pos=tree_loc,
                zpos=level["player"],
                id = cut_tree.id,
                )
                cut_tree.kill()

            # APPLE LOGIC
            for tree in self.apple_tree:
                if tree.apples < len(apples[tree.sprite_type]) and randint(0, 2) == 1:
                    tree.apples += 1
                    locations = []
                    for apple in self.apple_group:
                        if apple.id == tree.id:
                            locations += [apple.loc_on_map]
                    possible = [1, 2, 3, 4, 5]
                    if tree.sprite_type == 'small_tree':
                        possible = [1, 2]
                    possible = [x for x in possible if x not in locations]

                    k = choice(possible)
                    Generic(
                    image_surf=self.apple_surf,
                    sprite_type="apple",
                    groups=[self.display_sprites, self.apple_group],
                    pos=pygame.math.Vector2(tree.rect.topleft)+ offset +apples[tree.sprite_type]['loc' + str(k)][1],
                    zpos=level["apple"],
                    loc_on_map=k,
                    id = tree.id,
                    )


            for dirt in self.player.dirt_group:
                if dirt.watered:
                    for seed in self.player.seed_soil_group:
                        if math.floor(dirt.rect.centerx/16) == math.floor(seed.rect.centerx/16)\
                            and math.floor(dirt.rect.centery/16) == math.floor(seed.rect.centery/16):
                            seed.seed_age += 0.5
                        

            for sprite in self.player.seed_soil_group.sprites():
                sprite.seed_age += 0.5

                if sprite.seed_age >= len(self.player.seed_surfs[sprite.seed_type]):
                    sprite.seed_age = len(self.player.seed_surfs[sprite.seed_type]) - 1   

                sprite.image = self.player.seed_surfs[sprite.seed_type][int(sprite.seed_age)]

                if sprite.seed_age >= 1:
                    self.collide_sprites.add(sprite)
                    sprite.z = level['player']

            for sprite in self.player.dirt_group.sprites():
                sprite.watered = 0

            for sprite in self.player.water_soil_group:
                sprite.kill()

            if randint(1, 10) > 8: # 1/5 chance to rain
                self.display_sprites.raining = True
                for sprite in self.player.dirt_group.sprites():
                    sprite.watered = 1
                    Generic(image_surf=self.player.water_surf,
                            sprite_type='water_soil',
                            groups=[self.display_sprites, self.player.water_soil_group],
                            pos=sprite.rect.topleft + offset,
                            zpos=level['water_soil'])
            else:
                self.display_sprites.raining = False  

        self.overlay.draw()
        self.overlay.update()

        if self.display_sprites.raining:
            for drop in self.rain:
                drop.update(dt, zoom)
            for spot in self.rain_spots:
                spot.update(dt, zoom)

class CameraGroup(pygame.sprite.Group):
    def __init__(self, world_screen):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.world_screen = world_screen 
        self.zoom_factor = 1.5

        # raining
        self.raining = randint(0, 1)

        # sky transition
        self.colour_inc_or_dec = -1
        self.trans_colour = pygame.math.Vector3(255, 255, 255)
        self.day_or_night = 'day'
        self.day = 0
        self.prev_day = 0

    def custom_draw(self, offset, dt):
        self.world_screen.fill('black')
        self.offset = offset
        level_count = 0
        for sprite in sorted(sorted(self.sprites(), key=lambda sprite: sprite.rect.centery)\
                             ,key=lambda sprite: sprite.z):
                
            if sprite.sprite_type in ['player', 'dirt', 'seed_soil', 'big_tree', 'small_tree', 'rock_flower', 'dragon']:
                self.world_screen.blit(sprite.image, sprite.rect)
            elif sprite.sprite_type == 'water_soil': ### WATER EFFECT ###
                copy_sprite_rect = sprite.rect.copy()
                copy_sprite_rect.center -= offset
                self.world_screen.blit(sprite.image, copy_sprite_rect, special_flags=pygame.BLEND_MULT)
            else:
                copy_sprite_rect = sprite.rect.copy()
                copy_sprite_rect.center -= offset
                self.world_screen.blit(sprite.image, copy_sprite_rect)

        # sky transistion logic
        self.trans_change = pygame.math.Vector3(dt*self.colour_inc_or_dec,
                                                dt*self.colour_inc_or_dec,
                                                dt*self.colour_inc_or_dec)
        self.world_screen = self.transition_sky_colour(self.world_screen)

        # zooming
        zoomedsurface = pygame.transform.scale_by(self.world_screen, factor=self.zoom_factor)
            
        zoomedrect = zoomedsurface.get_rect()
        zoomedrect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.screen.blit(zoomedsurface, zoomedrect)
    
    def zoom(self, zoom):
        self.zoom_factor = zoom

    def transition_sky_colour(self, surface):
        another_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        another_surf.fill((int(self.trans_colour.x), int(self.trans_colour.y), int(self.trans_colour.z)))


        if self.raining:
            rain_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            rain_surf.fill((RAIN_COLOUR_SKY, RAIN_COLOUR_SKY, RAIN_COLOUR_SKY))
            surface.blit(rain_surf, (0, 0),  special_flags=pygame.BLEND_MULT)

        # debug
        # print(self.day_or_night)

        self.trans_colour += self.trans_change

        if not MIN_COLOUR_SKY <= self.trans_colour.x <= MAX_COLOUR_SKY:
            self.colour_inc_or_dec *= -1

            if self.day_or_night == 'night':
                self.day += 1

        if MIN_COLOUR_SKY >= self.trans_colour.x:
            self.trans_colour = pygame.math.Vector3(MIN_COLOUR_SKY, MIN_COLOUR_SKY, MIN_COLOUR_SKY)
        if self.trans_colour.x >= MAX_COLOUR_SKY:
            self.trans_colour = pygame.math.Vector3(MAX_COLOUR_SKY, MAX_COLOUR_SKY, MAX_COLOUR_SKY)

        if self.trans_colour.x < (MIN_COLOUR_SKY + MAX_COLOUR_SKY)//2:
            self.day_or_night = 'night'
        else:
            self.day_or_night = 'day'

        surface.blit(another_surf, (0, 0),  special_flags=pygame.BLEND_MULT)

        return surface
    
    def next_day(self):
        self.current_day = self.day
        if self.current_day != self.prev_day:
            self.prev_day = self.current_day
            return True
        
        return False
