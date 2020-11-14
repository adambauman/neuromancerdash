#!/usr/bin/env python

import pygame
import time
import sys, getopt

from aida64_sse_data import AIDA64SSEData


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

# TODO: (Adam) 2020-11-14 This is a bit of mess, could use something like Pint for slick unit handling
class Unit:
    name = ""
    symbol = ""
    def __init__(self, name = "", symbol = ""):
        self.name = name
        self.symbol = symbol

class Units:
    null_unit = Unit()
    celsius = Unit("Celcius", "C")
    percent = Unit("Percent", "%")

class AIDAField:
    field_name = ""
    description = ""
    unit = Units.null_unit
    def __init__(self, field_name = "", description = "", unit = Units.null_unit):
        self.field_name = field_name
        self.description = description
        self.unit = unit

class DashData:
    cpu_temp = AIDAField("cpu_temp", "CPU Temperature", Units.celsius)
    cpu_util = AIDAField("cpu_util", "CPU Utilization", Units.percent)


def print_usage():
    print("\nUsage: neuromancer_dash.py --server <full http address to sse stream>\n")

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

    pygame.init()
    pygame.mouse.set_visible(False)
    
    display_surface = pygame.display.set_mode(
        (Hardware.screen_width, Hardware.screen_height),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    display_surface.fill(Color.black)

    font_name, font_size = Font.open_sans(), 32
    font = pygame.font.SysFont(font_name, font_size)

    # Start connection to the AIDA64 SSE data stream
    server_messages = AIDA64SSEData.connect(server_address)

    # This is a generator loop, it will keep going as long as the AIDA64 stream is open
    # NOTE: (Adam) 2020-11-14 Stream data is sometimes out of sync with the generated loop,
    #       just skip and try again on the next go-around
    for server_message in server_messages:
        if 0 == len(server_message.data) or None == server_message.data:
            continue

        parsed_data = AIDA64SSEData.parse_data(server_message.data)
        assert(0 != len(parsed_data))

        display_surface.fill(Color.black)
        
        text_surface = font.render(
            DashData.cpu_temp.description + ": {}".format(parsed_data[DashData.cpu_temp.field_name]) + DashData.cpu_temp.unit.symbol, 
            True, Color.yellow, None
        )
        display_surface.blit(text_surface, (10, 10))

        text_surface = font.render(
            DashData.cpu_util.description + ": {}".format(parsed_data[DashData.cpu_util.field_name]) + DashData.cpu_util.unit.symbol,
            True, Color.yellow, None
        )
        display_surface.blit(text_surface, (10, 40))

        pygame.display.flip()


    pygame.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
