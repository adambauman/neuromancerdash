#
# visualizers - visualizer display elements
# =========================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

import os, sys

from .helpers import Helpers
from .styles import Color, AssetPath, FontPath
from .bargraph import BarGraph, BarGraphConfig

if not pygame.freetype.get_init():
    pygame.freetype.init()

# Set true to benchmark the update process
g_benchmark = False

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
    _config = CoreVisualizerConfig

    _working_surface = None
    _direct_rect = None

    # Tracking outside config in case we need to adjust on the fly
    _core_height = 0
    _core_width = 0
    
    _core_count = 0
    _cores_per_row = 0
    _last_core_activity = []

    # TODO: Ditch this, check if surfaces are prepped, last core activity is populated, etc.
    _first_run = True

    def __init__(self, core_visualizer_config, direct_surface=None, direct_rect=None, surface_flags=0):

        self._config = core_visualizer_config

        # NOTE: (Adam) 2020-11-19 Setting for compatability with new config setup
        self._core_count = self._config.core_count

        self._core_width = self._config.core_width
        self._core_height = self._config.core_height
        if self._core_height is None:
            self._core_height = self._core_width

        assert(0 != self._core_height)

        # Rounds up if reminder exists
        self._cores_per_row =\
            int(self._core_count / self._config.core_rows) + (self._core_count % self._config.core_rows > 0)

        # Initialize working surface
        base_width =\
            (self._core_width * self._cores_per_row) + (self._config.core_spacing * (self._cores_per_row -1))
        base_height =\
            (self._core_height * self._config.core_rows) + (self._config.core_spacing * (self._config.core_rows - 1))

        if None != direct_surface and None != direct_rect:
            assert(base_width <= direct_rect[2] and base_height <= direct_rect[3])

            self._working_surface = direct_surface.subsurface(direct_rect)
            self._direct_rect = direct_rect
        else:
            self._working_surface = pygame.Surface((base_width, base_height), surface_flags)

        # Initialize last core activity and do a hack update
        initialize_data = {}
        for index in range(self._core_count):
            key = "cpu{}_util".format(index)
            initialize_data[key] = 0
            self._last_core_activity.append(False)

        self.update(initialize_data)
        self._first_run = False

    def update(self, data):
        assert(self._working_surface is not None)
        assert(0 != len(self._last_core_activity))
        assert(len(data) >= self._core_count)

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # Copy in last core surface, we will only update the altered representations
        #self._base_surface.blit(self._last_base_surface, (0, 0))

        core_origin_x = 0
        core_origin_y = 0
        core_activity_tracking = []
        for index in range(self._core_count):

            key_name = "cpu{}_util".format(index)
            core_activity_value = 0
            try:
                core_activity_value = int(data[key_name])
            except:
                core_activity_value = 0
                if __debug__:
                    print("Data error: core {}".format(index))
                    #traceback.print_exc()

            core_active = False
            if core_activity_value >= self._config.activity_threshold_percent:
                #print("Core{} active at {}%".format(index, core_activity_value))
                core_active = True

            # Track activity for the next update call
            core_activity_tracking.append(core_active)

            # No need to re-draw if status hasn't changed
            if self._last_core_activity[index] == core_active and self._first_run is not False:
                continue

            core_color = self._config.inactive_color
            if core_active:
                core_color = self._config.active_color

            pygame.draw.rect(
                self._working_surface, 
                core_color, 
                (core_origin_x, core_origin_y, self._core_width, self._core_width)
            )

            if len(core_activity_tracking) == self._cores_per_row:
                # Move to the next row
                core_origin_y += self._core_width + self._config.core_spacing
                core_columns_drawn = 0
                core_origin_x = 0
            else:
                # Move to the next column
                core_origin_x += self._core_width + self._config.core_spacing

        #assert(len(self._last_core_activity) == len(core_activity_tracking))
        self._last_core_activity = core_activity_tracking

        if g_benchmark:
            print("BENCHMARK: CoreVisualizer: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self._working_surface, self._direct_rect

class PumpStatusConfig:
    def __init__(self, size=(80, 80), temperature_font=None):
        self.size = size
        if temperature_font is None:
            self.temperature_font = pygame.freetype.Font(FontPath.fira_code_semibold(), 18)
            self.temperature_font.kerning = True
        else:
            self.temperature_font = font
        
        self.temperature_font_color = Color.white
        self.temperature_shadow_color = Color.black
        self.pump_indicator_bg_color = Color.windows_cyan_1_medium
        self.draw_temperature_shadow = True
        self.warning_temperature = 82
        self.draw_heat_colorization = True # Gradually make temperature text appear more red as temps increase
        self.start_heat_colorization_value = 50 # Value to start injecting the red. Remains solid green below this

        self.pump_rpm_underspeed_value = 900
        self.pump_indicator_warning_color = Color.windows_red_1

class PumpStatus:
    _working_surface = None
    _cpu_pump = None
    _pump_indicator_okay = None
    _pump_indicator_warn = None
    _temperature_origin = (44, 42)

    _current_temperature_value = None
    _current_rpm_value = None

    def __init__(self, pump_status_config=PumpStatusConfig(), direct_surface=None, direct_rect=None, surface_flags=0):

        self._config = pump_status_config
        self._surface_flags = surface_flags
        self._direct_rect = direct_rect

        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
        else:
            self._working_surface = pygame.Surface(size, self._surface_flags)

        # Prepare the initial working surface
        self._working_surface.fill((0,0,0,0))
        cpu_pump = pygame.image.load(os.path.join(AssetPath.hardware, "corsair_h100_head.png")).convert_alpha()
        scale_modifier = self._config.size[0] / cpu_pump.get_width()
        # CPU pump graphic is pretty big, scale it down to fit the configured element width
        self._cpu_pump = pygame.transform.rotozoom(cpu_pump, 0, scale_modifier)

        # Create initial indicator surfaces
        # Scale the pump indicator graphic as well!
        pump_indicator = pygame.image.load(os.path.join(AssetPath.hardware, "corsair_h100_head_indicator.png")).convert_alpha()
        self._pump_indicator_okay = pygame.transform.rotozoom(pump_indicator, 0, scale_modifier)
        self._pump_indicator_okay.fill(self._config.pump_indicator_bg_color, special_flags=pygame.BLEND_RGBA_MULT)
        self._pump_indicator_warn = pygame.transform.rotozoom(pump_indicator, 0, scale_modifier)
        self._pump_indicator_warn.fill(self._config.pump_indicator_warning_color, special_flags=pygame.BLEND_RGBA_MULT)


    def draw_update(self, temperature_value, pump_rpm_value):
        assert(self._working_surface is not None)
        assert(self._pump_indicator_okay is not None and self._pump_indicator_warn is not None)

        self._working_surface.blit(self._cpu_pump, (0, 0))

        # Save some processing and return previous surface. If using direct surface draw the previous area will 
        # remain static
        # unless you draw something over/under it.
        #if self._current_temperature_value == temperature_value and self._current_rpm_value == pump_rpm_value:
        #    return self._working_surface, None
        #else:
        #    if __debug__:
        #        print("Updating PumpStatus, temp: {}, pump_rpm: {}".format(temperature_value, pump_rpm_value))

        # Do not clear the entire working surface, everything we need to update is within the indicator 
        # surface's bounds
        draw_warning = False
        if self._config.pump_rpm_underspeed_value >= int(pump_rpm_value):
            draw_warning = True
        if self._config.warning_temperature <= int(temperature_value):
            draw_warning = True

        if draw_warning:
            # Pump is under speed, use warning surface!
            self._working_surface.blit(self._pump_indicator_warn, (0, 0))
        else:
            self._working_surface.blit(self._pump_indicator_okay, (0, 0))

        # TODO: Font coloration based on temperature, if enabled
        # Draw temperature text within the indicator
        shadowed_temperature_text = Helpers.get_shadowed_text(
                self._config.temperature_font, "{}\u00b0".format(temperature_value), 
                self._config.temperature_font_color, self._config.temperature_shadow_color)
        # TODO: Dynamic temperature origin tied to scaled size
        self._working_surface.blit(shadowed_temperature_text, self._temperature_origin)

        self._current_temperature_value = temperature_value
        self._current_rpm_value = pump_rpm_value
            
        return self._working_surface, self._direct_rect


class GPUTemperatureConfig:
    def __init__(self, size=(305, 71), temperature_font=None):
        self.size = size
        if temperature_font is None:
            self.temperature_font = pygame.freetype.Font(FontPath.fira_code_semibold(), 18)
            self.temperature_font.kerning = True
        else:
            self.temperature_font = font

        self.fan_dash_data = None
        self.temperature_dash_data = None
        
        self.temperature_font_color = Color.white
        self.temperature_shadow_color = Color.black
        self.indicator_bg_color = Color.windows_cyan_1_medium
        self.draw_temperature_shadow = True
        self.warning_temperature = 82
        self.draw_heat_colorization = True # Gradually make temperature text appear more red as temps increase
        self.start_heat_colorization_value = 50 # Value to start injecting the red. Remains solid green below this
        self.indicator_warning_color = Color.windows_red_1

# TODO: This is all a bit of a mismash ATM, clean it up, make more dynamic for sizing, etc.
class GPUTemperature:
    _working_surface = None
    _heatsink_fins = None
    _indicator_housing = None
    _indicator_okay = None
    _indicator_warn = None
    _indicator_origin = None

    _current_temperature_value = None
    _current_rpm_value = None

    def __init__(self, pump_status_config=GPUTemperatureConfig(), direct_surface=None, direct_rect=None, surface_flags=0):

        self._config = pump_status_config
        self._surface_flags = surface_flags
        self._direct_rect = direct_rect

        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
        else:
            self._working_surface = pygame.Surface(size, self._surface_flags)

        fan_graph_config = BarGraphConfig((230, 32), (0,2000))
        fan_graph_config.draw_background = False
        fan_graph_config.dash_data = self._config.fan_dash_data
        fan_graph_config.unit_draw = True
        fan_graph_config.current_value_draw = True
        fan_graph_config.current_value_position = (155, 10)
        fan_graph_rect = pygame.Rect((0, 29), fan_graph_config.size)
        self._fan_graph = BarGraph(fan_graph_config, self._working_surface, fan_graph_rect)

        self.__prepare_surfaces_()


    def __prepare_surfaces_(self):
        assert(self._working_surface is not None)

        # Load images, using pre-scaled for now
        self._heatsink_fins = pygame.image.load(os.path.join(AssetPath.hardware, "gpu_fins.png")).convert_alpha()
        assert(self._config.size[0] >= self._heatsink_fins.get_width())

        self._indicator_housing = pygame.image.load(os.path.join(AssetPath.hardware, "loose_indicator_housing_scaled.png")).convert_alpha()
        assert(self._config.size[1] >= self._indicator_housing.get_height())

        indicator_base = pygame.image.load(os.path.join(AssetPath.hardware, "loose_indicator_scaled.png")).convert_alpha()
        assert(self._indicator_housing.get_width() == indicator_base.get_width() and self._indicator_housing.get_height() == indicator_base.get_height())

        # Setup okay and warning indicators with multiplied fills
        self._indicator_okay = indicator_base.copy()
        self._indicator_okay.fill(self._config.indicator_bg_color, special_flags=pygame.BLEND_RGBA_MULT)
        self._indicator_warn = indicator_base.copy()
        self._indicator_warn.fill(self._config.indicator_warning_color, special_flags=pygame.BLEND_RGBA_MULT)


    def draw_update(self, temperature_value, fan_rpm_value):
        assert(self._working_surface is not None)
        assert(self._heatsink_fins is not None)
        assert(self._indicator_housing is not None)
        assert(self._indicator_okay is not None and self._indicator_warn is not None)

        indicator_origin = (220, 4)
        self._working_surface.blit(self._heatsink_fins, (0, 0))
        self._fan_graph.draw_update(fan_rpm_value)
        self._working_surface.blit(self._indicator_housing, indicator_origin)

        # TODO: Could add GPU fan warning, lots of modern GPUs spin down when idle though
        if self._config.warning_temperature <= int(temperature_value):
            self._working_surface.blit(self._indicator_warn, indicator_origin)
        else:
            self._working_surface.blit(self._indicator_okay, indicator_origin)

        # TODO: Font coloration based on temperature, if enabled
        # Draw temperature text within the indicator
        shadowed_temperature_text = Helpers.get_shadowed_text(
                self._config.temperature_font, "{}\u00b0".format(temperature_value), 
                self._config.temperature_font_color, self._config.temperature_shadow_color)
        # TODO: Dynamic temperature origin tied to scaled size
        self._working_surface.blit(shadowed_temperature_text, (242, 32))

        self._current_temperature_value = temperature_value
        self._current_rpm_value = fan_rpm_value
            
        return self._working_surface, self._direct_rect

class HomeTemperatureConfig:
    def __init__(self):
        self.text_color = Color.windows_cyan_1
        self.temperature_font = pygame.freetype.Font(FontPath.fira_code_semibold(), 16)
        self.temperature_font.kerning = True
        self.temperature_text_template = "{:.1f}\u00b0"
        self.icon_text_spacing = 6
        self.override_home_icon_filename = None
        self.home_icon_color = Color.grey_40
        self.display_fahrenheit = True

class HomeTemperature:
    _config = None
    _working_surface = None
    
    direct_rect = None
    base_size = None
    current_value = None

    def __init__(self, home_temperature_config=HomeTemperatureConfig(), direct_surface=None, direct_rect=None, surface_flags=0):

        self._config = home_temperature_config
        self._surface_flags = surface_flags

        # Load home icon
        icon_filename = "home_48px.png"
        if self._config.override_home_icon_filename:
            icon_filename = self._config.override_home_icon_filename
        self._icon_home = pygame.image.load(os.path.join(AssetPath.icons, icon_filename)).convert_alpha()
        self._icon_home.fill(self._config.home_icon_color, special_flags=pygame.BLEND_RGB_MULT)

        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect, surface_flags)
            self.base_size = (direct_rect[0], direct_rect[1])
            self.direct_rect = direct_rect
        else:
            # Render a test readout and get the surface parameters
            test_text = self.__draw_temperature__(temperature=900)
            required_width = self._icon_home.get_width()
            if required_width < test_text.get_width():
                required_width = test_text.get_width()
            required_height =\
               self._icon_home.get_height() + self._config.icon_text_spacing + self._config.temperature_font.get_sized_height()
            self.base_size = (required_width, required_height)

            self._working_surface = pygame.Surface(self.base_size, self._surface_flags)


    def __draw_temperature__(self, temperature):
        assert(self._config)

        config = self._config
        text_template = config.temperature_text_template
        return config.temperature_font.render(text_template.format(temperature), config.text_color)[0]

    def set_direct_draw(self, direct_surface, direct_rect):
        # Draw element directly to a subsurface of the direct_surface
        assert(direct_surface)
        assert(0 != direct_rect[2] and 0 != direct_rect[3])

        self._working_surface = direct_surface.subsurface(direct_rect)

    def draw_update(self, room_temperature):
        assert(self._working_surface)
        assert(self._config)

        if self.current_value == room_temperature:
            # No update necessary
            return self._working_surface, None
        
        self._working_surface.fill((0, 0, 0, 0))
        icon_centered_origin = Helpers.get_centered_origin(self._working_surface.get_size(), self._icon_home.get_size())
        self._working_surface.blit(self._icon_home, (icon_centered_origin[0], 0))

        text_surface = self.__draw_temperature__(room_temperature)
        text_x = Helpers.get_centered_origin(self._working_surface.get_size(), text_surface.get_size())[0]
        text_y = self._icon_home.get_height() + self._config.icon_text_spacing
        assert(self._working_surface.get_height() >= text_y)

        self._working_surface.blit(self.__draw_temperature__(room_temperature), (text_x, text_y))
        self._current_value = room_temperature

        return self._working_surface, self.direct_rect
