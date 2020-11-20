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
    def calculate_center_align(parent_surface, child_surface):

        parent_center = (parent_surface.get_width() / 2, parent_surface.get_height() / 2)
        child_center = (child_surface.get_width() / 2, child_surface.get_height() / 2)
        
        child_align_x = parent_center[0] - child_center[0]
        child_align_y = parent_center[1] - child_center[1]

        return (child_align_x, child_align_y)

    def transpose_ranges(input, input_high, input_low, output_high, output_low):
        #print("transpose, input: {} iHI: {} iLO: {} oHI: {} oLO: {}".format(input, input_high, input_low, output_high, output_low))
        diff_multiplier = (input - input_low) / (input_high - input_low)
        return ((output_high - output_low) * diff_multiplier) + output_low

    def clamp_text(text, max_characters, trailing_text="..."):
        trimmed_text = text[0:max_characters]
        return trimmed_text + trailing_text

    # TODO: (Adam) 2020-11-18 Switch to regex for tighter comparisons
    # TODO: (Adam) 2020-11-18 Maybe move this into the DataField class with a count method
    def is_cpu_core_utilization(key):
        # Skip combined cpu_util
        if "cpu_util" == key:
            return False

        is_match = False
        # cpu(n)_util
        if "cpu" == key[0:3] and "_util" == key[-5: ]:
            is_match = True

        return is_match

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
    grey_40 = "#666666"
    grey_75 = "#c0c0c0"
    black = "#000000"
    cyan_dark = "#1c2f2b"
    # Colors pulled from Win10 design doc swatches
    windows_cyan_1 = "#00b693"
    windows_cyan_1_dark = "#015b4a"
    windows_cyan_2 = "#008589"
    windows_red_1 = "#eb2400"
    windows_dkgrey_1 = "#4c4a48"
    windows_light_grey_1 = "#7b7574"

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
    cpu_fan = DataField("cpu_fan", "CPU Fan Speed", Units.rpm, min_value=1000, max_value=1460, warn_value=1100)
    cpu_opt_fan = DataField("cpu_opt_fan", "CPU OPT Fan Speed", Units.rpm, warn_value=300, min_value=500, max_value=1500)
    chassis_1_fan = DataField("chassis_1_fan", "Chassis 1 Fan Speed", Units.rpm, warn_value=300, min_value=500, max_value=2000)
    chassis_2_fan = DataField("chassis_2_fan", "Chassis 2 Fan Speed", Units.rpm, warn_value=300,min_value=500, max_value=2000)
    chassis_2_fan = DataField("chassis_3_fan", "Chassis 3 Fan Speed", Units.rpm, warn_value=300, min_value=500, max_value=2000)
    gpu_fan = DataField("gpu_fan", "GPU Fan Speed", Units.rpm, warn_value=300, min_value=500, max_value=2000)
    gpu_2_fan = DataField("gpu_2_fan", "GPU Fan Speed?", Units.rpm, min_value=0, max_value=2000)
    desktop_resolution = DataField("desktop_resolution", "Desktop Display Resolution")
    desktop_refresh_rate = DataField("vertical_refresh_rate", "Display Vertical Refresh Rate")
    motherboard_temp = DataField("motherboard_temp", "Motherboard Temperature", Units.celsius, min_value=15, caution_value=50, max_value=60, warn_value=62)
    rtss_fps = DataField("rtss_fps", "Frames Per Second", Units.fps, min_value=0, max_value=120)

    # Iterate the following, labels in data source should be setup to be 0-indexed
    disk_activity = DataField("disk_{}_activity", "Disk {} Activity", Units.percent, min_value=0, max_value=100)
    cpu_core_utilization = DataField("cpu{}_util", "CPU Core {} Utilization", Units.percent, min_value=0, max_value=100)


class CoreVisualizerConfig:
    def __init__(self, core_count):
        self.core_count = core_count
        self.core_width = 13
        self.core_spacing = 2
        self.core_rows = 2
        self.core_height = None
        self.active_color = Color.windows_cyan_1
        self.inactive_color = Color.windows_cyan_1_dark
        # Percentage of activity required to light up core representation
        self.activity_threshold_percent = 12
