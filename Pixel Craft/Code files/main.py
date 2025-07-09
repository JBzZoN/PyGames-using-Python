import pygame
from support import Timer

# cd "Python/Pygame/Pixelcraft/Code files"
pygame.init()
from settings import *
import sys
from level import Level

# main screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA).convert()

# icon and name of the display
pygame.display.set_caption("Pixelcraft")
icon_surf = pygame.image.load("../Graphics/other_images/icon.png")
pygame.display.set_icon(icon_surf)

# initialising class level
level = Level()

# zoom
zoom = 1.5
scroll_speed = 10

# timer and clocks
timer = Timer(100)
clock = pygame.time.Clock()

while True:
    # delta time
    dt = clock.tick() / 1000
    level.run(dt, zoom)
    timer.update()

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEWHEEL and not timer.active:
            timer.activate()
            if event.y > 0:
                zoom = zoom + 0.5
            elif event.y < 0:
                zoom = zoom - 0.5

            if zoom > ZOOM_MAX:
                zoom = ZOOM_MAX
            elif zoom < ZOOM_MIN:
                zoom = ZOOM_MIN

    # for everything to appear on screen
    pygame.display.update()