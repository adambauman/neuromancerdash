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
    def __init__(self, size, value_range, font=None):
        assert(2 == len(size) and 2 == len(value_range))

        self.size = size
        self.value_range = value_range
        self.value_bar_fill = Color.windows_cyan_1
        self.range_bar_fill = Color.windows_cyan_1_dark
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
    _config = None
    _data_field = None

    _working_surface = None
    _outline = None
    _minmax_history = None
    _outline_rect = None
    _direct_rect = None

    current_value = None
    min_history = None
    max_history = None

    def __init__(self, bar_graph_config, data_field, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != bar_graph_config.size)
        assert(data_field)

        self._config = bar_graph_config
        self._data_field = data_field
        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
            self._direct_rect = direct_rect
        else:
            self._working_surface = pygame.Surface(self._config.size, surface_flags)

        self.__setup_bargraph__(surface_flags)

    def __setup_levelbar__(self, surface_flags):
        assert(self._config)
        assert(self._data_field)

        # Setup rect for the outline. P
        outline_origin = (
            self._config.size[0] + self._config.outline_thickness, 
            self._config.size[1] + self._config.outline_thickness)
        outline_size = (
            self._working_surface.get_width() - (self._config.outline_thickness * 2),
            self._working_surface.get_height() - (self._config.outline_thickness * 2))
        outline_rect = pygame.Rect(outline_origin, )


    def draw_update(self, value):
        assert(self._working_surface is not None)
        assert(self._static_overlay_surface is not None)
        


        return self._working_surface, self._direct_rect