class SimpleCoreVisualizer:
    __config = CoreVisualizerConfig
    __core_count = 0
    __base_surface = None
    __cores_per_row = 0

    # Tracking outside config in case we need to adjust on the fly
    __core_height = 0
    __core_width = 0
    
    __last_core_activity = []
    __last_base_surface = None

    __first_run = True

    def __init__(self, core_visualizer_config):
        self.__config = core_visualizer_config
        
        # NOTE: (Adam) 2020-11-19 Setting for compatability with new config setup
        self.__core_count = self.__config.core_count

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
        #assert(self.__core_count == len(self.__last_core_activity))
        assert(len(data) >= self.__core_count)

        # Copy in last core surface, we will only update the altered representations
        self.__base_surface = self.__last_base_surface.copy()

        core_origin_x = 0
        core_origin_y = 0
        core_activity_tracking = []
        for index in range(self.__core_count):

            key_name = "cpu{}_util".format(index)
            core_activity_value = 0
            if key_name in data:
                # NOTE: (Adam) 2020-11-19 Util key data sometimes get mixed up, just set false if a \
                #           core or two are missing
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


        #assert(len(self.__last_core_activity) == len(core_activity_tracking))
        self.__last_core_activity = core_activity_tracking

        # Save for next update
        self.__last_base_surface = self.__base_surface.copy()

        return self.__base_surface


class LineGraphConfig:
    def __init__(self, height, width, data_field):
        self.height, self.width = height, width
        self.plot_padding = 0
        self.data_field = data_field
        self.steps_per_update = 6
        self.line_color = Color.yellow
        self.line_width = 1
        self.vertex_color = Color.yellow
        self.vertex_weight = 1
        self.draw_vertices = False
        self.display_background = False
        self. draw_on_zero = True
