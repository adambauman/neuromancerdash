#
# disk_visualizer_scratch - messing around with a new disk activity visualizer
# ============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

if __debug__:
    import time

import pygame
import sys, getopt
import threading
import random
import requests

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


        
#def start_stream_read(data_queue):
#        server_messages = SSEClient("http://localhost:8080/sse", timeout=2.0)

#        for server_message in server_messages:
#            if None == server_message.data or 0 == len(server_message.data):
#                continue

#            if "reload" == server_message.data.lower():
#                if __debug__:
#                    print("Encountered reload message")
#                continue

#            #print("Parsing data...")
#            parsed_data = AIDA64LCDSSE.parse_data(server_message.data)
#            #print("Asserting data length: {}".format(len(parsed_data)))
#            assert(0 != len(parsed_data))
#            #print("Finished parsing data")

#            data_queue.append(parsed_data)

def test_deque_max(data_queue):
    for index in range(999999):
        data_queue.append(index)
        time.sleep(0.200)


def main(argv):

    #pygame.init()
    #pygame.mouse.set_visible(false)
    #pygame.event.set_allowed([pygame.quit])
    
    #display_surface = pygame.display.set_mode(
    #    (480, 320),
    #    pygame.hwsurface | pygame.doublebuf
    #)
   
    
    data = deque([], maxlen=2)

    server_address = "http://localhost:8080/sse"
    print("Starting LCD stream thread")
    lcd_thread = threading.Thread(target=AIDA64LCDSSE.threadable_stream_read, args = (data, server_address))
    #lcd_thread = threading.Thread(target=test_deque_max, args = (data,))
    lcd_thread.setDaemon(True)
    lcd_thread.start()
    print("LCD stream thread started")
    
    if __debug__:
        loop_millis = 0
        start_millis = 0

    while True:
        if __debug__:
            start_millis = int(round(time.time() * 1000))

        if 2 > len(data):
            # NOTE: (Adam) 2020-12-2 Add a small delay to avoid thrashing resources while waiting for data.
            time.sleep(0.050)
            continue

        leftmost_data = data.popleft()
        print("Data_in_main_thread: {}".format(leftmost_data))
        #print("Remaining length: {}".format(len(data)))

        if __debug__:
            print("Data loop time: {}".format((int(round(time.time() * 1000)) - start_millis)))

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
