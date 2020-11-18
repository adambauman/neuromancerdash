#!/usr/bin/env python

import pygame, pygame.freetype

import os

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

class Helpers:
    @staticmethod
    def transpose_ranges(input, input_high, input_low, output_high, output_low):
        #print("transpose, input: {} iHI: {} iLO: {} oHI: {} oLO: {}".format(input, input_high, input_low, output_high, output_low))
        diff_multiplier = (input - input_low) / (input_high - input_low)
        return ((output_high - output_low) * diff_multiplier) + output_low

    @staticmethod
    def clamp_text(text, max_characters, trailing_text="..."):
        trimmed_text = text[0:max_characters]
        return trimmed_text + trailing_text

    @staticmethod
    def multiply_surface(surface, value):
        "Value is 0 to 255. So 128 would be 50% darken"
        arr = pygame.surfarray.array3d(surface) * value
        arr >>= 8
        pygame.surfarray.blit_array(surface, arr)

class AssetPath:
    # No trailing slashes
    fonts = "assets/fonts"
    gauges = "assets/images/gauges"

class Color:
    yellow = "#ffff00"
    green = "#00dc00"
    dark_green = "#173828"
    red = "#dc0000"
    white = "#ffffff"
    grey_20 = "#333333"
    grey_75 = "#c0c0c0"
    black = "#000000"
    windows_dkgrey_1 = "#4c4a48"

class FontPaths:
    # TODO: (Adam) 2020-11-15 Use os.path.join instead of string concact
    @staticmethod
    def open_sans_regular():
        return AssetPath.fonts + "/Open_Sans/OpenSans-Regular.ttf"
    def open_sans_semibold():
        return AssetPath.fonts + "/Open_Sans/OpenSans-SemiBold.ttf"
    def dm_sans_medium():
        return AssetPath.fonts + "/DM_Sans/DMSans-Medium.ttf"
    def goldman_regular():
        return AssetPath.fonts + "/Goldman/Goldman-Regular.ttf"
    def fira_code_variable():
        return AssetPath.fonts + "/Fira_Code/FiraCode-VariableFont_wght.ttf"
    def fira_code_semibold():
        return AssetPath.fonts + "/Fira_Code/static/FiraCode-SemiBold.ttf"

