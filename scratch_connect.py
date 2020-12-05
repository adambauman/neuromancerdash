#
# disk_visualizer_scratch - messing around with a new disk activity visualizer
# ============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import os
import pygame
import sys, getopt
#import random
#import requests
from collections import deque
import threading

# Simple check for RPi GPIO, will disable any stuff that requires GPIO access so you can
# debug and develop on other platforms.
g_gpio_available = True
#try:
#    import RPi.GPIO as GPIO
#    print("RPi GPIO Available")
#except:
#    g_gpio_available = False
#    print("RPi GPIO Not Available")
#
if g_gpio_available:
    from data.dht22 import DHT22, DHT22Data

from data.aida64lcdsse import AIDA64LCDSSE

from elements.styles import FontPaths, Color
from dashpages import DashPage1Painter
from elements.styles import Color, AssetPath, FontPaths
#from utilities.screensaver import MatrixScreensaver


class Hardware:
    screen_width = 480
    screen_height = 320

def print_usage():
    print("")
    print("Usage: neuromancer_dash.py <options>")
    print("Example: python3 neuromancer_dash.py --aidasse http://localhost:8080/sse")
    print("")
    print("       Required Options:")
    print("           --aidasse <full http address:port to AIDA64 LCD SSE stream>")

def get_command_args(argv):
    aida_sse_server = None
    gpio_enabled = True

    try:
        opts, args = getopt.getopt(argv,"aidasse:",["aidasse=", ])

    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("--aidasse"):
            aida_sse_server = arg

    if (None == aida_sse_server):
        print_usage()
        sys.exit()

    return aida_sse_server

def main(argv):
    aida_sse_server = get_command_args(argv)
    assert(None != aida_sse_server)

    if __debug__:
        print("Passed arguments:")
        print("    aidasse = {}".format(aida_sse_server))

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

    data_queue_maxlen = 1

    # Start the AIDA64 data thread, fastest update interval is usually ~100ms and can be
    # adjusted in the AIDA64 preferences.
    aida64_deque = deque([], maxlen=data_queue_maxlen)
    aida64_data_thread = threading.Thread(target=AIDA64LCDSSE.threadable_stream_read, args=(aida64_deque, aida_sse_server))
    aida64_data_thread.setDaemon(True)
    aida64_data_thread.start()

    # Start DHT22 thread if GPIO is available. Reading this data can take awhile, don't expect
    # updates to occur under 3-5 seconds.
    dht22_deque = None
    dht22_last_data = None
    if g_gpio_available:
        dht22_deque = deque([], maxlen=data_queue_maxlen)
        dht22_data_thread = threading.Thread(target=DHT22.threadable_read_retry, args=(dht22_deque,))
        dht22_data_thread.setDaemon(True)
        dht22_data_thread.start()

    dash_page_1_painter = DashPage1Painter(display_surface)

    # Main loop, this will juggle data and painting the dash page(s)
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
                # TODO: (Adam) 2020-12-02 Properly close out threads and active connections
        pygame.event.clear()

        if data_queue_maxlen > len(aida64_deque):
            # We can't safely access data if the data queue isn't deep enough. Add a tiny delay
            # while we wait to stop system resources from getting thrashed.
            # TODO: (Adam) 2020-12-02 Jump into wait-for-reconnect mode with screen saver if we lost
            #           the data feed for more than a few seconds.
            #time.sleep(0.050)
            pygame.time.wait(50)
            continue

        # Paint the updated dashboard page and flip the display. DHT22 data will not be available if
        # the system running the script doesn't have RPi.GPIO support.
        if None == dht22_deque:
            dash_page_1_painter.paint(aida64_deque.popleft(), None)
        else:
            if data_queue_maxlen <= len(dht22_deque):
                dht22_data = dht22_deque.popleft()
                dht22_last_data = dht22_data
                print("New dht22_data. H: {:0.1f} T: {:0.1f}".format(dht22_data.humidity, dht22_data.temperature))
            else:
                dht22_data = dht22_last_data

            dash_page_1_painter.paint(aida64_deque.popleft(), dht22_data)

        pygame.display.flip()


if __name__ == "__main__":
    main(sys.argv[1:])
