#
# disk_visualizer_scratch - messing around with a new disk activity visualizer
# ============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import os
import pygame
import sys, getopt
from collections import deque
import threading

from utilities.screensaver import MatrixScreensaver

# Set true to benchmark various parts of the update process
g_benchmark = False

# Simple check for RPi GPIO, will disable any stuff that requires GPIO access so you can
# debug and develop on other platforms.
if __debug__:
    g_dht22_enabled = False
    g_gpio_button_enabled = False
else:
    g_dht22_enabled = True
    g_gpio_button_enabled = False

if g_dht22_enabled:
    from data.dht22 import DHT22, DHT22Data

if g_gpio_button_enabled:
    import RPi.GPIO as GPIO

from data.aida64lcdsse import AIDA64LCDSSE

from elements.styles import FontPaths, Color
from pages.systemstats import SystemStats
from pages.cooling import Cooling
from elements.styles import Color, AssetPath, FontPaths

if __debug__:
    class DHT22Data:
        humidity = None
        temperature = None

        def __init__(self, humidity=0.0, temperature=0.0):
            self.humidity = humidity
            self.temperature = temperature


class Hardware:
    screen_width = 480
    screen_height = 320
    gpio_button = 15

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

    if g_gpio_button_enabled:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(Hardware.gpio_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pygame.init()
    pygame.mixer.quit()
    pygame.mouse.set_visible(False)
    #pygame.event.set_allowed([pygame.QUIT])

    if __debug__:
        surface_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    else:
        surface_flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN

    display_surface = pygame.display.set_mode((Hardware.screen_width, Hardware.screen_height), surface_flags)

    if __debug__:
        display_info = pygame.display.Info()
        print("pygame started display started. driver: {}, display_info: \n{}".format(pygame.display.get_driver(), display_info))

    display_surface.fill(Color.black)
    font_message = pygame.freetype.Font(FontPaths.fira_code_semibold(), 16)
    font_message.kerning = True
    font_message.render_to(display_surface, (10, 10), "Building elements and connecting...", Color.white)
    pygame.display.flip()


    ########
    # Data Gathering
    ########
    # Start the AIDA64 data thread, fastest update interval is usually ~100ms and can be
    # adjusted in the AIDA64 preferences.
    data_queue_maxlen = 1
    aida64_deque = deque([], maxlen=data_queue_maxlen)
    aida64_data_thread = threading.Thread(target=AIDA64LCDSSE.threadable_stream_read, args=(aida64_deque, aida_sse_server))
    aida64_data_thread.setDaemon(True)
    aida64_data_thread.start()

    # Start DHT22 thread if GPIO is available. Reading this data can take awhile, don't expect
    # updates to occur under 3-5 seconds.
    dht22_deque = None
    dht22_data = None
    dht22_last_data = None
    if g_dht22_enabled:
        dht22_deque = deque([], maxlen=data_queue_maxlen)
        dht22_data_thread = threading.Thread(target=DHT22.threadable_read_retry, args=(dht22_deque,))
        dht22_data_thread.setDaemon(True)
        dht22_data_thread.start()


    ########
    # Dash Page Setup
    ########
    # Prepare dash page(s)
    base_size = (display_surface.get_width(), display_surface.get_height())
    base_rect = pygame.Rect(0, 0, display_surface.get_width(), display_surface.get_height())
    available_pages = []
    available_pages.append(SystemStats(base_size, direct_surface=display_surface, direct_rect=base_rect))
    available_pages.append(Cooling(base_size, direct_surface=display_surface, direct_rect=base_rect))

    # Track selected page and copies of previously displayed pages
    current_page = 0
    requested_page = current_page

    ########
    # Main loop, this will juggle data and painting the dash page(s)
    ########
    ticks_since_last_data = 0
    data_retry_delay = 50
    retry_ticks_before_screensaver = 2000
    while True:

        if g_benchmark:
            loop_start_ticks = pygame.time.get_ticks()

        display_surface.fill(Color.black)

        # Handle any GPIO inputs
        if g_gpio_button_enabled:
            if GPIO.input(Hardware.gpio_button):
                if __debug__:
                    print("Page selected button depressed")

                # Bump up a page, wrap around if it would overrun page list
                if len(available_pages) != current_page + 1:
                    requested_page = current_page + 1
                else:
                    requested_page = 0

                if __debug__:
                    print("Requested page now {}".format(requested_page))

        # Handle events
        for event in pygame.event.get():
            # TODO: Swap for GPIO read of hardware key
            if __debug__:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        # Bump up a page, wrap around if it would overrun page list
                        if len(available_pages) != current_page + 1:
                            requested_page = current_page + 1
                        else:
                            requested_page = 0
                        print("Requested page now {}".format(requested_page))

            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
                # TODO: (Adam) 2020-12-02 Properly close out threads and active connections
        pygame.event.clear()

        # AIDA64 data is critical, if it stops we will display a screensaver until the feed returns
        if data_queue_maxlen > len(aida64_deque):
            # We can't safely access data if the data queue isn't deep enough. 
            ticks_since_last_data += data_retry_delay
            if ticks_since_last_data > retry_ticks_before_screensaver:
                if __debug__:
                    print("Data stream lost, starting screensaver...")

                MatrixScreensaver.start(data_queue_length = lambda : len(aida64_deque))

            # Add a tiny delay while we wait to stop system resources from getting thrashed.
            pygame.time.wait(data_retry_delay)
            continue
        else:
            ticks_since_last_data = 0

        # Best attempt to grab DHT22 Data for ambient temperature and humidity readings
        if None != dht22_deque:
            if data_queue_maxlen <= len(dht22_deque):
                dht22_data = dht22_deque.popleft()
                dht22_last_data = dht22_data
            else:
                dht22_data = dht22_last_data

        if __debug__:
            # Debug override, probably developing on a system without GPIO, here's some fake values for testing
            dht22_data = DHT22Data(humidity=44.6, temperature=67.8)


        if g_benchmark:
            draw_start_ticks = pygame.time.get_ticks()


        # Data is ready, select the page and bring it to the display surface
        if current_page != requested_page:
            assert(len(available_pages) >= requested_page)

            if __debug__:
                print("Switching from page index {} to {}".format(current_page, requested_page))

            #display_surface.blit(
            update_rects = available_pages[current_page].draw_update(aida64_deque.popleft(), dht22_data)[1]
            current_page = requested_page
        else:
            # Returns a surface to blit, if direct_surface and direct_rect defined it uses subsurfaces and
            # returns "blitable_surface, updated rects" for each element that will not be None if they were redrawn.
            update_rects = available_pages[current_page].draw_update(aida64_deque.popleft(), dht22_data)[1]


        if g_benchmark:
            print("BENCHMARK: Draw: {}ms".format(pygame.time.get_ticks() - draw_start_ticks))
        

        # Update areas that have been modified. Elements will return "None" if they didn't draw an update,
        # pygame.display.update will ignore those list entries.
        assert(0 != len(update_rects))
        pygame.display.update(update_rects)


        if g_benchmark:
            print("BENCHMARK: Loop update: {}ms".format(pygame.time.get_ticks() - loop_start_ticks))


    # Loop broken, exit pygame to cleanup resources
    pygame.quit()

if __name__ == "__main__":
    command_arguments = sys.argv[1:]

    # Saves headaches when debugging in VS2019
    if __debug__ and 0 == len(command_arguments):
        command_arguments = ['--aidasse', 'http://localhost:8080/sse']

    main(command_arguments)
