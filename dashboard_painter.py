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

    # TODO: (Adam) 2020-11-18 Switch to regex for tighter comparisons
    # TODO: (Adam) 2020-11-18 Maybe move this into the DataField class with a count method
    @staticmethod
    def is_cpu_core_utilization(key):
        # Skip combined cpu_util
        if "cpu_util" == key:
            return False

        is_match = False
        # cpu(n)_util
        if "cpu" == key[0:3] and "_util" == key[-5: ]:
            is_match = True

        return is_match

    @staticmethod
    def is_disk_activity(key):
        is_match = False
        # disk(n)_activity
        if "disk_" == key[0:3] and "_activity" == key[-9: ]:
            is_match = True
        return is_match


class AssetPath:
    # No trailing slashes
    fonts = "assets/fonts"
    gauges = "assets/images/gauges"
    graphs = "assets/images/graphs"

class Color:
    yellow = "#ffff00"
    green = "#00dc00"
    dark_green = "#173828"
    red = "#dc0000"
    white = "#ffffff"
    grey_20 = "#333333"
    grey_75 = "#c0c0c0"
    black = "#000000"
    windows_cyan_1 = "#00b693"
    windows_cyan_1_dark = "#015b4a"
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
    rtss_fps = DataField("rtss_fps", "Frames Per Second", Units.fps, min_value=0, max_value=120)

    # Iterate the following, labels in data source should be setup to be 0-indexed
    disk_activity = DataField("disk_{}_activity", "Disk {} Activity", Units.percent, min_value=0, max_value=100)
    cpu_core_utilization = DataField("cpu{}_util", "CPU Core {} Utilization", Units.percent, min_value=0, max_value=100)


class CoreVisualizerConfig:
    core_width = 13
    core_spacing = 2
    core_rows = 2
    core_height = None
    active_color = Color.windows_cyan_1
    inactive_color = Color.windows_cyan_1_dark
    # Percentage of activity required to light up core representation
    activity_threshold_percent = 12
class SimpleCoreVisualizer:
    __config = CoreVisualizerConfig
    __core_count = 0 # Found by iterating all "cpu{}_util" fields
    __base_surface = None
    __cores_per_row = 0

    # Tracking outside config in case we need to adjust on the fly
    __core_height = 0
    __core_width = 0
    
    __last_core_activity = []
    __last_base_surface = None

    __first_run = True

    def __init__(self, data, core_visualizer_config = CoreVisualizerConfig):
        assert(0 != self.__config.core_width)
        assert(0 != len(data))

        self.__config = core_visualizer_config

        self.__core_count = 0
        for single_data in data:
            if Helpers.is_cpu_core_utilization(single_data):
                self.__core_count += 1

        assert(0 != self.__core_count)

        self.__core_width = self.__config.core_width
        self.__core_height = self.__config.core_height
        if None == self.__core_height:
            self.__core_height = self.__core_width

        assert(0 != self.__core_height)

        # Rounds up if reminder exists
        self.__cores_per_row = int(self.__core_count / self.__config.core_rows) + (self.__core_count % self.__config.core_rows > 0)

        # Initialize last surface
        base_width = (self.__core_width * self.__cores_per_row) + (self.__config.core_spacing * (self.__cores_per_row -1))
        base_height = (self.__core_height * self.__config.core_rows) + (self.__config.core_spacing * (self.__config.core_rows - 1))
        self.__last_base_surface = pygame.Surface((base_width, base_height))

        # Initialize last core activity and do a hack update
        initialize_data = {}
        for index in range(self.__core_count):
            key = "cpu{}_util".format(index)
            initialize_data[key] = 0
            self.__last_core_activity.append(False)

        self.update(initialize_data)
        self.__first_run = False

    def update(self, data):
        assert(None != self.__last_base_surface and 0 != len(self.__last_core_activity))
        assert(self.__core_count == len(self.__last_core_activity))
        assert(len(data) >= self.__core_count)

        # Copy in last core surface, we will only update the altered representations
        self.__base_surface = self.__last_base_surface.copy()

        core_origin_x = 0
        core_origin_y = 0
        core_activity_tracking = []
        for index in range(self.__core_count):

            key_name = "cpu{}_util".format(index)
            core_activity_value = int(data[key_name])
            core_active = False
            if core_activity_value >= self.__config.activity_threshold_percent:
                #print("Core{} active at {}%".format(index, core_activity_value))
                core_active = True

            # Track activity for the next update call
            core_activity_tracking.append(core_active)

            # No need to re-draw if status hasn't changed
            if self.__last_core_activity[index] == core_active and self.__first_run != False:
                continue

            core_color = self.__config.inactive_color
            if core_active:
                core_color = self.__config.active_color

            pygame.draw.rect(
                self.__base_surface, 
                core_color, 
                (core_origin_x, core_origin_y, self.__core_width, self.__core_width)
            )

            if len(core_activity_tracking) == self.__cores_per_row:
                # Move to the next row
                core_origin_y += self.__core_width + self.__config.core_spacing
                core_columns_drawn = 0
                core_origin_x = 0
            else:
                # Move to the next column
                core_origin_x += self.__core_width + self.__config.core_spacing


        assert(len(self.__last_core_activity) == len(core_activity_tracking))
        self.__last_core_activity = core_activity_tracking

        # Save for next update
        self.__last_base_surface = self.__base_surface.copy()

        return self.__base_surface

