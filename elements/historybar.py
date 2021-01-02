#
# historybar - bar that visualizes current value and min/max history
# ==================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from .styles import Color
from .helpers import Helpers

class HistoryBarConfig:
    def __init__(self, size, dash_data, font=None):
        assert(2 == len(size))

        self.size = size
        self.dash_data = dash_data
        self.indicator_width = 8
        self.indicator_color = Color.windows_cyan_1
        self.history_bar_color = Color.windows_cyan_1_dark
        self.outline_color = Color.grey_75
        self.outline_thickness = 3 # Odd numbers recommended, will provide more uniform result
        self.outline_radius = 0
        self.bg_color = Color.black

        self.out_of_range_warn = True
        self.warn_indicator_color = Color.windows_red_1_bright
        self.warn_history_bar_color = Color.windows_red_1_dark
        self.warn_outline_color = Color.windows_red_1_medium

        # Use system default if font isn't passed in
        self.text_color = Color.white
        self.text_shadow_color = (0, 0, 0, 255) # Supports alpha blending
        self.text_shadow_draw = True
        text_template = "{}"
        if None == font:
            self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 12)
        else:
            self.font = font

class HistoryBar:
    working_surface = None
    base_rect = None

    current_value = None
    min_history_value = None
    max_history_value = None

    _outline_rect = None
    _base_size = None
    _min_history_x = None
    _max_history_x = None

    def __init__(self, bar_graph_config, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != bar_graph_config.size)

        self._config = bar_graph_config
        self._base_size = self._config.size

        if direct_surface and direct_rect:
            self.working_surface = direct_surface.subsurface(direct_rect)
            self.base_rect = direct_rect
        else:
            self.working_surface = pygame.Surface(self._config.size, surface_flags)

        # Draw an initial outline element to lock in the _outline_rect dimensions
        self.__draw_outline__()

    def __draw_outline__(self, warn=False):
        assert(self._config)

        outline_color = self._config.outline_color
        if warn:
            outline_color = self._config.warn_outline_color

        # Setup outline rect, we have to account for the way lines grow when the ouline width > 1
        # Store the outline_rect as a member so future draws don't spill over the lines
        if not self._outline_rect:
            thiccccc_ness = self._config.outline_thickness
            outline_origin = (thiccccc_ness / 2, thiccccc_ness / 2)
            outline_size = (self.working_surface.get_width() - thiccccc_ness, self.working_surface.get_height() - thiccccc_ness)
            self._outline_rect = pygame.Rect(outline_origin, outline_size)

        pygame.draw.rect(
            self.working_surface, 
            outline_color, self._outline_rect, self._config.outline_thickness, self._config.outline_radius)

    def __draw_history__(self, transposed_x, warn=False):
        history_color = self._config.history_bar_color
        if warn:
            history_color = self._config.warn_history_bar_color

        # Initialize on the first run
        if not self._min_history_x and not self._max_history_x:
            self._min_history_x = transposed_x
            self._max_history_x = transposed_x

        assert(self._max_history_x >= self._min_history_x)

        # Update minmax ranges
        if self._min_history_x > transposed_x:
            self._min_history_x = transposed_x
        if self._max_history_x < transposed_x:
            self._max_history_x = transposed_x

        # Draw the history rect
        end_width = self._max_history_x - self._min_history_x
        history_rect = (self._min_history_x, 0, end_width, self.working_surface.get_height())
        pygame.draw.rect(self.working_surface, history_color, history_rect)

    def __draw_indicator__(self, transposed_x, warn=False):
        assert(self._outline_rect)

        indicator_color = self._config.indicator_color
        if warn:
            indicator_color = self._config.warn_indicator_color

        line_width = self._config.indicator_width
        # Clamp the x position so the indicator remains within ouline bounds
        # TODO: This is a bit ugly, maybe use rect overlaps to clamp positioning
        if self._outline_rect.left > transposed_x - (line_width / 2):
            transposed_x = self._outline_rect.left + (line_width / 2)
        if self._outline_rect.right < transposed_x + (line_width / 2):
            transposed_x = self._outline_rect.right - (line_width / 2)

        line_start = (transposed_x, self._outline_rect.top)
        line_end = (transposed_x, self._outline_rect.height)
        pygame.draw.line(self.working_surface, indicator_color, line_start, line_end, line_width)

    def set_direct_draw(self, direct_surface, direct_rect):
        # Draw element directly to a subsurface of the direct_surface
        assert(direct_surface)
        assert(0 != direct_rect[2] and 0 != direct_rect[3])

        self.working_surface = direct_surface.subsurface(direct_rect)
        self.base_rect = direct_rect

    def draw_update(self, value):
        assert(self.working_surface)

        value_float = float(value)

        # Return last draw result if the value hasn't changed
        if self.current_value == value_float:
            return None

        self.working_surface.fill((0, 0, 0, 0))

        # Start tracking min/max values
        if not self.min_history_value or not self.max_history_value:
            self.min_history_value = value_float
            self.max_history_value = value_float

        if self.min_history_value > value_float:
            self.min_history_value = value_float
        
        if self.max_history_value < value_float:
            self.max_history_value = value_float

        # Translate value to element display face
        max_value = self._config.dash_data.max_value
        min_value = self._config.dash_data.min_value
        transposed_x = Helpers.transpose_ranges(value_float, max_value, min_value, self.working_surface.get_width(), 0)
        
        is_warning = False
        if max_value <= value_float or min_value >= value_float:
            is_warning = True

        self.__draw_history__(transposed_x, is_warning)
        self.__draw_indicator__(transposed_x, is_warning)
        self.__draw_outline__(is_warning)

        self.current_value = value_float

        return self.base_rect