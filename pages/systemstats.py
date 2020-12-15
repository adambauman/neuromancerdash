#
# systemstats.py - Contains layout, configurations, and update routines for the SystemStats page
# ==============================================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame, pygame.freetype

import os
from copy import copy
#from threading import Thread
from datetime import datetime

from data.units import Unit, Units
from data.dataobjects import DataField, DashData

from elements.styles import Color, AssetPath, FontPaths
from elements.gauge import FlatArcGauge, GaugeConfig 
from elements.bargraph import BarGraph, BarGraphConfig
from elements.linegraph import LineGraphReverse, LineGraphConfig
from elements.visualizers import SimpleCoreVisualizer, CoreVisualizerConfig
from elements.text import FPSText, CPUDetails, GPUDetails, TemperatureHumidity, NetworkInformation, SimpleText

from elements.helpers import Helpers

if __debug__:
    import traceback

class SystemStatsConfigs:

    def __init__(self, base_font):

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

        self.cpu_temp_gauge = GaugeConfig(DashData.cpu_temp, 45, value_font_size=16, value_font_origin=(35, 70))
        self.cpu_temp_gauge.show_unit_symbol = False
        self.gpu_temp_gauge = GaugeConfig(DashData.gpu_temp, 45, value_font_size=16, value_font_origin=(35, 70))
        self.gpu_temp_gauge.show_unit_symbol = False 

        self.fps_graph = LineGraphConfig(70, 200, DashData.rtss_fps)
        self.fps_graph.display_background = True
        self.fps_graph.draw_on_zero = False

        # NOTE: (Adam) On Neuromancer AIDA64 has fans a bit mixed up
        # Base for chassis fans
        case_fan_base = GaugeConfig(DashData.cpu_opt_fan, 20, value_font_size=10, value_font_origin=(17, 29))
        case_fan_base.arc_main_color = Color.grey_40
        case_fan_base.needle_color = Color.white
        case_fan_base.bg_color = Color.black
        case_fan_base.counter_sweep = True
        case_fan_base.show_unit_symbol = False
        case_fan_base.show_label_instead_of_value = True
        case_fan_base.draw_shadow = False

        # FAN1 = Front intakes combines
        self.fan1_gauge = copy(case_fan_base)
        self.fan1_gauge.data_field = DashData.chassis_1_fan
        self.fan1_gauge.label = "I"

        # FAN2 = Bottom intake
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

        self.cpu_graph = pygame.Rect(0, 0, 300, 70)
        self.sys_memory = pygame.Rect(0, 75, 300, 25)
        self.gpu_graph = pygame.Rect(0, 110, 300, 70)
        self.gpu_memory = pygame.Rect(0, 185, 300, 25)

        # Core visualizer is dynamic based on config and number of cores, you will have to
        # fiddle with the rect dimensions if modifying those values.
        self.core_visualizer = pygame.Rect(310, 0, 58, 28)

        self.cpu_details_rect = pygame.Rect(310, 33, 74, 72)
        self.gpu_details_rect = pygame.Rect(310, 114, 74, 102)

        self.cpu_temp_gauge = pygame.Rect(width-90, 7, 90, 90)
        self.gpu_temp_gauge = pygame.Rect(width-90, 117, 90, 90)

        self.fps_graph = pygame.Rect(0, 230, 200, 70)
        self.fps_text_rect = pygame.Rect(210, 240, 98, 62)

        self.temperature_humidity_rect = pygame.Rect(self.cpu_details_rect[0], 240, 74, 56)

        self.fan1_gauge = pygame.Rect(self.cpu_temp_gauge[0], 230, 40, 40)
        self.fan_opt_gauge = pygame.Rect(width - 40, 230, 40, 40)
        self.cpu_fan_gauge = pygame.Rect(self.cpu_temp_gauge[0], 275, 40, 40)
        self.gpu_fan_gauge = pygame.Rect(self.fan_opt_gauge[0], self.cpu_fan_gauge[1], 40, 40)
        self.mobo_temp_rect = pygame.Rect(width-52, 268, 14, 14)

        self.network_info = pygame.Rect(0, height-12, 300, 12)
        self.clock = pygame.Rect(self.cpu_details_rect[0], height-12, 70, 12)

