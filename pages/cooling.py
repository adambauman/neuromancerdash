#
# cooling.py - Contains layout, configurations, and update routines for cooling info page
# =======================================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame, pygame.freetype

import os
from copy import copy

from data.units import Unit, Units
from data.dataobjects import DataField, DashData

from elements.styles import Color, AssetPath, FontPaths
from elements.bargraph import BarGraph, BarGraphConfig
from elements.text import  TemperatureHumidity

from elements.helpers import Helpers

if __debug__:
    import traceback

class CoolingConfigs:

    def __init__(self, base_font=None):

        fan_base_rpm_range = (300, 2000)
        base_fan_bar_config = BarGraphConfig((140, 20), fan_base_rpm_range, base_font)
        base_fan_bar_config.unit_draw = True
        base_fan_bar_config.current_value_draw = True
        
        # On Neuromancer AIDA64 is has mixed some of these assignments up (verified by looking directly at the
        #   app data), here are the actual assignemnts:
        # chassis_1_fan = front intakes combined
        # chassis_2_fan = bottom intakes
        # chassis_3_fan = rear exhaust
        # cpu_opt = forward exhaust

        self.rear_exhaust_bar = copy(base_fan_bar_config)
        self.rear_exhaust_bar.dash_data = DashData.chassis_3_fan

        self.forward_exhaust_bar = copy(base_fan_bar_config)
        self.forward_exhaust_bar.dash_data = DashData.cpu_opt_fan
        
        self.front_intake_fan_bar = copy(base_fan_bar_config)
        self.front_intake_fan_bar.size = (110, 20)
        self.front_intake_fan_bar.dash_data = DashData.chassis_1_fan

        self.bottom_intake_fan_bar = copy(base_fan_bar_config)
        self.bottom_intake_fan_bar.size = (110, 20)
        self.bottom_intake_fan_bar.background_color = Color.grey_20
        self.bottom_intake_fan_bar.foreground_color = Color.grey_40
        self.bottom_intake_fan_bar.dash_data = DashData.chassis_2_fan

        self.cpu_fan_bar = copy(base_fan_bar_config)
        self.cpu_fan_bar.size = (100, 20)
        self.cpu_fan_bar.dash_data = DashData.cpu_fan

        self.gpu_fan_bar = copy(base_fan_bar_config)
        self.gpu_fan_bar.dash_data = DashData.gpu_fan

class CoolingPositions:

    def __init__(self, display_size, cooling_configs):
        assert(0 != display_size[0] and 0 != display_size[1])

        # Upper exahust fans centered and spaced from each other
        exhaust_fans_bars_width = cooling_configs.rear_exhaust_bar.size[0]
        exhaust_fans_bars_spacing = 20
        #exhaust_fans_bars_combined_width = (exhaust_fans_bars_width * 2) + exhaust_fans_bars_spacing
        #exhaust_fans_x = (display_size[0] / 2) - (exhaust_fans_bars_combined_width / 2)
        exhaust_fans_x = 20
        exhaust_fans_y = 50

        self.rear_exhaust_fan_bar = pygame.Rect(exhaust_fans_x, exhaust_fans_y, 110, 20)
        forward_exhaust_fan_x = exhaust_fans_x + exhaust_fans_bars_width + exhaust_fans_bars_spacing
        self.forward_exhaust_fan_bar = pygame.Rect(forward_exhaust_fan_x, exhaust_fans_y, 110, 20)
        self.front_intake_fan_bar = pygame.Rect(350, 80, 110, 20)
        self.bottom_intake_fan_bar = pygame.Rect(190, 250, 110, 20)
        self.cpu_fan_bar = pygame.Rect(70, 130, 110, 20)
        self.gpu_fan_bar = pygame.Rect(70, 180, 110, 20)

        self.temperature_humidity_rect = pygame.Rect(406, 180, 74, 56)


