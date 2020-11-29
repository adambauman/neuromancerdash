#
# dash_pages - Contains layouts and methods to paint dashboard pages
# ==================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame, pygame.freetype

import os

from elements.styles import Color, AssetPath, FontPaths

from elements.gauge import FlatArcGauge, GaugeConfig 
from elements.bargraph import BarGraph, BarGraphConfig
from elements.linegraph import LineGraphReverse, LineGraphConfig
from elements.visualizers import SimpleCoreVisualizer, CoreVisualizerConfig

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

# TODO: (Adam) 2020-11-14 This is a bit of mess, could use something like Pint for slick unit handling
class Unit:
    def __init__(self, name = "", symbol = "", alt_symbol = ""):
        self.name = name
        self.symbol = symbol
        self.alt_symbol = alt_symbol
class Units:
    null_unit = Unit()
    celsius = Unit("Celcius", "C")
    percent = Unit("Percent", "%")
    megahertz = Unit("Megahertz", "Mhz")
    megabytes = Unit("Megabytes", "MB")
    megabits = Unit("Megabits", "Mb")
    megabytes_per_second = Unit("Megabytes/sec", "MBps", "MB/s")
    megabits_per_second = Unit("Megabits/sec", "Mbps", "Mb/s")
    kilobytes = Unit("Kilobytes", "KB")
    kilobits = Unit("Kilobits", "Kb")
    kilobytes_per_second = Unit("Kilobytes/sec", "KBps", "KB/s")
    kilobits_per_second = Unit("Kilobits/sec", "Kbps", "Kb/s")
    rpm = Unit("Revolutions Per Second", "RPM")
    fps = Unit("Frames Per Second", "FPS")
    watts = Unit("Watts", "W")
class DataField:
    def __init__(
        self, field_name = "", description = "", unit = Units.null_unit,
        min_value = None, caution_value = None, warn_value = None, max_value = None):

        self.field_name = field_name
        self.description = description
        self.unit = unit
        self.min_value = min_value
        self.caution_value = caution_value
        self.warn_value = warn_value
        self.max_value = max_value
