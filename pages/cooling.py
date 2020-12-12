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
from elements.gauge import FlatArcGauge, GaugeConfig 
from elements.bargraph import BarGraph, BarGraphConfig
from elements.linegraph import LineGraphReverse, LineGraphConfig
from elements.visualizers import SimpleCoreVisualizer, CoreVisualizerConfig
from elements.text import FPSText, CPUDetails, GPUDetails, TemperatureHumidity, MotherboardTemperature, NetworkInformation, BasicClock

from elements.helpers import Helpers

if __debug__:
    import traceback

class CoolingConfigs:

    def __init__(self, base_font=None):

        fan_base_rpm_range = (300, 2000)
        base_fan_bar_config = BarGraphConfig((150, 20), fan_base_rpm_range, base_font)
        base_fan_bar_config.unit_draw = True
        base_fan_bar_config.current_value_draw = True
        
        self.rear_exhaust_bar = copy(base_fan_bar_config)
        self.rear_exhaust_bar.dash_data = DashData.chassis_1_fan

        self.forward_exhaust_bar = copy(base_fan_bar_config)
        self.forward_exhaust_bar.dash_data = DashData.chassis_3_fan

        self.cpu_fan_bar = copy(base_fan_bar_config)
        self.cpu_fan_bar.size = ((100, 20))
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

        self.rear_exhaust_fan_bar = (exhaust_fans_x, exhaust_fans_y)
        self.forward_exhaust_fan_bar = (exhaust_fans_x + exhaust_fans_bars_width + exhaust_fans_bars_spacing, exhaust_fans_y)
        self.cpu_fan_bar = (70, 130)
        self.gpu_fan_bar = (70, 180)

class Cooling:
    __background = None

    def __init__(self, width, height):
        assert(0 != width and 0 != height)

        self.__working_surface = pygame.Surface((width, height))

        self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        self.__font_normal.kerning = True

        if __debug__:
            self.__background = pygame.image.load(os.path.join(AssetPath.backgrounds, "480_320_grid.png"))
            self.__working_surface.blit(self.__background, (0,0))


        # TODO: (Adam) 2020-12-11 Pass in a shared fonts object, lots of these controls have their own
        #           font instances. Would cut down on memory usage and make it easier to match font styles.

        self.__element_configs = CoolingConfigs(self.__font_normal)
        self.__element_positions = CoolingPositions((width, height), self.__element_configs)

        self.__rear_exhaust_fan_bar = BarGraph(self.__element_configs.rear_exhaust_bar)
        self.__forward_exhaust_fan_bar = BarGraph(self.__element_configs.forward_exhaust_bar)
        self.__cpu_fan_bar = BarGraph(self.__element_configs.cpu_fan_bar)
        self.__gpu_fan_bar = BarGraph(self.__element_configs.gpu_fan_bar)


    def draw_update(self, aida64_data, dht22_data=None, redraw_all=False):
        assert(0 != len(aida64_data))

        if None != self.__background:
            self.__working_surface.blit(self.__background, (0, 0))
        else:
            self.__working_surface.fill(Color.black)

        # Fan bar graphs
        rear_exhaust_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")
        self.__working_surface.blit(
            self.__rear_exhaust_fan_bar.draw_update(rear_exhaust_fan_value), 
            self.__element_positions.rear_exhaust_fan_bar)

        forward_exhaust_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_3_fan, "0")
        self.__working_surface.blit(
            self.__forward_exhaust_fan_bar.draw_update(forward_exhaust_fan_value), 
            self.__element_positions.forward_exhaust_fan_bar)

        cpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")
        self.__working_surface.blit(
            self.__cpu_fan_bar.draw_update(cpu_fan_value),
            self.__element_positions.cpu_fan_bar)

        gpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")
        self.__working_surface.blit(
            self.__gpu_fan_bar.draw_update(gpu_fan_value),
            self.__element_positions.gpu_fan_bar)

        return self.__working_surface
