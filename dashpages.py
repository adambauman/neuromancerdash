#
# dash_pages - Contains layouts and methods to paint dashboard pages
# =================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame, pygame.freetype

import os
from datetime import datetime

from data.units import Unit, Units
from data.dataobjects import DataField, DashData

from elements.styles import Color, AssetPath, FontPaths
from elements.gauge import FlatArcGauge, GaugeConfig 
from elements.bargraph import BarGraph, BarGraphConfig
from elements.linegraph import LineGraphReverse, LineGraphConfig
from elements.visualizers import SimpleCoreVisualizer, CoreVisualizerConfig
from elements.ambientreadout import TemperatureHumidity
from elements.text import FPSText, CPUDetails, GPUDetails

from elements.helpers import Helpers

if __debug__:
    import traceback

class TweenState:
    unknown = 0
    idle = 1
    rising = 2
    falling = 3
class TweenAcceleration:
    unknown = 0
    stable = 1
    accelerating = 2
    decelerating = 3
class Tweening:
    tween_state = TweenState.unknown
    tween_acceleration = TweenAcceleration.unknown
    last_absolute_value = 0
    tween_steps = 0

    def calculate_tween_steps(self, new_absolute_value, frames_since_last_calculation):
        new_tween_state = TweenState.unknown
        if new_absolute_value == self.last_absolute_value:
            new_tween_state = TweenState.idle
        elif new_absolute_value > self.last_absolute_value:
            new_tween_state = TweenState.rising
        else:
            new_tween_state = TweenState.falling

        delta = new_absolute_value - self.last_absolute_value
        if 0 != frames_since_last_calculation:
            self.tween_steps = delta / frames_since_last_calculation

        self.last_absolute_value = new_absolute_value

class SharedFonts:
    def __init__(self):
        self.font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        #font_normal.strong = True
        self.font_normal.kerning = True

class Page01ElementConfigurations:

    def __init__(self):
        ### Fonts

        self.__font_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 16)
        self.__font_gauge_value.strong = True
        self.__fan_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 10)
        #self.fan_gauge_value.strong = True
        #self.__shared_fonts = SharedFonts()

        ### Configurations
        self.core_visualizer = CoreVisualizerConfig(8)

        self.cpu_graph = LineGraphConfig(70, 300, DashData.cpu_util)
        self.cpu_graph.display_background = True
        self.gpu_graph = LineGraphConfig(70, 300, DashData.gpu_util)
        self.gpu_graph.display_background = True

        self.sys_memory_bar = BarGraphConfig(300, 25, DashData.sys_ram_used)
        self.sys_memory_bar.foreground_color = Color.windows_dkgrey_1_highlight
        self.gpu_memory_bar = BarGraphConfig(300, 25, DashData.gpu_ram_used)
        self.gpu_memory_bar.foreground_color = Color.windows_dkgrey_1_highlight

        self.cpu_temp_gauge = GaugeConfig(DashData.cpu_temp, 45, self.__font_gauge_value, (35, 70))
        self.cpu_temp_gauge.show_unit_symbol = False
        self.gpu_temp_gauge = GaugeConfig(DashData.gpu_temp, 45, self.__font_gauge_value, (35, 70))
        self.gpu_temp_gauge.show_unit_symbol = False 

        self.fps_graph = LineGraphConfig(70, 200, DashData.rtss_fps)
        self.fps_graph.display_background = True
        self.fps_graph.draw_on_zero = False

