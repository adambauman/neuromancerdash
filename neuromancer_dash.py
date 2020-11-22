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


def start_dashboard(server_messages, display_surface, dash_page_1_painter):

    # This is a generator loop, it will keep going as long as the AIDA64 stream is open
    # NOTE: (Adam) 2020-11-14 Stream data is sometimes out of sync with the generated loop,
    #       just skip and try again on the next go-around
    for server_message in server_messages:
        if 0 == len(server_message.data) or None == server_message.data:
            continue

        # NOTE: (Adam) 2020-11-22 The very first connection to AIDA64's LCD module seems to always
        #           return this "ReLoad" message. The next message will be the start of the stream.
        if "reload" == server_message.data.lower():
            if __debug__:
                print("Encountered reload message")
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

    reconnect_attempt_count = 0
    reconnect_attempts_until_screensaver = 1
    screensaver_running = False
    request_screensaver_stop = False
    screensaver = threading.Thread(target=MatrixScreenSaver, args=(display_surface, "", lambda:request_screensaver_stop)) 
    
    while True:
        # Dashboard will fail if the computer sleeps or is otherwise unavailable, keep
        # retrying until it starts to respond again.
        try:
            # Start connection to the AIDA64 SSE data stream
            server_messages = AIDA64SSEData.connect(server_address)
            if screensaver_running:
                reconnect_attempt_count = 0
                request_screensaver_stop = True
                screensaver.join()
                screensaver_running = False

            start_dashboard(server_messages, display_surface, dash_page_1_painter)
        except Exception:
            if __debug__:
                traceback.print_exc()
                print("Reconnect attempt #{}...".format(reconnect_attempt_count))

        if reconnect_attempts_until_screensaver <= reconnect_attempt_count and False == screensaver_running:
            screensaver.start()
            screensaver_running = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
        pygame.event.clear()

        reconnect_attempt_count += 1

        # Take it easy with the retry when the screen saver is active, host machine is offline or sleeping,
        # otherwise use a short delay to avoid hammering network requests.
        if screensaver_running:
            pygame.time.wait(2000)
        else:
            if __debug__:
                print("Short retry timeout")
            pygame.time.wait(50)


    pygame.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
