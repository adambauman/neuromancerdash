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
g_benchmark = False

class BarGraphConfig:
    def __init__(self, size, value_range, font=None, label=None):
        assert(2 == len(size) and 2 == len(value_range))

        self.size = size
        self.value_range = value_range
        self.data_field = None
        self.foreground_color = Color.windows_dkgrey_1_highlight
        self.background_color = Color.windows_dkgrey_1

        # Use system default if font isn't passed in
        if None == font:
            self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 12)
        else:
            self.font = font

        self.label = label
        self.label_color = Color.white
        self.label_dropshadow = True
        self.label_dropshadow_color = (0, 0, 0, 60) # Supports alpha
        self.label_position = None
        # Assume user wants to draw a label if defined
        self.draw_label = True
        if None != label:
            self.draw_label = False

        self.draw_value_connector = False # draws line connecting end of bar to current value text
        self.value_connector_color = Color.white

        self.draw_current_value = False
        self.current_value_follows_bar = False # ignores current_value_position and draws value at bar position
        self.current_value_follows_bar_x_offset = 0 # offsets value from bar, can be negative
        self.current_value_follows_bar_y_offset = 0 # offsets value from bar, can be negative
        self.current_value_position = None # if None draws inside end of bar

        self.draw_min_value = False
        self.min_value_position = None # if None draws before label at start of bar
        self.draw_max_value = False
        self.max_value_position = None # if None draws inside of end of bar, after current_value (if enabled)

        self.draw_unit = False
        self.unit_position = None # if None unit is draw next to current value


class BarGraph:
    __config = None
    __working_surface = None
    __label_surface = None
    __font = None

    current_value = None

    def __init__(self, bar_graph_config):
        assert(0 != bar_graph_config.size[0] and 0 != bar_graph_config.size[1])

        self.__config = bar_graph_config
        self.__setup_bargraph__()

    def __setup_bargraph__(self):
        assert(None != self.__config)

        if __debug__:
            debug_label = "<labelnone>"
            if None != self.__config.label:
                debug_label = self.__config.label
            print("Setting up {} Bargraph...".format(debug_label))

        # Use actual data field minmax if it's present in the config
        if None != self.__config.data_field:
            self.__config.value_range = (self.__config.data_field.min_value, self.__config.data_field.max_value)

        if None != self.__config.label and 0 != len(self.__config.label):
            self.__setup_label__()

        self.__setup_working_surface__()

    def __setup_label__(self):
        assert(None != self.__config.label or 0 != len(self.__config.label))
        assert(None == self.__label_surface)
        
        # Create a throwaway objects we can use to get some sizing information from
        temp_label = self.__config.font.render(self.__config.label)
        temp_bar = pygame.Surface(self.__config.size, pygame.SRCALPHA)

        # Draw the final label surface now, we can use it for more calculations as we go
        label_size = (temp_label[0].get_width(), temp_label[0].get_height())
        drop_shadow_offset = 2
        if False != self.__config.label_dropshadow:
            # Give label surface enough room for drop shadow pixels
            label_size = (label_size[0] + drop_shadow_offset, label_size[1] + drop_shadow_offset)

        self.__label_surface = pygame.Surface(label_size, pygame.SRCALPHA)
        if False != self.__config.label_dropshadow:
            self.__config.font.render_to(
                self.__label_surface, (drop_shadow_offset, drop_shadow_offset),
                self.__config.label, self.__config.label_dropshadow_color)
        self.__config.font.render_to(self.__label_surface, (0, 0), self.__config.label, self.__config.label_color)
        
        if None == self.__config.label_position:
            self.__config.label_position = Helpers.get_centered_origin(temp_bar.get_size(), self.__label_surface.get_size())

    def __setup_working_surface__(self):
        self.__working_surface = pygame.Surface(self.__config.size, pygame.SRCALPHA)


    def draw_update(self, value):
        
        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # Create fresh working surface
        self.__working_surface.fill(self.__config.background_color)

        # Draw the value rect
        data_field = self.__config.data_field
        transposed_value = Helpers.transpose_ranges(
            float(value), self.__config.value_range[1], self.__config.value_range[0], self.__config.size[0], 0)
        draw_rect = (0, 0, transposed_value, self.__config.size[1])
        pygame.draw.rect(self.__working_surface, self.__config.foreground_color, draw_rect)

        # Draw label
        if None != self.__label_surface:
            self.__working_surface.blit(self.__label_surface, self.__config.label_position)

        self.__last_value = value

        if g_benchmark:
            print("BENCHMARK: BarGraph {}: {}ms".format(self.__config.data_field.field_name, pygame.time.get_ticks() - start_ticks))

        return self.__working_surface