# TODO: (Adam) 2020-11-14 This is a bit of mess, could use something like Pint for slick unit handling
class Unit:
    name = ""
    symbol = ""
    alt_symbol = ""
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
    field_name = ""
    description = ""
    unit = Units.null_unit
    min_value = None
    caution_value = None
    warn_value = None
    max_value = None
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
class DashData:
    unknown = DataField("", "Unknown", Units.null_unit)
    cpu_util = DataField("cpu_util", "CPU Utilization", Units.percent, min_value=0, max_value=100)
    cpu_temp = DataField("cpu_temp", "CPU Temperature", Units.celsius, min_value=20, caution_value=75, max_value=80, warn_value=82)
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
    cpu_fan = DataField("cpu_fan", "CPU Fan Speed", Units.rpm, min_value=0, max_value=1500)
    cpu_opt_fan = DataField("cpu_opt_fan", "CPU OPT Fan Speed", Units.rpm, min_value=0, max_value=1500)
    chassis_1_fan = DataField("chassis_1_fan", "Chassis 1 Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    chassis_2_fan = DataField("chassis_2_fan", "Chassis 2 Fan Speed", Units.rpm, warn_value=300,min_value=400, max_value=2000)
    chassis_2_fan = DataField("chassis_3_fan", "Chassis 3 Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    gpu_fan = DataField("gpu_fan", "GPU Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    gpu_2_fan = DataField("gpu_2_fan", "GPU Fan Speed?", Units.rpm, min_value=0, max_value=2000)
    desktop_resolution = DataField("desktop_resolution", "Desktop Display Resolution")
    desktop_refresh_rate = DataField("vertical_refresh_rate", "Display Vertical Refresh Rate")
    motherboard_temp = DataField("motherboard_temp", "Motherboard Temperature", Units.celsius, min_value=15, caution_value=50, max_value=60, warn_value=62)
    rtss_fps = DataField("rtss_fps", "Frames Per Second", Units.fps, min_value=0, max_value=60) #Capping at desired max 'cuz slow monitor
    disk_1_activity = DataField("disk_1_activity", "Disk 1 Activity", Units.percent, min_value=0, max_value=100)
    disk_2_activity = DataField("disk_2_activity", "Disk 2 Activity", Units.percent, min_value=0, max_value=100)
    disk_3_activity = DataField("disk_3_activity", "Disk 3 Activity", Units.percent, min_value=0, max_value=100)
    disk_4_activity = DataField("disk_4_activity", "Disk 4 Activity", Units.percent, min_value=0, max_value=100)
    cpu1_util = DataField("cpu1_util", "CPU Core 1 Utilization", Units.percent, min_value=0, max_value=100)
    cpu2_util = DataField("cpu2_util", "CPU Core 2 Utilization", Units.percent, min_value=0, max_value=100)
    cpu3_util = DataField("cpu3_util", "CPU Core 3 Utilization", Units.percent, min_value=0, max_value=100)
    cpu4_util = DataField("cpu4_util", "CPU Core 4 Utilization", Units.percent, min_value=0, max_value=100)
    cpu5_util = DataField("cpu5_util", "CPU Core 5 Utilization", Units.percent, min_value=0, max_value=100)
    cpu6_util = DataField("cpu6_util", "CPU Core 6 Utilization", Units.percent, min_value=0, max_value=100)
    cpu7_util = DataField("cpu7_util", "CPU Core 7 Utilization", Units.percent, min_value=0, max_value=100)
    cpu8_util = DataField("cpu8_util", "CPU Core 8 Utilization", Units.percent, min_value=0, max_value=100)


class GraphConfiguration:
    height = 0
    width = 0
    data_field = None
    font = None
    steps_per_update = 6
    line_color = Color.white
    blend_mode = 0
    vertex_color = Color.white
    vertex_weight = 1
    draw_vertices = False
    display_background = False
    display_range = False
    display_keys = False
    display_unit = False

class LineGraphReverse:
    # Simple line graph that plots data from right to left

    __last_value = 0
    __last_plot_y = 0
    __last_plot_surface = None
    __graph_configuration = None
    __working_surface = None

    def __init__(self, graph_configuration):
        assert(graph_configuration.height != 0 and graph_configuration.width != 0)
        assert(None != graph_configuration.data_field)
        
        self.__graph_configuration = graph_configuration

        self.__working_surface = pygame.Surface((graph_configuration.width, graph_configuration.height))
        self.__last_plot_surface = pygame.Surface((graph_configuration.width, graph_configuration.height))
        
        steps_per_update = graph_configuration.steps_per_update
        self.__last_plot_position = (self.__working_surface.get_width() - steps_per_update, self.__working_surface.get_height())

         # TODO: (Adam) 2020-11-17 Draw initial range, keys, background, etc.

    def update(self, value):
        assert(None != self.__graph_configuration)
        assert(None != self.__last_plot_surface)
        assert(None != self.__working_surface)

        # Clear working surface
        self.__working_surface.fill(Color.black)
       
        # Re-draw or copy static bits

        # Transform self.__previous_plot_surface left by self.__steps_per_update
        steps_per_update = self.__graph_configuration.steps_per_update
        last_plot_position = (self.__working_surface.get_width() - steps_per_update, self.__last_plot_y)

        # Calculate self.__previous_plot_position lefy by self.__steps_per_update, calculate new plot position
        data_field = self.__graph_configuration.data_field
        transposed_value = Helpers.transpose_ranges(
            float(value), 
            data_field.max_value, data_field.min_value, 
            self.__working_surface.get_height(), 0
        )
        new_plot_y = int(self.__working_surface.get_height() - transposed_value)
        new_plot_position = (self.__working_surface.get_width(), new_plot_y)

        # Save values for the next update
        self.__last_plot_y = new_plot_y

        #print("last_plot_position: {}, new_plot_position: {}".format(last_plot_position, new_plot_position))

        # Blit down self.__last_plot_surface and shift to the left by self.__steps_per_update, draw the new line segment
        plot_surface_width = self.__last_plot_surface.get_width()
        plot_surface_height = self.__last_plot_surface.get_height()
        new_plot_surface = pygame.Surface((plot_surface_width, plot_surface_height))

        # Copy down the previous surface but shifted left. TODO: Mess with scroll some more
        new_plot_surface.blit(self.__last_plot_surface, (-steps_per_update, 0))
        pygame.draw.aaline(
            new_plot_surface, 
            self.__graph_configuration.line_color, 
            last_plot_position, new_plot_position, 
            self.__graph_configuration.blend_mode
        )
        self.__working_surface.blit(new_plot_surface, (0, 0))

        # Save values for the next update
        self.__last_plot_surface = new_plot_surface.copy()

        # Blit out any remaining elements that should appear above the rest of the graph elements

        # Return completed working surface
        return self.__working_surface


# TODO: (Adam) 2020-11-17 Gauge config class, make a little more customizable for broader use
class Gauge:
    @staticmethod
    def arc_gauge_flat_90x(value, min_value, max_value, unit_text = "", background_alpha = 0):
        assert(min_value != max_value)

        gauge = pygame.Surface((90,90))

        # NOTE: (Adam) 2020-11-17 Leaning on lazy image loading to cache and discard images, after first call
        #           these should remain in memory until the Image controller detects that no more references exist.
        gauge_face =  pygame.image.load(os.path.join(AssetPath.gauges, "arc_flat_90px_style1.png"))
        needle = pygame.image.load(os.path.join(AssetPath.gauges, "arc_flat_90px_needle.png"))

        gauge_center = ((gauge.get_width() / 2), (gauge.get_height() / 2))

        # needle_0 = 135, needle_redline = -90, needle_100 = -135
        arc_transposed_value = Helpers.transpose_ranges(float(value), max_value, min_value, -135, 135)

        # Needle
        # NOTE: (Adam) 2020-11-17 Not scaling but rotozoom provides a cleaner rotation surface
        rotated_needle = pygame.transform.rotozoom(needle, arc_transposed_value, 1)
        needle_x = gauge_center[0] - (rotated_needle.get_width() / 2)
        needle_y = gauge_center[1] - (rotated_needle.get_height() / 2)

        # Shadow
        shadow = needle.copy()
        shadow.fill((0, 0, 0, 50), special_flags=pygame.BLEND_RGBA_MULT)

        # Add a small %-change multiplier to give the shadow farther distance as values approach limits
        abs_change_from_zero = abs(arc_transposed_value)
        shadow_distance = 4 + ((abs(arc_transposed_value) / 135) * 10)

        shadow_rotation = arc_transposed_value
        if arc_transposed_value > 0: #counter-clockwise
            shadow_rotation += shadow_distance
        else: #clockwise
            shadow_rotation += -shadow_distance
        rotated_shadow = pygame.transform.rotozoom(shadow, shadow_rotation, 0.93)
        #needle_shadow.set_alpha(20)
        shadow_x = gauge_center[0] - (rotated_shadow.get_width() / 2)
        shadow_y = gauge_center[1] - (rotated_shadow.get_height() / 2)

        # Background
        if 0 != background_alpha:
            background_surface = pygame.Surface((gauge.get_width(), gauge.get_height()))
            pygame.draw.circle(background_surface, Color.windows_dkgrey_1, gauge_center, gauge.get_width() / 2)
            background_surface.set_alpha(background_alpha)
            gauge.blit(background_surface, (0, 0))

        # Start blitting down the gauge components
        gauge.blit(gauge_face, (0, 0))
        gauge.blit(rotated_shadow, (shadow_x, shadow_y))
        gauge.blit(rotated_needle, (needle_x, needle_y))

        # Value
        if 0 != len(unit_text):
            font_unit = pygame.freetype.Font(FontPaths.fira_code_semibold(), 8)
            font_unit.strong = True
            font_unit.render_to(gauge, (43, 59), unit_text, Color.white)

        # Readout text
        font_value = pygame.freetype.Font(FontPaths.fira_code_semibold(), 16)
        font_value.strong = True
        # NOTE: (Adam) 2020-11-17 Dynamic centered text dances around a little, sticking with
        #           static placement for now.
        font_value.render_to(gauge, (35, 70), value, Color.white)

        return gauge


class DashPainter:
    __cpu_graph = None
    __gpu_graph = None

    def __init__(self, display_surface):
        self.display_surface = display_surface

    def __get_next_vertical_stack_origin__(self, last_origin, font, padding = 0):
        x = last_origin[0]
        y = last_origin[1] + font.get_sized_height() + padding
        return (x,y)

    def __paint_cpu_text_stack__(self, origin, font_normal, data):
        assert(0 != len(data))

        stack_vertical_adjustment = -2

        text_origin = origin
        text = "{} {}".format(data[DashData.cpu_power.field_name], DashData.cpu_power.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(data[DashData.cpu_clock.field_name], DashData.cpu_clock.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{}{}".format(data[DashData.cpu_util.field_name], DashData.cpu_util.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "RAM"
        font_normal.render_to(self.display_surface, text_origin, text, Color.grey_75)

    def __paint_gpu_text_stack__(self, origin, font_normal, data):
        assert(0 != len(data))

        stack_vertical_adjustment = -2

        text_origin = origin
        text = "PerfCap:"
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{}".format(data[DashData.gpu_perfcap_reason.field_name])
        font_normal.render_to(self.display_surface, text_origin, Helpers.clamp_text(text,11, ""), Color.yellow)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(data[DashData.gpu_power.field_name], DashData.gpu_power.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(data[DashData.gpu_clock.field_name], DashData.gpu_clock.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.white)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{}{}".format(data[DashData.gpu_util.field_name], DashData.gpu_util.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "RAM"
        font_normal.render_to(self.display_surface, text_origin, text, Color.grey_75)

    def paint(self, data):
        assert(0 != len(data))

        self.display_surface.fill(Color.black)

        font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        font_normal.strong = False
        font_normal.kerning = True

        cpu_detail_stack_origin = (310, 33)
        gpu_detail_stack_origin = (310, 110)
        cpu_temp_gauge_origin = (self.display_surface.get_width() - 90, 3)
        gpu_temp_gauge_origin = (self.display_surface.get_width() - 90, 107)
        cpu_graph_origin = (0, 2)

        # CPU Data
        self.__paint_cpu_text_stack__(cpu_detail_stack_origin, font_normal, data)

        # GPU Data
        self.__paint_gpu_text_stack__(gpu_detail_stack_origin, font_normal, data)

        # CPU and GPU Temps
        cpugpu_gauge_bg_alpha = 200
        cpu_temp_gauge = Gauge.arc_gauge_flat_90x(
            data[DashData.cpu_temp.field_name],
            DashData.cpu_temp.min_value, DashData.cpu_temp.max_value, DashData.cpu_temp.unit.symbol,
            cpugpu_gauge_bg_alpha
        )
        self.display_surface.blit(cpu_temp_gauge, cpu_temp_gauge_origin)

        gpu_temp_gauge = Gauge.arc_gauge_flat_90x(
            data[DashData.gpu_temp.field_name],
            DashData.gpu_temp.min_value, DashData.gpu_temp.max_value, DashData.gpu_temp.unit.symbol,
            cpugpu_gauge_bg_alpha
        )
        self.display_surface.blit(gpu_temp_gauge, gpu_temp_gauge_origin)

        # CPU and GPU Utilization
        if None == self.__cpu_graph:
            graph_config = GraphConfiguration
            graph_config.data_field = DashData.cpu_util
            graph_config.line_color = Color.yellow
            graph_config.blend_mode = 0
            graph_config.height = 68
            graph_config.width = 300
            self.__cpu_graph = LineGraphReverse(graph_config)

        cpu_graph = self.__cpu_graph.update(data[DashData.cpu_util.field_name])
        self.display_surface.blit(cpu_graph, cpu_graph_origin)
        