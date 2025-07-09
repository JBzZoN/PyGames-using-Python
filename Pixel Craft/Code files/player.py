from settings import *
import pygame, math, random
from support import *
from generic import Generic

class Entity(pygame.sprite.Sprite):

    def __init__(self, group, image_sheet, sprite_type, z, collide_sprites, start_pos):
        super().__init__(group)
        self.screen = pygame.display.get_surface()

        # sprite sheet
        self.image_sheet = image_sheet
        self.sprite_type = sprite_type
        self.start_pos = start_pos

        # timer
        self.timer = Timer(300)
        self.dragon_timer = Timer(300)

        # layer
        self.z = z

        # motion current status (idle/move + direction)
        self.status = None
        self.dir_status = None

        # motion control variables
        self.direction = pygame.math.Vector2()
        self._pos_in_display_ph = pygame.math.Vector2()
        self.pos_in_display = pygame.math.Vector2() # place holder for center

        # collision
        self.hit_box = None
        self.collide_sprites = collide_sprites
        self.has_collided = False
        self.hit_direction = None

        # hit point action
        self.hit_point = None # for farming
        self.access_hit_point = None # for accessing something like apples bed talking stuff
        self.for_hit_point = {'right': pygame.math.Vector2(1, 0),
                              'left': pygame.math.Vector2(-1, 0),
                              'up': pygame.math.Vector2(0, -1),
                              'down': pygame.math.Vector2(0, 1)}

    def update(self, dt):
        self.input()
        if not self.timer.active:
            self.animation(dt)

        if self.collision() or self.has_collided:
            self.direction = pygame.math.Vector2(0, 0)
            self.status = 'idle'
            self.has_collided = wasd_keysdown(self.hit_direction)

                
        self.move(dt)
        self.timer.update()

    def move(self, dt):
        if not self.timer.active:
            self._pos_in_display_ph += pygame.math.Vector2(self.direction) * self.speed * dt
            self.pos_in_display = round(self._pos_in_display_ph)

    def animation(self, dt):
        pass

    def collision(self):
        
        for sprite in self.collide_sprites.sprites():
            if not self.has_collided and sprite.hit_box.colliderect(self.hit_box):

                # move all the surrounding structures in opposite direction by 2
                if sprite.sprite_type in ["left_hit_box", "right_hit_box"]:
                    if self.hit_box.right <= sprite.hit_box.right + 2:
                        self._pos_in_display_ph.x -= 2
                    elif self.hit_box.left >= sprite.hit_box.left - 2:
                        self._pos_in_display_ph.x += 2

                elif sprite.sprite_type in ["top_hit_box", "bottom_hit_box", "seed_soil", 'big_tree', 'small_tree', 'rock_flower', 'dragon', 'cut_big_tree', 'cut_small_tree']:
                    if self.hit_box.bottom > sprite.hit_box.bottom + 2:
                        self._pos_in_display_ph.y += 2
                    elif self.hit_box.top < sprite.hit_box.top - 2:
                        self._pos_in_display_ph.y -= 2

                # collision data
                self.rect.centerx = self.hit_box.centerx
                self.rect.centery = self.hit_box.centery - 5
                self.has_collided = True
                self.hit_direction = self.dir_status
                return True
        return False   

