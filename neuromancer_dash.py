#!/usr/bin/env python

import pygame
import sys, getopt
import threading

if __debug__:
    import traceback

from aida64_sse_data import AIDA64SSEData
from dashboard_painter import DashPage1Painter, FontPaths, Color
from reconnect_screensaver import MatrixScreenSaver

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


def start_dashboard(server_address, display_surface, dash_page_1_painter):
    assert(0 != len(server_address))

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
        
        dash_page_1_painter.paint(parsed_data)
        pygame.display.flip()
        
        # TODO: (Adam) 2020-11-17 Refactor so we can tween gauge contents while waiting for data
        #           updates. Current model is pretty choppy looking.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
        pygame.event.clear()


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

    display_surface.fill(Color.black)
    dash_page_1_painter = DashPage1Painter(display_surface)

    retry_attempt_count = 0
    retry_attempts_until_screensaver = 1
    screensaver_started = False
    request_stop = False
    screensaver_process = threading.Thread(target=MatrixScreenSaver, args=(display_surface, lambda:request_stop)) 
    
    while True:
        # Dashboard will fail if the computer sleeps or is otherwise unavailable, keep
        # retrying until it starts to respond again.
        try:
            start_dashboard(server_address, display_surface, dash_page_1_painter)
        except Exception:
            print("retry_attempt_count: {}".format(retry_attempt_count))
            #if __debug__:
                #traceback.print_exc()


        if retry_attempts_until_screensaver < retry_attempt_count and False == screensaver_started:
            screensaver_process.start()
            screensaver_started = True

        if 4 < retry_attempt_count:
            print("Requesting stop...")
            request_stop = True
            screensaver_process.join()

        retry_attempt_count += 1
        pygame.time.wait(2000)


    pygame.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