# TODO: (Adam) 2020-11-18 Really dumbed here with Python classes, configurations need to be re-structured
class GraphConfig:
    height = 0
    width = 0
    plot_padding = 0
    data_field = None
    steps_per_update = 6
    line_color = Color.yellow
    line_width = 2 # Line weights below 2 might result in missing segments
    vertex_color = Color.yellow
    vertex_weight = 1
    draw_vertices = False
    display_background = False
    draw_on_zero = True
class LineGraphReverse:
    # Simple line graph that plots data from right to left

    __last_plot_y = 0
    __last_plot_surface = None
    __graph_config = None
    __working_surface = None
    __background = None

    def __init__(self, graph_config):
        assert(graph_config.height != 0 and graph_config.width != 0)
        assert(None != graph_config.data_field)
        
        self.__graph_config = graph_config

        self.__working_surface = pygame.Surface((graph_config.width, graph_config.height), pygame.SRCALPHA)

        plot_width = graph_config.width - (graph_config.plot_padding * 2)
        plot_height = graph_config.height - (graph_config.plot_padding * 2)
        self.__last_plot_surface = pygame.Surface((graph_config.width, graph_config.height), pygame.SRCALPHA)
        
        steps_per_update = graph_config.steps_per_update
        self.__last_plot_y = self.__last_plot_surface.get_height()

        if self.__graph_config.display_background:
            self.__background = pygame.image.load(os.path.join(AssetPath.graphs, "grid_8px_dkcyan.png"))
            self.__working_surface.blit(self.__background, (0, 0))

    def update(self, value):
        assert(None != self.__graph_config)
        assert(None != self.__last_plot_surface)
        assert(None != self.__working_surface)

        # Clear working surface
        if None != self.__background:
            self.__working_surface.blit(self.__background, (0, 0))
        else:
            self.__working_surface.fill(Color.black)

        # Transform self.__previous_plot_surface left by self.__steps_per_update
        steps_per_update = self.__graph_config.steps_per_update
        last_plot_position = (self.__working_surface.get_width() - steps_per_update, self.__last_plot_y)

        # Calculate self.__previous_plot_position lefy by self.__steps_per_update, calculate new plot position
        data_field = self.__graph_config.data_field
        transposed_value = Helpers.transpose_ranges(
            float(value), 
            data_field.max_value, data_field.min_value, 
            self.__working_surface.get_height(), 0
        )

        plot_padding = self.__graph_config.plot_padding
        new_plot_y = int(self.__working_surface.get_height() - transposed_value)

        # Clamp the reanges in case something rounds funny
        if self.__graph_config.line_width >= new_plot_y:
            new_plot_y = self.__graph_config.line_width
        if (self.__working_surface.get_height() - self.__graph_config.line_width) <= new_plot_y:
            new_plot_y = self.__working_surface.get_height() - self.__graph_config.line_width

        new_plot_position = (self.__working_surface.get_width() - plot_padding, new_plot_y)

        # Save values for the next update
        self.__last_plot_y = new_plot_y

        # Blit down self.__last_plot_surface and shift to the left by self.__steps_per_update, draw the new line segment
        plot_surface_width = self.__last_plot_surface.get_width()
        plot_surface_height = self.__last_plot_surface.get_height()
        new_plot_surface = pygame.Surface((plot_surface_width, plot_surface_height), pygame.SRCALPHA)

        # Copy down the previous surface but shifted left. TODO: Mess with scroll some more
        new_plot_surface.blit(self.__last_plot_surface, (-steps_per_update, 0))

        enable_draw = True
        if 0 == int(value) and self.__graph_config.draw_on_zero == False:
            enable_draw = False

        if enable_draw:
            pygame.draw.line(
                new_plot_surface,
                self.__graph_config.line_color,
                last_plot_position, new_plot_position,
                self.__graph_config.line_width
            )

            # Draw vertex if enabled
            if self.__graph_config.draw_vertices:
                pygame.draw.circle(
                    new_plot_surface,
                    self.__graph_config.vertex_color,
                    last_plot_position,
                    1 * self.__graph_config.vertex_weight
                )

        self.__working_surface.blit(new_plot_surface, (plot_padding, plot_padding))

        # Save values for the next update
        self.__last_plot_surface = new_plot_surface.copy()

        # Return completed working surface
        return self.__working_surface


