#
# textstack - stacked text displays for grouped value readouts
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from data.dataobjects import DataField, DashData
from .styles import Color, FontPaths, AssetPath
from .helpers import Helpers

# Set true to benchmark the update process
g_benchmark = False

class DynamicField:
    def __init__(self, origin, subsurface, text, text_color, font, value=None, clamp_chars=0):
        # Will be an updatable subsurface of the working surface
        self._subsurface = subsurface 
        self._text_color = text_color
        self._font = font
        self._origin = origin
        self._text = text
        self._clamp_chars = clamp_chars

        self.current_value = value

    def update(self, new_value):

        if 0 < self._clamp_chars:
            render_text = self._text.format(Helpers.clamp_text(new_value, 11, ""))
        else:
            render_text = self._text.format(new_value)
        self._font.render_to(self._subsurface, (0,0), render_text, self._text_color)
        self.current_value = new_value

class StackHelpers:
    def __get_next_y_stack_origin__(self, last_origin, font, padding = 0):
        x = last_origin[0]
        y = last_origin[1] + font.get_sized_height() + padding
        return (x,y)

class DetailsStackConfig:
    def __init__(self, font_normal=None, stack_y_offset=-2, draw_zero=True):
        self.font_normal = font_normal
        self.stack_y_offset = stack_y_offset
        self.draw_zero = draw_zero

class CPUDetails:
    # Surfaces
    _working_surface = None
    _static_elements = None
    _direct_rect = None

    # DynamicFields
    _cpu_power = None
    _cpu_clock = None
    _cpu_utilization = None
    _page_alloc = None

    def __init__(self, element_rect, details_stack_config=DetailsStackConfig(), direct_surface=None, surface_flags=0):

        # Config and fonts
        self._config = details_stack_config
        if self._config.font_normal is None:
            self._font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            self._font_normal.kerning = True
        else:
            self._font_normal = self._config.font_normal

        base_size = (element_rect[2], element_rect[3])

        if direct_surface is not None:
            self._working_surface = direct_surface.subsurface(element_rect)
            self._direct_rect = element_rect
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

        # Surface setup
        self.__setup_surfaces_and_fields__(element_rect, surface_flags)

    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(self._static_elements is None)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        self._static_elements = pygame.Surface(base_size, surface_flags)

        y_offset = self._config.stack_y_offset
        font_height = self._font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static elements are positioned
        origin = (0, 0)
        self._cpu_power = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.cpu_power.unit.symbol, Color.white, self._font_normal)

        # CPU Clock
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._cpu_clock = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.cpu_clock.unit.symbol, Color.white, self._font_normal)

        # CPU Utilization
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._cpu_utilization = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{}" + DashData.cpu_util.unit.symbol, Color.yellow, self._font_normal)

        # Static label, write to the static background
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._font_normal.render_to(self._static_elements, origin, "Page Alloc", Color.grey_75)

        # Page Alloc
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._page_alloc = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.used_virtual_memory.unit.symbol, Color.yellow, self._font_normal)


    def draw_update(self, data):
        assert(self._working_surface is not None)
        assert(self._static_elements is not None)
        assert(0 != len(data))

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self._working_surface.fill((0,0,0,0))
        self._working_surface.blit(self._static_elements, (0, 0))

        cpu_power_value = DashData.best_attempt_read(data, DashData.cpu_power, "0")
        self._cpu_power.update(cpu_power_value)

        cpu_clock_value = DashData.best_attempt_read(data, DashData.cpu_clock, "0")
        self._cpu_clock.update(cpu_clock_value)

        cpu_utilization_value = DashData.best_attempt_read(data, DashData.cpu_util, "0")
        self._cpu_utilization.update(cpu_utilization_value)

        page_alloc_value = DashData.best_attempt_read(data, DashData.used_virtual_memory, "0")
        self._page_alloc.update(page_alloc_value)

        if g_benchmark:
            print("BENCHMARK: CPU Details: {}ms".format(pygame.time.get_ticks() - start_ticks))


        return self._working_surface, self._direct_rect


