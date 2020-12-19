#
# cooling.py - Contains layout, configurations, and update routines for cooling info page
# =======================================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

import os
from copy import copy

from data.units import Unit, Units
from data.dataobjects import DataField, DashData

from elements.helpers import Helpers
from elements.styles import Color, AssetPath, FontPath
from elements.bargraph import BarGraph, BarGraphConfig
from elements.text import  TemperatureHumidity, MotherboardTemperatureSensors
from elements.visualizers import PumpStatus, PumpStatusConfig, GPUTemperature, GPUTemperatureConfig

if __debug__:
    import traceback

class CoolingConfigs:

    def __init__(self, base_font=None):

        fan_base_rpm_range = (300, 2000)
        base_fan_bar_config = BarGraphConfig((140, 20), fan_base_rpm_range, base_font)
        base_fan_bar_config.unit_draw = True
        base_fan_bar_config.current_value_draw = True
        
        # On Neuromancer AIDA64 is has mixed some of these assignments up (verified by looking directly at the
        #   app data), here are the actual assignemnts:
        # chassis_1_fan = front intakes combined
        # chassis_2_fan = bottom intakes
        # chassis_3_fan = rear exhaust
        # cpu_opt = forward exhaust

        # NOTE: Make horizontal bars a bit longer and narrower because of funny eye perception of sizes
        # Horizontal bars
        self.rear_exhaust_bar = copy(base_fan_bar_config)
        self.rear_exhaust_bar.size = (140, 32)
        self.rear_exhaust_bar.dash_data = DashData.chassis_3_fan

        self.forward_exhaust_bar = copy(base_fan_bar_config)
        self.forward_exhaust_bar.size = (140, 32)
        self.forward_exhaust_bar.dash_data = DashData.cpu_opt_fan

        self.bottom_intake_fan_bar = copy(base_fan_bar_config)
        self.bottom_intake_fan_bar.size = (140, 32)
        self.bottom_intake_fan_bar.dash_data = DashData.chassis_2_fan
        
        # Vertical bar(s)
        self.front_intake_fan_bar = copy(base_fan_bar_config)
        self.front_intake_fan_bar.size = (122, 35)
        self.front_intake_fan_bar.dash_data = DashData.chassis_1_fan

        self.cpu_pump_status = PumpStatusConfig((100, 100))
        self.gpu_temperature = GPUTemperatureConfig()
        self.gpu_temperature.fan_dash_data = DashData.gpu_fan
        self.gpu_temperature.temperature_dash_data = DashData.gpu_temp


class CoolingPositions:

    def __init__(self, display_size, element_configs):
        assert(0 != display_size[0] and 0 != display_size[1])

        exhaust_fans_bars_width = element_configs.rear_exhaust_bar.size[0]
        exhaust_fans_bars_spacing = 20
        exhaust_fans_x = 10
        exhaust_fans_y = 0
        exhaust_fan_bar_size = element_configs.rear_exhaust_bar.size
        self.rear_exhaust_fan_bar = pygame.Rect((exhaust_fans_x, exhaust_fans_y), exhaust_fan_bar_size)
        forward_exhaust_fan_x = exhaust_fans_x + exhaust_fans_bars_width + exhaust_fans_bars_spacing
        self.forward_exhaust_fan_bar = pygame.Rect((forward_exhaust_fan_x, exhaust_fans_y), exhaust_fan_bar_size)

        front_intake_bar_size = element_configs.front_intake_fan_bar.size
        #self.front_intake_fan_bars = pygame.Rect((438, 50), front_intake_bar_size)
        self.front_intake_fan_bars = pygame.Rect((350, 40), front_intake_bar_size)

        bottom_intake_fan_bar_size = element_configs.bottom_intake_fan_bar.size
        self.bottom_intake_fan_bars = pygame.Rect((10, display_size[1] - bottom_intake_fan_bar_size[1]), bottom_intake_fan_bar_size)

        self.cpu_pump = pygame.Rect((40, 70), element_configs.cpu_pump_status.size)
        self.gpu_temperature = pygame.Rect((10, 200), element_configs.gpu_temperature.size)

        # Text elements
        self.motherboard_temps_rect = pygame.Rect(175, 78, 130, 100)
        self.temperature_humidity_rect = pygame.Rect(405, 250, 74, 56)


