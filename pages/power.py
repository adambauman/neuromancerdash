#
# power.py - Contains layout, configurations, and update routines for power info page
# =======================================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

import os
from copy import copy

from data.units import Unit, Units
from data.dataobjects import DataField, DashData
from elements.historybar import HistoryBar, HistoryBarConfig
from elements.text import EnclosedLabel, EnclosedLabelConfig
from elements.helpers import Helpers
from elements.styles import Color, AssetPath, FontPath

if __debug__:
    import traceback

class PowerConfigs:

    def __init__(self, base_font=None):

        volt_bar_width = 300

        self.volts_12 = HistoryBarConfig((volt_bar_width, 31), DashData.volts_12)
        self.volts_5 = HistoryBarConfig((volt_bar_width, 31), DashData.volts_5)
        self.volts_3_3 = HistoryBarConfig((volt_bar_width, 31), DashData.volts_3_3)
        self.volts_cpuvid = HistoryBarConfig((volt_bar_width, 31), DashData.volts_cpu_vid)
        self.volts_dimm = HistoryBarConfig((volt_bar_width, 31), DashData.volts_dimm)
        self.volts_gpu_core = HistoryBarConfig((volt_bar_width, 31), DashData.volts_gpu_core)

        self.volt_label_config = EnclosedLabelConfig(
            base_font, text_padding=10, text_color=Color.black,
            outline_line_width=0, outline_radius=0, outline_color=Color.grey_75)

        self.volt_value_config = EnclosedLabelConfig(
            base_font, text_padding=10, text_color=Color.black,
            outline_line_width=0, outline_radius=0, outline_color=Color.grey_75)

class PowerPositions:

    def __init__(self, display_size, element_configs):
        assert((0, 0) != display_size)

        value_offset = 298
        bar_x = 90
        
        self.volts_12 = (bar_x, 0)
        self.volts_12_label = (self.volts_12[0] - 68, self.volts_12[1])
        self.volts_12_value = (self.volts_12[0] + value_offset, self.volts_12[1])

        self.volts_5 = (bar_x, 30)
        self.volts_5_label = (self.volts_5[0] - 68, self.volts_5[1])
        self.volts_5_value = (self.volts_5[0] + value_offset, self.volts_5[1])

        self.volts_3_3 = (bar_x, 60)
        self.volts_3_3_label = (self.volts_3_3[0] - 68, self.volts_3_3[1])
        self.volts_3_3_value = (self.volts_3_3[0] + value_offset, self.volts_3_3[1])

        self.volts_cpuvid = (bar_x, 100)
        self.volts_cpuvid_label = (self.volts_cpuvid[0] - 68, self.volts_cpuvid[1])
        self.volts_cpuvid_value = (self.volts_cpuvid[0] + value_offset, self.volts_cpuvid[1])

        self.volts_dimm = (bar_x, 130)
        self.volts_dimm_label = (self.volts_dimm[0] - 68, self.volts_dimm[1])
        self.volts_dimm_value = (self.volts_dimm[0] + value_offset, self.volts_dimm[1])

        self.volts_gpu_core = (bar_x, 170)
        self.volts_gpu_core_label = (self.volts_gpu_core[0] - 68, self.volts_gpu_core[1])
        self.volts_gpu_core_value = (self.volts_gpu_core[0] + value_offset, self.volts_gpu_core[1])


