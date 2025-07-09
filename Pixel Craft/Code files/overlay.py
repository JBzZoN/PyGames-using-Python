import pygame
from settings import *
from support import *
from random import randint

class Overlay():

    def __init__(self):
        super().__init__()
        # Font file
        self.retro = pygame.font.Font("../Font/retro.ttf", 20)
        
        # Timers used
        self.timer = Timer(300)
        ### TESTING ###
        self.screen = pygame.display.get_surface()
        

        # is overlay box being displayed
        self.box_is_displayed = False
        
        # help button
        self.help_surf = pygame.image.load("../Graphics/other_images/help.png").convert_alpha()
        self.help_surf = pygame.transform.scale_by(self.help_surf, 0.1).convert_alpha()
        self.help_rect = self.help_surf.get_rect(topright = (SCREEN_WIDTH - 20, 20))

        # help box
        self.help_box_surf = pygame.image.load("../Graphics/other_images/help_box.png").convert_alpha()
        self.help_box_surf = pygame.transform.scale_by(self.help_box_surf, 0.9).convert_alpha()
        self.help_box_rect = self.help_box_surf.get_rect()
        self.help_box_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

        # bag button
        self.bag_surf = pygame.image.load("../Graphics/other_images/bag.png").convert_alpha()
        self.bag_surf = pygame.transform.scale_by(self.bag_surf, 0.2).convert_alpha()
        self.bag_rect = self.bag_surf.get_rect(bottomleft = (15, SCREEN_HEIGHT - 20))

        # tools
        self.tool_index = 0
        self.tool_surfaces = list_of_image_surfaces_in_folder('../Graphics/tools/')

        self.tool_surf = self.tool_surfaces[0]
        self.tool_surf = pygame.transform.scale_by(self.tool_surf, 1).convert_alpha()
        self.tool_rect = self.bag_surf.get_rect(center = (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50))

        # seeds
        self.seed_index = 0
        self.seed_surfaces = list_of_image_surfaces_in_folder('../Graphics/seeds/')

        self.seed_surf = self.seed_surfaces[0]
        self.seed_surf = pygame.transform.scale_by(self.seed_surf, 1).convert_alpha()
        self.seed_rect = self.bag_surf.get_rect(center = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))

        # inventory
        self.inventory_surf = pygame.image.load("../Graphics/other_images/inventory.png").convert_alpha()
        self.inventory_surf = pygame.transform.scale_by(self.inventory_surf, 0.9).convert_alpha()
        self.inventory_rect = self.inventory_surf.get_rect()
        self.inventory_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

        # tools and seeds
        self.tools = ['axe', 'hoe', 'water']
        self.seeds = ['corn', 'tomato']
        self.tool_or_seed = 'tool'

        # dragon text
        self.dragon_touch = False

        self.dragon_text_surf = pygame.image.load("../Graphics/other_images/dragon_text.png")
        self.dragon_text_rect = self.dragon_text_surf.get_rect()
        self.dragon_text_rect.centerx = SCREEN_WIDTH//2
        self.dragon_text_rect.bottom = SCREEN_HEIGHT - 10

    def draw(self):

        self.screen.blit(self.help_surf, self.help_rect)
        self.screen.blit(self.bag_surf, self.bag_rect)
        
        if self.tool_or_seed == "tool":
            self.screen.blit(self.seed_surf, self.seed_rect)
            self.screen.blit(pygame.transform.scale_by(self.tool_surf, 1.2), self.tool_rect)
        else:
            self.screen.blit(pygame.transform.scale_by(self.seed_surf, 1.3), self.seed_rect)
            self.screen.blit(self.tool_surf, self.tool_rect)

        if self.dragon_touch:
            self.draw_dragon_text()

    def draw_dragon_text(self):
        self.screen.blit(self.dragon_text_surf, self.dragon_text_rect)

    def update(self):
        self.tool_surf = self.tool_surfaces[self.tool_index]
        self.seed_surf = self.seed_surfaces[self.seed_index]
        
        # Timers
        self.timer.update()

        # user input like bag, help, tool-seed operation
        self.input()

    def input(self):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # press mouse on help
        if self.help_rect.left < mouse_pos[0] < self.help_rect.right and self.help_rect.top < mouse_pos[1] < self.help_rect.bottom:
            if pygame.mouse.get_pressed()[0]:
                self.screen.blit(self.help_box_surf, self.help_box_rect)
                self.box_is_displayed = True
            else:
                self.box_is_displayed = False

        # press mouse on bag
        if self.bag_rect.left < mouse_pos[0] < self.bag_rect.right and self.bag_rect.top < mouse_pos[1] < self.bag_rect.bottom:
            if pygame.mouse.get_pressed()[0]:
                self.screen.blit(self.inventory_surf, self.inventory_rect)
                self.box_is_displayed = True

                # From 112, increment 52 loop 6 times, SCREEN_WIDTH//2 + 10

                for i in range(len(inventory)):
                    temp = self.retro.render(str(inventory[inventory_order[i]]), True, (219,60,76))
                    self.screen.blit(temp, (SCREEN_WIDTH//2 + 10, 112 + i*52))
                
            else:
                self.box_is_displayed = False
                
        # press q to switch between seed and tool
        if keys[pygame.K_q] and not self.timer.active:
            self.timer.activate()
            if self.tool_or_seed == 'seed':
                self.tool_or_seed = 'tool'
            else:
                self.tool_or_seed = 'seed'

        # press shift to switch between seeds or tools
        if keys[pygame.K_LSHIFT] and not self.timer.active and self.tool_or_seed == 'tool':
            self.timer.activate()
            self.tool_index += 1
            if self.tool_index >= len(self.tools):
                self.tool_index = 0

        if keys[pygame.K_LSHIFT] and not self.timer.active and self.tool_or_seed == 'seed':
            self.timer.activate()
            self.seed_index += 1
            if self.seed_index >= len(self.seeds):
                self.seed_index = 0    

class Rain:
    def __init__(self, player):
        # timers
        self.rain_timer = Timer(randint(500, 3000))

        # player
        self.player = player

        self.screen = pygame.display.get_surface()
        
        self.rainx = randint(-500, SCREEN_WIDTH + 500)
        self.rainy = randint(-500, SCREEN_HEIGHT + 500)

        self.speed = 50

    def update(self, dt, zoom):
        if not self.rain_timer.active:
            self.rainx = randint(-500, SCREEN_WIDTH + 500)
            self.rainy = randint(-500, SCREEN_HEIGHT + 500)
            self.rain_timer.activate()

        pygame.draw.line(self.screen, (25, 25, 112), (round(self.rainx), round(self.rainy)), (round(self.rainx) - 3, round(self.rainy) + 9), 1)
        self.rainx -= dt*self.speed
        self.rainy += dt*self.speed*3

        if self.player.status != "idle" and not self.player.timer.active:
            self.rainx -= dt*self.player.speed*self.player.direction[0]*zoom
            self.rainy -= dt*self.player.speed*self.player.direction[1]*zoom

        self.rain_timer.update()

class Rain_spots: # use ellipse stuff, change size during timer, when ends change
    def __init__(self, player):
        # timers
        self.rain_timer = Timer(randint(500, 1500))

        # player
        self.player = player

        self.screen = pygame.display.get_surface()
        
        self.rainx = randint(-500, SCREEN_WIDTH + 500)
        self.rainy = randint(-500, SCREEN_HEIGHT + 500)

        self.rain_rect = pygame.rect.Rect(self.rainx, self.rainy, 2, 2)
        self.center = self.rain_rect.center
        self.speed = 5

        self.size = 2

    def update(self, dt, zoom):
        if not self.rain_timer.active:
            self.rainx = randint(-500, SCREEN_WIDTH + 500)
            self.rainy = randint(-500, SCREEN_HEIGHT + 500)
            self.rain_rect = pygame.rect.Rect(self.rainx, self.rainy, 1, 1)
            self.center = list(self.rain_rect.center)
            self.size = 2
            self.rain_timer.activate()

        pygame.draw.ellipse(self.screen, (25, 25, 112), self.rain_rect, 1)
        self.size += self.speed*dt

        self.rain_rect.width = round(self.size)
        self.rain_rect.height = round(self.size)
        self.rain_rect.center = list(self.center)

        if self.player.status != "idle" and not self.player.timer.active:
            self.center[0] -= dt*self.player.speed*self.player.direction[0]*zoom
            self.center[1] -= dt*self.player.speed*self.player.direction[1]*zoom

        self.rain_timer.update()