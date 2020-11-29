#!/usr/bin/env python

from time import sleep
import sys

import pygame

from dashboard_painter import Color

def main(argv):

    # TODO: Process command arguments. ;)

    ### SETUP
    ###

    grid_background_color = "#000000"
    grid_width = 400
    grid_height = 200
    grid_spacing = 8
    grid_line_width = 1
    grid_color = Color.cyan_dark 

    ###
    ###

    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.event.set_allowed([pygame.QUIT])
    
    display_surface = pygame.display.set_mode(
        (grid_width, grid_height),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    display_surface.fill(grid_background_color)

    current_width = grid_spacing # Start with spacing if you don't want borders
    while grid_width >= current_width:
        pygame.draw.line(display_surface, grid_color, (current_width, 0), (current_width, grid_height), grid_line_width)
        current_width += grid_spacing

    current_height = grid_spacing # Start with spacing if you don't want borders
    while grid_height >= current_height:
        pygame.draw.line(display_surface, grid_color, (0, current_height), (grid_width, current_height), grid_line_width)
        current_height += grid_spacing
    
    pygame.display.flip()
    pygame.image.save(display_surface, "./pygrid.png")
    print ("File saved to ./pygrid.png")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()

        pygame.event.clear()

        sleep(0.200)

    pygame.quit()


if __name__ == "__main__":
    main(sys.argv[1:])
