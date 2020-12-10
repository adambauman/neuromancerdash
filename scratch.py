
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
    display_surface.fill(Color.cyan_dark)


    # Setup our stuff
    #working_surface = pygame.Surface((Hardware.screen_width, Hardware.screen_height), pygame.SRCALPHA)
    display_surface.set_alpha(255)
    working_surface = display_surface.subsurface(50, 50, 200, 200)
    working_surface.fill((0,0,255,100))
    test_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 14)
    test_font.kerning = True
        
    origin = (20, 20)
    value_field_rect = pygame.Rect(origin[0], origin[1], 100, test_font.get_sized_height())
    print("value_field_rect; {}".format(value_field_rect))
    test_subsurface = working_surface.subsurface(value_field_rect)
    
    display_flags = display_surface.get_flags()
    working_flags = working_surface.get_flags()
    testsubsurface_flags = test_subsurface.get_flags()

    # Count down from number, should clear pixels and not have overlap
    for value in range(110, 0, -1):
        #test_pxarray = pygame.PixelArray(test_subsurface)
        ##print("shape0: {}    shape1: {}".format(test_pxarray.shape[0], test_pxarray.shape[1]))
        #for array_x in range(0, test_pxarray.shape[0]):
        #    for array_y in range(0, test_pxarray.shape[1]):
        #        #print("x: {}, y: {}".format(array_x, array_y))
        #        test_pxarray[array_x, array_y] = (0,0,0,0)
        #test_pxarray.close()

        test_subsurface.fill((0,0,0,0))

        print("value: {}".format(value))
        test_font.render_to(test_subsurface, (0,0), "Test: {}".format(value), Color.white)
        #test_font.render_to(working_surface, origin, "Test: {}".format(value), Color.white)
        
        #display_surface.blit(working_surface, (0,0))
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
