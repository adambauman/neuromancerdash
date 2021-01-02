#
# systemstats.py - Contains layout, configurations, and update routines for the SystemStats page
# ==============================================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

import os
from copy import copy
#from threading import Thread
from datetime import datetime

from data.units import Unit, Units
from data.dataobjects import DataField, DashData

from elements.styles import Color, AssetPath, FontPath
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

        self.cpu_graph = LineGraphConfig(DashData.cpu_util)
        self.cpu_graph.display_background = True
        self.gpu_graph = LineGraphConfig(DashData.gpu_util)
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
        self.cpu_temp_gauge.draw_unit_symbol = False
        self.gpu_temp_gauge = GaugeConfig(DashData.gpu_temp, 45, value_font_size=16, value_font_origin=(35, 70))
        self.gpu_temp_gauge.show_unit_symbol = False 

        self.fps_graph = LineGraphConfig(DashData.rtss_fps)
        self.fps_graph.display_background = True
        self.fps_graph.draw_on_zero = False

        # NOTE: (Adam) On Neuromancer AIDA64 has fans a bit mixed up
        # Base for chassis fans
        case_fan_base = GaugeConfig(DashData.cpu_opt_fan, 20, value_font_size=10, value_font_origin=(17, 29))
        case_fan_base.arc_main_color = Color.grey_40
        case_fan_base.needle_color = Color.white
        case_fan_base.bg_color = Color.black
        case_fan_base.counter_sweep = True
        case_fan_base.draw_unit_symbol = False
        case_fan_base.draw_label_instead_of_value = True
        case_fan_base.draw_shadow = False
        case_fan_base.use_smoothed_rotation = False

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

        self.mobo_temp_label = pygame.Rect(self.cpu_temp_gauge[0]+5, 282, 34, 14)
        self.mobo_temp_rect = pygame.Rect(self.cpu_temp_gauge[0]+5, 294, 34, 14)

        self.network_info = pygame.Rect(0, height-12, 300, 12)
        self.clock = pygame.Rect(self.cpu_details_rect[0], height-12, 70, 12)


