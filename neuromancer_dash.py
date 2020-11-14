import pygame
import time
import sys, getopt
from sseclient import SSEClient


class AssetPath:
    # No trailing slashes
    fonts = "./assets/fonts"


class Hardware:
    screen_width = 480
    screen_height = 320


class Color:
    yellow = "#ffff00"
    green = "#00dc00"
    dark_green = "#173828"
    red = "#dc0000"
    white = "#ffffff"
    grey_20 = "#333333"
    grey_75 = "#c0c0c0"
    black = "#000000"


class Font:
    @staticmethod
    def open_sans():
        return AssetPath.fonts + "/Open_Sans/OpenSans-Regular.ttf"


def print_usage():
    print("\nUsage: neuromancer_dash.py --server <ip or hostname:port>\n")


def get_command_args(argv):
    server_address = None
    try:
        opts, args = getopt.getopt(argv,"server:",["server="])

    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("--server"):
            server_address = arg

    if (None == server_address):
        print_usage()
        sys.exit()

    return server_address


def main(argv):
    server_address = get_command_args(argv)

    assert(None != server_address)

    print("Specified server: " + server_address)

    server_messages = SSEClient(server_address)

    pygame.init()
    pygame.mouse.set_visible(False)
    
    display_surface = pygame.display.set_mode(
        (Hardware.screen_width, Hardware.screen_height),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    display_surface.fill(Color.black)

    font_name, font_size = Font.open_sans(), 32
    font = pygame.font.SysFont(font_name, font_size)

    x = 0

    while True:

        for server_message in server_messages:
            print(server_message)

        time.sleep(1)
        display_surface.fill(Color.black)
        x += 5
        text_surface = font.render("{}".format(x), True, Color.yellow, None)
        display_surface.blit(text_surface, (20, 20))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