class Player(Entity):

    def __init__(self, group, image_sheet, sprite_type, z,\
                  collide_sprites, overlay, not_farmable_matrix, start_pos, movement_group, bed, dragon\
                    , apple_group, apple_tree_group):
        super().__init__(group, image_sheet, sprite_type, z, collide_sprites, start_pos)

        # main init
        self.image = get_image_from_sheet(image_sheet, 0, 0, pixel_size[sprite_type])
        self.rect = self.image.get_rect()
        self.bed_sprite = bed
        self.dragon = dragon
        self.cut_tree_surfs = {'small_tree': pygame.image.load('../Graphics/other_images/small_tree_cut.png').convert_alpha(),\
                               'big_tree':pygame.image.load('../Graphics/other_images/big_tree_cut.png').convert_alpha()}

        # surfs
        self.dirt_surf = pygame.image.load('../Graphics/other_images/dirt.png')
        self.water_surf = pygame.image.load('../Graphics/other_images/watered.png')

        # overlay
        self.overlay = overlay

        # sprite groups
        self.display_sprites = group
        self.not_farmable_matrix = not_farmable_matrix
        self.dirt_group = pygame.sprite.Group()
        self.movement_group = movement_group
        self.water_soil_group = pygame.sprite.Group()
        self.seed_soil_group = pygame.sprite.Group()
        self.apple_group = apple_group
        self.apple_tree_group = apple_tree_group
        self.cut_trees = pygame.sprite.Group()

        # tracking lists
        self.hoed = [] # to prevent rehoeing

        # motion
        self.start_pos = pygame.math.Vector2(start_pos) # marker position

        self.rect.center = pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.pos_in_display = pygame.math.Vector2(start_pos) # place holder for center
        self._pos_in_display_ph = pygame.math.Vector2(start_pos)
        self.status = "idle" # idle down
        self.dir_status = "down"
        self.speed = 75

        # for tools and seeds
        self.start_tool = 0
        self.seed_surfs = {'corn': [], 'tomato' : []}

        # for animation
        self.setup()
        self.animation_speed = 3
        self.frame_index = 0

        # switch offs
        self.switch_off_tool_animation = False

        # for collision
        self.hit_box = self.rect.inflate(-pixel_size['player'][0]*0.8, -pixel_size['player'][1]*0.85)
        self.hit_box.y += 5

        # sleeping
        self.sleeper = False
        self.sleep_dir = None

        # timers
        self.transition = Timer(100000) # 100 seconds for sleep
        self.dragon_timer = Timer(3000)

    def setup(self):
        # col - idle, idle, move, move
        # row - down, up, left, right

        # tool sprite sheet

        tool_sheet = pygame.image.load('../Graphics/other_images/toolsheet.png')

        self.anime_images = {'idle': {'up': [], 'down': [], 'left': [], 'right': []}, 
                             'move': {'up': [], 'down': [], 'left': [], 'right': []}}

        for col, ctype in enumerate(['idle', 'idle', 'move', 'move']):
            for row, rtype in enumerate(['down', 'up', 'left', 'right']):
                self.anime_images[ctype][rtype].append(get_image_from_sheet(self.image_sheet, col, row, pixel_size['player']))

        self.tool_anime_images = {'hoe': {'down': [], 'up': [], 'left': [], 'right': []},
                                  'axe': {'down': [], 'up': [], 'left': [], 'right': []},
                                  'water': {'down': [], 'up': [], 'left': [], 'right': []}}
        
        for itool, ttype in enumerate(['hoe', 'axe', 'water']):
            for row, rtype in enumerate(['down', 'up', 'left', 'right']):
                self.tool_anime_images[ttype][rtype].append(get_image_from_sheet(tool_sheet,
                                                            xpos=0,
                                                            ypos=row + 4*itool,
                                                            size_tuple=(48, 48)))
                self.tool_anime_images[ttype][rtype].append(get_image_from_sheet(tool_sheet,
                                                            xpos=1,
                                                            ypos=row + 4*itool,
                                                            size_tuple=(48, 48)))
                
        seed_sheet = "../Graphics/other_images/Basic_Plants.png"
        seed_surf = pygame.image.load(seed_sheet)
        # 16 by 16 sprite sheet
        for row, seed in enumerate(['corn', 'tomato']):
            for col in range(1, 5):
                self.seed_surfs[seed].append(get_image_from_sheet(seed_surf,
                                                            xpos=col,
                                                            ypos=row,
                                                            size_tuple=(16, 16)))
        del(self.seed_surfs['tomato'][-1])
                
    def use_tool(self):

        if not self.sleeper and self.keys[pygame.K_SPACE] and not self.timer.active and self.overlay.tool_or_seed == 'tool':
            self.timer.activate()
            self.start_tool = 1
            self.image = self.tool_anime_images[self.overlay.tools[self.overlay.tool_index]][self.dir_status][0]

        if self.start_tool == 1 and not self.timer.active:
            self.timer.activate()
            self.start_tool = 0
            self.image = self.tool_anime_images[self.overlay.tools[self.overlay.tool_index]][self.dir_status][1]
            if self.hit_point_a and self.overlay.tools[self.overlay.tool_index] == 'hoe':
                posx = self.hit_point_a.x
                posy = self.hit_point_a.y
                
                # as dirt is made where the player is already offset exists at that time for the player hence
                # we should add the offset in the initial position
                # and self.hit_point_b is the position on the screen itself, only having four values btw
                # hence making it more simple

                # removing grown plants
                # all seed stuff in seed_soil_group

                if (posx, posy) in self.hoed:
                    for seed in self.seed_soil_group:
                        if seed.loc_on_map == (posx, posy) and \
                            int(seed.seed_age) == len(self.seed_surfs[seed.seed_type]) - 1:
                            seed.kill()
                            inventory[seed.seed_type + '_seed'] += random.choice([0] + [1]*5 + [2]*2 + [3]*2)
                            inventory[seed.seed_type] += 1
                            for dirt in self.dirt_group:
                                if (posx, posy) == dirt.loc_on_map:
                                    dirt.seeded = 0


                if (posx, posy) in self.hoed:
                    return
                
                self.hoed.append((posx, posy))
                Generic(image_surf=self.dirt_surf.copy(),
                        sprite_type='dirt',
                        groups=[self.display_sprites, self.dirt_group, self.movement_group],
                        pos=(round((posx)*16-self.start_pos.x +SCREEN_WIDTH//2), round((posy)*16-self.start_pos.y + SCREEN_HEIGHT//2)),
                        zpos=level['dirt'],
                        loc_on_map=(posx, posy),
                        )
                
            elif self.hit_point_a and self.overlay.tools[self.overlay.tool_index] == 'water':
                ### WATERING ###
                for sprite in self.dirt_group:
                    if sprite.watered == 0 and sprite.rect.collidepoint(self.hit_point_b):
                        Generic(image_surf=self.water_surf,
                                sprite_type='water_soil',
                                groups=[self.display_sprites, self.water_soil_group],
                                pos=sprite.rect.topleft + self.display_sprites.offset, # as offset is already
                                zpos=level['water_soil']) # present when water is being poured
                        sprite.watered = 1
                        break

            elif self.overlay.tools[self.overlay.tool_index] == 'axe':
                for tree in self.apple_tree_group:
                    if tree.apples == 0 and tree.rect.collidepoint(self.hit_point_b):
                        tree.kill()                                                    # HERE
                        inventory['log'] += 1
                        a = Generic(
                            image_surf=self.cut_tree_surfs[tree.sprite_type],
                            sprite_type="cut_"+tree.sprite_type,
                            groups=[self.display_sprites, self.collide_sprites, self.cut_trees],
                            pos=tree.id+pygame.math.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2) - self.start_pos\
                                + pygame.math.Vector2(cut_tree_offset[tree.sprite_type]),
                            zpos=level["log"],
                            id=tree.id,
                            )
                        ...
                    elif tree.rect.collidepoint(self.hit_point_b):
                        for apple in self.apple_group:
                            if apple.id == tree.id:
                                apple.kill()
                                inventory['apple'] += 1
                                tree.apples -= 1   
                                break           


    def use_seed(self):
        
        if self.hit_point_a and inventory[self.overlay.seeds[self.overlay.seed_index] + '_seed'] and self.keys[pygame.K_SPACE] and not self.timer.active and self.overlay.tool_or_seed == 'seed':
            for sprite in self.dirt_group:
                if sprite.seeded == 0 and sprite.rect.collidepoint(self.hit_point_b):

                    Generic(image_surf=self.seed_surfs[self.overlay.seeds[self.overlay.seed_index]][0],
                            sprite_type='seed_soil',
                            groups=[self.display_sprites, self.seed_soil_group, self.movement_group],
                            pos=sprite.rect.topleft + self.display_sprites.offset + pygame.math.Vector2(0, -2),
                            zpos=level['small_seed'],
                            loc_on_map=(self.hit_point_a.x,self.hit_point_a.y)).seed_type = self.overlay.seeds[self.overlay.seed_index]
                    
                    inventory[self.overlay.seeds[self.overlay.seed_index] + '_seed'] -= 1
                    
                    sprite.seeded = 1
                    break

    def sleep(self):
        if self.access_hit_point and self.bed_sprite.rect.collidepoint(self.access_hit_point):
            self.sleeper = True
            if self.keys[pygame.K_SPACE] and not self.transition.active:
                self.transition.activate()
                self.display_sprites.colour_inc_or_dec *= 200
                self.sleep_dir = self.dir_status
        else:
            self.sleeper = False

        if self.transition.active:
            if self.display_sprites.trans_colour.x == MAX_COLOUR_SKY:
                self.display_sprites.colour_inc_or_dec /= 200
                self.transition.deactivate()

    def input(self):
        self.keys = pygame.key.get_pressed()

        if self.keys[pygame.K_s]: 
            self.direction.y = 1
            self.dir_status = "down"
            self.status = "move"
        elif self.keys[pygame.K_w]: 
            self.direction.y = -1
            self.dir_status = "up"
            self.status = "move"
        elif not self.keys[pygame.K_s] and not self.keys[pygame.K_w]: self.direction.y = 0
        
        if self.keys[pygame.K_d]: 
            self.direction.x = 1
            self.dir_status = "right"
            self.status = "move"
        elif self.keys[pygame.K_a]: 
            self.direction.x = -1
            self.dir_status = "left"
            self.status = "move"
        elif not self.keys[pygame.K_d] and not self.keys[pygame.K_a]: self.direction.x = 0

        if self.direction.magnitude() not in [0, 1]: 
            self.direction = self.direction.normalize()
            ...

        if self.direction.magnitude() == 0:
            self.status = "idle"

        ### DRAGON ###
        if self.access_hit_point and self.dragon.rect.collidepoint(self.access_hit_point):
            self.switch_off_tool_animation = True
            if self.keys[pygame.K_SPACE] and not self.dragon_timer.active:
                self.overlay.dragon_touch = True
                self.sleep_dir = self.dir_status
                self.dragon_timer.activate()
                self.dragon_dir = self.dir_status
            elif not self.dragon_timer.active:
                self.overlay.dragon_touch = False
                self.switch_off_tool_animation = False

        # sleeping
        if self.transition.active:
            self.direction = pygame.math.Vector2(0, 0)
            self.status = "idle"
            self.dir_status = self.sleep_dir

        # dragon
        if self.dragon_timer.active:
            self.direction = pygame.math.Vector2(0, 0)
            self.status = "idle"
            self.dir_status = self.dragon_dir

    def animation(self, dt):
        self.frame_index = self.frame_index + self.animation_speed*dt
        if self.frame_index >= len(self.anime_images[self.status][self.dir_status]):
            self.frame_index = 0
        self.image = self.anime_images[self.status][self.dir_status][int(self.frame_index)]

    def update(self, dt):

        # Timer update
        self.transition.update()
        self.dragon_timer.update()

        self.hit_point_a = pygame.math.Vector2((self.pos_in_display.x - self.pos_in_display.x%16)/16,\
                                              (self.pos_in_display.y - self.pos_in_display.y%16)/16)\
                                              + self.for_hit_point[self.dir_status]
        

        self.hit_point_b = pygame.math.Vector2(self.hit_box.center) + self.for_hit_point[self.dir_status]*10
        self.access_hit_point = pygame.math.Vector2(self.hit_box.center) + self.for_hit_point[self.dir_status]*10

        if self.not_farmable_matrix[int(self.hit_point_a.y)][int(self.hit_point_a.x)]:
            self.hit_point_a = None


        self.input()
        if not self.switch_off_tool_animation:
            self.use_tool()
            self.use_seed()
        super().update(dt)
        self.sleep()

        # debug
        # print(f"Water: {self.water_soil_group.__len__()}, Dirt: {self.dirt_group.__len__()}, Seed: {self.seed_soil_group}")