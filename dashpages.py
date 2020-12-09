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

class DashPage1:
    def __init__(self, display_width, display_height):
        self.font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        #font_normal.strong = True
        self.font_normal.kerning = True

        self.font_large = pygame.freetype.Font(FontPaths.fira_code_semibold(), 50)
        #font_large.strong = True
        self.font_large_kerning = True

        self.font_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 16)
        self.font_gauge_value.strong = True

        self.fan_gauge_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 10)
        #self.fan_gauge_value.strong = True

        ### Positioning

        self.core_visualizer_origin = (310, 0)
        self.cpu_detail_stack_origin = (310, 33)
        self.gpu_detail_stack_origin = (310, 115)
        self.cpu_temp_gauge_origin = (display_width - 90, 7)
        self.gpu_temp_gauge_origin = (display_width - 90, 117)
        self.cpu_graph_origin = (0, 0)
        self.gpu_graph_origin = (0, 110)

        self.sys_memory_origin = (0, 75)
        self.gpu_memory_origin = (0, 185)

        self.fps_graph_origin = (0, 230)
        self.fps_text_origin = (210, 240)
        self.fps_label_origin = (212, 285)
        self.network_text_origin = (0, 310)
        self.time_origin = (self.cpu_detail_stack_origin[0], 310)

        self.fan1_gauge_origin = (self.cpu_temp_gauge_origin[0], 230)
        self.fan_opt_gauge_origin = (display_width - 40, 230)
        self.cpu_fan_gauge_origin = (self.cpu_temp_gauge_origin[0], 275)
        self.gpu_fan_gauge_origin = (self.fan_opt_gauge_origin[0], self.cpu_fan_gauge_origin[1])

        self.mobo_temp_origin = (display_width - 52, 268)

        #self.disk_activity_origin = (self.cpu_detail_stack_origin[0], 230)
        self.ambient_humidity_temp_origin = (self.cpu_detail_stack_origin[0], 240)

        #####

        cpu_temp_gauge_config = GaugeConfig(DashData.cpu_temp, 45, self.font_gauge_value, (35, 70))
        cpu_temp_gauge_config.show_unit_symbol = False
        self.cpu_temp_gauge = FlatArcGauge(cpu_temp_gauge_config)

        gpu_temp_gauge_config = GaugeConfig(DashData.gpu_temp, 45, self.font_gauge_value, (35, 70))
        gpu_temp_gauge_config.show_unit_symbol = False
        self.gpu_temp_gauge = FlatArcGauge(gpu_temp_gauge_config)

        cpu_graph_config = LineGraphConfig(70, 300, DashData.cpu_util)
        cpu_graph_config.display_background = True
        self.cpu_graph = LineGraphReverse(cpu_graph_config)

        gpu_graph_config = LineGraphConfig(70, 300, DashData.gpu_util)
        gpu_graph_config.display_background = True
        self.gpu_graph = LineGraphReverse(gpu_graph_config)

        core_visualizer_config = CoreVisualizerConfig(8)
        self.core_visualizer = SimpleCoreVisualizer(core_visualizer_config)

        sys_memory_bar_config = BarGraphConfig(300, 25, DashData.sys_ram_used)
        sys_memory_bar_config.foreground_color = Color.windows_dkgrey_1_highlight
        self.sys_memory_bar = BarGraph(sys_memory_bar_config)

        gpu_memory_bar_config = BarGraphConfig(300, 25, DashData.gpu_ram_used)
        gpu_memory_bar_config.foreground_color = Color.windows_dkgrey_1_highlight
        self.gpu_memory_bar = BarGraph(gpu_memory_bar_config)

        fps_graph_config = LineGraphConfig(70, 200, DashData.rtss_fps)
        fps_graph_config.display_background = True
        fps_graph_config.draw_on_zero = False
        self.fps_graph = LineGraphReverse(fps_graph_config)

        # FAN1 = Upper intake (lower intake does not report)
        fan1_gauge_config = GaugeConfig(DashData.chassis_1_fan, 20, self.fan_gauge_value, (17, 29))
        fan1_gauge_config.arc_main_color = Color.grey_40
        fan1_gauge_config.needle_color = Color.white
        fan1_gauge_config.bg_alpha = 0
        fan1_gauge_config.counter_sweep = True
        fan1_gauge_config.show_unit_symbol = False
        fan1_gauge_config.show_label_instead_of_value = True
        fan1_gauge_config.label = "I"
        self.fan1_gauge = FlatArcGauge(fan1_gauge_config)

        # FAN2 = Drive bay intake?
        # FAN3 = Rear exhaust

        # CPU OPT fan = Forward exhaust
        fan_opt_gauge_config = GaugeConfig(DashData.cpu_opt_fan, 20, self.fan_gauge_value, (18, 29))
        fan_opt_gauge_config.arc_main_color = Color.grey_40
        fan_opt_gauge_config.needle_color = Color.white
        fan_opt_gauge_config.bg_alpha = 0
        fan_opt_gauge_config.counter_sweep = True
        fan_opt_gauge_config.show_label_instead_of_value = True
        fan_opt_gauge_config.label = "E"
        self.fan_opt_gauge = FlatArcGauge(fan_opt_gauge_config)

        cpu_fan_gauge_config = GaugeConfig(DashData.cpu_fan, 20, self.fan_gauge_value, (17, 29))
        cpu_fan_gauge_config.arc_main_color = Color.grey_40
        cpu_fan_gauge_config.needle_color = Color.white
        cpu_fan_gauge_config.bg_alpha = 0
        cpu_fan_gauge_config.counter_sweep = True
        cpu_fan_gauge_config.show_unit_symbol = False
        cpu_fan_gauge_config.show_label_instead_of_value = True
        cpu_fan_gauge_config.label = "C"
        self.cpu_fan_gauge = FlatArcGauge(cpu_fan_gauge_config)

        gpu_fan_gauge_config = GaugeConfig(DashData.gpu_fan, 20, self.fan_gauge_value, (17, 29))
        gpu_fan_gauge_config.arc_main_color = Color.grey_40
        gpu_fan_gauge_config.needle_color = Color.white
        gpu_fan_gauge_config.bg_alpha = 0
        gpu_fan_gauge_config.counter_sweep = True
        gpu_fan_gauge_config.show_unit_symbol = False
        gpu_fan_gauge_config.show_label_instead_of_value = True
        gpu_fan_gauge_config.label = "G"
        self.gpu_fan_gauge = FlatArcGauge(gpu_fan_gauge_config)

        # This will be set on the first update if DHT22 data is available
        self.ambient_humidity_temp_display = None

        # Disk activity
        #disk_activity_bar_config = BarGraphConfig(65, 19, DashData.disk_activity)
        #disk_activity_bar_config.foreground_color = Color.windows_dkgrey_1_highlight
        #self.disk_activity_bar = BarGraph(disk_activity_bar_config)
        #self.disk_activity_y_spacing = 21


