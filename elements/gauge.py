#
# gauge - gauge display elements
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

import os

from .helpers import Helpers
from .styles import Color, FontPaths, AssetPath

# Set true to benchmark the update process
g_benchmark = False

class GaugeConfig:
    def __init__(self, data_field, radius=45, value_font=None, value_font_origin=None):
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

        # TODO: (Adam) Copy in the background behind the gauge so we can clear and apply it when
        #           drawing updates. Or do something fancy with subsurfaces. Right now bg_alpha 
        #           will only appear on the first draw
        self.bg_alpha = 255

        self.counter_sweep = False
        self.show_value = True
        self.show_unit_symbol = True
        self.show_label_instead_of_value = False
        self.label = ""

class FlatArcGauge:
    __config = None

    __working_surface = None
    __current_value = None

    __static_elements_surface = None # Should not be changed after init
    __needle_surface = None # Should not be changed after init
    __needle_shadow_surface = None  # Should not be changed after init

    def __init__(self, gauge_config):
        assert(None != gauge_config.data_field)
        assert(0 < gauge_config.radius)

        self.__config = gauge_config

        diameter = self.__config.radius * 2
        base_size = (diameter, diameter)
        self.__working_surface = pygame.Surface(base_size, pygame.SRCALPHA)

        self.__static_elements_surface = pygame.Surface(base_size, pygame.SRCALPHA)
        self.__prepare_constant_elements()

        assert(None != self.__static_elements_surface)
        assert(None != self.__needle_surface and None != self.__needle_shadow_surface)

    def __prepare_constant_elements(self):
        assert(None != self.__static_elements_surface)
        assert(0 < self.__config.aa_multiplier)
        
        # NOTE: (Adam) 2020-12-11 Careful with source image sizes if running on a weaker
        #           board like the RPi Zero, generation could take a while if you go overboard. 

        if __debug__:
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

        if __debug__:
            print("Done generating components!")
        
    def draw_update(self, value):
        assert(None != self.__working_surface)

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # Return the previous working surface if the value hasn't changed
        if self.__current_value == value:
            return self.__working_surface
        else:
            self.__working_surface.fill((0, 0, 0, 0))

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
        self.current_value = value

        if g_benchmark:
            print("BENCHMARK: ArcGauge {}: {}ms".format(self.__config.data_field.field_name, pygame.time.get_ticks() - start_ticks))

        return self.__working_surface

