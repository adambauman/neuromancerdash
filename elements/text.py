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

class DynamicField:
    def __init__(self, origin, subsurface, text, text_color, font, value=None, clamp_chars=0):
        # Will be an updatable subsurface of the working surface
        self.__subsurface = subsurface 
        self.__static_background = subsurface.copy()
        self.__text_color = text_color
        self.__font = font
        self.__origin = origin
        self.__text = text
        self.__clamp_chars = clamp_chars

        self.current_value = value

    def update(self, new_value):
        self.__subsurface.blit(self.__static_background, (0, 0))
        if 0 < self.__clamp_chars:
            render_text = self.__text.format(Helpers.clamp_text(new_value, 11, ""))
        else:
            render_text = self.__text.format(new_value)
        self.__font.render_to(self.__subsurface, (0,0), render_text, self.__text_color)
        self.current_value = new_value
        # No need to return subsurface, it update it's slice of the working surface

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
    __static_background = None

    # DynamicFields
    __cpu_power = None
    __cpu_clock = None
    __cpu_utilization = None
    __ram_used = None

    def __init__(self, element_rect, target_surface, details_stack_config=DetailsStackConfig()):

        # Config and fonts
        self.__config = details_stack_config
        if None == self.__config.font_normal:
            self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            #self.__font_normal.strong = True
            self.__font_normal.kerning = True

        # Surface setup
        self.__setup_surfaces_and_fields__(element_rect, target_surface)

    def __setup_surfaces_and_fields__(self, element_rect, target_surface):
        assert(None == self.__working_surface and None == self.__static_background)

        width, height = element_rect[2], element_rect[3]
        assert(0 != height or 0 != width)

        # NOTE: (Adam) 2020-12-10 No luck experimenting with 0 alpha fill wipes or pixel clearing,
        #           for now copying out the pixels from the target surface and saving as base for redraws
        target_surface_sub = target_surface.subsurface(element_rect)
        self.__static_background = target_surface_sub.copy()        
        self.__working_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.__working_surface.blit(self.__static_background, (0, 0))

        static_labels = pygame.Surface((width, height), pygame.SRCALPHA)
        y_offset = self.__config.stack_y_offset
        font_height = self.__font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        # and where we need to setup subsurfaces for updates
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
        self.__font_normal.render_to(self.__static_background, origin, "RAM Used", Color.grey_75)

        # RAM Used
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__ram_used = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}" + DashData.sys_ram_used.unit.symbol, Color.yellow, self.__font_normal)

        # A little hacky, but blit the static background down again to include the static bits
        self.__working_surface.blit(self.__static_background, (0, 0))

    def draw_update(self, data):
        assert(None != self.__working_surface and None != self.__static_background)
        assert(0 != len(data))


        cpu_power_value = DashData.best_attempt_read(data, DashData.cpu_power, "0")
        if self.__cpu_power.current_value != cpu_power_value:
            self.__cpu_power.update(cpu_power_value)

        cpu_clock_value = DashData.best_attempt_read(data, DashData.cpu_clock, "0")
        if self.__cpu_clock.current_value != cpu_clock_value:
            self.__cpu_clock.update(cpu_clock_value)

        cpu_utilization_value = DashData.best_attempt_read(data, DashData.cpu_util, "0")
        if self.__cpu_utilization.current_value != cpu_utilization_value:
            self.__cpu_utilization.update(cpu_utilization_value)

        ram_used_value = DashData.best_attempt_read(data, DashData.sys_ram_used, "0")
        if self.__ram_used.current_value != ram_used_value:
            self.__ram_used.update(ram_used_value)

        return self.__working_surface


