
import os, sys
import pygame, pygame.freetype
from elements.styles import Color, AssetPath, FontPaths

class Hardware:
    screen_width = 480
    screen_height = 320


def main():
    pygame.init()
    pygame.mixer.quit()
    pygame.mouse.set_visible(False)
    pygame.event.set_allowed([pygame.QUIT])

    display_surface = pygame.display.set_mode(
        (Hardware.screen_width, Hardware.screen_height),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )
    display_surface.fill(Color.red)


    # This will be the base serface that's flipped every update
    working_surface = pygame.Surface((Hardware.screen_width, Hardware.screen_height), pygame.SRCALPHA)
    working_surface.fill(Color.cyan_dark)

    test_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 14)
    test_font.kerning = True

    ambient_rect = pygame.Rect(50, 50, 100, 100)
    ambient_surface = working_surface.subsurface(ambient_rect)

    working_origin = (0, 0)
    test_font.render_to(ambient_surface, working_origin, "Temp", Color.white)

    working_origin = (0, working_origin[1] + test_font.get_sized_height())
    value_rect = pygame.Rect(working_origin[0], working_origin[1], ambient_surface.get_width(), test_font.get_sized_height())
    print("value_rect: {}".format(value_rect))
    value_surface = ambient_surface.subsurface(value_rect)
    value_original_bg = value_surface.get_abs_parent().copy()

    # Count down from number, should clear pixels and not have overlap
    for value in range(110, 0, -1):
        value_surface.blit(value_original_bg, (0, 0))

        print("value: {}".format(value))
        test_font.render_to(value_surface, (0,0), "{} F".format(value), Color.yellow)
        
        display_surface.blit(working_surface, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
                # TODO: (Adam) 2020-12-02 Properly close out threads and active connections
        pygame.event.clear()

        pygame.time.wait(500)

    pygame.quit()

if __name__ == "__main__":
    main()