class BarGraphConfig:
    width = 0
    height = 0
    data_field = None
    foreground_color = Color.white
    background_color = Color.windows_dkgrey_1

    def __init__(self, width, height, data_field):
        assert(0 != width and 0 != height)
        self.width, self.height = width, height
        self.data_field = data_field

class BarGraph:
    __config = None
    __working_surface = None
    __first_run = True
    __last_value = 0

    def __init__(self, bar_graph_config):
        assert(0 != bar_graph_config.width and 0 != bar_graph_config.height)
        assert(None != bar_graph_config.data_field)

        self.__config = bar_graph_config
        self.__working_surface = pygame.Surface((self.__config.width, self.__config.height))
        
        self.update(0)
        self.__first_run = False

    def update(self, value):
        
        # Reuse previous surface if value hasn't changed
        if self.__last_value == value and self.__first_run != True:
            return self.__working_surface

        # Draw the background, we'll use the existing member surface
        self.__working_surface.fill(self.__config.background_color)

        # Draw the value rect
        data_field = self.__config.data_field
        transposed_value = Helpers.transpose_ranges(float(value), data_field.max_value, data_field.min_value, self.__config.width, 0)
        draw_rect = (0, 0, transposed_value, self.__config.height)
        pygame.draw.rect(self.__working_surface, self.__config.foreground_color, draw_rect)

        self.__last_value = value

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
    __fps_graph = None
    __core_visualizer = None
    __sys_memory_bar = None
    __gpu_memory_bar = None

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
        text = "RAM Used"
        font_normal.render_to(self.display_surface, text_origin, text, Color.grey_75)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(data[DashData.sys_ram_used.field_name], DashData.sys_ram_used.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

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
        text = "RAM Used"
        font_normal.render_to(self.display_surface, text_origin, text, Color.grey_75)

        text_origin = self.__get_next_vertical_stack_origin__(text_origin, font_normal, stack_vertical_adjustment)
        text = "{} {}".format(data[DashData.gpu_ram_used.field_name], DashData.gpu_ram_used.unit.symbol)
        font_normal.render_to(self.display_surface, text_origin, text, Color.yellow)

    def paint(self, data):
        assert(0 != len(data))

        self.display_surface.fill(Color.black)

        font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        #font_normal.strong = True
        font_normal.kerning = True

        font_large = pygame.freetype.Font(FontPaths.fira_code_semibold(), 50)
        #font_large.strong = True
        font_large_kerning = True

        core_visualizer_origin = (310, 0)
        cpu_detail_stack_origin = (310, 33)
        gpu_detail_stack_origin = (310, 115)
        cpu_temp_gauge_origin = (self.display_surface.get_width() - 90, 7)
        gpu_temp_gauge_origin = (self.display_surface.get_width() - 90, 117)
        cpu_graph_origin = (0, 0)
        gpu_graph_origin = (0, 110)

        sys_memory_origin = (0, 75)
        gpu_memory_origin = (0, 185)

        fps_graph_origin = (0, 220)
        fps_text_origin = (210, 230)
        fps_label_origin = (212, 275)
        network_text_origin = (0, 310)

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
            cpu_graph_config = GraphConfig
            cpu_graph_config.data_field = DashData.cpu_util
            cpu_graph_config.height, cpu_graph_config.width = 70, 300
            cpu_graph_config.display_background = True
            self.__cpu_graph = LineGraphReverse(cpu_graph_config)

        cpu_graph = self.__cpu_graph.update(data[DashData.cpu_util.field_name])
        self.display_surface.blit(cpu_graph, cpu_graph_origin)

        if None == self.__gpu_graph:
            gpu_graph_config = GraphConfig
            gpu_graph_config.data_field = DashData.gpu_util
            gpu_graph_config.height, gpu_graph_config.width = 70, 300
            gpu_graph_config.display_background = True
            self.__gpu_graph = LineGraphReverse(gpu_graph_config)

        gpu_graph = self. __gpu_graph.update(data[DashData.gpu_util.field_name])
        self.display_surface.blit(gpu_graph, gpu_graph_origin)

        # CPU Core Visualizer
        if None == self.__core_visualizer:
            core_visualizer_config = CoreVisualizerConfig
            self.__core_visualizer = SimpleCoreVisualizer(data, core_visualizer_config)

        core_visualizer = self.__core_visualizer.update(data)
        self.display_surface.blit(core_visualizer, core_visualizer_origin)

        # System and GPU memory usage
        if None == self.__sys_memory_bar:
            sys_memory_bar_config = BarGraphConfig(300, 25, DashData.sys_ram_used)
            self.__sys_memory_bar = BarGraph(sys_memory_bar_config)

        sys_memory_bar_surface = self.__sys_memory_bar.update(data[DashData.sys_ram_used.field_name])
        self.display_surface.blit(sys_memory_bar_surface, sys_memory_origin)

        if None == self.__gpu_memory_bar:
            gpu_memory_bar_config = BarGraphConfig(300, 25, DashData.gpu_ram_used)
            self.__gpu_memory_bar = BarGraph(gpu_memory_bar_config)

        gpu_memory_bar_surface = self.__gpu_memory_bar.update(data[DashData.gpu_ram_used.field_name])
        self.display_surface.blit(gpu_memory_bar_surface, gpu_memory_origin)

        # FPS Graph and Text
        if None == self.__fps_graph:
            fps_graph_config = GraphConfig
            fps_graph_config.data_field = DashData.rtss_fps
            fps_graph_config.height, fps_graph_config.width = 70, 200
            fps_graph_config.display_background = True
            fps_graph_config.draw_on_zero = False
            self.__fps_graph = LineGraphReverse(fps_graph_config)

        fps_value = data[DashData.rtss_fps.field_name]
        fps_graph = self.__fps_graph.update(fps_value)
        self.display_surface.blit(fps_graph, fps_graph_origin)
        font_large.render_to(self.display_surface, fps_text_origin, "{}".format(fps_value), Color.white)
        font_normal.render_to(self.display_surface, fps_label_origin, "FPS", Color.white)

        # Network Text
        network_download_text = "NIC 1 Down: {} {}".format(data[DashData.nic1_download_rate.field_name], DashData.nic1_download_rate.unit.symbol)
        font_normal.render_to(self.display_surface, network_text_origin, network_download_text, Color.white)
        network_upload_text = "Up: {} {}".format(data[DashData.nic1_upload_rate.field_name], DashData.nic1_upload_rate.unit.symbol)
        font_normal.render_to(self.display_surface, (network_text_origin[0] + 180, network_text_origin[1]), network_upload_text, Color.white)
