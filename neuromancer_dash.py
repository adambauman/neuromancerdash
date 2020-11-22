#!/usr/bin/env python

import pygame
import sys, getopt
import threading
import random
import requests

if __debug__:
    import traceback

from aida64_sse_data import AIDA64SSEData
from dashboard_painter import DashPage1Painter, FontPaths, Color
#from reconnect_screensaver import MatrixScreenSaver

g_connection_test_success = False

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


# TODO: (Adam) 2020-11-14 Copypasta'd from https://gist.github.com/MrKioZ/c07b9377d20bab53af6ebcdfbdeabb64, fork and properly link
class MatrixScreensaver:

    __color = (0, 200, 200) #The Color of the Matrix
    __zero_one = False #Makes a rain of zeros and ones instead of random ASCII character  

    __xHeads = None
    __maxCol = None

    __surface = None
    __startup_message = ""
    __stop_requested = lambda:False

    def IsWritten(self, lettersOnScreen, str):
        defTemp = True
        for x in range(int((lettersOnScreen[0] / 2) - (len(str) / 2)), int((lettersOnScreen[0] / 2) + (len(str) / 2) + 1)):
            if self.__xHeads[x] == -1:
                defTemp = False
        return defTemp

    def getColor(self, fx, fy):
        defTemp=self.__xHeads[fx]-fy

        if (self.__maxCol>defTemp>0):
            return defTemp
        else:
            return self.__maxCol-1

    def __init__(self, surface=None, startup_message="", stop_requested=lambda:False):

        self.__startup_message = startup_message
        self.__stop_requested = stop_requested

        if None == surface:
            self.__surface = pygame.display.get_surface()
            assert(None != self.__surface)
        else:
            self.__surface = surface

    def start(self):


        surface = self.__surface
        surface.fill("#000000")

        #try:
        #    fo = open("indata.txt", "r+")
        #    str = fo.readline()
        #    # Close opend file
        #    fo.close()
        #except:
        #    str = ''
        str = self.__startup_message
        str = str.upper()  # for better placement

        stop_requested = self.__stop_requested

        # Pygame init
        #pygame.init()
        temp = pygame.display.Info()
        displLength = (temp.current_w, temp.current_h)
        #surface = pygame.display.set_mode(displLength, pygame.FULLSCREEN)
        # Font init
        #pygame.font.init()
        fontObj = pygame.font.Font(pygame.font.get_default_font(), 14)
        sampleLetter = fontObj.render('_', False, (0, 111, 0))
        letterSize = (sampleLetter.get_width(), sampleLetter.get_height())
        lettersOnScreen = (int(displLength[0] / letterSize[0]), int(displLength[1] / letterSize[1]))

        # color init
        colorList = [(255, 255, 255)]
        primeColors = len(colorList)+1
        R,G,B = self.__color
        colorList += [(R+10, G+10, B+10)] * ((lettersOnScreen[1] - 10))
        endColors = len(colorList)
        colorList += [(R-50 if R else 0, B-50 if B else 0, G-50 if G else 0),(R-100 if R else 0, B-100 if B else 0, G-100 if G else 0),(0, 0, 0)]
        endColors = len(colorList) - endColors+1

        self.__maxCol = len(colorList)

        # char generator
        letters = [[0 for _ in range(lettersOnScreen[1] + 1)] for _ in range(lettersOnScreen[0])]
        if self.__zero_one:
            char = chr(random.randint(48, 49))
        else:
            char = chr(random.randint(32, 126))

        for y in range(lettersOnScreen[1] + 1):
            for x in range(lettersOnScreen[0]):
                letters[x][y] = [fontObj.render(char, False, colorList[col]) for col in range(self.__maxCol)]
                if self.__zero_one:
                    char = chr(random.randint(48, 49))
                else:
                    char = chr(random.randint(32, 126))

        xRangeNeg = int((lettersOnScreen[0] / 2) - (len(str) / 2))
        xRangePos = int((lettersOnScreen[0] / 2) + (len(str) / 2))
        yRangePos = int((lettersOnScreen[1] / 2) + 1)

        # word write
        wordMode = False
        if len(str) > 0:
            wordMode = True

            for x in range(xRangeNeg, xRangePos):
                letters[x][int(lettersOnScreen[1] / 2)] =\
                   [fontObj.render(str[x - xRangeNeg], False, (255, 255, 255)) for col in range(self.__maxCol)]

            for y in range(yRangePos, lettersOnScreen[1] + 1):
                for x in range(xRangeNeg, xRangePos):
                    letters[x][y] = [fontObj.render(char, False, (0, 0, 0)) for col in range(self.__maxCol)]
                    char = chr(random.randint(32, 126))

            if len(str) % 2 == 1:
                letters[xRangePos][lettersOnScreen[1] / 2] =\
                    [fontObj.render(str[len(str) - 1], False, (255, 255, 255)) for col in range(self.__maxCol)]

                for y in range(yRangePos, lettersOnScreen[1] + 1):
                    letter[xRangePos][y] = [fontObj.render(char, False, (0, 0, 0)) for col in range(self.__maxCol)]
                    char = chr(random.randint(32, 126))

        if wordMode:
            self.__xHeads = [-1 for _ in range(lettersOnScreen[0] + 1)]
        else:
            self.__xHeads = [0 for _ in range(lettersOnScreen[0] + 1)]

        # 1st loop - word write, no char switch
        notDone = True
        ticksLeft = lettersOnScreen[1] + self.__maxCol
        while ticksLeft > 0 and (notDone) and (wordMode):
            if stop_requested():
                print("Stop request confirmed")
                return

            if g_connection_test_success:
                return

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    notDone = False
                if event.type == pygame.KEYDOWN:
                    notDone = False
            if self.IsWritten(lettersOnScreen, str):
                ticksLeft -= 1
            if random.randint(1, 2) == 1:
                randomInt = random.randint(0, lettersOnScreen[0])
                if wordMode:
                    if self.__xHeads[randomInt] == -1:
                        self.__xHeads[randomInt] = 1
                    if random.randint(1, 6):
                        randomInt = random.randint((lettersOnScreen[0] / 2) - len(str),
                                                   (lettersOnScreen[0] / 2) + len(str) + 1)
                        if self.__xHeads[randomInt] == -1:
                            self.__xHeads[randomInt] = 1
                else:
                    if self.__xHeads[randomInt] == 0:
                        self.__xHeads[randomInt] = 1
            for x in range(lettersOnScreen[0]):
                col = 0
                counter = self.__xHeads[x]
                while (counter > 0) and (col < self.__maxCol):
                    if (counter < lettersOnScreen[1] + 2) and (col < primeColors or
                                            col > (self.__maxCol - endColors)):
                        surface.blit(letters[x][counter - 1][col], (x * letterSize[0],
                                                                    (counter - 1) * letterSize[1]))
                    col += 1
                    counter -= 1
                if self.__xHeads[x] > 0:
                    self.__xHeads[x] += 1
                if self.__xHeads[x] - self.__maxCol > lettersOnScreen[1]:
                    self.__xHeads[x] = 0

            pygame.display.update()
            clock = pygame.time.Clock()
            clock.tick(20)

        # word delete
        if len(str) % 2 == 1:
            strLen = xRangePos + 1
        else:
            strLen = xRangePos

        for x in range(xRangeNeg, strLen):
            letters[x][int(lettersOnScreen[1] / 2)] =\
                [fontObj.render(str[x - xRangeNeg], False, colorList[col]) for col in range(self.__maxCol)]

        char = chr(random.randint(32, 126))
        for y in range(int(lettersOnScreen[1] / 2 + 1), int(lettersOnScreen[1] + 1)):
             for x in range(xRangeNeg, xRangePos + 1):
                letters[x][y] = [fontObj.render(char, False, colorList[col]) for col in range(self.__maxCol)]
                char = chr(random.randint(32, 126))


        # main matrix, has char switch
        while notDone:
            if g_connection_test_success:
                print("Screensaver: Connection test success")
                return

            if stop_requested():
                print("Screensaver: Stop request confirmed")
                return

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    notDone = False
                if event.type == pygame.KEYDOWN:
                    notDone = False

            if random.randint(1, 2) == 1:
                randomInt = random.randint(0, lettersOnScreen[0])
                if self.__xHeads[randomInt] <= 0:
                    self.__xHeads[randomInt] = 1
            for x in range(lettersOnScreen[0]):
                col = 0
                counter = self.__xHeads[x]
                # main loop for redraw
                while (counter > 0) and (col < self.__maxCol):
                    if (counter < lettersOnScreen[1] + 2) and (col < primeColors or
                                            col > (self.__maxCol - endColors)):
                        surface.blit(letters[x][counter - 1][col], (x * letterSize[0],
                                                                    (counter - 1) * letterSize[1]))
                    col += 1
                    counter -= 1

                # charswirch
                randomInt = random.randint(1, self.__maxCol - 1)
                charPosY = self.__xHeads[x] - randomInt
                if (lettersOnScreen[1] - 1 > charPosY > 0):
                    temp = letters[x][charPosY]
                    randomX = random.randint(1, lettersOnScreen[0] - 1)
                    randomY = random.randint(1,lettersOnScreen[1] - 1)

                    surface.blit(letters[x][charPosY][self.__maxCol - 1], (x * letterSize[0],
                                                                    charPosY * letterSize[1]))
                    surface.blit(letters[randomX][randomY][self.__maxCol - 1], (randomX * letterSize[0],
                                                                    randomY * letterSize[1]))
                    # char swap
                    letters[x][charPosY] = letters[randomX][randomY]
                    letters[randomX][randomY] = temp

                    surface.blit(letters[x][charPosY][randomInt], (x * letterSize[0], charPosY * letterSize[1]))
                    surface.blit(letters[randomX][randomY][self.getColor(randomX,randomY)],
                                 (randomX * letterSize[0], randomY * letterSize[1]))
                # check if is out of screen
                if self.__xHeads[x] > 0:
                    self.__xHeads[x] += 1
                if self.__xHeads[x] - self.__maxCol > lettersOnScreen[1]:
                    self.__xHeads[x] = 0

            pygame.display.update()
            clock = pygame.time.Clock()
            clock.tick(20)

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


