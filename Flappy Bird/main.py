import pygame
import sys
import os
import random

pygame.init()

# constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 600
BIRD_HEIGHT = 60
BIRD_WIDTH = 60
TIME_BETWEEN_BARS = 4000
GAP_BETWEEN_BARS = 200 # Fixed for now

BAR_CENTER_Y_MIN = 180
BAR_CENTER_Y_MAX = 420

# score
score = 0

FONT1 = pygame.font.Font('Assets/Font/BungeeTint-Regular.ttf', 40)
FONT2 = pygame.font.Font('Assets/Font/BungeeTint-Regular.ttf', 70)
FONT3 = pygame.font.Font('Assets/Font/BungeeTint-Regular.ttf', 30)
FONT4 = pygame.font.Font('Assets/Font/BungeeTint-Regular.ttf', 55)

# clock
clock = pygame.time.Clock()

class Bird(pygame.sprite.Sprite):

    def __init__(self):
        self.gravity = 0
        self.space = 0

        # smoke image
        self.smoke_surf_list = []
        for index, file in enumerate(sorted(os.listdir('Assets/Image/White puff'))):
            self.smoke_surf_list.append(pygame.image.load('Assets/Image/White puff/' + file).convert_alpha())
            self.smoke_surf_list[index] = pygame.transform.scale(self.smoke_surf_list[index], (BIRD_WIDTH, BIRD_HEIGHT)).convert_alpha()

        super().__init__()
        # to change costumes
        self.time = 0
        self.image_surf_list = []

        for index, file in enumerate(sorted(os.listdir('Assets/Image/bird'))):
            self.image_surf_list.append(pygame.image.load('Assets/Image/bird/' + file).convert_alpha())
            self.image_surf_list[index] = pygame.transform.scale(self.image_surf_list[index], (BIRD_WIDTH, BIRD_HEIGHT)).convert_alpha()
            

        self.image = self.image_surf_list[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (70, SCREEN_HEIGHT/2)

    def update(self):
        # costume
        if self.time >= len(self.image_surf_list):
            self.time = 0
        self.image = self.image_surf_list[int(self.time)]
        self.mask = pygame.mask.from_surface(self.image)
        self.time += 0.25
        
        # movement
        self.movement()

    def movement(self):
        # movement
        if self.space:
            self.rect.centery += self.gravity

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        else:
            self.gravity += 1

        # space bar press
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self.space = 1
            # as every single time the image is taken from the list to initialise
            # self.image this works
            self.gravity = -7   

        # constraining top
        if self.rect.top <= 0:
            self.rect.top = 0
            self.gravity = 1

    def explode(self):
        if self.time >= len(self.smoke_surf_list):
            self.time = 0
            return False
        self.image = self.smoke_surf_list[int(self.time)]
        self.time += 0.15
        return True

class Up_bar(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        # center is a tuple containing the (x, y) coordinates of generation

        self.image = pygame.image.load('Assets/Image/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() + 5, SCREEN_HEIGHT*0.8))

        self.image = pygame.transform.rotozoom(self.image, 180, 1)
        self.rect = self.image.get_rect()

        self.rect.bottom = center[1] - GAP_BETWEEN_BARS//2
        self.rect.left = center[0]

    def update(self):
        self.rect.centerx -= 2

        if self.rect.right <= 0:
            self.kill()

class Down_bar(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.image.load('Assets/Image/pipe-green.png').convert_alpha()

        self.image = pygame.transform.scale(self.image, (self.image.get_width() + 5, SCREEN_HEIGHT*0.8))
        self.rect = self.image.get_rect()

        self.rect.top = center[1] + GAP_BETWEEN_BARS//2
        self.rect.left = center[0]

    def update(self):
        self.rect.centerx -= 2

        if self.rect.right <= 0:
            self.kill()

class Score_track(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        # down bar
        bar = pygame.image.load('Assets/Image/pipe-green.png').convert_alpha()
        self.image = pygame.Surface((bar.get_width() + 5, SCREEN_HEIGHT*0.8), flags=pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        self.rect = self.image.get_rect()

        self.rect.top = center[1] + GAP_BETWEEN_BARS//2
        self.rect.left = center[0]
    
    def update(self):
        self.rect.centerx -= 2

        if self.rect.right <= 0:
            self.kill()

class Button:

    def __init__(self, button_text, center = None):
        self.text_surf = FONT1.render(button_text, True, 'Red')
        self.text_rect = self.text_surf.get_rect()
        self.text_rect.left = 0 + 25
        self.text_rect.bottom = SCREEN_HEIGHT - 20
        if center:
            self.text_rect.center = center
        self.border = self.text_rect.scale_by(1.2, 1.2)
        self.border.center = self.text_rect.center

    def display(self):
        mouse = pygame.mouse.get_pos()

        if self.border.left <= mouse[0] <= self.border.right \
            and self.border.top <= mouse[1] <= self.border.bottom:
            pygame.draw.rect(screen, (31, 124, 16), self.border, border_radius=5)
            pygame.draw.rect(screen, (13, 161, 139), self.text_rect, border_radius=5)

            if pygame.mouse.get_pressed()[0]:
                return False
        else:
            pygame.draw.rect(screen, (33, 75, 143), self.border, border_radius=5)
            pygame.draw.rect(screen, (34, 107, 228), self.text_rect, border_radius=5)

        screen.blit(self.text_surf, self.text_rect)
        return True

# TEXTS
FONT1_surf = FONT1.render('FLEPPY BERD', True, 'Red')
FONT1_rect = FONT1_surf.get_rect()
FONT1_rect.right = SCREEN_WIDTH - 10
FONT1_rect.top = 0

FONT2_surf = FONT2.render('GAME OVER', True, 'Red')
FONT2_rect = FONT2_surf.get_rect()
FONT2_rect.center = (SCREEN_WIDTH//2, 80)

score_surf = FONT3.render(f'SCORE: {score}', True, 'Red')
score_rect = score_surf.get_rect()
score_rect.left = 10
score_rect.top = 0

score_final_surf = FONT4.render(f'SCORE: {score}', True, 'Red')
score_final_rect = score_final_surf.get_rect()
score_final_rect.center = (SCREEN_WIDTH//2, 160)


# main display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Fleppy Berd')
icon_surf = pygame.image.load('Assets/Image/icon.png').convert_alpha()
pygame.display.set_icon(icon_surf)

# Bird sprite
bird = Bird()
bird_group = pygame.sprite.GroupSingle(bird)

# Bar sprites
center = (SCREEN_WIDTH, random.randint(BAR_CENTER_Y_MIN, BAR_CENTER_Y_MAX))
up_bar = Up_bar(center)
down_bar = Down_bar(center)
bar_group = pygame.sprite.Group(up_bar, down_bar)

# Transparent score sprite
score_track = Score_track(center)
score_group = pygame.sprite.Group(score_track)

# intro image
intro_surf = pygame.image.load('Assets/Image/intro.jpg').convert()
intro_surf = pygame.transform.scale(intro_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
intro_rect = intro_surf.get_rect()

# game image
game_surf = pygame.image.load('Assets/Image/game.png').convert()
game_surf = pygame.transform.scale(game_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_rect = game_surf.get_rect()

# game over image
game_over_surf = pygame.image.load('Assets/Image/game_over.jpg').convert()
game_over_surf = pygame.transform.scale(game_over_surf, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_over_rect = game_over_surf.get_rect()

replay_button = Button("REPLAY", center=None)

# music
intro_music = pygame.mixer.Sound('Assets/Music/intro.wav')
game_music = pygame.mixer.Sound('Assets/Music/game.wav')
scream = pygame.mixer.Sound('Assets/Music/scream.wav')

intro_music.play(loops=-1)

# game states
(game_intro, game, game_over) = (1, 0, 0)

# buttons
start_button = Button('PLAY')

# timer for generating bars
bar_timer = pygame.USEREVENT + 1
pygame.time.set_timer(bar_timer, TIME_BETWEEN_BARS)

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game:
            if event.type == bar_timer:

                center = (SCREEN_WIDTH, random.randint(BAR_CENTER_Y_MIN, BAR_CENTER_Y_MAX))

                bar_group.add(Up_bar(center), Down_bar(center))
                score_group.add(Score_track(center))                     

    if game_intro:

        screen.blit(intro_surf, intro_rect)
        screen.blit(FONT1_surf, FONT1_rect)

        game_intro = start_button.display()
        if game_intro == False:
            intro_music.stop()
            game = True
            game_music.play(loops=-1)
        ...
    elif game: # game going on

        screen.blit(game_surf, game_rect)

        bar_group.draw(screen)
        bar_group.update()

        score_group.draw(screen)
        score_group.update()

        bird_group.draw(screen)
        bird_group.update()

        screen.blit(score_surf, score_rect)

        for sprite in score_group.sprites():
            if sprite.rect.right < bird_group.sprite.rect.left:
                sprite.kill()
                score += 1
                score_surf = FONT3.render(f'SCORE: {score}', True, 'Red')

        if pygame.sprite.spritecollide(bird_group.sprite, bar_group, False):
            screen.blit(game_surf, game_rect)
            bar_group.draw(screen)
            game = 0
            game_over = 1
            game_music.stop()
            scream.play()
            bird_group.sprite.time = 0
            while bird_group.sprite.explode():
                screen.blit(game_surf, game_rect)
                bar_group.draw(screen)
                bird_group.draw(screen)
                pygame.display.update()
                clock.tick(60)
            scream.stop()
            bar_group.empty()
            bird_group.empty()
            score_group.empty()
            bird_group.add(Bird())
    
    elif game_over:
        score_final_surf = FONT4.render(f'SCORE: {score}', True, 'Red')
        screen.blit(game_over_surf, game_over_rect)
        screen.blit(FONT2_surf, FONT2_rect)
        screen.blit(score_final_surf, score_final_rect)
        
        game_over = replay_button.display()
        if game_over == False:
            score = 0
            score_surf = FONT3.render(f'SCORE: {score}', True, 'Red')
            intro_music.stop()
            game = True
            game_music.play(loops=-1)

    pygame.display.update()
    clock.tick(60)
