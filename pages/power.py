#
# power.py - Contains layout, configurations, and update routines for power info page
# =======================================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

import os
from copy import copy

from data.units import Unit, Units
from data.dataobjects import DataField, DashData

from elements.helpers import Helpers
from elements.styles import Color, AssetPath, FontPath

if __debug__:
    import traceback

class PowerConfigs:

    def __init__(self, base_font=None):

        

class PowerPositions:

    def __init__(self, display_size, element_configs):
        assert(0 != display_size[0] and 0 != display_size[1])




class Power:
    _working_surface = None
    _background = None
    _surface_flags = None

    def __init__(self, base_size, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != base_size)

        self._surface_flags = surface_flags
        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

        self._font_normal = pygame.freetype.Font(FontPath.fira_code_semibold(), 12)
        self._font_normal.kerning = True

        element_configs = PowerConfigs(self._font_normal)
        self._element_positions = PowerPositions(base_size, element_configs)


    def draw_update(self, aida64_data, dht22_data=None, redraw_all=False):

        assert(0 != len(aida64_data))

        

        return self._working_surface, update_rects
