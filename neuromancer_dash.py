#!/usr/bin/env python

import pygame
import sys, getopt

if __debug__:
    import traceback

from aida64_sse_data import AIDA64SSEData
from dashboard_painter import DashPainter

class Hardware:
    screen_width = 480
    screen_height = 320

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


def start_dashboard(server_address, display_surface):
    assert(0 != len(server_address))

    # Start connection to the AIDA64 SSE data stream
    server_messages = AIDA64SSEData.connect(server_address)

    dash_painter = DashPainter(display_surface)

    # This is a generator loop, it will keep going as long as the AIDA64 stream is open
    # NOTE: (Adam) 2020-11-14 Stream data is sometimes out of sync with the generated loop,
    #       just skip and try again on the next go-around
    for server_message in server_messages:
        if 0 == len(server_message.data) or None == server_message.data:
            continue

        parsed_data = AIDA64SSEData.parse_data(server_message.data)
        assert(0 != len(parsed_data))
        
        dash_painter.paint(parsed_data)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
        pygame.event.clear()


def start_reconnect_screensaver(server_address, display_surface):
    assert(0 != len(server_address))
    assert(None != display_surface)

    #font_name, font_size = Font.open_sans(), 32
    #font = pygame.font.SysFont(font_name, font_size)

    #seconds_remaining = 10
    #while 0 < seconds_remaining:
    #    display_surface.fill(Color.black)
    #    text_surface = font.render("Connection timeout, retry in {} seconds...".format(seconds_remaining), True, Color.grey_75, None)
    #    display_surface.blit(text_surface, (0, 0))
    #    pygame.display.flip()
    #    seconds_remaining -= 1
    #    pygame.time.wait(1000)

def main(argv):
    server_address = get_command_args(argv)
    assert(None != server_address)

    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.event.set_allowed([pygame.QUIT])
    
    display_surface = pygame.display.set_mode(
        (Hardware.screen_width, Hardware.screen_height),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    while True:
        # Dashboard will fail if the computer sleeps or is otherwise unavailable, keep
        # retrying until it starts to respond again.
        #try:
        start_dashboard(server_address, display_surface)
        #except Exception:
            #if __debug__:
                #traceback.print_exc()
            
            # TODO: (Adam) 2020-11-15 thread matrix screen saver during reconnect attempts
            #start_reconnect_screensaver(server_address, display_surface)


    pygame.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