class Cooling:
    _working_surface = None
    _background = None
    _surface_flags = None

    def __init__(self, base_size, direct_surface=None, direct_rect=None, surface_flags=0):
        assert(0 != base_size[0] and 0 != base_size[1])

        self._surface_flags = surface_flags

        if direct_surface and direct_rect is not None:
            self._working_surface = direct_surface.subsurface(direct_rect)
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

        self._font_normal = pygame.freetype.Font(FontPath.fira_code_semibold(), 12)
        self._font_normal.kerning = True

        if __debug__:
            self._background = pygame.image.load(os.path.join(AssetPath.backgrounds, "480_320_grid.png")).convert_alpha()
            self._working_surface.blit(self._background, (0,0))

        # TODO: (Adam) 2020-12-11 Pass in a shared fonts object, lots of these controls have their own
        #           font instances. Would cut down on memory usage and make it easier to match font styles.

        element_configs = CoolingConfigs(self._font_normal)
        self._element_positions = CoolingPositions(base_size, element_configs)

        self._rear_exhaust_fan_bar = BarGraph(
            element_configs.rear_exhaust_bar, self._working_surface, self._element_positions.rear_exhaust_fan_bar)
        self._forward_exhaust_fan_bar = BarGraph(
            element_configs.forward_exhaust_bar, self._working_surface, self._element_positions.forward_exhaust_fan_bar)

        self._cpu_pump_status = PumpStatus(element_configs.cpu_pump_status, self._working_surface, self._element_positions.cpu_pump)
        self._gpu_temperature = GPUTemperature(element_configs.gpu_temperature, self._working_surface, self._element_positions.gpu_temperature)

        self._motherboard_temps = MotherboardTemperatureSensors(
            self._element_positions.motherboard_temps_rect, direct_surface=self._working_surface)
        self._temperature_humidity = TemperatureHumidity(
            self._element_positions.temperature_humidity_rect, direct_surface=self._working_surface)

        # Not using direct draw, elements need transforms before blit
        self._front_intake_fan_bar = BarGraph(element_configs.front_intake_fan_bar)
        self._bottom_intake_fan_bar = BarGraph(element_configs.bottom_intake_fan_bar)

        # Load image files
        self._icon_linked = pygame.image.load(os.path.join(AssetPath.icons, "linked_24px.png")).convert_alpha()
        self._icon_linked.fill(Color.grey_40, special_flags=pygame.BLEND_RGB_MULT)

    def __draw_front_intake_fans__(self, value, using_direct_surface=False):
        assert(self._surface_flags is not None)

        # Draw two bars matching the exhaust style, flip 90 CCW
        single_intake_bar = self._front_intake_fan_bar.draw_update(value)[0]
        fan_spacing = 20
        dual_surface_size = ((single_intake_bar.get_width() * 2) + fan_spacing, single_intake_bar.get_height())
        dual_fan_surface = pygame.Surface(dual_surface_size, self._surface_flags)
        dual_fan_surface.blit(single_intake_bar, (0, 0))
        dual_fan_surface.blit(single_intake_bar, (single_intake_bar.get_width() + fan_spacing, 0))
        #dual_fan_rotated_surface = pygame.transform.rotozoom(dual_fan_surface, 90, 1)
        dual_fan_rotated_surface = pygame.transform.rotate(dual_fan_surface, 90)
        # TODO: Use maths to align link icon
        dual_fan_rotated_surface.blit(self._icon_linked, (6, 127))

        update_rect = self._element_positions.front_intake_fan_bars
        if using_direct_surface:
            update_rect = self._working_surface.blit(dual_fan_rotated_surface, update_rect)
            #self._working_surface.blit(dual_fan_rotated_surface, update_rect)

        return dual_fan_rotated_surface, update_rect

    def __draw_bottom_intake_fans_(self, value, using_direct_surface=False):
        single_bar = self._bottom_intake_fan_bar.draw_update(value)[0]
        fan_spacing = 20
        dual_surface_size = (single_bar.get_width() * 2 + fan_spacing, single_bar.get_height())
        dual_fan_surface = pygame.Surface(dual_surface_size, self._surface_flags)
        dual_fan_surface.blit(single_bar, (0, 0))
        dual_fan_surface.blit(single_bar, (single_bar.get_width() + fan_spacing, 0))
        dual_fan_surface.blit(pygame.transform.rotate(self._icon_linked, 90), (144, 3))

        update_rect = self._element_positions.bottom_intake_fan_bars
        if using_direct_surface:
            update_rect = self._working_surface.blit(dual_fan_surface, update_rect)
         
        return dual_fan_surface, update_rect

    def draw_update(self, aida64_data, dht22_data=None, redraw_all=False):
        assert(0 != len(aida64_data))

        #if self._background is not None:
        #    self._working_surface.blit(self._background, (0, 0))
        #else:
        #    self._working_surface.fill(0, 0, 0, 0)

        # chassis_1_fan = front intakes combined
        # chassis_2_fan = bottom intakes
        # chassis_3_fan = rear exhaust
        # cpu_opt = forward exhaust

        update_rects = []

        cpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.cpu_fan, "0")
        cpu_temperature_value = DashData.best_attempt_read(aida64_data, DashData.cpu_temp, "0")
        update_rects.append(self._cpu_pump_status.draw_update(cpu_temperature_value, cpu_fan_value)[1])
        #if cpu_pump_rect is not None:
        #    update_rects.append(cpu_pump_rect)

        gpu_temperature_value = DashData.best_attempt_read(aida64_data, DashData.gpu_temp, "0")
        gpu_fan_value = DashData.best_attempt_read(aida64_data, DashData.gpu_fan, "0")
        update_rects.append(self._gpu_temperature.draw_update(gpu_temperature_value, gpu_fan_value)[1])

        # Fan bar graphs
        rear_exhaust_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_3_fan, "0")
        update_rects.append(self._rear_exhaust_fan_bar.draw_update(rear_exhaust_fan_value)[1])

        forward_exhaust_fan_value = DashData.best_attempt_read(aida64_data, DashData.cpu_opt_fan, "0")
        update_rects.append(self._forward_exhaust_fan_bar.draw_update(forward_exhaust_fan_value)[1])

        front_intake_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_1_fan, "0")
        update_rects.append(
            self.__draw_front_intake_fans__(front_intake_fan_value, using_direct_surface=True)[1])

        bottom_intake_fan_value = DashData.best_attempt_read(aida64_data, DashData.chassis_2_fan, "0")
        update_rects.append(
            self.__draw_bottom_intake_fans_(bottom_intake_fan_value, using_direct_surface=True)[1])

        motherboard_temp_value = DashData.best_attempt_read(aida64_data, DashData.motherboard_temp, "0")
        pch_temp_value = DashData.best_attempt_read(aida64_data, DashData.pch_temp, "0")
        unlabeled_temp_value = DashData.best_attempt_read(aida64_data, DashData.unlabeled_temp, "0")
        update_rects.append(
            self._motherboard_temps.draw_update(motherboard_temp_value, pch_temp_value, unlabeled_temp_value)[1])

        # Ambient temperature and humidity
        if dht22_data is not None:
            update_rects.append(self._temperature_humidity.draw_update(dht22_data)[1])

        return self._working_surface, update_rects