class Cooling:
    _working_surface = None
    _background = None
    _surface_flags = None

    def __init__(self, base_size, direct_surface=None, direct_rect=None, surface_flags=0):
        assert(0 != base_size[0] and 0 != base_size[1])

        if direct_surface and direct_rect is not None:
            self._working_surface = direct_surface.subsurface(direct_rect)
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

        self._font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        self._font_normal.kerning = True

        if __debug__:
            self._background = pygame.image.load(os.path.join(AssetPath.backgrounds, "480_320_grid.png")).convert_alpha()
            self._working_surface.blit(self._background, (0,0))

        # TODO: (Adam) 2020-12-11 Pass in a shared fonts object, lots of these controls have their own
        #           font instances. Would cut down on memory usage and make it easier to match font styles.

        element_configs = CoolingConfigs(self._font_normal)
        element_positions = CoolingPositions(base_size, element_configs)

        self._rear_exhaust_fan_bar = BarGraph(
            element_configs.rear_exhaust_bar, self._working_surface, element_positions.rear_exhaust_fan_bar)
        self._forward_exhaust_fan_bar = BarGraph(
            element_configs.forward_exhaust_bar, self._working_surface, element_positions.forward_exhaust_fan_bar)
        self._cpu_fan_bar = BarGraph(
            element_configs.cpu_fan_bar, self._working_surface, element_positions.cpu_fan_bar)
        self._gpu_fan_bar = BarGraph(
            element_configs.gpu_fan_bar, self._working_surface, element_positions.gpu_fan_bar)
        self._front_intake_fan_bar = BarGraph(
            element_configs.front_intake_fan_bar, self._working_surface, element_positions.front_intake_fan_bar)
        self._bottom_intake_fan_bar = BarGraph(
            element_configs.bottom_intake_fan_bar, self._working_surface, element_positions.bottom_intake_fan_bar)

        self._temperature_humidity = TemperatureHumidity(element_positions.temperature_humidity_rect)
    
    #def __draw_intake_fans__(self, value):
    #    # Draw two bars matching the exhaust style, flip 90 CCW
    #    single_intake_bar = self.__front_intake_fan_bar.draw_update(value)
    #    fan_spacing = 20
    #    dual_surface_size = ((single_intake_bar.get_width() * 2) + fan_spacing, single_intake_bar.get_height())
    #    dual_fan_surface = pygame.Surface(dual_surface_size, self.__surface_flags)
    #    dual_fan_surface.blit(single_intake_bar, (0,0))
    #    dual_fan_surface.blit(single_intake_bar, (single_intake_bar.get_width() + fan_spacing, 0))
        
    #    return pygame.transform.rotozoom(dual_fan_surface, 90, 1)

    def draw_update(self, aida64_data, dht22_data=None, redraw_all=False):
        assert(0 != len(aida64_data))

        if None != self._background:
            self._working_surface.blit(self._background, (0, 0))
        else:
            self._working_surface.fill(Color.black)

        # chassis_1_fan = front intakes combined
        # chassis_2_fan = bottom intakes
        # chassis_3_fan = rear exhaust
        # cpu_opt = forward exhaust

        update_rects = []

        # Fan bar graphs
        rear_exhaust_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_3_fan, "0")
        update_rects.append(self._rear_exhaust_fan_bar.draw_update(rear_exhaust_fan_value)[1])

        forward_exhaust_fan_value = DashData.best_attempt_read(aida64_data, DashData.cpu_opt_fan, "0")
        update_rects.append(self._forward_exhaust_fan_bar.draw_update(forward_exhaust_fan_value)[1])

        #front_intake_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")
        #self.__working_surface.blit(
        #    self.__draw_intake_fans__(front_intake_fan_value),
        #    self.__element_positions.front_intake_fan_bar)

        bottom_intake_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_2_fan, "0")
        update_rects.append(self._bottom_intake_fan_bar.draw_update(bottom_intake_fan_value)[1])

        cpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")
        update_rects.append(self._cpu_fan_bar.draw_update(cpu_fan_value)[1])

        gpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")
        update_rects.append(self._gpu_fan_bar.draw_update(gpu_fan_value)[1])

        # Ambient temperature and humidity
        if dht22_data is not None:
            update_rects.append(self._temperature_humidity.draw_update(dht22_data)[1])

        return self._working_surface, update_rects