class GPUDetails:
     # Surfaces
    _working_surface = None
    _static_elements = None
    _direct_rect = None

    # DynamicFields
    _perfcap_reason = None
    _gpu_power = None
    _gpu_clock = None
    _gpu_utilization = None
    _dynamic_ram_used = None

    def __init__(self, element_rect, details_stack_config=DetailsStackConfig(), direct_surface=None, surface_flags=0):

        # Config and fonts
        self._config = details_stack_config
        if self._config.font_normal is None:
            self._font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            self._font_normal.kerning = True

        if direct_surface is not None:
            self._working_surface = direct_surface.subsurface(element_rect)
            self._using_direct_surface = True
            self._direct_rect = element_rect
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)
            self._using_direct_surface = False

        # Surface setup
        self.__setup_surfaces_and_fields__(element_rect, surface_flags)

    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(self._static_elements is None)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        self._static_elements = pygame.Surface(base_size)

        y_offset = self._config.stack_y_offset
        font_height = self._font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        origin = (0, 0)
        # Static Label
        self._font_normal.render_to(self._static_elements, origin, "PerfCap", Color.white)

        # PerfCap Reason
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._perfcap_reason = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{}", Color.yellow, self._font_normal, clamp_chars=11)

        # GPU Power
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._gpu_power = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.gpu_power.unit.symbol, Color.white, self._font_normal)

        # GPU Clock
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._gpu_clock = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.gpu_clock.unit.symbol, Color.white, self._font_normal)

        # GPU Utilization
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._gpu_utilization = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{}" + DashData.gpu_util.unit.symbol, Color.yellow, self._font_normal)

        # Static RAM Label
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._font_normal.render_to(self._static_elements, origin, "Dyn RAM", Color.grey_75)

        # Dynamic RAM Used
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._dynamic_ram_used = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.gpu_used_dynamic_memory.unit.symbol, Color.yellow, self._font_normal)


    def draw_update(self, data):
        assert(self._working_surface is not None)
        assert(self._static_elements is not None)
        assert(0 != len(data))

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self._working_surface.fill((0,0,0,0))
        self._working_surface.blit(self._static_elements, (0, 0))

        perfcap_reason_data = DashData.best_attempt_read(data, DashData.gpu_perfcap_reason, "")
        self._perfcap_reason.update(perfcap_reason_data)

        gpu_power_value = DashData.best_attempt_read(data, DashData.gpu_power, "0")
        self._gpu_power.update(gpu_power_value)

        gpu_clock_value = DashData.best_attempt_read(data, DashData.gpu_clock, "0")
        self._gpu_clock.update(gpu_clock_value)

        gpu_utilization = DashData.best_attempt_read(data, DashData.gpu_util, "0")
        self._gpu_utilization.update(gpu_utilization)

        dynamic_ram_used_value = DashData.best_attempt_read(data, DashData.gpu_used_dynamic_memory, "0")
        self._dynamic_ram_used.update(dynamic_ram_used_value)

        if g_benchmark:
            print("BENCHMARK: GPU Details: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self._working_surface, self._direct_rect


class FPSConfig:
    def __init__(self, number_font=None, label_font=None, draw_zero=True):
        self.number_font = number_font
        self.label_font = label_font
        self.draw_zero = draw_zero

class FPSText:
    _current_value = None
    _direct_rect = None

    def __init__(self, fps_field_rect, fps_config=FPSConfig(), direct_surface=None, surface_flags=0):

        base_size = (fps_field_rect[2], fps_field_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        # Config and fonts
        self._config = fps_config

        if self._config.number_font is None:
            self._config.number_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 50)
            self._config.number_font.kerning = True
            self._direct_rect = fps_field_rect

        if self._config.label_font is None:
            self._config.label_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            self._config.label_font.kerning = True

        if direct_surface is not None:
            self._working_surface = direct_surface.subsurface(fps_field_rect)
        else:
            self._working_surface = pygame.Surface((base_size), surface_flags)

        # Setup the last loose bits
        # Could probably be a bit more dynamic based on number font parameters, etc.
        label_x = 3
        label_y = self._working_surface.get_height() - self._config.label_font.get_sized_height()
        self._label_position = (label_x, label_y)

    def draw_update(self, value):

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self._working_surface.fill((0,0,0,0))
        self._config.label_font.render_to(self._working_surface, self._label_position, "FPS", Color.white)
        if 0 == int(value) and self._config.draw_zero is False:
            pass
        else:
            self._config.number_font.render_to(self._working_surface, (0, 0), "{}".format(value), Color.white)

        if g_benchmark:
            print("BENCHMARK: CPU Details: {}ms".format(pygame.time.get_ticks() - start_ticks))
        
        return self._working_surface, self._direct_rect


class TemperatureHumidity:
    
    # DynamicFields
    _temperature = None
    _humidity = None

    # Surfaces
    _working_surface = None
    _static_elements = None
    _direct_rect = None

    def __init__(self, element_rect, font=None, direct_surface=None, surface_flags=0):

        if font is None:
            self._font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            self._font.kerning = True
        else:
            self._font = font

        base_size = (element_rect[2], element_rect[3])
        if direct_surface is not None:
            self._working_surface = direct_surface.subsurface(element_rect)
            self._direct_rect = element_rect
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

        self.__setup_surfaces_and_fields__(element_rect, surface_flags)


    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(self._static_elements is None)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])
    
        self._static_elements = pygame.Surface(base_size, surface_flags)

        y_offset = -2
        font_height = self._font.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        # Static Label
        origin = (0, 0)
        self._font.render_to(self._static_elements, origin, "Room Temp", Color.white)

        # Temperature
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._temperature = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{:.1f}\u00b0F", Color.white, self._font)

        # Static Label
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._font.render_to(self._static_elements, origin, "Humidity", Color.white)

        # Humidity
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self._humidity = DynamicField(
            origin,
            self._working_surface.subsurface((origin[0], origin[1], self._working_surface.get_width(), font_height + y_offset)),
            "{:.1f}%", Color.white, self._font)

    def draw_update(self, data):
        assert(self._working_surface is not None)
        assert(self._static_elements is not None)

        self._working_surface.fill((0,0,0,0))
        self._working_surface.blit(self._static_elements, (0, 0))

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self._temperature.update(data.temperature)
        self._humidity.update(data.humidity)

        if g_benchmark:
            print("BENCHMARK: FPS Text: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self._working_surface, self._direct_rect


class SimpleText:
    _working_surface = None
    _using_direct_surface = False
    _current_value = None
    _direct_rect = None

    def __init__(self, element_rect, text_template="{}", font=None, text_color=Color.white, direct_surface=None, surface_flags=0):
        assert(0 != element_rect[2] and 0 != element_rect[3])
        assert(0 != len(text_template))
        assert(-1 != text_template.find("{}"))

        self._text_color = text_color
        self._text_template = text_template

        if font is None:
            self._font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        else:
            self._font = font

        base_size = (element_rect[2], element_rect[3])
        if direct_surface is not None:
            self._working_surface = direct_surface.subsurface(element_rect)
            self._using_direct_surface = True
            self._direct_rect = element_rect
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

    def draw_update(self, value, force_draw=False):
        assert(self._working_surface is not None)

        if self._current_value != value or force_draw:
            self._working_surface.fill((0,0,0,0))
            self._font.render_to(self._working_surface, (0, 0), self._text_template.format(value), self._text_color)

        self._current_value = value

        return self._working_surface, self._direct_rect


class NetworkInformation:

    # Surfaces
    _working_surface = None
    _static_elements = None
    _direct_rect = None

    # Dynamic Fields
    _down_speed = None
    _up_speed = None

    def __init__(self, element_rect, font=None, value_color=Color.white, label_color=Color.white, direct_surface=None, surface_flags=0):

        self._value_color = value_color
        self._label_color = label_color

        if font is None:
            self._font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        else:
            self._font_normal = font

        base_size = (element_rect[0], element_rect[1])
        if direct_surface is not None:
            self._working_surface = direct_surface.subsurface(element_rect)
            self._direct_rect = element_rect
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

        self.__setup_surfaces_and_fields__(element_rect, surface_flags)

    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(self._static_elements is None)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        self._static_elements = pygame.Surface(base_size)

        label_value_x_space = 5
        intervalue_x_space = 100
        value_width = 80
        font_height = self._font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        # Static Label
        origin = (0, 0)
        rendered_rect = self._font_normal.render_to(self._static_elements, origin, "NIC 1 Down:", self._label_color)

        # Download Rate
        origin = (rendered_rect[2] + label_value_x_space, 0)
        self._down_speed = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], value_width, base_size[1])),
            "{} " + DashData.nic1_download_rate.unit.symbol, self._value_color, self._font_normal)

        # Static Label
        origin = (origin[0] + intervalue_x_space, 0)
        rendered_rect = self._font_normal.render_to(self._static_elements, origin, "Up:", self._label_color)

        # Upload Rate
        origin = (origin[0] + rendered_rect[2] + label_value_x_space, 0)
        self._up_speed = DynamicField(
            origin, 
            self._working_surface.subsurface((origin[0], origin[1], value_width, base_size[1])),
            "{} " + DashData.nic1_upload_rate.unit.symbol, self._value_color, self._font_normal)


    def draw_update(self, download_value, upload_value):
        assert(self._working_surface is not None)
        assert(self._static_elements is not None)

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self._working_surface.fill((0,0,0,0))
        self._working_surface.blit(self._static_elements, (0, 0))

        self._down_speed.update(download_value)
        self._up_speed.update(upload_value)

        if g_benchmark:
            print("BENCHMARK: NetworkInformation: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self._working_surface, self._direct_rect
