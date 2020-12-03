#
# disk_visualizer_scratch - messing around with a new disk activity visualizer
# ============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

if __debug__:
    import time

import os
import pygame
import sys, getopt
import threading
import random
import requests

# Simple check for RPi GPIO, will disable any stuff that requires GPIO access so you can
# debug and develop on other platforms.
g_gpio_available = True
try:
    import RPi.GPIO as GPIO
    print("RPi GPIO Available")
except:
    g_gpio_available = False
    print("RPi GPIO Not Available")

if g_gpio_available:
    from data.dht22 import DHT22, DHT22Data

# TODO: (Adam) 2020-12-1 Conditionally load modules that require GPIO for easier development
#            and debugging on non-GPIO equipped platforms.
from data.aida64lcdsse import AIDA64LCDSSE
#from data.dht22 import DHT22

from elements.styles import FontPaths, Color
from dashpages import DashPage1Painter
from utilities.screensaver import MatrixScreensaver

from collections import deque
import threading

from sseclient import SSEClient

from data.aida64lcdsse import AIDA64LCDSSE

#from dashboardpainter import Color, FontPaths, DataField, DashData, AssetPath, Units
        
def main(argv):

    #pygame.init()
    #pygame.mouse.set_visible(false)
    #pygame.event.set_allowed([pygame.quit])
    
    #display_surface = pygame.display.set_mode(
    #    (480, 320),
    #    pygame.hwsurface | pygame.doublebuf
    #)
   
    data_queue_maxlen = 1

    # Start the AIDA64 data thread, fastest update interval is usually ~100ms and can be
    # adjusted in the AIDA64 preferences. 
    aida64_deque = deque([], maxlen=data_queue_maxlen)
    server_address = "http://localhost:8080/sse"
    aida64_data_thread = threading.Thread(target=AIDA64LCDSSE.threadable_stream_read, args=(aida64_deque, server_address))
    aida64_data_thread.setDaemon(True)
    aida64_data_thread.start()

    # Start DHT22 thread if GPIO is available. Reading this data can take awhile, don't expect
    # updates to occur under 3-5 seconds.
    dht22_deque = deque([], maxlen=data_queue_maxlen)
    if g_gpio_available:
        dht22_data_thread = threading.Thread(target=DHT22.threadable_read_retry, args=(dht22_deque,))
        dht22_data_thread.setDaemon(True)
        dht22_data_thread.start()

    # Main loop, this will juggle data and painting the dash page(s)
    while True:
        if data_queue_maxlen > len(aida64_deque):
            # We can't safely popleft data if the data queue isn't deep enough. Add a tiny delay
            # while we wait to stop system resources from getting thrashed.
            # TODO: (Adam) 2020-12-02 Jump into wait-for-reconnect mode with screen saver if we lost
            #           the data feed for more than a few seconds.
            time.sleep(0.050)
            continue


        leftmost_data = aida64_deque.popleft()
        print("Data_in_main_thread: {}".format(leftmost_data))
        #print("Remaining length: {}".format(len(data)))


    print("Exited main loop")
    lcd_thread.join()

    #aida64_lcd.get()

    #while True:
    #    display_surface.fill(Color.black)

    #    display_surface.blit(disk_activity.update(data), (20,20))
        
    #    for event in pygame.event.get():
    #        if event.type == pygame.QUIT:
    #            print("User quit")
    #            pygame.quit()
    #            sys.exit()

    #    pygame.event.clear()

    #    pygame.display.flip()

    #    time.sleep(0.100)

    #pygame.quit()


if __name__ == "__main__":
    main(sys.argv[1:])
