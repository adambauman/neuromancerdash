#
# systemstats.py - Contains layout, configurations, and update routines for the SystemStats page
# ==============================================================================================
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

class SystemStatsConfigs:

    def __init__(self, base_font):

        ### Fonts
        self.__font_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 16)
        self.__font_gauge_value.strong = True
        self.__fan_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 10)
        #self.fan_gauge_value.strong = True

        ### Configurations
        self.core_visualizer = CoreVisualizerConfig(8)

        self.cpu_graph = LineGraphConfig(70, 300, DashData.cpu_util)
        self.cpu_graph.display_background = True
        self.gpu_graph = LineGraphConfig(70, 300, DashData.gpu_util)
        self.gpu_graph.display_background = True

        self.sys_memory_bar = BarGraphConfig((300, 25), (0, 32768), base_font)
        self.sys_memory_bar.dash_data = DashData.sys_ram_used
        self.sys_memory_bar.unit_draw = True
        self.sys_memory_bar.max_value_draw = True
        self.sys_memory_bar.current_value_draw = True

        self.gpu_memory_bar = BarGraphConfig((300,25), (0, 10240), base_font)
        self.gpu_memory_bar.dash_data = DashData.gpu_ram_used
        self.gpu_memory_bar.unit_draw = True
        self.gpu_memory_bar.max_value_draw = True
        self.gpu_memory_bar.current_value_draw = True

        self.cpu_temp_gauge = GaugeConfig(DashData.cpu_temp, 45, self.__font_gauge_value, (35, 70))
        self.cpu_temp_gauge.show_unit_symbol = False
        self.gpu_temp_gauge = GaugeConfig(DashData.gpu_temp, 45, self.__font_gauge_value, (35, 70))
        self.gpu_temp_gauge.show_unit_symbol = False 

        self.fps_graph = LineGraphConfig(70, 200, DashData.rtss_fps)
        self.fps_graph.display_background = True
        self.fps_graph.draw_on_zero = False

        # NOTE: (Adam) On Neuromancer AIDA64 has fans a bit mixed up
        # Base for chassis fans
        case_fan_base = GaugeConfig(DashData.cpu_opt_fan, 20, self.__fan_gauge_value, (17, 29))
        case_fan_base.arc_main_color = Color.grey_40
        case_fan_base.needle_color = Color.white
        case_fan_base.bg_color = Color.black
        case_fan_base.counter_sweep = True
        case_fan_base.show_unit_symbol = False
        case_fan_base.show_label_instead_of_value = True

        # FAN1 = Front intakes combines
        self.fan1_gauge = copy(case_fan_base)
        self.fan1_gauge.data_field = DashData.chassis_1_fan
        self.fan1_gauge.label = "I"

        # FAN2 = Drive bay intake
        # FAN3 = rear exhaust

        # CPU OPT fan = Forward exhaust
        self.fan_opt_gauge = copy(case_fan_base)
        self.fan_opt_gauge.data_field = DashData.cpu_opt_fan
        self.fan_opt_gauge.label = "E"

        self.cpu_fan_gauge = copy(case_fan_base)
        self.cpu_fan_gauge.data_field = DashData.cpu_fan
        self.cpu_fan_gauge.label = "C"

        self.gpu_fan_gauge = copy(case_fan_base)
        self.gpu_fan_gauge.data_field = DashData.gpu_fan
        self.gpu_fan_gauge.label = "G"


class SystemStatsPositions:

    def __init__(self, width, height):
        assert(0 != width and 0 != height)

        self.cpu_graph = (0, 0)
        self.sys_memory = (0, 75)
        self.gpu_graph = (0, 110)
        self.gpu_memory = (0, 185)

        self.core_visualizer = (310, 0)

        self.cpu_details_rect = pygame.Rect(310, 33, 74, 72)
        self.gpu_details_rect = pygame.Rect(310, 114, 74, 102)

        self.cpu_temp_gauge = (width-90, 7)
        self.gpu_temp_gauge = (width-90, 117, 90, 90)

        self.fps_graph = (0, 230)
        self.fps_text_rect = pygame.Rect(210, 240, 98, 62)

        self.temperature_humidity_rect = pygame.Rect(self.cpu_details_rect[0], 240, 74, 56)

        self.fan1_gauge = (self.cpu_temp_gauge[0], 230)
        self.fan_opt_gauge = (width - 40, 230)
        self.cpu_fan_gauge = (self.cpu_temp_gauge[0], 275)
        self.gpu_fan_gauge = (self.fan_opt_gauge[0], self.cpu_fan_gauge[1])
        self.mobo_temp_rect = pygame.Rect(width-52, 268, 18, 16)

        self.network_info = pygame.Rect(0, height-18, 290, 18)
        self.clock = pygame.Rect(self.cpu_details_rect[0], height-18, 70, 18)

