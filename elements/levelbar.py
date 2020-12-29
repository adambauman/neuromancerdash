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
    def __init__(self, size, font=None):
        assert(2 == len(size))

        self.size = size
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
    _outline_rect = None
    _minmax_history = None
    _direct_rect = None

    base_size = None
    current_value = None
    min_history = None
    max_history = None

    def __init__(self, bar_graph_config, data_field, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != bar_graph_config.size)
        assert(data_field)

        self._config = bar_graph_config
        self._data_field = data_field
        self.base_size = self._config.size

        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
            self._direct_rect = direct_rect
        else:
            self._working_surface = pygame.Surface(self._config.size, surface_flags)

        self.__setup_levelbar__(surface_flags)

    def __setup_levelbar__(self, surface_flags):
        assert(self._config)
        assert(self._data_field)

        # Setup rect for the outline. 
        outline_origin = ((self._config.outline_thickness, self._config.outline_thickness))
        outline_size = (
            self._working_surface.get_width() - (self._config.outline_thickness * 2),
            self._working_surface.get_height() - (self._config.outline_thickness * 2))
        self._outline_rect = pygame.Rect(outline_origin, outline_size)
        self._outline = pygame.Surface(self._working_surface.get_size(), pygame.SRCALPHA)
        self._outline.fill((0,0,0,0))
        pygame.draw.rect(
            self._outline, 
            self._config.outline_color, 
            self._outline_rect, self._config.outline_thickness, self._config.outline_radius)

    def set_direct_draw(self, direct_surface, direct_rect):
        # Draw element directly to a subsurface of the direct_surface
        assert(direct_surface)
        assert(0 != direct_rect[2] and 0 != direct_rect[3])

        self._working_surface = direct_surface.subsurface(direct_rect)
        self._direct_rect = direct_rect

    def draw_update(self, value):
        assert(self._working_surface)
        assert(self._outline)
        
        self._working_surface.blit(self._outline, (0, 0))

        return self._working_surface, self._direct_rect