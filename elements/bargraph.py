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
        self.text_shadow_color = (0, 0, 0, 255) # Supports alpha blending
        if None == font:
            self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 12)
        else:
            self.font = font

        self.draw_background = True

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
    working_surface = None
    direct_rect = None
    current_value = None

    _config = None
    _static_overlay_surface = None
    _font = None

    def __init__(
        self, bar_graph_config, direct_surface=None, direct_rect=None, surface_flags=0, force_update=False):

        assert((0, 0) != bar_graph_config.size)

        self._config = bar_graph_config
        self._force_update = force_update

        if direct_surface and direct_rect:
            self.working_surface = direct_surface.subsurface(direct_rect)
            self.direct_rect = direct_rect
        else:
            self.working_surface = pygame.Surface(self._config.size, surface_flags)

        self.__setup_bargraph__(surface_flags)

    def __setup_bargraph__(self, surface_flags):
        assert(self._config)

        # Use actual data field minmax if it's present in the config
        if None != self._config.dash_data:
            self._config.value_range = (self._config.dash_data.min_value, self._config.dash_data.max_value)

        self.__prepare_static_overlay__(surface_flags)

    def __prepare_static_overlay__(self, surface_flags):
        assert(self._config)

        # Sets up static elements like min/max values
        # Must support alpha
        self._static_overlay_surface = pygame.Surface(self._config.size, surface_flags | pygame.SRCALPHA)
        config = self._config
        font = config.font

        x_padding = 3

        # This section requires valid dash data, return if we don't have it
        if config.dash_data is None:
            return

        # Min value
        if config.min_value_draw:
            shadow_text = Helpers.get_shadowed_text(
                font, "{}".format(config.dash_data.min_value), config.text_color, config.text_shadow_color)
            origin = config.min_value_position
            if origin is None:
                # Place y-centered on the left with a small indent
                origin = (x_padding, (config.size[1] / 2) - (shadow_text.get_height() / 2) + 1)

            self._static_overlay_surface.blit(shadow_text, origin)
        
        unit_text = None
        # Draw unit if position is valid. Otherwise will be draw with max value
        if config.unit_draw:
            if config.unit_use_full_name:
                unit_text = config.dash_data.unit.name
            else:
                unit_text = config.dash_data.unit.symbol
            
            if config.unit_position:
                shadow_text = Helpers.get_shadowed_text(font, unit_text, config.text_color, config.text_shadow_color)
                origin = config.unit_position
                assert(origin[0] < config.size[0] and origin[1] < config.size[1])

                self._static_overlay_surface.blit(shadow_text, origin)

        # Max value if position is valid. Otherwise we'll draw this with current value during updates
        if config.max_value_draw and config.max_value_position:
            if unit_text:
                max_value_text = "{} {}".format(config.dash_data.max_value, unit_text)
            else:
                max_value_text = "{}".format(config.dash_data.max_value)

            shadow_text = Helpers.get_shadowed_text(
                font, max_value_text, config.text_color, config.text_shadow_color)
            origin = config.max_value_position
            assert(origin[0] < config.size[0] and origin[1] < config.size[1])

            self._static_overlay_surface.blit(shadow_text, origin)

    def set_direct_draw(self, direct_surface, direct_rect):
        # Draw element directly to a subsurface of the direct_surface
        assert(direct_surface)
        assert((0, 0) != direct_rect.size)

        self.working_surface = direct_surface.subsurface(direct_rect)
        self.base_rect = direct_rect

    def draw_update(self, value):
        assert(self.working_surface)
        assert(self._static_overlay_surface)

        if not self._force_update:
            if self.current_value == value:
                return None
        
        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        config = self._config
        if config.draw_background:
            self.working_surface.fill(self._config.background_color)

        # Draw the value rect
        data_field = config.dash_data
        transposed_value = Helpers.transpose_ranges(
            float(value), config.value_range[1], config.value_range[0], config.size[0], 0)
        draw_rect = (0, 0, transposed_value, config.size[1])
        pygame.draw.rect(self.working_surface, config.foreground_color, draw_rect)

        # Draw value, unit, max value text if configured
        x_padding = 3
        value_text = ""
        if config.current_value_draw:
            value_text += "{}".format(value)

        if config.max_value_draw and config.dash_data:
            if config.current_value_draw:
                value_text += "/"
            value_text += "{}".format(config.dash_data.max_value)

        if config.unit_draw and config.dash_data and not config.unit_position:
            if config.unit_use_full_name:
                value_text += " {}".format(config.dash_data.unit.name)
            else:
                value_text += " {}".format(config.dash_data.unit.symbol)

        value_position = self._config.current_value_position
        if 0 != len(value_text):
            shadow_text = Helpers.get_shadowed_text(
                config.font, value_text, config.text_color, config.text_shadow_color)

            if value_position is None:
                value_position = (
                    config.size[0] - x_padding - shadow_text.get_width(), 
                    (config.size[1] / 2) - (shadow_text.get_height() / 2) + 1)

            self.working_surface.blit(shadow_text, value_position)

        # Draw static overlay with min/max values, etc.
        self.working_surface.blit(self._static_overlay_surface, (0, 0))

        self.current_value = value

        if g_benchmark:
            print("BENCHMARK: BarGraph {}: {}ms".format(self.config.dash_data.field_name, pygame.time.get_ticks() - start_ticks))

        return self.direct_rect