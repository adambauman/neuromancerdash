#
# neuromancer_dash - main script that starts and controls the dashboard display
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame
import sys, getopt
import threading
import random
import requests

if __debug__:
    import traceback

from data.aida64lcdsse import AIDA64LCDSSE
from elements.styles import FontPaths, Color
from dash_pages import DashPage1Painter
from utilities.screensaver import MatrixScreensaver

# Global that will be used to signal the reconnect screensaver that it's time to stop.
g_host_available = False

class Hardware:
    screen_width = 480
    screen_height = 320

def print_usage():
    print("")
    print("Usage: neuromancer_dash.py <options>")
    print("Example: python3 neuromancer_dash.py --aidasse http://localhost:8080/sse --gpioenabled")
    print("")
    print("       Required Options:")
    print("           --aidasse <full http address:port to AIDA64 LCD SSE stream>")
    print("")
    print("       Optional Options:")
    print("           --gpioenabled (specifying will enable features that require GPIO pins)")

def get_command_args(argv):
    aida_sse_server = None
    gpio_enabled = False

    try:
        opts, args = getopt.getopt(argv,"aidasse:gpioenabled",["aidasse=", "gpioenabled"])

    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("--aidasse"):
            aida_sse_server = arg
        elif opt in ("--gpioenabled"):
            gpio_enabled = True

    if (None == aida_sse_server):
        print_usage()
        sys.exit()

    return aida_sse_server, gpio_enabled


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

        parsed_data = AIDA64LCDSSE.parse_data(server_message.data)
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


# TODO: (Adam) 2020-11-22 Try to move away from using a global to control execution
def test_server_connection(server_address):
    assert(0 != len(server_address))

    while True:
        try:
            if __debug__:
                print("Attempting to reach host...")

            response = requests.get("http://192.168.1.202:8080", timeout=1.0)

            if __debug__:
                print("Received response: {}".format(response.status_code))

            # Request didn't throw, if status is HTTP 200 the host is ready.
            if 200 == response.status_code:
                global g_host_available
                g_host_available = True
                return
        except:
            if __debug__:
                traceback.print_exc()
                print("Connect test exception, connection failed")

        if __debug__:
            print("3 seconds before next attempt...")

        pygame.time.wait(3000)


def main(argv):
    aida_sse_server, gpio_enabled = get_command_args(argv)
    assert(None != aida_sse_server and None != gpio_enabled)

    if __debug__:
        print("Passed arguments:")
        print("    aidasse = {}".format(aida_sse_server))
        print("    gpioenabled = {}".format(gpio_enabled))

    pygame.init()
    pygame.mixer.quit()
    pygame.mouse.set_visible(False)
    pygame.event.set_allowed([pygame.QUIT])

    display_surface = pygame.display.set_mode(
        (Hardware.screen_width, Hardware.screen_height),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    display_surface.fill(Color.black)
    font_message = pygame.freetype.Font(FontPaths.fira_code_semibold(), 16)
    font_message.kerning = True
    font_message.render_to(display_surface, (10, 10), "Building display and connecting...", Color.white)
    pygame.display.flip()

    dash_page_1_painter = DashPage1Painter(display_surface)

    retry_count = 0
    while True:
        # Dashboard will fail if the computer sleeps or is otherwise unavailable, keep
        # retrying until it starts to respond again.
        try:
            # Start connection to the AIDA64 SSE data stream
            server_messages = AIDA64LCDSSE.connect(aida_sse_server)
            start_dashboard(server_messages, display_surface, dash_page_1_painter)
        except Exception:
            if __debug__:
                print("Exception in neuromancer_dash.py")
                traceback.print_exc()

        # NOTE: (Adam) 2020-11-24 Attempt a couple quick reconnects in case it's just a packet or two
        #           falling behind (happens a bit if connecting wirelessly)
        if __debug__:
            print("Exception during server_message() or start_dashboard(), retry #{}".format(retry_count))

        if 3 > retry_count:
            retry_count += 1
            pygame.time.wait(100)
            continue

        # Reset retry_count and screensaver aborting global then move to screensaver mode
        retry_count = 0
        global g_host_available
        g_host_available = False

        # NOTE: (Adam) 2020-11-22 Originally had the screensaver running in a new thread while
        #           the main thread tested the connection. Had to abandon that because the
        #           underlying bits of pygame on the Pi didn't like sharing display surfaces
        #           between threads.
        if __debug__:
            print("General failure, starting connection test thread and screensaver...")

        connection_test_thread = threading.Thread(target=test_server_connection, args=(aida_sse_server,))
        connection_test_thread.start()
        MatrixScreensaver.start(stop_requested = lambda : g_host_available)

        if __debug__:
            print("Screensaver aborted, joining thread")
        #screensaver.start() # Will loop internally until the connection test thread signals
        connection_test_thread.join()

        if __debug__:
            print("Connection test thread joined, processing events and continuing")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
        pygame.event.clear()


    pygame.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
