#
# bargraph - bargraph display elements
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from .styles import Color
from .helpers import Helpers

# Set true to benchmark the update process
g_benchmark = True

class BarGraphConfig:
    width = 0
    height = 0
    data_field = None
    foreground_color = Color.white
    background_color = Color.windows_dkgrey_1

    def __init__(self, width, height, data_field):
        assert(0 != width and 0 != height)
        self.width, self.height = width, height
        self.data_field = data_field

class BarGraph:
    __config = None
    __working_surface = None
    __first_run = True
    __last_value = 0

    def __init__(self, bar_graph_config):
        assert(0 != bar_graph_config.width and 0 != bar_graph_config.height)
        assert(None != bar_graph_config.data_field)

        self.__config = bar_graph_config
        self.__working_surface = pygame.Surface((self.__config.width, self.__config.height))
        
        self.update(0)
        self.__first_run = False

    def update(self, value):
        
        if g_benchmark:
            start_ticks = pygame.time.get_ticks()
        
        # Reuse previous surface if value hasn't changed
        if self.__last_value == value and self.__first_run != True:
            return self.__working_surface

        # Draw the background, we'll use the existing member surface
        self.__working_surface.fill(self.__config.background_color)

        # Draw the value rect
        data_field = self.__config.data_field
        transposed_value = Helpers.transpose_ranges(float(value), data_field.max_value, data_field.min_value, self.__config.width, 0)
        draw_rect = (0, 0, transposed_value, self.__config.height)
        pygame.draw.rect(self.__working_surface, self.__config.foreground_color, draw_rect)

        self.__last_value = value

        if g_benchmark:
            print("BENCHMARK: BarGraph {}: {}ms".format(self.__config.data_field.field_name, pygame.time.get_ticks() - start_ticks))

        return self.__working_surface