class SystemStats:
    __background = None
    __base_size = None

    def __init__(self, width, height):
        assert(0 != width and 0 != height)

        self.__base_size = (width, height)
        self.__working_surface = pygame.Surface(self.__base_size, pygame.SRCALPHA)

        self.font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        #font_normal.strong = True
        self.font_normal.kerning = True

        if __debug__:
            self.__background = pygame.image.load(os.path.join(AssetPath.backgrounds, "480_320_grid.png"))
            self.__working_surface.blit(self.__background, (0,0))

        # TODO: (Adam) 2020-12-11 Pass in a shared fonts object, lots of these controls have their own
        #           font instances. Would cut down on memory usage and make it easier to match font styles.

        self.__element_configs = SystemStatsConfigs(self.font_normal)
        self.__element_positions = SystemStatsPositions(width, height)

        self.__sys_memory_bar = BarGraph(self.__element_configs.sys_memory_bar)
        self.__gpu_memory_bar = BarGraph(self.__element_configs.gpu_memory_bar)
        self.__cpu_graph = LineGraphReverse(self.__element_configs.cpu_graph)
        self.__gpu_graph = LineGraphReverse(self.__element_configs.gpu_graph)

        self.__core_visualizer = SimpleCoreVisualizer(self.__element_configs.core_visualizer)
        self.__cpu_details = CPUDetails(self.__element_positions.cpu_details_rect)
        self.__gpu_details = GPUDetails(self.__element_positions.gpu_details_rect)
        self.__cpu_temp_gauge = FlatArcGauge(self.__element_configs.cpu_temp_gauge)
        self.__gpu_temp_gauge = FlatArcGauge(self.__element_configs.gpu_temp_gauge)

        self.__fps_graph = LineGraphReverse(self.__element_configs.fps_graph)
        self.__fps_text = FPSText(self.__element_positions.fps_text_rect, self.__working_surface)

        self.__temperature_humidity = TemperatureHumidity(
            self.__element_positions.temperature_humidity_rect, self.__working_surface)

        # TODO: (Adam) 2020-12-11 Address slight red tinge around diameter when viewed on larger displays
        self.__fan1_gauge = FlatArcGauge(self.__element_configs.fan1_gauge)
        self.__fan_opt_gauge = FlatArcGauge(self.__element_configs.fan_opt_gauge)
        self.__cpu_fan_gauge = FlatArcGauge(self.__element_configs.cpu_fan_gauge)
        self.__gpu_fan_gauge = FlatArcGauge(self.__element_configs.gpu_fan_gauge)
        self.__mobo_temperature = MotherboardTemperature(
            self.__element_positions.mobo_temp_rect, self.__working_surface)

        self.__network_info = NetworkInformation(
            self.__element_positions.network_info, self.__working_surface)

        self.__clock = BasicClock(
            self.__element_positions.clock, self.__working_surface)


    def draw_update(self, aida64_data, dht22_data=None):
        assert(0 != len(aida64_data))

        if None != self.__background:
            self.__working_surface.blit(self.__background, (0, 0))
        else:
            self.__working_surface.fill(Color.black)

        # CPU and GPU Utilization
        self.__working_surface.blit(
            self.__cpu_graph.update(DashData.best_attempt_read(aida64_data, DashData.cpu_util, "0")),
            self.__element_positions.cpu_graph)

        self.__working_surface.blit(
            self.__gpu_graph.update(DashData.best_attempt_read(aida64_data, DashData.gpu_util, "0")),
            self.__element_positions.gpu_graph)

        # System and GPU memory usage
        self.__working_surface.blit(
            self.__sys_memory_bar.draw_update(DashData.best_attempt_read(aida64_data, DashData.sys_ram_used, "0")),
            self.__element_positions.sys_memory)

        self.__working_surface.blit(
            self.__gpu_memory_bar.draw_update(DashData.best_attempt_read(aida64_data, DashData.gpu_ram_used, "0")),
            self.__element_positions.gpu_memory)

        # CPU Core Visualizer
        self.__working_surface.blit(
            self.__core_visualizer.update(aida64_data),
            self.__element_positions.core_visualizer)

        # CPU and GPU Details
        self.__working_surface.blit(
            self.__cpu_details.draw_update(aida64_data),
            (self.__element_positions.cpu_details_rect[0], self.__element_positions.cpu_details_rect[1]))

        self.__working_surface.blit(
            self.__gpu_details.draw_update(aida64_data),
            (self.__element_positions.gpu_details_rect[0], self.__element_positions.gpu_details_rect[1]))

        # CPU Temperature Gauge
        cpu_temperature = DashData.best_attempt_read(aida64_data, DashData.cpu_temp, "0")
        #if self.__cpu_temp_gauge.current_value != cpu_temperature or redraw_all:
        self.__working_surface.blit(
            self.__cpu_temp_gauge.draw_update(cpu_temperature),
            self.__element_positions.cpu_temp_gauge)

        # GPU Temperature Gauge
        gpu_temperature = DashData.best_attempt_read(aida64_data, DashData.gpu_temp, "0")
        self.__working_surface.blit(
            self.__gpu_temp_gauge.draw_update(gpu_temperature),
            self.__element_positions.gpu_temp_gauge)

        # FPS Graph and Text
        fps_value = DashData.best_attempt_read(aida64_data, DashData.rtss_fps, "0")
        self.__working_surface.blit(self.__fps_graph.update(fps_value), self.__element_positions.fps_graph)
        self.__working_surface.blit(
            self.__fps_text.draw_update(fps_value),
            (self.__element_positions.fps_text_rect[0], self.__element_positions.fps_text_rect[1]))

        # Ambient temperature and humidity
        if None != dht22_data:
            self.__working_surface.blit(
                self.__temperature_humidity.draw_update(dht22_data),
                (self.__element_positions.temperature_humidity_rect[0], self.__element_positions.temperature_humidity_rect[1]))

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
        self.__working_surface.blit(
            self.__mobo_temperature.draw_update(mobo_temperature_value),
            (self.__element_positions.mobo_temp_rect[0], self.__element_positions.mobo_temp_rect[1]))

        # Network Info
        nic1_down_value = DashData.best_attempt_read(aida64_data, DashData.nic1_download_rate, "0")
        nic1_up_value = DashData.best_attempt_read(aida64_data, DashData.nic1_upload_rate, "0")
        self.__working_surface.blit(
            self.__network_info.draw_update(nic1_down_value, nic1_up_value),
            (self.__element_positions.network_info[0], self.__element_positions.network_info[1]))

        # Clock
        self.__working_surface.blit(
           self.__clock.draw_update(),
           (self.__element_positions.clock[0], self.__element_positions.clock[1]))

        return self.__working_surface
