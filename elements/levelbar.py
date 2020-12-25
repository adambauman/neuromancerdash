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
        self.dash_data = None
        self.value_bar_fill = Color.windows_cyan_1
        self.range_bar_fill = Color.windows_cyan_1_dark
        self.outline_color = Color.grey_75
        self.outline_thickness = 2
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
    _working_surface = None
    _outline = None
    _minmax_history = None
    _direct_rect = None

    current_value = None
    min_history = None
    max_history = None

    def __init__(self, bar_graph_config, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != bar_graph_config.size)

        self._config = bar_graph_config
        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
            self._direct_rect = direct_rect
        else:
            self._working_surface = pygame.Surface(self._config.size, surface_flags)

        self.__setup_bargraph__(surface_flags)

    def __setup_levelbar__(self, surface_flags):
        assert(self._config is not None)

        # Use actual data field minmax if it's present in the config
        if None != self._config.dash_data:
            self._config.value_range = (self._config.dash_data.min_value, self._config.dash_data.max_value)

            outline_working = pygame.Surface(self._working_surface.get_size(), pygame.SRCALPHA)
            outline_working.fill(self._config.outline_color)
            inner_erase_size =\
                (outline_working.get_width() - (self._config.outline_thickness * 2),


    def draw_update(self, value):
        assert(self._working_surface is not None)
        assert(self._static_overlay_surface is not None)
        


        return self._working_surface, self._direct_rect