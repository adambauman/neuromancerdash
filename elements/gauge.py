#
# gauge - gauge display elements
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

import os

from .helpers import Helpers
from .styles import Color, FontPath, AssetPath

# Set true to benchmark the update process
g_benchmark = False

class GaugeConfig:
    def __init__(self, data_field, radius=45, value_font=None, value_font_size=16, value_font_origin=None):
        self.radius = radius
        self.data_field = data_field
        self.redline_degrees = 35

        # Uses smooth rotozoom animation. This has a bit of a performance penalty if enabled.
        self.use_smoothed_rotation = True

        self.value_font_size = value_font_size
        self.value_font_origin = value_font_origin # If None the value will be centered
        self.value_font = value_font
        if not self.value_font:
            self.value_font = pygame.freetype.Font(FontPath.fira_code_semibold(), self.value_font_size)
            self.value_font.strong = True

        self.arc_main_color = Color.windows_cyan_1
        self.arc_redline_color = Color.windows_red_1
        self.needle_color = Color.windows_light_grey_1
        self.shadow_color = Color.black
        self.shadow_alpha = 50
        self.draw_shadow = True
        self.unit_text_color = Color.white
        self.value_text_color = Color.white
        self.value_text_warn_color = Color.windows_red_1
        self.bg_color = Color.windows_dkgrey_1

        # TODO: (Adam) Copy in the background behind the gauge so we can clear and apply it when
        #           drawing updates. Or do something fancy with subsurfaces. Right now bg_alpha 
        #           will only appear on the first draw
        self.bg_alpha = 255

        self.counter_sweep = False
        self.draw_value = True
        self.draw_unit_symbol = True
        self.draw_label_instead_of_value = False
        self.label = ""

