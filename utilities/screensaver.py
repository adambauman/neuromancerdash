#
# screensaver - Falling Matrix code screensaver, supports basic cancellation token
# ================================================================================
#
# Author: MrKioZ (https://gist.github.com/MrKioZ)
# Current modifications: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame, pygame.font
import random

# TODO: (Adam) 2020-11-14 Initial code copypasta'd from https://gist.github.com/MrKioZ/c07b9377d20bab53af6ebcdfbdeabb64,
# fork and properly link.

class MatrixScreensaverConfig:
    def __init__(self):
        self.matrix_color = (0, 200, 200)
        #self.matrix_color = (240, 240, 240)
        self.leading_character_color = (255, 255, 255)
        self.background_color = (0, 0, 0, 255)
        self.matrix_font = None
        self.binary_mode = False
        self.cycle_rgb = False

class MatrixScreensaver:
    def __is_written__(max_letters, x_heads, the_string):
        assert(0 != len(max_letters))
        assert(0 != len(x_heads))
        assert(0 != len(the_string))
        
        x_range_neg = int((max_letters[0] / 2) - (len(the_string) / 2))
        x_range_pos = int((max_letters[0] / 2) + (len(the_string) / 2))
        is_written = True
        for x in range(x_range_neg, x_range_pos + 1):
            if x_heads[x] == -1:
                is_written = False

        return is_written

    def __get_column__(fx, fy, x_heads, max_columns):
        assert(0 != len(x_heads))

        value = x_heads[fx] - fy
        if (max_columns > value > 0):
            return value
        else:
            return max_columns -1

    @classmethod
    def start(
        cls,
        surface = None, 
        startup_message = "", config = MatrixScreensaverConfig(), 
        stop_requested = lambda : False):

        if None == surface:
            surface = pygame.display.get_surface()
        
        assert(None != surface)

        x_heads = None
        max_colors = None

        surface.fill(config.background_color)

        startup_message = startup_message.upper()  # for better placement

        display_info = pygame.display.Info()
        display_size = (display_info.current_w, display_info.current_h)

        # Font and letters setup
        if None == config.matrix_font:
            matrix_font = pygame.font.Font(pygame.font.get_default_font(), 14)
        else:
            matrix_font = config.matrix_font

        sample_letter = matrix_font.render('_', False, (0, 111, 0))
        letter_size = (sample_letter.get_width(), sample_letter.get_height())
        max_letters = (int(display_size[0] / letter_size[0]), int(display_size[1] / letter_size[1]))

        # Color setup
        # TODO: Optional, gradual RGB shifting of colors for a spectrum effect
        color_list = [(255, 255, 255)]
        prime_colors = len(color_list) + 1
        R,G,B = config.matrix_color
        color_list += [(R+10, G+10, B+10)] * ((max_letters[1] - 10))
        end_colors = len(color_list)
        color_list += [
            (R-50 if R else 0, B-50 if B else 0, G-50 if G else 0), 
            (R-100 if R else 0, B-100 if B else 0, G-100 if G else 0), 
            (0, 0, 0)]

        end_colors = len(color_list) - end_colors + 1
        max_colors = len(color_list)

        current_color = 0

        # Generate characters
        letters = [[0 for _ in range(max_letters[1] + 1)] for _ in range(max_letters[0])]
        if config.binary_mode:
            character = chr(random.randint(48, 49))
        else:
            character = chr(random.randint(32, 126))

        for y in range(max_letters[1] + 1):
            for x in range(max_letters[0]):

                letters[x][y] = [matrix_font.render(character, False, color_list[current_color]) for current_color in range(max_colors)]

                if config.binary_mode:
                    character = chr(random.randint(48, 49))
                else:
                    character = chr(random.randint(32, 126))

        x_range_neg = int((max_letters[0] / 2) - (len(startup_message) / 2))
        x_range_pos = int((max_letters[0] / 2) + (len(startup_message) / 2))
        y_range_pos = int((max_letters[1] / 2) + 1)

        # word write
        startup_display_mode = False
        if 0 < len(startup_message):
            startup_display_mode = True

            for x in range(x_range_neg, x_range_pos):
                letters[x][int(max_letters[1] / 2)] =\
                   [matrix_font.render(startup_message[x - x_range_neg], False, (255, 255, 255)) for current_color in range(max_colors)]

            for y in range(y_range_pos, max_letters[1] + 1):
                for x in range(x_range_neg, x_range_pos):
                    letters[x][y] = [matrix_font.render(character, False, (0, 0, 0)) for current_color in range(max_colors)]
                    character = chr(random.randint(32, 126))

            if len(startup_message) % 2 == 1:
                letters[x_range_pos][max_letters[1] / 2] =\
                    [matrix_font.render(startupmessage[len(startup_message) - 1], False, (255, 255, 255)) for current_color in range(max_colors)]

                for y in range(y_range_pos, max_letters[1] + 1):
                    letter[x_range_pos][y] = [matrix_font.render(character, False, (0, 0, 0)) for current_color in range(max_colors)]
                    character = chr(random.randint(32, 126))

        if startup_display_mode:
            x_heads = [-1 for _ in range(max_letters[0] + 1)]
        else:
            x_heads = [0 for _ in range(max_letters[0] + 1)]

        # 1st loop - word write, no char switch
        not_done = True
        ticks_left = max_letters[1] + max_colors
        clock = pygame.time.Clock()
        while ticks_left > 0 and (not_done) and (startup_display_mode):
            
            assert(0 != len(x_heads))

            # Immediately bail if the caller requests a stop through the signaling lambda
            if stop_requested():
                return

            # Process events to avoid freezing behavior
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            if cls.__is_written__(max_letters, x_heads, startup_message):
                ticks_left -= 1

            if random.randint(1, 2) == 1:
                random_integer = random.randint(0, max_letters[0])
                if startup_display_mode:

                    if x_heads[random_integer] == -1:
                        x_heads[random_integer] = 1

                    if random.randint(1, 6):
                        random_integer = random.randint(
                            (max_letters[0] / 2) - len(startup_message),
                            (max_letters[0] / 2) + len(startup_message) + 1)

                        if x_heads[random_integer] == -1:
                            x_heads[random_integer] = 1

                else:
                    if x_heads[random_integer] == 0:
                        x_heads[random_integer] = 1

            assert(0 != len(x_heads))

            for x in range(max_letters[0]):
                current_color = 0
                counter = x_heads[x]
                while (counter > 0) and (current_color < max_colors):

                    if (counter < max_letters[1] + 2) and (current_color < prime_colors or current_color > (max_colors - end_colors)):
                        surface.blit(
                            letters[x][counter - 1][current_color], (x * letter_size[0],
                            (counter - 1) * letter_size[1]))

                    current_color += 1
                    counter -= 1

                if x_heads[x] > 0:
                    x_heads[x] += 1

                if x_heads[x] - max_colors > max_letters[1]:
                    x_heads[x] = 0

            pygame.display.flip()
            clock.tick(20)

        # word delete
        if len(startup_message) % 2 == 1:
            startup_message_length = x_range_pos + 1
        else:
            startup_message_length = x_range_pos

        for x in range(x_range_neg, startup_message_length):
            letters[x][int(max_letters[1] / 2)] =\
                [matrix_font.render(startup_message[x - x_range_neg], False, color_list[current_color]) for current_color in range(max_colors)]

        character = chr(random.randint(32, 126))
        for y in range(int(max_letters[1] / 2 + 1), int(max_letters[1] + 1)):
             for x in range(x_range_neg, x_range_pos + 1):
                letters[x][y] = [matrix_font.render(character, False, color_list[current_color]) for current_color in range(max_colors)]
                character = chr(random.randint(32, 126))

        # main matrix, has char switch
        while not_done:

            # Immediately bail if the caller requests a stop through the signaling lambda
            if stop_requested():
                return

            # Process events to avoid freezing behavior
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            if random.randint(1, 2) == 1:
                random_integer = random.randint(0, max_letters[0])
                if x_heads[random_integer] <= 0:
                    x_heads[random_integer] = 1

            assert(0 != len(x_heads))

            for x in range(max_letters[0]):
                current_color = 0
                counter = x_heads[x]

                # Main loop for redraw
                while (counter > 0) and (current_color < max_colors):

                    if (counter < max_letters[1] + 2) and (current_color < prime_colors or current_color > (max_colors - end_colors)):
                        surface.blit(
                            letters[x][counter - 1][current_color], 
                            (x * letter_size[0], (counter - 1) * letter_size[1]))
                    current_color += 1
                    counter -= 1

                # Character Switch
                random_integer = random.randint(1, max_colors - 1)
                character_position_y = x_heads[x] - random_integer
                if (max_letters[1] - 1 > character_position_y > 0):
                    display_info = letters[x][character_position_y]
                    random_x = random.randint(1, max_letters[0] - 1)
                    random_y = random.randint(1,max_letters[1] - 1)

                    surface.blit(
                        letters[x][character_position_y][max_colors - 1],
                        (x * letter_size[0], character_position_y * letter_size[1]))

                    surface.blit(
                        letters[random_x][random_y][max_colors - 1], 
                        (random_x * letter_size[0], random_y * letter_size[1]))

                    # Character swap action
                    letters[x][character_position_y] = letters[random_x][random_y]
                    letters[random_x][random_y] = display_info

                    surface.blit(
                        letters[x][character_position_y][random_integer], 
                        (x * letter_size[0], character_position_y * letter_size[1]))

                    surface.blit(
                        letters[random_x][random_y][cls.__get_column__(random_x, random_y, x_heads, max_colors)],
                        (random_x * letter_size[0], random_y * letter_size[1]))

                # Limit position if it's off the screen
                if x_heads[x] > 0:
                    x_heads[x] += 1
                if x_heads[x] - max_colors > max_letters[1]:
                    x_heads[x] = 0

            pygame.display.flip()
            clock.tick(20)


if __name__ == "__main__":
    #main(sys.argv[1:])

    pygame.init()
    pygame.mouse.set_visible(False)
    
    display_surface = pygame.display.set_mode(
        (480, 320),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    screensaver = MatrixScreensaver.start(display_surface)

    pygame.quit()
