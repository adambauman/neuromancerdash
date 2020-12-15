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
        self.__subsurface = subsurface 
        self.__previous_font_surface = None
        self.__text_color = text_color
        self.__font = font
        self.__origin = origin
        self.__text = text
        self.__clamp_chars = clamp_chars

        self.current_value = value

    def update(self, new_value):

        if 0 < self.__clamp_chars:
            render_text = self.__text.format(Helpers.clamp_text(new_value, 11, ""))
        else:
            render_text = self.__text.format(new_value)
        self.__font.render_to(self.__subsurface, (0,0), render_text, self.__text_color)
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
    __working_surface = None
    __static_elements = None
    __use_direct_surface = False

    # DynamicFields
    __cpu_power = None
    __cpu_clock = None
    __cpu_utilization = None
    __page_alloc = None

    def __init__(self, element_rect, details_stack_config=DetailsStackConfig(), direct_surface=None, surface_flags=0):

        # Config and fonts
        self.__config = details_stack_config
        #if None == self.__config.font_normal:
        self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        self.__font_normal.kerning = True

        base_size = (element_rect[2], element_rect[3])

        if None != direct_surface:
            self.__working_surface = direct_surface.subsurface(element_rect)
            self.__using_direct_surface = True
        else:
            self.__working_surface = pygame.Surface(base_size, surface_flags)
            self.__using_direct_surface = False

        # Surface setup
        self.__setup_surfaces_and_fields__(element_rect, surface_flags)

    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(None == self.__static_elements)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        self.__static_elements = pygame.Surface(base_size, surface_flags)

        y_offset = self.__config.stack_y_offset
        font_height = self.__font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static elements are positioned
        origin = (0, 0)
        self.__cpu_power = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.cpu_power.unit.symbol, Color.white, self.__font_normal)

        # CPU Clock
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__cpu_clock = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.cpu_clock.unit.symbol, Color.white, self.__font_normal)

        # CPU Utilization
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__cpu_utilization = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}" + DashData.cpu_util.unit.symbol, Color.yellow, self.__font_normal)

        # Static label, write to the static background
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__font_normal.render_to(self.__static_elements, origin, "Page Alloc", Color.grey_75)

        # Page Alloc
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__page_alloc = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.used_virtual_memory.unit.symbol, Color.yellow, self.__font_normal)


    def draw_update(self, data):
        assert(None != self.__working_surface)
        assert(None != self.__static_elements)
        assert(0 != len(data))

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self.__working_surface.fill((0,0,0,0))
        self.__working_surface.blit(self.__static_elements, (0, 0))

        cpu_power_value = DashData.best_attempt_read(data, DashData.cpu_power, "0")
        self.__cpu_power.update(cpu_power_value)

        cpu_clock_value = DashData.best_attempt_read(data, DashData.cpu_clock, "0")
        self.__cpu_clock.update(cpu_clock_value)

        cpu_utilization_value = DashData.best_attempt_read(data, DashData.cpu_util, "0")
        self.__cpu_utilization.update(cpu_utilization_value)

        page_alloc_value = DashData.best_attempt_read(data, DashData.used_virtual_memory, "0")
        self.__page_alloc.update(page_alloc_value)

        if g_benchmark:
            print("BENCHMARK: CPU Details: {}ms".format(pygame.time.get_ticks() - start_ticks))

        if False == self.__use_direct_surface:
            return self.__working_surface