class FlatArcGauge:
    current_value = None

    _current_needle_rotation = 0
    _static_elements_surface = None
    _needle_surface = None
    _needle_shadow_surface = None

    def __init__(self, gauge_config, direct_surface=None, direct_rect=None, surface_flags=0):
        assert(gauge_config.data_field)
        assert(0 < gauge_config.radius)

        self._config = gauge_config

        diameter = self._config.radius * 2
        base_size = (diameter, diameter)

        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
            self.update_rect = direct_rect
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)
            self.update_rect = pygame.Rect((0, 0), base_size)
        
        # Setup static elements, these are things like the gauge arcs that will not need updating
        self.__prepare_constant_elements__(base_size, surface_flags)

    def __prepare_constant_elements__(self, base_size, surface_flags):
        assert((0, 0) != base_size)
        
        # NOTE: (Adam) 2020-12-11 Careful with source image sizes if running on a weaker
        #           board like the RPi Zero, startup generation could take a while if you go overboard. 

        if __debug__:
            print("Preparing {} arc gauge components...".format(self._config.data_field.field_name))

        # Have tried drawing arcs with pygame.draw and gfxdraw but the results were sub-par. Now using large
        # PNG shapes to build up the gauge then scaling down to final size.
        arc_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1_base_1.png")).convert_alpha()
        redline_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1_redline_1.png")).convert_alpha()

        ########
        # Base Surface
        ########

        # Create the base surface for stuff like the gauge background, arc, redline
        assert(arc_bitmap.get_width() >= arc_bitmap.get_height())
        base_surface_size = (arc_bitmap.get_width(), arc_bitmap.get_width()) # TODO: figure out which is actually bigger
        gauge_base_surface = pygame.Surface(base_surface_size, surface_flags)

        # Calculate some bounds and origin points
        center = (gauge_base_surface.get_width() / 2, gauge_base_surface.get_height() / 2)
        scaled_radius = arc_bitmap.get_width() / 2

        # Draw background circle
        bg_color = pygame.Color(self._config.bg_color)
        pygame.draw.circle(gauge_base_surface, bg_color, center, scaled_radius)

        # Apply color to main arc and blit
        arc_main_color = pygame.Color(self._config.arc_main_color)
        arc_bitmap.fill(arc_main_color, special_flags = pygame.BLEND_RGBA_MULT)
        gauge_base_surface.blit(arc_bitmap, (0, 0))

        # Apply color to redline and blit
        arc_redline_color = pygame.Color(self._config.arc_redline_color)
        redline_bitmap.fill(arc_redline_color, special_flags = pygame.BLEND_RGBA_MULT)
        if self._config.counter_sweep:
            gauge_base_surface.blit(pygame.transform.flip(redline_bitmap, True, False), (0, 0))
        else:
            gauge_base_surface.blit(redline_bitmap, (0, 0))

        # Draw static text to a discrete surface then blit it with center alignments as reference
        # Unit
        if self._config.draw_unit_symbol:
            font_unit = pygame.freetype.Font(FontPath.fira_code_semibold(), 120)
            unit_text_surface = font_unit.render(self._config.data_field.unit.symbol, self._config.unit_text_color)
            center_align = Helpers.calculate_center_align(gauge_base_surface, unit_text_surface[0])
            gauge_base_surface.blit(unit_text_surface[0], (center_align[0], center_align[1] + 300))

        # Scale the base surface to the final size and blit to the static elements surface
        assert(self._working_surface.get_size() == base_size)
        self._static_elements_surface = pygame.transform.smoothscale(gauge_base_surface, base_size)

        ########
        # Needle
        ########

        # Create a temporary working surface for the needle, mirror dimensions of the unscaled arc bitmap
        # for proper centering. Alpha flag required.
        needle_surface = pygame.Surface(gauge_base_surface.get_size(), surface_flags | pygame.SRCALPHA)

        # Setup needle elements, these will be rotated when blitted but the memeber surfaces will remain static
        needle_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1_needle_1.png")).convert_alpha()
        
        # Apply color to needle
        needle_color = pygame.Color(self._config.needle_color)
        needle_bitmap.fill(needle_color, special_flags = pygame.BLEND_RGBA_MULT)

        # Find the needle's center, blit to center of the working surface, then store it as a member surface
        needle_center = Helpers.calculate_center_align(gauge_base_surface, needle_bitmap)
        needle_surface.blit(needle_bitmap, needle_center)
        self._needle_surface = pygame.transform.smoothscale(needle_surface, base_size)

        ########
        # Needle Shadow
        ########

        # Needle shadow
        if self._config.draw_shadow:
            self._needle_shadow_surface = self._needle_surface.copy()
            shadow_color = pygame.Color(self._config.shadow_color)
            shadow_color.a = self._config.shadow_alpha
            self._needle_shadow_surface.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)

        if __debug__:
            print("Done generating components!")

    def __draw_needle_rotation__(self, rotation_degrees):
        if self._config.use_smoothed_rotation:
            rotated_needle = pygame.transform.rotozoom(self._needle_surface, rotation_degrees, 1)
        else:
            rotated_needle = pygame.transform.rotate(self._needle_surface, rotation_degrees)

        # Shadow
        # Add a small %-change multiplier to give the shadow farther distance as values approach limits
        if self._config.draw_shadow:
            abs_change_from_zero = abs(rotation_degrees)
            shadow_distance = 4 + ((abs(rotation_degrees) / 135) * 10)

            shadow_rotation = rotation_degrees
            if rotation_degrees > 0: #counter-clockwise
                shadow_rotation += shadow_distance
            else: #clockwise
                shadow_rotation += -shadow_distance
            rotated_shadow = pygame.transform.rotozoom(self._needle_shadow_surface, shadow_rotation, 0.93)
            shadow_center = Helpers.calculate_center_align(self._working_surface, rotated_shadow)
            self._working_surface.blit(rotated_shadow, shadow_center)

        needle_center = Helpers.calculate_center_align(self._working_surface, rotated_needle)
        self._working_surface.blit(rotated_needle, needle_center)

    def __draw_value_text__(self, value):
        # Set value text color, change it to the warning color if the data field has a warn level value
        value_color = self._config.value_text_color
        if self._config.data_field.warn_value:
            if not self._config.counter_sweep and int(value) > self._config.data_field.warn_value:
                value_color = self._config.value_text_warn_color
            elif self._config.counter_sweep and int(value) < self._config.data_field.warn_value:
                value_color = self._config.value_text_warn_color

        if self._config.draw_label_instead_of_value:
            value_text = self._config.label
        else:
            value_text = "{}".format(value)

        # Draw value to temporary surface so we can calculate centers
        value_surface = self._config.value_font.render(value_text, value_color)[0]

        # Use configured origin point, otherwise calculate it
        if self._config.value_font_origin:
            value_origin = self._config.value_font_origin
        else:
            value_origin = Helpers.calculate_center_align(self._working_surface, value_surface)

        self._working_surface.blit(value_surface, value_origin)

        # Return the rect for udpating the value area, this could be used to keep value fresh without
        # redrawing the needle on every update
        value_update_rect = pygame.Rect((value_origin), value_surface.get_size())
        return value_update_rect

    def draw_update(self, value):
        assert(self._working_surface)
        assert(self._static_elements_surface)
        assert(self._needle_surface)

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # No need to update, return previous working surface and no update rect
        if self.current_value == value:
            return self._working_surface, None

        # Reset the working surface
        self._working_surface.blit(self._static_elements_surface, (0, 0))

        self.__draw_value_text__(value)
            
        # Transpose value into gauge rotation space
        max_value = self._config.data_field.max_value
        min_value = self._config.data_field.min_value
        arc_transposed_value = Helpers.transpose_ranges(float(value), max_value, min_value, -135, 135)

        self.__draw_needle_rotation__(arc_transposed_value)
        # Use full update rect if we had to draw the needle

        # Track for the next update
        self.current_value = value

        if g_benchmark:
            print("BENCHMARK: ArcGauge {}: {}ms".format(self._config.data_field.field_name, pygame.time.get_ticks() - start_ticks))

        return self._working_surface, self.update_rect