class Page01ElementPositions:

    def __init__(self, width, height):
        assert(0 != width and 0 != height)

        self.cpu_graph = (0, 0)
        self.sys_memory = (0, 75)
        self.gpu_graph = (0, 110)
        self.gpu_memory = (0, 185)

        self.core_visualizer = (310, 0)

        self.cpu_details_rect = pygame.Rect(310, 33, 74, 72)
        self.gpu_details_rect = pygame.Rect(310, 114, 74, 102)

        self.cpu_temp_gauge = (width - 90, 7)
        self.gpu_temp_gauge = (width - 90, 117, 90, 90)

        self.fps_graph = (0, 230)
        self.fps_text_rect = pygame.Rect(210, 240, 98, 62)

        self.network_text = (0, 310)
        self.time = (self.cpu_details_rect[0], 310)

        #self.fan1_gauge_origin = (self.cpu_temp_gauge_origin[0], 230)
        #self.fan_opt_gauge_origin = (display_width - 40, 230)
        #self.cpu_fan_gauge_origin = (self.cpu_temp_gauge_origin[0], 275)
        #self.gpu_fan_gauge_origin = (self.fan_opt_gauge_origin[0], self.cpu_fan_gauge_origin[1])

        #self.mobo_temp_origin = (display_width - 52, 268)

        #self.disk_activity_origin = (self.cpu_detail_stack_origin[0], 230)
        #self.ambient_humidity_temp_origin = (self.cpu_detail_stack_origin[0], 240)

        ### Element configuration

        

        ## FAN1 = Upper intake (lower intake does not report)
        #fan1_gauge_config = GaugeConfig(DashData.chassis_1_fan, 20, self.fan_gauge_value, (17, 29))
        #fan1_gauge_config.arc_main_color = Color.grey_40
        #fan1_gauge_config.needle_color = Color.white
        #fan1_gauge_config.bg_alpha = 0
        #fan1_gauge_config.counter_sweep = True
        #fan1_gauge_config.show_unit_symbol = False
        #fan1_gauge_config.show_label_instead_of_value = True
        #fan1_gauge_config.label = "I"
        #self.fan1_gauge = FlatArcGauge(fan1_gauge_config)

        # FAN2 = Drive bay intake?
        # FAN3 = Rear exhaust

        # CPU OPT fan = Forward exhaust
        #fan_opt_gauge_config = GaugeConfig(DashData.cpu_opt_fan, 20, self.fan_gauge_value, (18, 29))
        #fan_opt_gauge_config.arc_main_color = Color.grey_40
        #fan_opt_gauge_config.needle_color = Color.white
        #fan_opt_gauge_config.bg_alpha = 0
        #fan_opt_gauge_config.counter_sweep = True
        #fan_opt_gauge_config.show_label_instead_of_value = True
        #fan_opt_gauge_config.label = "E"
        #self.fan_opt_gauge = FlatArcGauge(fan_opt_gauge_config)

        #cpu_fan_gauge_config = GaugeConfig(DashData.cpu_fan, 20, self.fan_gauge_value, (17, 29))
        #cpu_fan_gauge_config.arc_main_color = Color.grey_40
        #cpu_fan_gauge_config.needle_color = Color.white
        #cpu_fan_gauge_config.bg_alpha = 0
        #cpu_fan_gauge_config.counter_sweep = True
        #cpu_fan_gauge_config.show_unit_symbol = False
        #cpu_fan_gauge_config.show_label_instead_of_value = True
        #cpu_fan_gauge_config.label = "C"
        #self.cpu_fan_gauge = FlatArcGauge(cpu_fan_gauge_config)

        #gpu_fan_gauge_config = GaugeConfig(DashData.gpu_fan, 20, self.fan_gauge_value, (17, 29))
        #gpu_fan_gauge_config.arc_main_color = Color.grey_40
        #gpu_fan_gauge_config.needle_color = Color.white
        #gpu_fan_gauge_config.bg_alpha = 0
        #gpu_fan_gauge_config.counter_sweep = True
        #gpu_fan_gauge_config.show_unit_symbol = False
        #gpu_fan_gauge_config.show_label_instead_of_value = True
        #gpu_fan_gauge_config.label = "G"
        #self.gpu_fan_gauge = FlatArcGauge(gpu_fan_gauge_config)

        ## This will be set on the first update if DHT22 data is available
        #self.ambient_humidity_temp_display = None

        # Disk activity
        #disk_activity_bar_config = BarGraphConfig(65, 19, DashData.disk_activity)
        #disk_activity_bar_config.foreground_color = Color.windows_dkgrey_1_highlight
        #self.disk_activity_bar = BarGraph(disk_activity_bar_config)
        #self.disk_activity_y_spacing = 21