class GPUDetails:
     # Surfaces
    __working_surface = None
    __static_elements = None
    __use_direct_surface = False

    # DynamicFields
    __perfcap_reason = None
    __gpu_power = None
    __gpu_clock = None
    __gpu_utilization = None
    __dynamic_ram_used = None

    def __init__(self, element_rect, details_stack_config=DetailsStackConfig(), direct_surface=None, surface_flags=0):

        # Config and fonts
        self.__config = details_stack_config
        if None == self.__config.font_normal:
            self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            self.__font_normal.kerning = True

        if None != direct_surface:
            self.__working_surface = direct_surface.subsurface(element_rect)
            self.__using_direct_surface = True
        else:
            self.__working_surface = pygame.Surface(base_size, surface_flags)
            self.__using_direct_surface = False

        # Surface setup
        self.__setup_surfaces_and_fields__(element_rect, surface_flags)

    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(None == self.__static_elements)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        self.__static_elements = pygame.Surface(base_size)

        y_offset = self.__config.stack_y_offset
        font_height = self.__font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        origin = (0, 0)
        # Static Label
        self.__font_normal.render_to(self.__static_elements, origin, "PerfCap", Color.white)

        # PerfCap Reason
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__perfcap_reason = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}", Color.yellow, self.__font_normal, clamp_chars=11)

        # GPU Power
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__gpu_power = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.gpu_power.unit.symbol, Color.white, self.__font_normal)

        # GPU Clock
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__gpu_clock = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.gpu_clock.unit.symbol, Color.white, self.__font_normal)

        # GPU Utilization
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__gpu_utilization = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}" + DashData.gpu_util.unit.symbol, Color.yellow, self.__font_normal)

        # Static RAM Label
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__font_normal.render_to(self.__static_elements, origin, "Dyn RAM", Color.grey_75)

        # Dynamic RAM Used
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__dynamic_ram_used = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.gpu_used_dynamic_memory.unit.symbol, Color.yellow, self.__font_normal)


    def draw_update(self, data):
        assert(None != self.__working_surface)
        assert(None != self.__static_elements)
        assert(0 != len(data))

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self.__working_surface.fill((0,0,0,0))
        self.__working_surface.blit(self.__static_elements, (0, 0))

        perfcap_reason_data = DashData.best_attempt_read(data, DashData.gpu_perfcap_reason, "")
        self.__perfcap_reason.update(perfcap_reason_data)

        gpu_power_value = DashData.best_attempt_read(data, DashData.gpu_power, "0")
        self.__gpu_power.update(gpu_power_value)

        gpu_clock_value = DashData.best_attempt_read(data, DashData.gpu_clock, "0")
        self.__gpu_clock.update(gpu_clock_value)

        gpu_utilization = DashData.best_attempt_read(data, DashData.gpu_util, "0")
        self.__gpu_utilization.update(gpu_utilization)

        dynamic_ram_used_value = DashData.best_attempt_read(data, DashData.gpu_used_dynamic_memory, "0")
        self.__dynamic_ram_used.update(dynamic_ram_used_value)

        if g_benchmark:
            print("BENCHMARK: GPU Details: {}ms".format(pygame.time.get_ticks() - start_ticks))

        if False == self.__use_direct_surface:
            return self.__working_surface


class FPSConfig:
    def __init__(self, number_font=None, label_font=None, draw_zero=True):
        self.number_font = number_font
        self.label_font = label_font
        self.draw_zero = draw_zero

class FPSText:
    __current_value = None
    __using_direct_surface = False

    def __init__(self, fps_field_rect, fps_config=FPSConfig(), direct_surface=None, surface_flags=0):

        base_size = (fps_field_rect[2], fps_field_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        # Config and fonts
        self.__config = fps_config

        if None == self.__config.number_font:
            self.__config.number_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 50)
            self.__config.number_font.kerning = True

        if None == self.__config.label_font:
            self.__config.label_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            self.__config.label_font.kerning = True

        if None != direct_surface:
            if __debug__:
                print("FPSText using direct surface, rect: {}".format(fps_field_rect))

            self.__working_surface = direct_surface.subsurface(fps_field_rect)
            self.__using_direct_surface = True
        else:
            self.__working_surface = pygame.Surface((base_size), surface_flags)
            self.__using_direct_surface = False

        # Setup the last loose bits
        # Could probably be a bit more dynamic based on number font parameters, etc.
        label_x = 3
        label_y = self.__working_surface.get_height() - self.__config.label_font.get_sized_height()
        self.__label_position = (label_x, label_y)

    def draw_update(self, value):

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self.__working_surface.fill((0,0,0,0))
        self.__config.label_font.render_to(self.__working_surface, self.__label_position, "FPS", Color.white)
        if 0 == int(value) and False == self.__config.draw_zero:
            pass
        else:
            self.__config.number_font.render_to(self.__working_surface, (0, 0), "{}".format(value), Color.white)

        if g_benchmark:
            print("BENCHMARK: CPU Details: {}ms".format(pygame.time.get_ticks() - start_ticks))
        
        if False == self.__using_direct_surface:
            return self.__working_surface