class SystemStats:
    __background = None
    __base_size = None
    __using_direct_surface = False

    def __init__(self, width, height, direct_surface=None, surface_flags=0):
        assert(0 != width and 0 != height)

        self.__base_size = (width, height)
        if None != direct_surface:
            self.__working_surface = direct_surface
            self.__using_direct_surface = True
        else:
            self.__working_surface = pygame.Surface(self.__base_size, surface_flags)
            self.__using_direct_surface = False

        self.font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        self.font_normal.kerning = True

        if __debug__:
            self.__background = pygame.image.load(os.path.join(AssetPath.backgrounds, "480_320_grid.png"))
            self.__working_surface.blit(self.__background, (0,0))

        # TODO: (Adam) 2020-12-11 Pass in a shared fonts object, lots of these controls have their own
        #           font instances. Would cut down on memory usage and make it easier to match font styles.
        
        assert(None != self.__working_surface)

        self.__element_configs = SystemStatsConfigs(self.font_normal)
        self.__element_positions = SystemStatsPositions(width, height)

        self.__sys_memory_bar = BarGraph(
            self.__element_configs.sys_memory_bar,
            self.__working_surface, self.__element_positions.sys_memory)
        self.__gpu_memory_bar = BarGraph(
            self.__element_configs.gpu_memory_bar,
            self.__working_surface, self.__element_positions.gpu_memory)

        self.__cpu_graph = LineGraphReverse(
            self.__element_configs.cpu_graph,
            self.__working_surface, self.__element_positions.cpu_graph)
        self.__gpu_graph = LineGraphReverse(
            self.__element_configs.gpu_graph,
            self.__working_surface, self.__element_positions.gpu_graph)

        self.__core_visualizer = SimpleCoreVisualizer(
            self.__element_configs.core_visualizer,
            self.__working_surface, self.__element_positions.core_visualizer)

        # NOTE: Rect and working surface are reversed from other elements
        self.__cpu_details = CPUDetails(
            self.__element_positions.cpu_details_rect, direct_surface=self.__working_surface)
        self.__gpu_details = GPUDetails(
            self.__element_positions.gpu_details_rect, direct_surface=self.__working_surface)

        self.__cpu_temp_gauge = FlatArcGauge(
            self.__element_configs.cpu_temp_gauge,
            self.__working_surface, self.__element_positions.cpu_temp_gauge)
        self.__gpu_temp_gauge = FlatArcGauge(
            self.__element_configs.gpu_temp_gauge,
            self.__working_surface, self.__element_positions.gpu_temp_gauge)

        self.__fps_graph = LineGraphReverse(
            self.__element_configs.fps_graph,
            self.__working_surface, self.__element_positions.fps_graph)
        self.__fps_text = FPSText(self.__element_positions.fps_text_rect, direct_surface=self.__working_surface)

        self.__temperature_humidity = TemperatureHumidity(self.__element_positions.temperature_humidity_rect)

        self.__fan1_gauge = FlatArcGauge(
            self.__element_configs.fan1_gauge, 
            self.__working_surface, self.__element_positions.fan1_gauge)
        self.__fan_opt_gauge = FlatArcGauge(
            self.__element_configs.fan_opt_gauge,
            self.__working_surface, self.__element_positions.fan_opt_gauge)
        self.__cpu_fan_gauge = FlatArcGauge(
            self.__element_configs.cpu_fan_gauge,
            self.__working_surface, self.__element_positions.cpu_fan_gauge)
        self.__gpu_fan_gauge = FlatArcGauge(
            self.__element_configs.gpu_fan_gauge,
            self.__working_surface, self.__element_positions.gpu_fan_gauge)

        self.__mobo_temperature = SimpleText(
            self.__element_positions.mobo_temp_rect, direct_surface=self.__working_surface)

        self.__network_info = NetworkInformation(self.__element_positions.network_info, direct_surface=self.__working_surface)
        self.__clock = SimpleText(self.__element_positions.clock, direct_surface=self.__working_surface)


    def draw_update(self, aida64_data, dht22_data=None):
        assert(0 != len(aida64_data))

        # Each element is now taking care of clearing its rect.
        #if None != self.__background:
        #    self.__working_surface.blit(self.__background, (0, 0))
        #else:
        #    self.__working_surface.fill(Color.black)

        cpu_utilization_value = DashData.best_attempt_read(aida64_data, DashData.cpu_util, "0")
        self.__cpu_graph.update(cpu_utilization_value)
        gpu_utilization_value = DashData.best_attempt_read(aida64_data, DashData.gpu_util, "0")
        self.__gpu_graph.update(gpu_utilization_value)

        cpu_temperature = DashData.best_attempt_read(aida64_data, DashData.cpu_temp, "0")
        self.__cpu_temp_gauge.draw_update(cpu_temperature)
        gpu_temperature = DashData.best_attempt_read(aida64_data, DashData.gpu_temp, "0")
        self.__gpu_temp_gauge.draw_update(gpu_temperature)

        fan1_value = DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")
        self.__fan1_gauge.draw_update(fan1_value)
        fan_opt_value = DashData.best_attempt_read(aida64_data, DashData.cpu_opt_fan, "0")
        self.__fan_opt_gauge.draw_update(fan_opt_value)
        cpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")
        self.__cpu_fan_gauge.draw_update(cpu_fan_value)
        gpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")
        self.__gpu_fan_gauge.draw_update(gpu_fan_value)

        self.__cpu_details.draw_update(aida64_data)
        self.__gpu_details.draw_update(aida64_data)

        sys_memory_value = DashData.best_attempt_read(aida64_data, DashData.sys_ram_used, "0")
        self.__sys_memory_bar.draw_update(sys_memory_value)
        gpu_memory_value = DashData.best_attempt_read(aida64_data, DashData.gpu_ram_used, "0")
        self.__gpu_memory_bar.draw_update(gpu_memory_value)
       
        self.__core_visualizer.update(aida64_data)

        fps_value = DashData.best_attempt_read(aida64_data, DashData.rtss_fps, "0")
        self.__fps_graph.update(fps_value)
        self.__fps_text.draw_update(fps_value)

        # Ambient temperature and humidity
        if None != dht22_data:
            self.__working_surface.blit(
                self.__temperature_humidity.draw_update(dht22_data),
                (self.__element_positions.temperature_humidity_rect[0], self.__element_positions.temperature_humidity_rect[1]))

        # Motherboard temp (nestled between all the fans)
        mobo_temperature_value = DashData.best_attempt_read(aida64_data, DashData.motherboard_temp, "0")
        self.__mobo_temperature.draw_update(mobo_temperature_value, force_draw=True)

        # Network Info
        nic1_down_value = DashData.best_attempt_read(aida64_data, DashData.nic1_download_rate, "0")
        nic1_up_value = DashData.best_attempt_read(aida64_data, DashData.nic1_upload_rate, "0")
        self.__network_info.draw_update(nic1_down_value, nic1_up_value)

        # Clock
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        self.__clock.draw_update(time_string, force_draw=True)


        if self.__using_direct_surface:
            pass
        else:
            return self.__working_surface