class DashPage01:
    __background = None

    def __init__(self, width, height):
        assert(0 != width and 0 != height)

        self.__working_surface = pygame.Surface((width, height))

        if __debug__:
            self.__background = pygame.image.load(os.path.join(AssetPath.backgrounds, "480_320_grid.png"))
            self.__working_surface.blit(self.__background, (0,0))

        self.__element_positions = Page01ElementPositions(width, height)
        self.__element_configs = Page01ElementConfigurations()
        self.__shared_fonts = SharedFonts()

        self.__sys_memory_bar = BarGraph(self.__element_configs.sys_memory_bar)
        self.__gpu_memory_bar = BarGraph(self.__element_configs.gpu_memory_bar)
        self.__cpu_graph = LineGraphReverse(self.__element_configs.cpu_graph)
        self.__gpu_graph = LineGraphReverse(self.__element_configs.gpu_graph)

        self.__core_visualizer = SimpleCoreVisualizer(self.__element_configs.core_visualizer)
        self.__cpu_details = CPUDetails(self.__element_positions.cpu_details_rect, self.__working_surface)
        self.__gpu_details = GPUDetails(self.__element_positions.gpu_details_rect, self.__working_surface)
        self.__cpu_temp_gauge = FlatArcGauge(self.__element_configs.cpu_temp_gauge)
        self.__gpu_temp_gauge = FlatArcGauge(self.__element_configs.gpu_temp_gauge)

        self.__fps_graph = LineGraphReverse(self.__element_configs.fps_graph)
        self.__fps_text = FPSText(self.__element_positions.fps_text_rect, self.__working_surface)


    def get_updated_surface(self, aida64_data, dht22_data=None):
        assert(0 != len(aida64_data))

        # CPU and GPU Utilization
        self.__working_surface.blit(
            self.__cpu_graph.update(DashData.best_attempt_read(aida64_data, DashData.cpu_util, "0")),
            self.__element_positions.cpu_graph)

        self.__working_surface.blit(
            self.__gpu_graph.update(DashData.best_attempt_read(aida64_data, DashData.gpu_util, "0")),
            self.__element_positions.gpu_graph)

        # System and GPU memory usage
        self.__working_surface.blit(
            self.__sys_memory_bar.update(DashData.best_attempt_read(aida64_data, DashData.sys_ram_used, "0")),
            self.__element_positions.sys_memory)

        self.__working_surface.blit(
            self.__gpu_memory_bar.update(DashData.best_attempt_read(aida64_data, DashData.gpu_ram_used, "0")),
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
        if self.__cpu_temp_gauge.current_value != cpu_temperature:
            self.__working_surface.blit(
                self.__cpu_temp_gauge.draw_update(cpu_temperature),
                self.__element_positions.cpu_temp_gauge)

        # GPU Temperature Gauge
        gpu_temperature = DashData.best_attempt_read(aida64_data, DashData.gpu_temp, "0")
        if self.__gpu_temp_gauge.current_value != gpu_temperature:
            self.__working_surface.blit(
                self.__gpu_temp_gauge.draw_update(gpu_temperature),
                self.__element_positions.gpu_temp_gauge)

        # FPS Graph and Text
        fps_value = DashData.best_attempt_read(aida64_data, DashData.rtss_fps, "0")
        self.__working_surface.blit(self.__fps_graph.update(fps_value), self.__element_positions.fps_graph)
        if self.__fps_text.current_value != fps_value:
            self.__working_surface.blit(
                self.__fps_text.draw_update(fps_value),
                (self.__element_positions.fps_text_rect[0], self.__element_positions.fps_text_rect[1]))


        return self.__working_surface



        ## Fan gauges
        #self.display_surface.blit(
        #    self.page.fan1_gauge.update(DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")),
        #    self.page.fan1_gauge_origin)
        #self.display_surface.blit(
        #    self.page.fan_opt_gauge.update(DashData.best_attempt_read(aida64_data, DashData.cpu_opt_fan, "0")),
        #    self.page.fan_opt_gauge_origin)
        #self.display_surface.blit(
        #    self.page.cpu_fan_gauge.update(DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")),
        #    self.page.cpu_fan_gauge_origin)
        #self.display_surface.blit(
        #    self.page.gpu_fan_gauge.update(DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")),
        #    self.page.gpu_fan_gauge_origin)

        ## Motherboard temp (nestled between all the fans)
        #self.page.font_normal.render_to(
        #    self.display_surface, self.page.mobo_temp_origin,
        #    "{}".format(DashData.best_attempt_read(aida64_data, DashData.motherboard_temp, "0")),
        #    Color.white)

        # Ambient Humidity and Temperature
        #if None != dht22_data:
        #    if None == self.page.ambient_humidity_temp_display:
        #        self.page.ambient_humidity_temp_display = TemperatureHumidity()

        #    self.display_surface.blit(
        #        self.page.ambient_humidity_temp_display.update(dht22_data),
        #        self.page.ambient_humidity_temp_origin)
        #    #self.__paint_ambient_text_stack__(self.page.ambient_humidity_temp_origin, self.page.font_normal, dht22_data)

        # Disk activity
        #disk_count = 4
        #disk_y_offset = 0
        #for index in range(disk_count):
        #    try:
        #        disk_activity_value = data["disk_{}_activity".format(index)]
        #    except:
        #        disk_activity_value = "0"
        #        if __debug__:
        #            print("Data error: disk_{}_activity".format(index))
        #            #traceback.print_exc()

        #    self.display_surface.blit(
        #        self.page.disk_activity_bar.update(disk_activity_value),
        #        (self.page.disk_activity_origin[0], self.page.disk_activity_origin[1] + disk_y_offset))
        #    disk_y_offset += self.page.disk_activity_y_spacing

        # Network Text
        #nic1_down_value = DashData.best_attempt_read(aida64_data, DashData.nic1_download_rate, "0")
        #network_download_text = "NIC 1 Down: {} {}".format(nic1_down_value, DashData.nic1_download_rate.unit.symbol)
        #self.page.font_normal.render_to(
        #    self.display_surface,
        #    self.page.network_text_origin,
        #    network_download_text, Color.white)

        #nic1_up_value = DashData.best_attempt_read(aida64_data, DashData.nic1_upload_rate, "0")
        #network_upload_text = "Up: {} {}".format(nic1_up_value, DashData.nic1_upload_rate.unit.symbol)
        #self.page.font_normal.render_to(
        #    self.display_surface,
        #    (self.page.network_text_origin[0] + 180, self.page.network_text_origin[1]),
        #    network_upload_text, Color.white)

        #now = datetime.now()
        #time_string = now.strftime("%H:%M:%S")
        #text = "{}".format(time_string)
        #self.page.font_normal.render_to(self.display_surface, self.page.time_origin, text, Color.white)