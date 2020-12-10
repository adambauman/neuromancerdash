#
# textstack - stacked text displays for grouped value readouts
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from .styles import Color, FontPaths, AssetPath
from .helpers import Helpers

class StackHelpers:
    def __get_next_y_stack_origin__(self, last_origin, font, padding = 0):
        x = last_origin[0]
        y = last_origin[1] + font.get_sized_height() + padding
        return (x,y)

class CPUDetails:
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
    def __init__(self, number_font=None, label_font=None, draw_zero=False):
        self.number_font = number_font
        self.label_font = label_font
        self.draw_zero = draw_zero

class FPSText:
    current_value = None

    def __init__(self, fps_field_rect, target_surface, fps_config=FPSConfig()):
        assert(0 != fps_field_rect[0] or 0 != fps_field_rect[1])

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
        
        width, height = fps_field_rect[2], fps_field_rect[3]
        self.__working_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Setup the last loose bits
        # Could probably be a bit more dynamic based on number font parameters, etc.
        self.__label_x = 3
        self.__label_y = self.__working_surface.get_height() - self.__config.label_font.get_sized_height()

        
    def draw_update(self, value):

        self.__working_surface.blit(self.__background, (0,0))

        #if 0 == value and False == self.__config.draw_zero:
        #    return self.__working_surface

        #self.fps_text = (210, 240)
        #self.fps_label = (212, 285)
        self.__config.number_font.render_to(self.__working_surface, (0, 0), "{}".format(value), Color.white)
        self.__config.label_font.render_to(self.__working_surface, (self.__label_x, self.__label_y), "FPS", Color.white)

        return self.__working_surface