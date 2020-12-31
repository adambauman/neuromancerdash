#
# levelbar - bar that visualizes current value level and min/max thresholds
# =========================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from .styles import Color
from .helpers import Helpers

# Set true to benchmark the update process
g_benchmark = False

class LevelBarConfig:
    def __init__(self, size, dash_data, font=None):
        assert(2 == len(size))

        self.size = size
        self.dash_data = dash_data
        self.indicator_width = 8
        self.indicator_color = Color.windows_cyan_1
        self.history_bar_color = Color.windows_cyan_1_dark
        self.outline_color = Color.grey_75
        self.outline_thickness = 2
        self.outline_radius = 0
        self.bg_color = Color.black

        out_of_range_warn = True

        # Use system default if font isn't passed in
        self.text_color = Color.white
        self.text_shadow_color = (0, 0, 0, 255) # Supports alpha blending
        self.text_shadow_draw = True
        text_template = "{}"
        if None == font:
            self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 12)
        else:
            self.font = font

class LevelBar:
    _working_surface = None
    _direct_rect = None

    base_size = None
    current_value = None
    min_history_x = None
    max_history_x = None

    def __init__(self, bar_graph_config, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != bar_graph_config.size)

        self._config = bar_graph_config
        self.base_size = self._config.size

        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
            self._direct_rect = direct_rect
        else:
            self._working_surface = pygame.Surface(self._config.size, surface_flags)

    def __draw_outline__(self):
        assert(self._config)

        # Setup rect for the outline. 
        outline_origin = ((self._config.outline_thickness, self._config.outline_thickness))
        outline_size = (
            self._working_surface.get_width() - (self._config.outline_thickness * 2),
            self._working_surface.get_height() - (self._config.outline_thickness * 2))
        self._outline_rect = pygame.Rect(outline_origin, outline_size)
        pygame.draw.rect(
            self._working_surface, 
            self._config.outline_color, 
            self._outline_rect, self._config.outline_thickness, self._config.outline_radius)

    def __draw_history__(self, transposed_x):
        # Initialize on the first run
        if not self.min_history_x and not self.max_history_x:
            self.min_history_x = transposed_x
            self.max_history_x = transposed_x

        # Update minmax ranges
        if self.min_history_x > transposed_x:
            self.min_history_x = transposed_x
        if self.max_history_x < transposed_x:
            self.max_history_x = transposed_x

        # Draw
        history_points = [
            (self.max_history_x, self._working_surface.get_height() - self._config.outline_thickness), 
            (self.min_history_x, self._working_surface.get_height() - self._config.outline_thickness),
            (self.min_history_x, self._config.outline_thickness), 
            (self.max_history_x, self._config.outline_thickness)]
        pygame.draw.polygon(self._working_surface, self._config.history_bar_color, history_points)

    def __draw_indicator__(self, transposed_x):
      
        pygame.draw.line(
            self._working_surface, self._config.indicator_color, 
            (transposed_x, 2), (transposed_x, self._working_surface.get_height() - 2), self._config.indicator_width)

    def set_direct_draw(self, direct_surface, direct_rect):
        # Draw element directly to a subsurface of the direct_surface
        assert(direct_surface)
        assert(0 != direct_rect[2] and 0 != direct_rect[3])

        self._working_surface = direct_surface.subsurface(direct_rect)
        self._direct_rect = direct_rect

    def draw_update(self, value):
        assert(self._working_surface)

        value_float = float(value)

        # Return last draw result if the value hasn't changed
        if self.current_value == value_float:
            return self._working_surface, None

        self._working_surface.fill((0, 0, 0, 0))

        max_value = self._config.dash_data.max_value
        min_value = self._config.dash_data.min_value
        transposed_x = Helpers.transpose_ranges(value_float, max_value, min_value, self._working_surface.get_width(), 0)
        
        self.__draw_history__(transposed_x)
        self.__draw_indicator__(transposed_x)
        self.__draw_outline__()

        self.current_value = value_float

        return self._working_surface, self._direct_rect