class GPUDetails:
     # Surfaces
    __working_surface = None
    __static_background = None

    # DynamicFields
    __perfcap_reason = None
    __gpu_power = None
    __gpu_clock = None
    __gpu_utilization = None
    __ram_used = None

    def __init__(self, element_rect, target_surface, details_stack_config=DetailsStackConfig()):

        # Config and fonts
        self.__config = details_stack_config
        if None == self.__config.font_normal:
            self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            #self.__font_normal.strong = True
            self.__font_normal.kerning = True

        # Surface setup
        self.__setup_surfaces_and_fields__(element_rect, target_surface)

    def __setup_surfaces_and_fields__(self, element_rect, target_surface):
        assert(None == self.__working_surface and None == self.__static_background)

        width, height = element_rect[2], element_rect[3]
        assert(0 != height or 0 != width)

        # NOTE: (Adam) 2020-12-10 No luck experimenting with 0 alpha fill wipes or pixel clearing,
        #           for now copying out the pixels from the target surface and saving as base for redraws
        target_surface_sub = target_surface.subsurface(element_rect)
        self.__static_background = target_surface_sub.copy()        
        self.__working_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.__working_surface.blit(self.__static_background, (0, 0))

        static_labels = pygame.Surface((width, height), pygame.SRCALPHA)
        y_offset = self.__config.stack_y_offset
        font_height = self.__font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        # and where we need to setup subsurfaces for updates
        origin = (0, 0)
        # Static Label
        self.__font_normal.render_to(self.__static_background, origin, "PerfCap", Color.white)

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
        self.__font_normal.render_to(self.__static_background, origin, "RAM Used", Color.grey_75)

        # GPU RAM Used
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__ram_used = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}" + DashData.gpu_ram_used.unit.symbol, Color.yellow, self.__font_normal)

        # A little hacky, but blit the static background down again to include the static bits
        self.__working_surface.blit(self.__static_background, (0, 0))

    def draw_update(self, data):
        assert(None != self.__working_surface and None != self.__static_background)
        assert(0 != len(data))

        perfcap_reason_data = DashData.best_attempt_read(data, DashData.gpu_perfcap_reason, "")
        if self.__perfcap_reason.current_value != perfcap_reason_data:
            self.__perfcap_reason.update(perfcap_reason_data)

        gpu_power_value = DashData.best_attempt_read(data, DashData.gpu_power, "0")
        if self.__gpu_power.current_value != gpu_power_value:
            self.__gpu_power.update(gpu_power_value)

        gpu_clock_value = DashData.best_attempt_read(data, DashData.gpu_clock, "0")
        if self.__gpu_clock.current_value != gpu_clock_value:
            self.__gpu_clock.update(gpu_clock_value)

        gpu_utilization = DashData.best_attempt_read(data, DashData.gpu_util, "0")
        if self.__gpu_utilization.current_value != gpu_utilization:
            self.__gpu_utilization.update(gpu_utilization)

        ram_used_value = DashData.best_attempt_read(data, DashData.gpu_ram_used, "0")
        if self.__ram_used.current_value != ram_used_value:
            self.__ram_used.update(ram_used_value)

        return self.__working_surface


class FPSConfig:
    def __init__(self, number_font=None, label_font=None, draw_zero=True):
        self.number_font = number_font
        self.label_font = label_font
        self.draw_zero = draw_zero

class FPSText:
    current_value = None

    def __init__(self, fps_field_rect, target_surface, fps_config=FPSConfig()):
        
        width, height = fps_field_rect[2], fps_field_rect[3]
        assert(0 != height or 0 != width)

        # Config and fonts
        self.__config = fps_config
        if None == self.__config.number_font:
            self.__config.number_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 50)
            #self.__config.number_font.strong = True
            self.__config.number_font.kerning = True

        if None == self.__config.label_font:
            self.__config.label_font = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
            #self.__config.label_font.strong = True
            self.__config.label_font.kerning = True

        # Surface setup
        # NOTE: (Adam) 2020-12-10 No luck experimenting with 0 alpha fill wipes or pixel clearing,
        #           for now copying out the pixels from the target surface and saving as base for redraws
        target_surface_sub = target_surface.subsurface(fps_field_rect)
        self.__background = target_surface_sub.copy()
        # TODO: Could draw label directly on the background since it's static. For now going to try
        #       keeping the field blank until FPS > 0 for a cleaner look.

        self.__working_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Setup the last loose bits
        # Could probably be a bit more dynamic based on number font parameters, etc.
        self.__label_x = 3
        self.__label_y = self.__working_surface.get_height() - self.__config.label_font.get_sized_height()

    def draw_update(self, value):

        self.__working_surface.blit(self.__background, (0,0))

        if 0 == int(value) and False == self.__config.draw_zero:
            return self.__working_surface

        self.__config.number_font.render_to(self.__working_surface, (0, 0), "{}".format(value), Color.white)
        self.__config.label_font.render_to(self.__working_surface, (self.__label_x, self.__label_y), "FPS", Color.white)

        return self.__working_surface