class SystemStats:
    working_surface = None

    _backup_surface = None
    _background = None
    _base_size = None

    def __init__(self, base_size, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != base_size)

        self._base_size = base_size
        if direct_surface and direct_rect is not None: 
            self.working_surface = direct_surface.subsurface(direct_rect)
        else:
            self.working_surface = pygame.Surface(self._base_size, surface_flags)

        self.font_normal = pygame.freetype.Font(FontPath.fira_code_semibold(), 12)
        self.font_normal.kerning = True
        
        assert(self.working_surface)

        self._configs = SystemStatsConfigs(self.font_normal)
        self._positions = SystemStatsPositions(base_size[0], base_size[1])

        self._sys_memory_bar = BarGraph(
            self._configs.sys_memory_bar,
            self.working_surface, self._positions.sys_memory)
        self._gpu_memory_bar = BarGraph(
            self._configs.gpu_memory_bar,
            self.working_surface, self._positions.gpu_memory)

        self._cpu_graph = LineGraphReverse(
            self._configs.cpu_graph,
            self.working_surface, self._positions.cpu_graph)
        self._gpu_graph = LineGraphReverse(
            self._configs.gpu_graph,
            self.working_surface, self._positions.gpu_graph)

        self._core_visualizer = SimpleCoreVisualizer(
            self._configs.core_visualizer,
            self.working_surface, self._positions.core_visualizer)

        # NOTE: Rect and working surface are reversed from other elements
        self._cpu_details = CPUDetails(
            self._positions.cpu_details_rect, direct_surface=self.working_surface)
        self._gpu_details = GPUDetails(
            self._positions.gpu_details_rect, direct_surface=self.working_surface)

        self._cpu_temp_gauge = FlatArcGauge(
            self._configs.cpu_temp_gauge,
            self.working_surface, self._positions.cpu_temp_gauge)
        self._gpu_temp_gauge = FlatArcGauge(
            self._configs.gpu_temp_gauge,
            self.working_surface, self._positions.gpu_temp_gauge)

        self._fps_graph = LineGraphReverse(
            self._configs.fps_graph,
            self.working_surface, self._positions.fps_graph)
        self._fps_text = FPSText(self._positions.fps_text_rect, direct_surface=self.working_surface)

        self._temperature_humidity = TemperatureHumidity(
            self._positions.temperature_humidity_rect, direct_surface=self.working_surface)

        self._fan1_gauge = FlatArcGauge(
            self._configs.fan1_gauge, 
            self.working_surface, self._positions.fan1_gauge)
        self._fan_opt_gauge = FlatArcGauge(
            self._configs.fan_opt_gauge,
            self.working_surface, self._positions.fan_opt_gauge)
        self._cpu_fan_gauge = FlatArcGauge(
            self._configs.cpu_fan_gauge,
            self.working_surface, self._positions.cpu_fan_gauge)
        self._gpu_fan_gauge = FlatArcGauge(
            self._configs.gpu_fan_gauge,
            self.working_surface, self._positions.gpu_fan_gauge)

        self._mobo_temperature_label = SimpleText(
            self._positions.mobo_temp_label, "{}", direct_surface=self.working_surface)
        self._mobo_temperature = SimpleText(
            self._positions.mobo_temp_rect, "{}\u00b0C", text_color=Color.yellow,direct_surface=self.working_surface)

        self._network_info = NetworkInformation(self._positions.network_info, direct_surface=self.working_surface)
        self._clock = SimpleText(self._positions.clock, direct_surface=self.working_surface)

    def backup_element_surface(self):
        # Blit, copy doesn't work if this is a subsurfaced direct-draw element
        self._backup_surface = pygame.Surface(self.working_surface.get_size())
        self._backup_surface.blit(self.working_surface, (0, 0))

    def restore_element_surface(self):
        if self._backup_surface:
            self.working_surface.blit(self._backup_surface, (0, 0))

    def draw_update(self, aida64_data, dht22_data=None):
        assert(0 != len(aida64_data))

        # Track the rects that were updated so we can tell the display surface where to redraw.
        # Elements that don't require updates will append a None value.
        update_rects = []

        cpu_utilization_value = DashData.best_attempt_read(aida64_data, DashData.cpu_util, "0")
        update_rects.append(self._cpu_graph.draw_update(cpu_utilization_value))

        gpu_utilization_value = DashData.best_attempt_read(aida64_data, DashData.gpu_util, "0")
        update_rects.append(self._gpu_graph.draw_update(gpu_utilization_value))

        cpu_temperature = DashData.best_attempt_read(aida64_data, DashData.cpu_temp, "0")
        update_rects.append(self._cpu_temp_gauge.draw_update(cpu_temperature))
        gpu_temperature = DashData.best_attempt_read(aida64_data, DashData.gpu_temp, "0")
        update_rects.append(self._gpu_temp_gauge.draw_update(gpu_temperature))

        fan1_value = DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")
        update_rects.append(self._fan1_gauge.draw_update(fan1_value))
        fan_opt_value = DashData.best_attempt_read(aida64_data, DashData.cpu_opt_fan, "0")
        update_rects.append(self._fan_opt_gauge.draw_update(fan_opt_value))
        gpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")
        update_rects.append(self._gpu_fan_gauge.draw_update(gpu_fan_value))

        # NOTE: CPU fan reporting is flaky on this motherboard? Disabling for now.
        #cpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")
        #update_rects.append(self._cpu_fan_gauge.draw_update(cpu_fan_value)[1])

        update_rects.append(self._cpu_details.draw_update(aida64_data))
        update_rects.append(self._gpu_details.draw_update(aida64_data))

        sys_memory_value = DashData.best_attempt_read(aida64_data, DashData.sys_ram_used, "0")
        update_rects.append(self._sys_memory_bar.draw_update(sys_memory_value))
        gpu_memory_value = DashData.best_attempt_read(aida64_data, DashData.gpu_ram_used, "0")
        update_rects.append(self._gpu_memory_bar.draw_update(gpu_memory_value))
       
        update_rects.append(self._core_visualizer.draw_update(aida64_data))

        fps_value = DashData.best_attempt_read(aida64_data, DashData.rtss_fps, "0")
        update_rects.append(self._fps_graph.draw_update(fps_value))
        update_rects.append(self._fps_text.draw_update(fps_value))

        # Ambient temperature and humidity
        if dht22_data is not None:
            update_rects.append(self._temperature_humidity.draw_update(dht22_data))

        # Motherboard temp (nestled between all the fans)
        mobo_temperature_value = DashData.best_attempt_read(aida64_data, DashData.motherboard_temp, "0")
        update_rects.append(self._mobo_temperature_label.draw_update("Mobo"))
        update_rects.append(self._mobo_temperature.draw_update(mobo_temperature_value))

        # Network Info
        nic1_down_value = DashData.best_attempt_read(aida64_data, DashData.nic1_download_rate, "0")
        nic1_up_value = DashData.best_attempt_read(aida64_data, DashData.nic1_upload_rate, "0")
        update_rects.append(self._network_info.draw_update(nic1_down_value, nic1_up_value))

        # Clock
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        update_rects.append(self._clock.draw_update(time_string))

        return update_rects
