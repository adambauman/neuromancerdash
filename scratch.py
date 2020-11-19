#!/usr/bin/env python

from time import sleep
import sys
import os
import math

import pygame
import pygame.gfxdraw

from dashboard_painter import Color, FontPaths, DataField, DashData, AssetPath

class Helpers:
    @staticmethod
    def calculate_center_align(parent_surface, child_surface):

        parent_center = (parent_surface.get_width() / 2, parent_surface.get_height() / 2)
        child_center = (child_surface.get_width() / 2, child_surface.get_height() / 2)
        
        child_align_x = parent_center[0] - child_center[0]
        child_align_y = parent_center[1] - child_center[1]

        return (child_align_x, child_align_y)

    @staticmethod
    def get_aa_circle(color, radius, aa_scale = 2, surface_flags = pygame.SRCALPHA):
        assert(0 != radius)

        diameter = int(radius * 2)
        aa_surface = pygame.Surface((diameter * aa_scale, diameter * aa_scale), surface_flags)
        aa_center = (aa_surface.get_width() / 2, aa_surface.get_height() / 2)
        pygame.draw.circle(aa_surface, color, aa_center, radius * aa_scale)
        return pygame.transform.smoothscale(aa_surface, (diameter, diameter))

    # Following taken and modified from here: https://sites.cs.ucsb.edu/~pconrad/cs5nm/08F/ex/ex09/drawCircleArcExample.py
    @staticmethod
    def degreesToRadians(deg):
        return deg/180.0 * math.pi

    # Draw an arc that is a portion of a circle.
    # We pass in screen and color,
    # followed by a tuple (x,y) that is the center of the circle, and the radius.
    # Next comes the start and ending angle on the "unit circle" (0 to 360)
    #  of the circle we want to draw, and finally the thickness in pixels
    @staticmethod
    def drawCircleArc(screen, color, center, radius, startDeg, endDeg, thickness):
        (x,y) = center
        rect = (x-radius,y-radius,radius*2,radius*2)
        startRad = Helpers.degreesToRadians(startDeg)
        endRad = Helpers.degreesToRadians(endDeg)
        pygame.draw.arc(screen, color, rect, startRad, endRad, thickness)

class GaugeConfig:
    def __init__(self, data_field, radius = 135):
        self.radius = radius
        self.data_field = data_field
        self.redline_degrees = 35
        self.aa_multiplier = 2

        self.arc_main_color = Color.windows_cyan_1
        self.arc_redline_color = Color.windows_red_1
        self.needle_color = Color.windows_light_grey_1
        self.shadow_color = Color.black
        self.shadow_alpha = 50
        self.text_color = Color.white
        self.bg_color = Color.windows_dkgrey_1
        self.bg_alpha = 200

        self.counter_sweep = False
        self.show_value = True
        self.show_unit_symbol = True

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

        self.__paint_static_elements()

    def __paint_static_elements(self):
        assert(None != self.__static_elements_surface)
        assert(0 < self.__config.aa_multiplier)
        
        # Have tried drwaing with pygame.draw and gfxdraw but the results were sub-par. Now using large
        # PNG shapes to build up the gauge then scaling down to final size.
        arc_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1.png"))
        redline_bitmap = pygame.image.load(os.path.join(AssetPath.gauges, "arc_1_redline_1.png"))

        assert(arc_bitmap.get_width() >= arc_bitmap.get_height())
        base_scaled_size = (arc_bitmap.get_width(), arc_bitmap.get_width())

        temp_surface = pygame.Surface(base_scaled_size)
        center = (temp_surface.get_width() / 2, temp_surface.get_height() / 2)

        #scaled_radius = self.__config.radius * self.__config.aa_multiplier
        scaled_radius = arc_bitmap.get_width() / 2

        # Draw background
        bg_surface = pygame.Surface((temp_surface.get_height(), temp_surface.get_width()))
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
            unit_text_surface = font_unit.render(self.__config.data_field.unit.symbol, self.__config.text_color)
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
        self.__static_elements_surface.blit(scaled_surface, (0, 0))


    def update(self, value):
        assert(None != self.__working_surface)

        self.__working_surface = self.__static_elements_surface.copy()
        return self.__working_surface


def main(argv):

    ### SETUP
    ###

    ###
    ###

    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.event.set_allowed([pygame.QUIT])
    
    display_surface = pygame.display.set_mode(
        (480, 320),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    display_surface.fill(Color.black)

    gauge_config = GaugeConfig(DashData.cpu_temp)
    cpu_temp_gauge = FlatArcGauge(gauge_config)
    display_surface.blit(cpu_temp_gauge.update(30), (20,20))


    #bg_color = gauge_config.bg_color
    #radius = 45
    #pygame.gfxdraw.aacircle(self.__static_elements_surface, surface_center_x, surface_center_y, radius, bg_color)
    #pygame.gfxdraw.filled_circle(self.__static_elements_surface, surface_center_x, surface_center_y, radius, bg_color)
    #pygame.draw.circle(display_surface, bg_color, (55, 55), radius)
    #self.__static_elements_surface = pygame.transform.smoothscale(aa_surface, (self.__static_elements_surface.get_width(), self.__static_elements_surface.get_height()))
    #display_surface.blit(Helpers.get_aa_circle(bg_color, radius, 2), (110, 10))
    #display_surface.blit(Helpers.get_aa_circle(bg_color, radius, 4), (210, 10))
    #display_surface.blit(Helpers.get_aa_circle(bg_color, radius, 100), (310, 10))

    #gauge_face =  pygame.image.load(os.path.join(AssetPath.gauges, "arc_flat_90px_style1.png"))
    #display_surface.blit(gauge_face, (110, 110))

    
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()

        pygame.event.clear()

        sleep(0.200)

    pygame.quit()


if __name__ == "__main__":
    main(sys.argv[1:])