class TemperatureHumidity:
    
    # DynamicFields
    __temperature = None
    __humidity = None

    # Surfaces
    __working_surface = None
    __static_background = None

    def __init__(self, element_rect, target_surface):
        self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        #self.__font_normal.strong = True
        self.__font_normal.kerning = True
        self.__setup_surfaces_and_fields__(element_rect, target_surface)

    def __setup_surfaces_and_fields__(self, element_rect, target_surface):
        assert(None == self.__working_surface and None == self.__static_background)

        width, height = element_rect[2], element_rect[3]
        assert(0 != height or 0 != width)

        target_surface_sub = target_surface.subsurface(element_rect)
        self.__static_background = target_surface_sub.copy()        
        self.__working_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.__working_surface.blit(self.__static_background, (0, 0))

        static_labels = pygame.Surface((width, height), pygame.SRCALPHA)
        y_offset = -2
        font_height = self.__font_normal.get_sized_height()

        # Start doing a little mock drawing here to workout where the static label(s) are positioned
        # and where we need to setup subsurfaces for updates
        
        # Static Label
        origin = (0, 0)
        self.__font_normal.render_to(self.__static_background, origin, "Room Temp", Color.white)

        # Temperature
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__temperature = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}\u00b0F", Color.white, self.__font_normal)

        # Static Label
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__font_normal.render_to(self.__static_background, origin, "Humidity", Color.white)

        # Humidity
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__humidity = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}%", Color.white, self.__font_normal)

        # A little hacky, but blit the static background down again to include the static bits
        self.__working_surface.blit(self.__static_background, (0, 0))

    def draw_update(self, data):
        assert(None != self.__working_surface and None != self.__static_background)

        if self.__temperature.current_value != data.temperature:
            self.__temperature.update(data.temperature)

        if self.__humidity.current_value != data.humidity:
            self.__humidity.update(data.humidity)

        return self.__working_surface

class MotherboardTemperature:
    # Basic double-digit (I hope!) display of motherboard temperature

    __working_surface = None
    __static_background = None
    
    current_value = None

    def __init__(self, element_rect, target_surface):

        self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        width, height = element_rect[2], element_rect[3]
        self.__working_surface = pygame.Surface((width, height))
        temp_target_subsurface = target_surface.subsurface(element_rect)
        self.__static_background = temp_target_subsurface.copy()

    def draw_update(self, value):
        self.__working_surface.blit(self.__static_background, (0, 0))
        self.__font_normal.render_to(self.__working_surface, (0, 0), "{}".format(value), Color.white)
        self.current_value = value
        return self.__working_surface

class NetworkInformation:
    # Basic network down/upstream stat display

    __working_surface = None
    __static_background = None
    
    current_download_value = None
    current_upload_value = None

    def __init__(self, element_rect, target_surface):

        self.__font_normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        width, height = element_rect[2], element_rect[3]
        self.__working_surface = pygame.Surface((width, height))
        temp_target_subsurface = target_surface.subsurface(element_rect)
        self.__static_background = temp_target_subsurface.copy()

        # Anchor text to bottom of surface, use static value for y because font sized_height is an average
        self.__y_offset = self.__working_surface.get_height() - 12

    def draw_update(self, download_value, upload_value):
        self.__working_surface.blit(self.__static_background, (0, 0))

        self.__font_normal.render_to(
            self.__working_surface, (0, self.__y_offset), 
            "NIC 1 Down: {} {}".format(download_value, DashData.nic1_download_rate.unit.symbol), 
            Color.white)

        self.__font_normal.render_to(
            self.__working_surface, (180, self.__y_offset), 
            "Up: {} {}".format(upload_value, DashData.nic1_upload_rate.unit.symbol), 
            Color.white)

        self.current_download_value = download_value
        self.current_upload_value = upload_value

        return self.__working_surface