class TemperatureHumidity:
    
    # DynamicFields
    __temperature = None
    __humidity = None

    # Surfaces
    __working_surface = None
    __static_elements = None

    def __init__(self, element_rect, font=None, surface_flags=0):

        if None == font:
            self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            self.__font_normal.kerning = True
        else:
            self.__font_normal = font

        self.__setup_surfaces_and_fields__(element_rect, surface_flags)


    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(None == self.__working_surface and None == self.__static_elements)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])
    
        self.__working_surface = pygame.Surface(base_size, surface_flags)
        self.__static_elements = self.__working_surface.copy()

        y_offset = -2
        font_height = self.__font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        
        # Static Label
        origin = (0, 0)
        self.__font_normal.render_to(self.__static_elements, origin, "Room Temp", Color.white)

        # Temperature
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__temperature = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{:.1f}\u00b0F", Color.white, self.__font_normal)

        # Static Label
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__font_normal.render_to(self.__static_elements, origin, "Humidity", Color.white)

        # Humidity
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__humidity = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{:.1f}%", Color.white, self.__font_normal)

    def draw_update(self, data):
        assert(None != self.__working_surface and None != self.__static_elements)

        self.__working_surface.fill((0,0,0,0))
        self.__working_surface.blit(self.__static_elements, (0, 0))

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self.__temperature.update(data.temperature)
        self.__humidity.update(data.humidity)

        if g_benchmark:
            print("BENCHMARK: FPS Text: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self.__working_surface


class SimpleText:
    _working_surface = None
    _using_direct_surface = False
    _current_value = None

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
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

    def draw_update(self, value, force_draw=False):
        assert(self._working_surface is not None)

        if self._current_value != value or force_draw:
            self._working_surface.fill((0,0,0,0))
            self._font.render_to(self._working_surface, (0, 0), self._text_template.format(value), self._text_color)

        self._current_value = value

        if self._using_direct_surface:
            pass
        else:
            return self._working_surface


class NetworkInformation:

    # Surfaces
    __working_surface = None
    __static_elements = None

    # Dynamic Fields
    __down_speed = None
    __up_speed = None

    def __init__(self, element_rect, font=None, surface_flags=0):

        if None == font:
            self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        else:
            self.__font_normal = font

        self.__setup_surfaces_and_fields__(element_rect, surface_flags)

    def __setup_surfaces_and_fields__(self, element_rect, surface_flags):
        assert(None == self.__working_surface and None == self.__static_elements)

        base_size = (element_rect[2], element_rect[3])
        assert(0 != base_size[0] or 0 != base_size[1])

        self.__working_surface = pygame.Surface(base_size, surface_flags)
        self.__static_elements = self.__working_surface.copy()

        label_value_x_space = 5
        intervalue_x_space = 100
        value_width = 80
        font_height = self.__font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        # Static Label
        origin = (0, 0)
        rendered_rect = self.__font_normal.render_to(self.__static_elements, origin, "NIC 1 Down:", Color.white)

        # Download Rate
        origin = (rendered_rect[2] + label_value_x_space, 0)
        self.__down_speed = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], value_width, font_height)),
            "{} " + DashData.nic1_download_rate.unit.symbol, Color.white, self.__font_normal)

        # Static Label
        origin = (origin[0] + intervalue_x_space, 0)
        rendered_rect = self.__font_normal.render_to(self.__static_elements, origin, "Up:", Color.white)

        # Upload Rate
        origin = (origin[0] + rendered_rect[2] + label_value_x_space, 0)
        self.__up_speed = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], value_width, font_height)),
            "{} " + DashData.nic1_upload_rate.unit.symbol, Color.white, self.__font_normal)


    def draw_update(self, download_value, upload_value):

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        self.__working_surface.fill((0,0,0,0))
        self.__working_surface.blit(self.__static_elements, (0, 0))

        self.__down_speed.update(download_value)
        self.__up_speed.update(upload_value)

        if g_benchmark:
            print("BENCHMARK: NetworkInformation: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self.__working_surface