#TODO: (Adam) 2020-11-14 AIDA64 layout file is plain text, could write a converter to grab fields names
#           from the client-side export file.
class DashData:
    unknown = DataField("", "Unknown", Units.null_unit)
    cpu_util = DataField("cpu_util", "CPU Utilization", Units.percent, min_value=0, max_value=100)
    cpu_temp = DataField("cpu_temp", "CPU Temperature", Units.celsius, min_value=20, caution_value=81, max_value=80, warn_value=82)
    cpu_clock = DataField("cpu_clock", "CPU Clock", Units.megahertz, min_value=799, max_value=4500)
    cpu_power = DataField("cpu_power", "CPU Power", Units.watts, min_value=0, max_value=91)
    gpu_clock = DataField("gpu_clock", "GPU Clock", Units.megahertz, min_value=300, max_value=1770)
    gpu_util = DataField("gpu_util", "GPU Utilization", Units.percent, min_value=0, max_value=100)
    gpu_ram_used = DataField("gpu_ram_used", "GPU RAM Used", Units.megabytes, min_value=0, max_value=8192)
    gpu_power = DataField("gpu_power", "GPU Power", Units.watts, min_value=0, max_value=215)
    gpu_temp = DataField("gpu_temp", "GPU Temperature", Units.celsius, min_value=20, caution_value=75, max_value=80, warn_value=88)
    gpu_perfcap_reason = DataField("gpu_perfcap_reason", "GPU Performance Cap Reason")
    sys_ram_used = DataField("sys_ram_used", "System RAM Used", Units.megabytes, min_value=0, caution_value=30000, max_value=32768)
    nic1_download_rate = DataField("nic1_download_rate", "NIC1 Download Rate", Units.kilobytes_per_second)
    nic1_upload_rate = DataField("nic1_upload_rate", "NIC2 Upload Rate", Units.kilobytes_per_second, min_value=0, max_value=1000000)
    cpu_fan = DataField("cpu_fan", "CPU Fan Speed", Units.rpm, warn_value=500, min_value=1000, max_value=1460)
    cpu_opt_fan = DataField("cpu_opt_fan", "CPU OPT Fan Speed", Units.rpm, warn_value=500, min_value=900, max_value=2000)
    chassis_1_fan = DataField("chassis_1_fan", "Chassis 1 Fan Speed", Units.rpm, warn_value=300, min_value=600, max_value=1700)
    chassis_2_fan = DataField("chassis_2_fan", "Chassis 2 Fan Speed", Units.rpm, warn_value=300,min_value=400, max_value=1200)
    chassis_3_fan = DataField("chassis_3_fan", "Chassis 3 Fan Speed", Units.rpm, warn_value=300, min_value=900, max_value=2000)
    gpu_fan = DataField("gpu_fan", "GPU Fan Speed", Units.rpm, warn_value=300, min_value=800, max_value=1800)
    gpu_2_fan = DataField("gpu_2_fan", "GPU Fan Speed?", Units.rpm, min_value=0, max_value=2000)
    desktop_resolution = DataField("desktop_resolution", "Desktop Display Resolution")
    desktop_refresh_rate = DataField("vertical_refresh_rate", "Display Vertical Refresh Rate")
    motherboard_temp = DataField("motherboard_temp", "Motherboard Temperature", Units.celsius, min_value=15, caution_value=50, max_value=60, warn_value=62)
    rtss_fps = DataField("rtss_fps", "Frames Per Second", Units.fps, min_value=0, max_value=120)

    # Iterate the following, labels in data source should be setup to be 0-indexed
    disk_activity = DataField("disk_{}_activity", "Disk {} Activity", Units.percent, min_value=0, max_value=100)
    cpu_core_utilization = DataField("cpu{}_util", "CPU Core {} Utilization", Units.percent, min_value=0, max_value=100)

    def best_attempt_read(data, data_field, default_value):
        try:
            value = data[data_field.field_name]
        except:
            value = default_value
            if __debug__:
                print("Data error: {}".format(data_field.field_name))
                #traceback.print_exc()

        return value

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

        self.fan1_gauge_origin = (self.cpu_temp_gauge_origin[0], 230)
        self.fan_opt_gauge_origin = (display_width - 40, 230)
        self.cpu_fan_gauge_origin = (self.cpu_temp_gauge_origin[0], 275)
        self.gpu_fan_gauge_origin = (self.fan_opt_gauge_origin[0], self.cpu_fan_gauge_origin[1])

        self.mobo_temp_origin = (display_width - 52, 268)

        self.disk_activity_origin = (self.cpu_detail_stack_origin[0], 230)

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

        # Disk activity
        disk_activity_bar_config = BarGraphConfig(65, 19, DashData.disk_activity)
        disk_activity_bar_config.foreground_color = Color.windows_dkgrey_1_highlight
        self.disk_activity_bar = BarGraph(disk_activity_bar_config)
        self.disk_activity_y_spacing = 21


