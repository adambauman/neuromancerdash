#
# page02.py - Contains layout, configurations, and update routines for Page02
# ===========================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame, pygame.freetype

import os

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

class Page02ElementConfigurations:

    def __init__(self):

        ### Fonts
        self.__font_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 16)
        self.__font_gauge_value.strong = True
        self.__fan_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 10)
        self.fan_gauge_value.strong = True

        # FAN1 = Rear exhaust
        self.fan1_gauge = GaugeConfig(DashData.chassis_1_fan, 20, self.__fan_gauge_value, (17, 29))
        self.fan1_gauge.arc_main_color = Color.grey_40
        self.fan1_gauge.needle_color = Color.white
        self.fan1_gauge.bg_color = Color.black
        self.fan1_gauge.counter_sweep = True
        self.fan1_gauge.show_unit_symbol = False
        self.fan1_gauge.show_label_instead_of_value = True
        self.fan1_gauge.label = "E"

        # FAN2 = Drive bay intake
        # FAN3 = Front exhaust

        # CPU OPT fan = Front intakes (combined)
        self.fan_opt_gauge = GaugeConfig(DashData.cpu_opt_fan, 20, self.__fan_gauge_value, (17, 29))
        self.fan_opt_gauge.arc_main_color = Color.grey_40
        self.fan_opt_gauge.needle_color = Color.white
        self.fan_opt_gauge.bg_color = Color.black
        self.fan_opt_gauge.counter_sweep = True
        self.fan_opt_gauge.show_unit_symbol = False
        self.fan_opt_gauge.show_label_instead_of_value = True
        self.fan_opt_gauge.label = "I"

        self.cpu_fan_gauge = GaugeConfig(DashData.cpu_fan, 20, self.__fan_gauge_value, (17, 29))
        self.cpu_fan_gauge.arc_main_color = Color.grey_40
        self.cpu_fan_gauge.needle_color = Color.white
        self.cpu_fan_gauge.bg_color = Color.black
        self.cpu_fan_gauge.counter_sweep = True
        self.cpu_fan_gauge.show_unit_symbol = False
        self.cpu_fan_gauge.show_label_instead_of_value = True
        self.cpu_fan_gauge.label = "C"

        self.gpu_fan_gauge = GaugeConfig(DashData.gpu_fan, 20, self.__fan_gauge_value, (17, 29))
        self.gpu_fan_gauge.arc_main_color = Color.grey_40
        self.gpu_fan_gauge.needle_color = Color.white
        self.gpu_fan_gauge.bg_color = Color.black
        self.gpu_fan_gauge.counter_sweep = True
        self.gpu_fan_gauge.show_unit_symbol = False
        self.gpu_fan_gauge.show_label_instead_of_value = True
        self.gpu_fan_gauge.label = "G"

class Page02ElementPositions:

    def __init__(self, width, height):
        assert(0 != width and 0 != height)

        self.temperature_humidity_rect = pygame.Rect(self.cpu_details_rect[0], 240, 74, 56)

        self.fan1_gauge = (self.cpu_temp_gauge[0], 230)
        self.fan_opt_gauge = (width - 40, 230)
        self.cpu_fan_gauge = (self.cpu_temp_gauge[0], 275)
        self.gpu_fan_gauge = (self.fan_opt_gauge[0], self.cpu_fan_gauge[1])
        self.mobo_temp_rect = pygame.Rect(width-52, 268, 18, 16)

class Page02:
    __background = None

    def __init__(self, width, height):
        assert(0 != width and 0 != height)

        self.__working_surface = pygame.Surface((width, height))

        self.font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        #font_normal.strong = True
        self.font_normal.kerning = True

        if __debug__:
            self.__background = pygame.image.load(os.path.join(AssetPath.backgrounds, "480_320_grid.png"))
            self.__working_surface.blit(self.__background, (0,0))

        # TODO: (Adam) 2020-12-11 Pass in a shared fonts object, lots of these controls have their own
        #           font instances. Would cut down on memory usage and make it easier to match font styles.

        self.__element_positions = Page01ElementPositions(width, height)
        self.__element_configs = Page01ElementConfigurations()

        self.__temperature_humidity = TemperatureHumidity(
            self.__element_positions.temperature_humidity_rect, self.__working_surface)

        # TODO: (Adam) 2020-12-11 Address slight red tinge around diameter when viewed on larger displays
        self.__fan1_gauge = FlatArcGauge(self.__element_configs.fan1_gauge)
        self.__fan_opt_gauge = FlatArcGauge(self.__element_configs.fan_opt_gauge)
        self.__cpu_fan_gauge = FlatArcGauge(self.__element_configs.cpu_fan_gauge)
        self.__gpu_fan_gauge = FlatArcGauge(self.__element_configs.gpu_fan_gauge)
        self.__mobo_temperature = MotherboardTemperature(
            self.__element_positions.mobo_temp_rect, self.__working_surface)


    def draw_update(self, aida64_data, dht22_data=None):
        assert(0 != len(aida64_data))

        # Fan gauges
        self.__working_surface.blit(
            self.__fan1_gauge.draw_update(DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")),
            self.__element_positions.fan1_gauge)
        self.__working_surface.blit(
            self.__fan_opt_gauge.draw_update(DashData.best_attempt_read(aida64_data, DashData.cpu_opt_fan, "0")),
            self.__element_positions.fan_opt_gauge)
        self.__working_surface.blit(
            self.__cpu_fan_gauge.draw_update(DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")),
            self.__element_positions.cpu_fan_gauge)
        self.__working_surface.blit(
            self.__gpu_fan_gauge.draw_update(DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")),
            self.__element_positions.gpu_fan_gauge)

        # Motherboard temp (nestled between all the fans)
        mobo_temperature_value = DashData.best_attempt_read(aida64_data, DashData.motherboard_temp, "0")
        if self.__mobo_temperature.current_value != mobo_temperature_value:
            self.__working_surface.blit(
                self.__mobo_temperature.draw_update(mobo_temperature_value),
                (self.__element_positions.mobo_temp_rect[0], self.__element_positions.mobo_temp_rect[1]))

        return self.__working_surface