class DashPage1Painter:
    page = None

    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.page = DashPage1(display_surface.get_width(), display_surface.get_height())

    def __get_next_vertical_stack_origin__(self, last_origin, font, padding = 0):
        x = last_origin[0]
        y = last_origin[1] + font.get_sized_height() + padding
        return (x,y)

    # TODO: (Adam) 2020-11-30 These text stacks could be optimized, only update change values and non-static bits, etc.
    def __paint_cpu_text_stack__(self, origin, font_normal, data):
        assert(0 != len(data))

        stack_vertical_adjustment = -2

        text_origin = origin
        text = "{} {}".format(DashData.best_attempt_read(data, DashData.cpu_power, "0"), DashData.cpu_power.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(DashData.best_attempt_read(data, DashData.cpu_clock, "0"), DashData.cpu_clock.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)


        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{}{}".format(DashData.best_attempt_read(data, DashData.cpu_util, "0"), DashData.cpu_util.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "RAM Used"
        font_normal.render_to(self.display_surface, text_origin, text, Color.grey_75)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(DashData.best_attempt_read(data, DashData.sys_ram_used, "0"), DashData.sys_ram_used.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

    def __paint_gpu_text_stack__(self, origin, font_normal, data):
        assert(0 != len(data))

        stack_vertical_adjustment = -2

        text_origin = origin
        text = "PerfCap:"
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{}".format(DashData.best_attempt_read(data, DashData.gpu_perfcap_reason, "0"))
        font_normal.render_to(self.display_surface, text_origin, Helpers.clamp_text(text,11, ""), Color.yellow)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(DashData.best_attempt_read(data, DashData.gpu_power, "0"), DashData.gpu_power.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(DashData.best_attempt_read(data, DashData.gpu_clock, "0"), DashData.gpu_clock.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{}{}".format(DashData.best_attempt_read(data, DashData.gpu_util, "0"), DashData.gpu_util.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "RAM Used"
        font_normal.render_to(self.display_surface, text_origin, text, Color.grey_75)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(DashData.best_attempt_read(data, DashData.gpu_ram_used, "0"), DashData.gpu_ram_used.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

    def __paint_ambient_text_stack__(self, origin, font_normal, dht22_data):
        assert(None != dht22_data)

        stack_vertical_adjustment = -2

        text_origin = origin
        text = "Room Temp "
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{:0.1f}".format(dht22_data.temperature) + u"\u00b0" + "F"
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "Humidity"
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{:0.1f}".format(dht22_data.humidity) + "%"
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

    def paint(self, aida64_data, dht22_data=None):
        assert(0 != len(aida64_data))
        assert(None != self.page)

        self.display_surface.fill(Color.black)

        # CPU Data
        self.__paint_cpu_text_stack__(self.page.cpu_detail_stack_origin, self.page.font_normal, aida64_data)

        # GPU Data
        self.__paint_gpu_text_stack__(self.page.gpu_detail_stack_origin, self.page.font_normal, aida64_data)

        # CPU and GPU Temps
        self.display_surface.blit(
            self.page.cpu_temp_gauge.update(DashData.best_attempt_read(aida64_data, DashData.cpu_temp, "0")),
            self.page.cpu_temp_gauge_origin)

        self.display_surface.blit(
            self.page.gpu_temp_gauge.update(DashData.best_attempt_read(aida64_data, DashData.gpu_temp, "0")),
            self.page.gpu_temp_gauge_origin)

        # CPU and GPU Utilization
        self.display_surface.blit(
            self.page.cpu_graph.update(DashData.best_attempt_read(aida64_data, DashData.cpu_util, "0")),
            self.page.cpu_graph_origin)

        self.display_surface.blit(
            self.page.gpu_graph.update(DashData.best_attempt_read(aida64_data, DashData.gpu_util, "0")),
            self.page.gpu_graph_origin)

        # CPU Core Visualizer
        self.display_surface.blit(
            self.page.core_visualizer.update(aida64_data),
            self.page.core_visualizer_origin)

        # System and GPU memory usage
        self.display_surface.blit(
            self.page.sys_memory_bar.update(DashData.best_attempt_read(aida64_data, DashData.sys_ram_used, "0")),
            self.page.sys_memory_origin)

        self.display_surface.blit(
            self.page.gpu_memory_bar.update(DashData.best_attempt_read(aida64_data, DashData.gpu_ram_used, "0")),
            self.page.gpu_memory_origin)

        # FPS Graph and Text
        fps_value = DashData.best_attempt_read(aida64_data, DashData.rtss_fps, "0")
        self.display_surface.blit(self.page.fps_graph.update(fps_value), self.page.fps_graph_origin)
        self.page.font_large.render_to(self.display_surface, self.page.fps_text_origin, "{}".format(fps_value), Color.white)
        self.page.font_normal.render_to(self.display_surface, self.page.fps_label_origin, "FPS", Color.white)

        # Fan gauges
        self.display_surface.blit(
            self.page.fan1_gauge.update(DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")),
            self.page.fan1_gauge_origin)
        self.display_surface.blit(
            self.page.fan_opt_gauge.update(DashData.best_attempt_read(aida64_data, DashData.cpu_opt_fan, "0")),
            self.page.fan_opt_gauge_origin)
        self.display_surface.blit(
            self.page.cpu_fan_gauge.update(DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")),
            self.page.cpu_fan_gauge_origin)
        self.display_surface.blit(
            self.page.gpu_fan_gauge.update(DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")),
            self.page.gpu_fan_gauge_origin)

        # Motherboard temp (nestled between all the fans)
        self.page.font_normal.render_to(
            self.display_surface, self.page.mobo_temp_origin,
            "{}".format(DashData.best_attempt_read(aida64_data, DashData.motherboard_temp, "0")),
            Color.white)

        # Ambient Humidity and Temperature
        if None != dht22_data:
            if None == self.page.ambient_humidity_temp_display:
                self.page.ambient_humidity_temp_display = TemperatureHumidity()

            self.display_surface.blit(
                self.page.ambient_humidity_temp_display.update(dht22_data),
                self.page.ambient_humidity_temp_origin)
            #self.__paint_ambient_text_stack__(self.page.ambient_humidity_temp_origin, self.page.font_normal, dht22_data)

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
        nic1_down_value = DashData.best_attempt_read(aida64_data, DashData.nic1_download_rate, "0")
        network_download_text = "NIC 1 Down: {} {}".format(nic1_down_value, DashData.nic1_download_rate.unit.symbol)
        self.page.font_normal.render_to(
            self.display_surface,
            self.page.network_text_origin,
            network_download_text, Color.white)

        nic1_up_value = DashData.best_attempt_read(aida64_data, DashData.nic1_upload_rate, "0")
        network_upload_text = "Up: {} {}".format(nic1_up_value, DashData.nic1_upload_rate.unit.symbol)
        self.page.font_normal.render_to(
            self.display_surface,
            (self.page.network_text_origin[0] + 180, self.page.network_text_origin[1]),
            network_upload_text, Color.white)

        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        text = "{}".format(time_string)
        self.page.font_normal.render_to(self.display_surface, self.page.time_origin, text, Color.white)