class Power:
    _working_surface = None
    _background = None
    _surface_flags = None

    def __init__(self, base_size, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != base_size)

        self._surface_flags = surface_flags
        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
        else:
            self._working_surface = pygame.Surface(base_size, surface_flags)

        self._font_normal = pygame.freetype.Font(FontPath.fira_code_semibold(), 12)
        self._font_normal.kerning = True

        element_configs = PowerConfigs(self._font_normal)
        element_positions = PowerPositions(base_size, element_configs)

        # PSU 12 Volt Rail
        self._volts_12_value = EnclosedLabel(
            element_positions.volts_12_value, 
            "12.000v", 
            element_configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_12_label = EnclosedLabel(
            element_positions.volts_12_label, 
            "PSU  12v", 
            element_configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_12 = HistoryBar(element_configs.volts_12)
        volts_12_rect = pygame.Rect(element_positions.volts_12, self._volts_12.base_size)
        self._volts_12.set_direct_draw(self._working_surface, volts_12_rect)

        # PSU 5 Volt Rail
        self._volts_5_value = EnclosedLabel(
            element_positions.volts_5_value, 
            " 5.000v", 
            element_configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_5_label = EnclosedLabel(
            element_positions.volts_5_label, 
            "PSU   5v", 
            element_configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_5 = HistoryBar(element_configs.volts_5)
        volts_5_rect = pygame.Rect(element_positions.volts_5, self._volts_5.base_size)
        self._volts_5.set_direct_draw(self._working_surface, volts_5_rect)

        # PSU 3.3 Volt Rail
        self._volts_3_3_value = EnclosedLabel(
            element_positions.volts_3_3_value, 
            " 3.300v", 
            element_configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_3_3_label = EnclosedLabel(
            element_positions.volts_3_3_label, 
            "PSU 3.3v", 
            element_configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_3_3 = HistoryBar(element_configs.volts_3_3)
        volts_3_3_rect = pygame.Rect(element_positions.volts_3_3, self._volts_3_3.base_size)
        self._volts_3_3.set_direct_draw(self._working_surface, volts_3_3_rect)

        # CPUVID
        self._volts_cpuvid_value = EnclosedLabel(
            element_positions.volts_cpuvid_value, 
            " 1.650v", 
            element_configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_cpuvid_label = EnclosedLabel(
            element_positions.volts_cpuvid_label, 
            "CPU  VID",
            element_configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_cpuvid = HistoryBar(element_configs.volts_cpuvid)
        volts_cpuvid_rect = pygame.Rect(element_positions.volts_cpuvid, self._volts_cpuvid.base_size)
        self._volts_cpuvid.set_direct_draw(self._working_surface, volts_cpuvid_rect)

        # DIMM
        self._volts_dimm_value = EnclosedLabel(
            element_positions.volts_dimm_value, 
            " 1.650v", 
            element_configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_dimm_label = EnclosedLabel(
            element_positions.volts_dimm_label, 
            "DIMM   V",
            element_configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_dimm = HistoryBar(element_configs.volts_dimm)
        volts_dimm_rect = pygame.Rect(element_positions.volts_dimm, self._volts_dimm.base_size)
        self._volts_dimm.set_direct_draw(self._working_surface, volts_dimm_rect)

        # GPU Core
        self._volts_gpu_core_value = EnclosedLabel(
            element_positions.volts_gpu_core_value, 
            " 1.650v", 
            element_configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_gpu_core_label = EnclosedLabel(
            element_positions.volts_gpu_core_label, 
            "GPU CORE",
            element_configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_gpu_core = HistoryBar(element_configs.volts_gpu_core)
        volts_gpu_core_rect = pygame.Rect(element_positions.volts_gpu_core, self._volts_gpu_core.base_size)
        self._volts_gpu_core.set_direct_draw(self._working_surface, volts_gpu_core_rect)

    def backup_element_surface(self):
        # Blit, copy doesn't work if this is a subsurfaced direct-draw element
        self._backup_surface = pygame.Surface(self._working_surface.get_size())
        self._backup_surface.blit(self._working_surface, (0, 0))

    def restore_element_surface(self):
        if self._backup_surface:
            self._working_surface.blit(self._backup_surface, (0, 0))

    def draw_update(self, aida64_data, dht22_data=None, redraw_all=False):

        assert(0 != len(aida64_data))

        update_rects = []

        # PSU 12v
        volts_12_value = DashData.best_attempt_read(aida64_data, DashData.volts_12, "0.0")
        update_rects.append(self._volts_12.draw_update(volts_12_value)[1])
        update_rects.append(self._volts_12_value.draw("{}v".format(volts_12_value))[1])
        update_rects.append(self._volts_12_label.draw()[1])

        # PSU 5v
        volts_5_value = DashData.best_attempt_read(aida64_data, DashData.volts_5, "0.0")
        update_rects.append(self._volts_5.draw_update(volts_5_value)[1])
        update_rects.append(self._volts_5_value.draw(" {}v".format(volts_5_value))[1])
        update_rects.append(self._volts_5_label.draw()[1])

        # PSU 3.3v
        volts_3_3_value = DashData.best_attempt_read(aida64_data, DashData.volts_3_3, "0.0")
        update_rects.append(self._volts_3_3.draw_update(volts_3_3_value)[1])
        update_rects.append(self._volts_3_3_value.draw(" {}v".format(volts_3_3_value))[1])
        update_rects.append(self._volts_3_3_label.draw()[1])

        # CPU VID
        volts_cpuvid_value = DashData.best_attempt_read(aida64_data, DashData.volts_cpu_vid, "0.0")
        update_rects.append(self._volts_cpuvid.draw_update(volts_cpuvid_value)[1])
        update_rects.append(self._volts_cpuvid_value.draw(" {}v".format(volts_cpuvid_value))[1])
        update_rects.append(self._volts_cpuvid_label.draw()[1])

        # DIMM V
        volts_dimm_value = DashData.best_attempt_read(aida64_data, DashData.volts_cpu_vid, "0.0")
        update_rects.append(self._volts_dimm.draw_update(volts_dimm_value)[1])
        update_rects.append(self._volts_dimm_value.draw(" {}v".format(volts_dimm_value))[1])
        update_rects.append(self._volts_dimm_label.draw()[1])

        # GPU Core
        volts_gpu_core_value = DashData.best_attempt_read(aida64_data, DashData.volts_cpu_vid, "0.0")
        update_rects.append(self._volts_gpu_core.draw_update(volts_gpu_core_value)[1])
        update_rects.append(self._volts_gpu_core_value.draw(" {}v".format(volts_gpu_core_value))[1])
        update_rects.append(self._volts_gpu_core_label.draw()[1])
        
        return self._working_surface, update_rects