class LineGraphReverse:
    # Simple line graph that plots data from right to left

    __last_plot_y = 0
    __last_plot_surface = None
    __config = None
    __working_surface = None
    __background = None

    def __init__(self, line_graph_config):
        assert(line_graph_config.height != 0 and line_graph_config.width != 0)
        assert(None != line_graph_config.data_field)
        
        self.__config = line_graph_config

        self.__working_surface = pygame.Surface((self.__config.width, self.__config.height), pygame.SRCALPHA)

        plot_width = self.__config.width - (self.__config.plot_padding * 2)
        plot_height = self.__config.height - (self.__config.plot_padding * 2)
        self.__last_plot_surface = pygame.Surface((self.__config.width, self.__config.height), pygame.SRCALPHA)
        
        steps_per_update = self.__config.steps_per_update
        self.__last_plot_y = self.__last_plot_surface.get_height()

        if self.__config.display_background:
            self.__background = pygame.image.load(os.path.join(AssetPath.graphs, "grid_8px_dkcyan.png"))
            self.__working_surface.blit(self.__background, (0, 0))

    def update(self, value):
        assert(None != self.__config)
        assert(None != self.__last_plot_surface)
        assert(None != self.__working_surface)

        # Clear working surface
        if None != self.__background:
            self.__working_surface.blit(self.__background, (0, 0))
        else:
            self.__working_surface.fill(Color.black)

        # Transform self.__previous_plot_surface left by self.__steps_per_update
        steps_per_update = self.__config.steps_per_update
        last_plot_position = (self.__working_surface.get_width() - steps_per_update, self.__last_plot_y)

        # Calculate self.__previous_plot_position lefy by self.__steps_per_update, calculate new plot position
        data_field = self.__config.data_field
        transposed_value = Helpers.transpose_ranges(
            float(value), 
            data_field.max_value, data_field.min_value, 
            self.__working_surface.get_height(), 0
        )

        plot_padding = self.__config.plot_padding
        new_plot_y = int(self.__working_surface.get_height() - transposed_value)

        # Clamp the reanges in case something rounds funny
        if self.__config.line_width >= new_plot_y:
            new_plot_y = self.__config.line_width
        if (self.__working_surface.get_height() - self.__config.line_width) <= new_plot_y:
            new_plot_y = self.__working_surface.get_height() - self.__config.line_width

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
        if 0 == int(value) and self.__config.draw_on_zero == False:
            enable_draw = False

        if enable_draw:
            pygame.draw.line(
                new_plot_surface,
                self.__config.line_color,
                last_plot_position, new_plot_position,
                self.__config.line_width
            )

            # Draw vertex if enabled
            if self.__config.draw_vertices:
                pygame.draw.circle(
                    new_plot_surface,
                    self.__config.vertex_color,
                    last_plot_position,
                    1 * self.__config.vertex_weight
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


class GaugeConfig:
    def __init__(self, data_field, radius = 45, value_font = None, value_font_origin = None):
        self.radius = radius
        self.data_field = data_field
        self.redline_degrees = 35
        self.aa_multiplier = 2

        self.value_font = value_font # Take from caller so you can match their other displays
        self.value_font_origin = value_font_origin # If None the value will be centered

        self.arc_main_color = Color.windows_cyan_1
        self.arc_redline_color = Color.windows_red_1
        self.needle_color = Color.windows_light_grey_1
        self.shadow_color = Color.black
        self.shadow_alpha = 50
        self.unit_text_color = Color.white
        self.value_text_color = Color.white
        self.bg_color = Color.windows_dkgrey_1
        self.bg_alpha = 200

        self.counter_sweep = False
        self.show_value = True
        self.show_unit_symbol = True
        self.show_label_instead_of_value = False
        self.label = ""
class FlatArcGauge:
    __config = None
    __last_value = None
    __working_surface = None

    __static_elements_surface = None # Should not be changed after init
    __needle_surface = None # Should not be changed after init
    __needle_shadow_surface = None  # Should not be changed after init

    def __init__(self, gauge_config):
        assert(None != gauge_config.data_field)
        assert(0 < gauge_config.radius)

        self.__config = gauge_config

        # NOTE: (Adam) 2020-11-19 Bit of a hack, adding small amount of padding so AA edges don't get clipped

        base_size = (self.__config.radius * 2, self.__config.radius * 2)
        self.__working_surface = pygame.Surface(base_size, pygame.SRCALPHA)
        self.__static_elements_surface = self.__working_surface.copy()

        self.__prepare_constant_elements()

        assert(None != self.__static_elements_surface)
        assert(None != self.__needle_surface and None != self.__needle_shadow_surface)

    def __prepare_constant_elements(self):
        assert(None != self.__static_elements_surface)
        assert(0 < self.__config.aa_multiplier)
        
        print("Preparing {} arc gauge components...".format(self.__config.data_field.field_name))

        # Have tried drwaing with pygame.draw and gfxdraw but the results were sub-par. Now using large
        # PNG shapes to build up the gauge then scaling down to final size.
        arc_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1_base_1.png"))
        redline_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1_redline_1.png"))

        assert(arc_bitmap.get_width() >= arc_bitmap.get_height())
        base_scaled_size = (arc_bitmap.get_width(), arc_bitmap.get_width())

        temp_surface = pygame.Surface(base_scaled_size, pygame.SRCALPHA)
        center = (temp_surface.get_width() / 2, temp_surface.get_height() / 2)

        scaled_radius = arc_bitmap.get_width() / 2

        # Draw background
        bg_surface = pygame.Surface((temp_surface.get_height(), temp_surface.get_width()), pygame.SRCALPHA)
        bg_color = pygame.Color(self.__config.bg_color)
        pygame.draw.circle(bg_surface, bg_color, center, scaled_radius)
        bg_surface.set_alpha(self.__config.bg_alpha)
        temp_surface.blit(bg_surface, (0, 0))

        # Apply color to main arc and blit
        arc_main_color = pygame.Color(self.__config.arc_main_color)
        arc_bitmap.fill(arc_main_color, special_flags = pygame.BLEND_RGBA_MULT)
        temp_surface.blit(arc_bitmap, (0, 0))

        # Apply color to redline and blit
        arc_redline_color = pygame.Color(self.__config.arc_redline_color)
        redline_bitmap.fill(arc_redline_color, special_flags = pygame.BLEND_RGBA_MULT)
        if self.__config.counter_sweep:
            temp_surface.blit(pygame.transform.flip(redline_bitmap, True, False), (0, 0))
        else:
            temp_surface.blit(redline_bitmap, (0, 0))

        # Draw static text
        # Unit
        if self.__config.show_unit_symbol:
            font_unit = pygame.freetype.Font(FontPaths.fira_code_semibold(), 120)
            font_unit.strong = False
            unit_text_surface = font_unit.render(self.__config.data_field.unit.symbol, self.__config.unit_text_color)
            center_align = Helpers.calculate_center_align(temp_surface, unit_text_surface[0])
            temp_surface.blit(unit_text_surface[0], (center_align[0], center_align[1] + 300))

        # Scale to the final size
        scale_to_size = (
            self.__static_elements_surface.get_width(), 
            self.__static_elements_surface.get_height()
        )
        scaled_surface = pygame.transform.smoothscale(temp_surface, scale_to_size)

        # Clear member static_elements surface and blit our scaled surface
        self.__static_elements_surface.fill((0, 0, 0, 0))
        self.__static_elements_surface = scaled_surface.copy()
     
        # Setup needle elements, these will be rotated when blitted but the memeber surfaces will remain static
        needle_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1_needle_1.png"))
        
        # Apply color to needle, scale, then blit out to the needle surface
        needle_color = pygame.Color(self.__config.needle_color)
        needle_bitmap.fill(needle_color, special_flags = pygame.BLEND_RGBA_MULT)
        needle_center = Helpers.calculate_center_align(temp_surface, needle_bitmap)
        temp_surface.fill((0, 0, 0, 0))
        temp_surface.blit(needle_bitmap, needle_center)

        needle_scaled_surface = pygame.transform.smoothscale(temp_surface, scale_to_size)
        self.__needle_surface = needle_scaled_surface.copy()

        # Needle shadow
        self.__needle_shadow_surface = self.__needle_surface.copy()
        shadow_color = pygame.Color(self.__config.shadow_color)
        shadow_color.a = self.__config.shadow_alpha
        self.__needle_shadow_surface.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)

        print("Done generating components!")
        

    def update(self, value):
        assert(None != self.__working_surface)

        # Don't draw if the value hasn't changed
        if self.__last_value == value:
            return(self.__working_surface)

        self.__working_surface = self.__static_elements_surface.copy()

        max_value = self.__config.data_field.max_value
        min_value = self.__config.data_field.min_value
        arc_transposed_value = Helpers.transpose_ranges(float(value), max_value, min_value, -135, 135)

        # Needle
        # NOTE: (Adam) 2020-11-17 Not scaling but rotozoom provides a cleaner rotation surface
        rotated_needle = pygame.transform.rotozoom(self.__needle_surface, arc_transposed_value, 1)

        # Shadow
        # Add a small %-change multiplier to give the shadow farther distance as values approach limits
        abs_change_from_zero = abs(arc_transposed_value)
        shadow_distance = 4 + ((abs(arc_transposed_value) / 135) * 10)

        shadow_rotation = arc_transposed_value
        if arc_transposed_value > 0: #counter-clockwise
            shadow_rotation += shadow_distance
        else: #clockwise
            shadow_rotation += -shadow_distance
        rotated_shadow = pygame.transform.rotozoom(self.__needle_shadow_surface, shadow_rotation, 0.93)
        #needle_shadow.set_alpha(20)
        shadow_center = Helpers.calculate_center_align(self.__working_surface, rotated_shadow)
        self.__working_surface.blit(rotated_shadow, shadow_center)

        needle_center = Helpers.calculate_center_align(self.__working_surface, rotated_needle)
        self.__working_surface.blit(rotated_needle, needle_center)

        # Value Text
        value_color = self.__config.value_text_color
        if None !=  self.__config.data_field.warn_value:
            if not self.__config.counter_sweep and int(value) > self.__config.data_field.warn_value:
                value_color = Color.windows_red_1 # TODO: configurable warn color?
            elif self.__config.counter_sweep and int(value) < self.__config.data_field.warn_value:
                value_color = Color.windows_red_1 # TODO: configurable warn color?

        if None != self.__config.value_font and False != self.__config.show_value:

            value_text = "{}".format(value)
            if self.__config.show_label_instead_of_value:
                value_text = self.__config.label

            value_surface = self.__config.value_font.render(value_text, value_color)

            if None != self.__config.value_font_origin:
                value_origin = self.__config.value_font_origin
            else:
                value_origin = Helpers.calculate_center_align(self.__working_surface, value_surface[0])

            self.__working_surface.blit(value_surface[0], value_origin)

        # Track for the next update
        self.__last_value = value

        return self.__working_surface


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
        self.cpu_temp_gauge = FlatArcGauge(cpu_temp_gauge_config)

        gpu_temp_gauge_config = GaugeConfig(DashData.gpu_temp, 45, self.font_gauge_value, (35, 70))
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
        self.sys_memory_bar = BarGraph(sys_memory_bar_config)

        gpu_memory_bar_config = BarGraphConfig(300, 25, DashData.gpu_ram_used)
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
        assert(None != self.page)

        self.display_surface.fill(Color.black)

        # CPU Data
        self.__paint_cpu_text_stack__(self.page.cpu_detail_stack_origin, self.page.font_normal, data)

        # GPU Data
        self.__paint_gpu_text_stack__(self.page.gpu_detail_stack_origin, self.page.font_normal, data)

        # CPU and GPU Temps
        self.display_surface.blit(        
            self.page.cpu_temp_gauge.update(data[DashData.cpu_temp.field_name]),
            self.page.cpu_temp_gauge_origin)

        self.display_surface.blit(
            self.page.gpu_temp_gauge.update(data[DashData.gpu_temp.field_name]), 
            self.page.gpu_temp_gauge_origin)

        # CPU and GPU Utilization
        self.display_surface.blit(
            self.page.cpu_graph.update(data[DashData.cpu_util.field_name]), 
            self.page.cpu_graph_origin)

        self.display_surface.blit(
            self.page.gpu_graph.update(data[DashData.gpu_util.field_name]), 
            self.page.gpu_graph_origin)

        # CPU Core Visualizer
        self.display_surface.blit(
            self.page.core_visualizer.update(data), 
            self.page.core_visualizer_origin)

        # System and GPU memory usage
        self.display_surface.blit(
            self.page.sys_memory_bar.update(data[DashData.sys_ram_used.field_name]), 
            self.page.sys_memory_origin)

        self.display_surface.blit(
            self.page.gpu_memory_bar.update(data[DashData.gpu_ram_used.field_name]), 
            self.page.gpu_memory_origin)

        # FPS Graph and Text
        fps_value = data[DashData.rtss_fps.field_name]
        self.display_surface.blit(self.page.fps_graph.update(fps_value), self.page.fps_graph_origin)
        self.page.font_large.render_to(self.display_surface, self.page.fps_text_origin, "{}".format(fps_value), Color.white)
        self.page.font_normal.render_to(self.display_surface, self.page.fps_label_origin, "FPS", Color.white)

        # Fan gauges
        self.display_surface.blit(        
            self.page.fan1_gauge.update(data[DashData.chassis_1_fan.field_name]),
            self.page.fan1_gauge_origin)
        self.display_surface.blit(        
            self.page.fan_opt_gauge.update(data[DashData.cpu_opt_fan.field_name]),
            self.page.fan_opt_gauge_origin)
        self.display_surface.blit(        
            self.page.cpu_fan_gauge.update(data[DashData.cpu_fan.field_name]),
            self.page.cpu_fan_gauge_origin)
        self.display_surface.blit(        
            self.page.gpu_fan_gauge.update(data[DashData.gpu_fan.field_name]),
            self.page.gpu_fan_gauge_origin)

        # Motherboard temp (nestled between all the fans)
        self.page.font_normal.render_to(self.display_surface, self.page.mobo_temp_origin, "{}".format(data[DashData.motherboard_temp.field_name]), Color.white)

        # Disk activity
        disk_count = 4
        disk_y_offset = 0
        for index in range(disk_count):
            self.display_surface.blit(
                self.page.disk_activity_bar.update(data["disk_{}_activity".format(index)]), 
                (self.page.disk_activity_origin[0], self.page.disk_activity_origin[1] + disk_y_offset))
            disk_y_offset += self.page.disk_activity_y_spacing

        # Network Text
        network_download_text = "NIC 1 Down: {} {}".format(data[DashData.nic1_download_rate.field_name], DashData.nic1_download_rate.unit.symbol)
        self.page.font_normal.render_to(
            self.display_surface, 
            self.page.network_text_origin, 
            network_download_text, Color.white)
        
        network_upload_text = "Up: {} {}".format(data[DashData.nic1_upload_rate.field_name], DashData.nic1_upload_rate.unit.symbol)
        self.page.font_normal.render_to(
            self.display_surface, 
            (self.page.network_text_origin[0] + 180, self.page.network_text_origin[1]),
            network_upload_text, Color.white)
