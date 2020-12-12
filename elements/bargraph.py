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
    def __init__(self, size, value_range, font=None):
        assert(2 == len(size) and 2 == len(value_range))

        self.size = size
        self.value_range = value_range
        self.dash_data = None
        self.foreground_color = Color.windows_dkgrey_1_highlight
        self.background_color = Color.windows_dkgrey_1

        # Use system default if font isn't passed in
        self.text_color = Color.white
        self.text_shadow_draw = True
        self.text_shadow_color = (0, 0, 0, 80)
        if None == font:
            self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 12)
        else:
            self.font = font

        self.current_value_draw = False
        self.current_value_position = None

        self.min_value_draw = False
        self.min_value_position = None
        self.max_value_draw = False
        self.max_value_position = None

        self.unit_draw = False
        self.unit_use_full_name = False
        self.unit_position = None


class BarGraph:
    __config = None
    __working_surface = None
    __static_overlay_surface = None
    __font = None

    current_value = None

    def __init__(self, bar_graph_config):
        assert(0 != bar_graph_config.size[0] and 0 != bar_graph_config.size[1])

        self.__config = bar_graph_config
        self.__setup_bargraph__()

    def __setup_bargraph__(self):
        assert(None != self.__config)

        # Use actual data field minmax if it's present in the config
        if None != self.__config.dash_data:
            self.__config.value_range = (self.__config.dash_data.min_value, self.__config.dash_data.max_value)

        self.__prepare_static_overlay__()
        self.__working_surface = pygame.Surface(self.__config.size, pygame.SRCALPHA)

    def __prepare_static_overlay__(self):
        assert(None != self.__config)

        # Sets up static elements like min/max values

        self.__static_overlay_surface = pygame.Surface(self.__config.size, pygame.SRCALPHA)
        config = self.__config
        font = config.font

        x_padding = 3

        # This section requires valid dash data, return if we don't have it
        if None == config.dash_data:
            return

        # Min value
        if False != config.min_value_draw:
            shadow_text = Helpers.get_shadowed_text(
                font, "{}".format(config.dash_data.min_value), config.text_color, config.text_shadow_color)
            origin = config.min_value_position
            if None == origin:
                # Place y-centered on the left with a small indent
                origin = (x_padding, (config.size[1] / 2) - (shadow_text.get_height() / 2) + 1)

            self.__static_overlay_surface.blit(shadow_text, origin)
        
        unit_text = None
        # Draw unit if position is valid. Otherwise will be draw with max value
        if False != config.unit_draw:
            if True == config.unit_use_full_name:
                unit_text = config.dash_data.unit.name
            else:
                unit_text = config.dash_data.unit.symbol
            
            if None != config.unit_position:
                shadow_text = Helpers.get_shadowed_text(font, unit_text, config.text_color, config.text_shadow_color)
                origin = config.unit_position
                assert(origin[0] < config.size[0] and origin[1] < config.size[1])

                self.__static_overlay_surface.blit(shadow_text, origin)

        # Max value if position is valid. Otherwise we'll draw this with current value during updates
        if False != config.max_value_draw and None != config.max_value_position:
            if None != unit_text:
                max_value_text = "{} {}".format(config.dash_data.max_value, unit_text)
            else:
                max_value_text = "{}".format(config.dash_data.max_value)

            shadow_text = Helpers.get_shadowed_text(
                font, max_value_text, config.text_color, config.text_shadow_color)
            origin = config.max_value_position
            assert(origin[0] < config.size[0] and origin[1] < config.size[1])

            self.__static_overlay_surface.blit(shadow_text, origin)

    def draw_update(self, value):
        assert(None != self.__working_surface)
        assert(None != self.__static_overlay_surface)
        
        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self.__working_surface.fill(self.__config.background_color)

        config = self.__config

        # Draw the value rect
        data_field = config.dash_data
        transposed_value = Helpers.transpose_ranges(
            float(value), config.value_range[1], config.value_range[0], config.size[0], 0)
        draw_rect = (0, 0, transposed_value, config.size[1])
        pygame.draw.rect(self.__working_surface, config.foreground_color, draw_rect)

        # Draw value, unit, max value text if configured
        x_padding = 3
        value_text = ""
        if config.current_value_draw:
            value_text += "{}".format(value)

        if config.max_value_draw and None != config.dash_data:
            if config.current_value_draw:
                value_text += "/"
            value_text += "{}".format(config.dash_data.max_value)

        if config.unit_draw and None != config.dash_data:
            if config.unit_use_full_name:
                value_text += " {}".format(config.dash_data.unit.name)
            else:
                value_text += " {}".format(config.dash_data.unit.symbol)

        if 0 != len(value_text):
            shadow_text = Helpers.get_shadowed_text(
                config.font, value_text, config.text_color, config.text_shadow_color)
            shadow_text_origin = (
                config.size[0] - x_padding - shadow_text.get_width(), 
                (config.size[1] / 2) - (shadow_text.get_height() / 2) + 1)
            self.__working_surface.blit(shadow_text, shadow_text_origin)

        # Draw static overlay with min/max values, etc.
        self.__working_surface.blit(self.__static_overlay_surface, (0, 0))

        self.__last_value = value

        if g_benchmark:
            print("BENCHMARK: BarGraph {}: {}ms".format(self.config.dash_data.field_name, pygame.time.get_ticks() - start_ticks))

        return self.__working_surface