# TODO: (Adam) 2020-11-22 Super ghetto, use proper thread piping and such
def test_server_connection(server_address):
    assert(0 != len(server_address))

    while True:
        try:
            if __debug__:
                print("Making test request to {}".format(server_address))

            response = requests.get(server_address, timeout = 1)
            if 200 == response.status.code:
                global g_connection_test_success
                g_connection_test_success = True
                break
        except:
            if __debug__:
                print("Connect test failed")


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

    #reconnect_attempt_count = 0
    #reconnect_attempts_until_screensaver = 1
    #screensaver_running = False
    request_screensaver_stop = False
    #screensaver = threading.Thread(target=MatrixScreenSaver, args=(None, "", lambda:request_screensaver_stop)) 
    connection_test_thread = threading.Thread(target=test_server_connection, args=(server_address,))
    screensaver = MatrixScreensaver(None, "", lambda : request_screensaver_stop)
    while True:
        # Dashboard will fail if the computer sleeps or is otherwise unavailable, keep
        # retrying until it starts to respond again.
        try:
            # Start connection to the AIDA64 SSE data stream
            server_messages = AIDA64SSEData.connect(server_address)
            #if screensaver_running:
                #reconnect_attempt_count = 0
                #request_screensaver_stop = True
                #screensaver.join()
                #screensaver_running = False

            start_dashboard(server_messages, display_surface, dash_page_1_painter)
        except Exception:
            if __debug__:
                traceback.print_exc()
                #print("Reconnect attempt #{}...".format(reconnect_attempt_count))

        #if reconnect_attempts_until_screensaver <= reconnect_attempt_count and False == screensaver_running:
        #    screensaver.start()
        #    screensaver_running = True

        connection_test_thread.start()
        screensaver.start()
        connection_test_thread.join()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
        pygame.event.clear()

        #reconnect_attempt_count += 1

        # Take it easy with the retry when the screen saver is active, host machine is offline or sleeping,
        # otherwise use a short delay to avoid hammering network requests.
        #if screensaver_running:
        pygame.time.wait(2000)
        #else:
        #    if __debug__:
        #        print("Short retry timeout")
        #    pygame.time.wait(50)


    pygame.quit()

if __name__ == "__main__":
    main(sys.argv[1:])

