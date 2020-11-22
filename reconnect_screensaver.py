#!/usr/bin/env python

import pygame, pygame.font
import random

# TODO: (Adam) 2020-11-14 Copypasta'd from https://gist.github.com/MrKioZ/c07b9377d20bab53af6ebcdfbdeabb64, fork and properly link

class MatrixScreenSaver:

    __color = (0, 200, 200) #The Color of the Matrix
    __zero_one = False #Makes a rain of zeros and ones instead of random ASCII character  

    __xHeads = None
    __maxCol = None

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

    def __init__(self, surface, startup_message = "", stop_requested = lambda : False):

        #try:
        #    fo = open("indata.txt", "r+")
        #    str = fo.readline()
        #    # Close opend file
        #    fo.close()
        #except:
        #    str = ''
        str = startup_message
        str = str.upper()  # for better placement

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
            if stop_requested():
                print("Stop request confirmed")
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


if __name__ == "__main__":
    #main(sys.argv[1:])

    pygame.init()
    pygame.mouse.set_visible(False)
    
    display_surface = pygame.display.set_mode(
        (480, 320),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    screensaver = MatrixScreenSaver(display_surface)
    pygame.quit()