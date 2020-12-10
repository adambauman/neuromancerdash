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
    def __init__(self, origin, subsurface, text, text_color, font, value=None):
        # Will be an updatable subsurface of the working surface
        self.__subsurface = subsurface 
        self.__static_background = subsurface.copy()
        self.__text_color = text_color
        self.__font = font
        self.__origin = origin
        self.__text = text

        self.current_value = value

    def update(self, new_value):
        self.__subsurface.blit(self.__static_background, (0, 0))
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

    # TODO: The two current detail stacks share a lot of init code and objects. Maybe inherit them both from
    #       a base detail stack class.
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

        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__cpu_clock = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{} " + DashData.cpu_clock.unit.symbol, Color.white, self.__font_normal)

        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__cpu_utilization = DynamicField(
            origin, 
            self.__working_surface.subsurface((origin[0], origin[1], self.__working_surface.get_width(), font_height + y_offset)),
            "{}" + DashData.cpu_util.unit.symbol, Color.yellow, self.__font_normal)

        # Static label, write to the static background
        origin = (origin[0], (origin[1] + font_height) + y_offset)
        self.__font_normal.render_to(self.__static_background, origin, "RAM Used", Color.grey_75)

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