class DashPage1Painter:
    page = None

    def __init__(self, display_surface):
        self.display_surface = display_surface
        self.page = DashPage1(display_surface.get_width(), display_surface.get_height())

    def __get_next_vertical_stack_origin__(self, last_origin, font, padding = 0):
        x = last_origin[0]
        y = last_origin[1] + font.get_sized_height() + padding
        return (x,y)

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

    def paint(self, data):
        assert(0 != len(data))
        assert(None != self.page)

        self.display_surface.fill(Color.black)

        # CPU Data
        self.__paint_cpu_text_stack__(self.page.cpu_detail_stack_origin, self.page.font_normal, data)

        # GPU Data
        self.__paint_gpu_text_stack__(self.page.gpu_detail_stack_origin, self.page.font_normal, data)

        # CPU and GPU Temps
        self.display_surface.blit(        
            self.page.cpu_temp_gauge.update(DashData.best_attempt_read(data, DashData.cpu_temp, "0")),
            self.page.cpu_temp_gauge_origin)

        self.display_surface.blit(
            self.page.gpu_temp_gauge.update(DashData.best_attempt_read(data, DashData.gpu_temp, "0")), 
            self.page.gpu_temp_gauge_origin)

        # CPU and GPU Utilization
        self.display_surface.blit(
            self.page.cpu_graph.update(DashData.best_attempt_read(data, DashData.cpu_util, "0")), 
            self.page.cpu_graph_origin)

        self.display_surface.blit(
            self.page.gpu_graph.update(DashData.best_attempt_read(data, DashData.gpu_util, "0")), 
            self.page.gpu_graph_origin)

        # CPU Core Visualizer
        self.display_surface.blit(
            self.page.core_visualizer.update(data), 
            self.page.core_visualizer_origin)

        # System and GPU memory usage
        self.display_surface.blit(
            self.page.sys_memory_bar.update(DashData.best_attempt_read(data, DashData.sys_ram_used, "0")), 
            self.page.sys_memory_origin)

        self.display_surface.blit(
            self.page.gpu_memory_bar.update(DashData.best_attempt_read(data, DashData.gpu_ram_used, "0")), 
            self.page.gpu_memory_origin)

        # FPS Graph and Text
        fps_value = DashData.best_attempt_read(data, DashData.rtss_fps, "0")
        self.display_surface.blit(self.page.fps_graph.update(fps_value), self.page.fps_graph_origin)
        self.page.font_large.render_to(self.display_surface, self.page.fps_text_origin, "{}".format(fps_value), Color.white)
        self.page.font_normal.render_to(self.display_surface, self.page.fps_label_origin, "FPS", Color.white)

        # Fan gauges
        self.display_surface.blit(        
            self.page.fan1_gauge.update(DashData.best_attempt_read(data, DashData.chassis_1_fan, "0")),
            self.page.fan1_gauge_origin)
        self.display_surface.blit(        
            self.page.fan_opt_gauge.update(DashData.best_attempt_read(data, DashData.cpu_opt_fan, "0")),
            self.page.fan_opt_gauge_origin)
        self.display_surface.blit(        
            self.page.cpu_fan_gauge.update(DashData.best_attempt_read(data, DashData.cpu_fan, "0")),
            self.page.cpu_fan_gauge_origin)
        self.display_surface.blit(        
            self.page.gpu_fan_gauge.update(DashData.best_attempt_read(data, DashData.gpu_fan, "0")),
            self.page.gpu_fan_gauge_origin)

        # Motherboard temp (nestled between all the fans)
        self.page.font_normal.render_to(
            self.display_surface, self.page.mobo_temp_origin, 
            "{}".format(DashData.best_attempt_read(data, DashData.motherboard_temp, "0")), 
            Color.white)

        # Disk activity
        disk_count = 4
        disk_y_offset = 0
        for index in range(disk_count):
            try:
                disk_activity_value = data["disk_{}_activity".format(index)]
            except:
                disk_activity_value = "0"
                if __debug__:
                    print("Data error: disk_{}_activity".format(index))
                    #traceback.print_exc()

            self.display_surface.blit(
                self.page.disk_activity_bar.update(disk_activity_value), 
                (self.page.disk_activity_origin[0], self.page.disk_activity_origin[1] + disk_y_offset))
            disk_y_offset += self.page.disk_activity_y_spacing

        # Network Text
        nic1_down_value = DashData.best_attempt_read(data, DashData.nic1_download_rate, "0")
        network_download_text = "NIC 1 Down: {} {}".format(nic1_down_value, DashData.nic1_download_rate.unit.symbol)
        self.page.font_normal.render_to(
            self.display_surface, 
            self.page.network_text_origin, 
            network_download_text, Color.white)
        
        nic1_up_value = DashData.best_attempt_read(data, DashData.nic1_upload_rate, "0")
        network_upload_text = "Up: {} {}".format(nic1_up_value, DashData.nic1_upload_rate.unit.symbol)
        self.page.font_normal.render_to(
            self.display_surface, 
            (self.page.network_text_origin[0] + 180, self.page.network_text_origin[1]),
            network_upload_text, Color.white)
