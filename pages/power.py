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
from elements.text import EnclosedLabel, EnclosedLabelConfig, SimpleText
from elements.helpers import Helpers
from elements.styles import Color, AssetPath, FontPath

if __debug__:
    import traceback

class PowerConfigs:

    def __init__(self, base_font=None):

        volt_bar_size = (200, 31)
        self.volts_12 = HistoryBarConfig(volt_bar_size, DashData.volts_12)
        self.volts_5 = HistoryBarConfig(volt_bar_size, DashData.volts_5)
        self.volts_3_3 = HistoryBarConfig(volt_bar_size, DashData.volts_3_3)
        self.volts_cpuvid = HistoryBarConfig(volt_bar_size, DashData.volts_cpu_vid)
        self.volts_dimm = HistoryBarConfig(volt_bar_size, DashData.volts_dimm)
        self.volts_gpu_core = HistoryBarConfig(volt_bar_size, DashData.volts_gpu_core)

        outline_size = (69, 30)
        self.volt_label_config = EnclosedLabelConfig(
            base_font, text_padding=10, text_color=Color.black,
            outline_line_width=0, outline_radius=0, outline_color=Color.grey_75, outline_size=outline_size)

        self.volt_value_config = EnclosedLabelConfig(
            base_font, text_padding=10, text_color=Color.black,
            outline_line_width=0, outline_radius=0, outline_color=Color.grey_75, outline_size=outline_size)

class PowerPositions:

    def __init__(self, display_size, element_configs):
        assert((0, 0) != display_size)

        value_offset = 198
        bar_x = 140
        minmax_rect_size = (50, 23)
        
        self.volts_12 = (bar_x, 0)
        self.volts_12_label = (self.volts_12[0] - 68, self.volts_12[1])
        self.volts_12_value = (self.volts_12[0] + value_offset, self.volts_12[1])
        self.volts_12_min = pygame.Rect((10, 8), minmax_rect_size)
        self.volts_12_max = pygame.Rect((420, 8), minmax_rect_size)

        self.volts_5 = (bar_x, 28)
        self.volts_5_label = (self.volts_5[0] - 68, self.volts_5[1])
        self.volts_5_value = (self.volts_5[0] + value_offset, self.volts_5[1])
        self.volts_5_min = pygame.Rect((10, 38), minmax_rect_size)
        self.volts_5_max = pygame.Rect((420, 38), minmax_rect_size)

        self.volts_3_3 = (bar_x, 57)
        self.volts_3_3_label = (self.volts_3_3[0] - 68, self.volts_3_3[1])
        self.volts_3_3_value = (self.volts_3_3[0] + value_offset, self.volts_3_3[1])
        self.volts_3_3_min = pygame.Rect((10, 68), minmax_rect_size)
        self.volts_3_3_max = pygame.Rect((420, 68), minmax_rect_size)

        self.volts_cpuvid = (bar_x, 100)
        self.volts_cpuvid_label = (self.volts_cpuvid[0] - 68, self.volts_cpuvid[1])
        self.volts_cpuvid_value = (self.volts_cpuvid[0] + value_offset, self.volts_cpuvid[1])
        self.volts_cpuvid_min = pygame.Rect((10, 108), minmax_rect_size)
        self.volts_cpuvid_max = pygame.Rect((420, 108), minmax_rect_size)

        self.volts_dimm = (bar_x, 128)
        self.volts_dimm_label = (self.volts_dimm[0] - 68, self.volts_dimm[1])
        self.volts_dimm_value = (self.volts_dimm[0] + value_offset, self.volts_dimm[1])
        self.volts_dimm_min = pygame.Rect((10, 138), minmax_rect_size)
        self.volts_dimm_max = pygame.Rect((420, 138), minmax_rect_size)

        self.volts_gpu_core = (bar_x, 170)
        self.volts_gpu_core_label = (self.volts_gpu_core[0] - 68, self.volts_gpu_core[1])
        self.volts_gpu_core_value = (self.volts_gpu_core[0] + value_offset, self.volts_gpu_core[1])
        self.volts_gpu_core_min = pygame.Rect((10, 178), minmax_rect_size)
        self.volts_gpu_core_max = pygame.Rect((420, 178), minmax_rect_size)

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

        self._configs = PowerConfigs(self._font_normal)
        self._positions = PowerPositions(base_size, self._configs)

        # PSU 12 Volt Rail
        self._volts_12_value = EnclosedLabel(
            self._positions.volts_12_value, 
            "12.000v", 
            self._configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_12_label = EnclosedLabel(
            self._positions.volts_12_label, 
            "PSU  12v", 
            self._configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_12 = HistoryBar(self._configs.volts_12)
        volts_12_rect = pygame.Rect(self._positions.volts_12, self._volts_12.base_size)
        self._volts_12.set_direct_draw(self._working_surface, volts_12_rect)

        self._volts_12_min = SimpleText(
            self._positions.volts_12_min, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)
        self._volts_12_max = SimpleText(
            self._positions.volts_12_max, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)

        # PSU 5 Volt Rail
        self._volts_5_value = EnclosedLabel(
            self._positions.volts_5_value, 
            " 5.000v", 
            self._configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_5_label = EnclosedLabel(
            self._positions.volts_5_label, 
            "PSU   5v", 
            self._configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_5 = HistoryBar(self._configs.volts_5)
        volts_5_rect = pygame.Rect(self._positions.volts_5, self._volts_5.base_size)
        self._volts_5.set_direct_draw(self._working_surface, volts_5_rect)

        self._volts_5_min = SimpleText(
            self._positions.volts_5_min, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)
        self._volts_5_max = SimpleText(
            self._positions.volts_5_max, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)

        # PSU 3.3 Volt Rail
        self._volts_3_3_value = EnclosedLabel(
            self._positions.volts_3_3_value, 
            " 3.300v", 
            self._configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_3_3_label = EnclosedLabel(
            self._positions.volts_3_3_label, 
            "PSU 3.3v", 
            self._configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_3_3 = HistoryBar(self._configs.volts_3_3)
        volts_3_3_rect = pygame.Rect(self._positions.volts_3_3, self._volts_3_3.base_size)
        self._volts_3_3.set_direct_draw(self._working_surface, volts_3_3_rect)

        self._volts_3_3_min = SimpleText(
            self._positions.volts_3_3_min, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)
        self._volts_3_3_max = SimpleText(
            self._positions.volts_3_3_max, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)

        # CPUVID
        self._volts_cpuvid_value = EnclosedLabel(
            self._positions.volts_cpuvid_value, 
            " 1.650v", 
            self._configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_cpuvid_label = EnclosedLabel(
            self._positions.volts_cpuvid_label, 
            "CPU  VID",
            self._configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_cpuvid = HistoryBar(self._configs.volts_cpuvid)
        volts_cpuvid_rect = pygame.Rect(self._positions.volts_cpuvid, self._volts_cpuvid.base_size)
        self._volts_cpuvid.set_direct_draw(self._working_surface, volts_cpuvid_rect)

        self._volts_cpuvid_min = SimpleText(
            self._positions.volts_cpuvid_min, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)
        self._volts_cpuvid_max = SimpleText(
            self._positions.volts_cpuvid_max, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)

        # DIMM
        self._volts_dimm_value = EnclosedLabel(
            self._positions.volts_dimm_value, 
            " 1.650v", 
            self._configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_dimm_label = EnclosedLabel(
            self._positions.volts_dimm_label, 
            "DIMM   V",
            self._configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_dimm = HistoryBar(self._configs.volts_dimm)
        volts_dimm_rect = pygame.Rect(self._positions.volts_dimm, self._volts_dimm.base_size)
        self._volts_dimm.set_direct_draw(self._working_surface, volts_dimm_rect)

        self._volts_dimm_min = SimpleText(
            self._positions.volts_dimm_min, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)
        self._volts_dimm_max = SimpleText(
            self._positions.volts_dimm_max, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)

        # GPU Core
        self._volts_gpu_core_value = EnclosedLabel(
            self._positions.volts_gpu_core_value, 
            " 1.650v", 
            self._configs.volt_value_config, 
            direct_surface=self._working_surface)

        self._volts_gpu_core_label = EnclosedLabel(
            self._positions.volts_gpu_core_label, 
            "GPU CORE",
            self._configs.volt_label_config, 
            direct_surface=self._working_surface)

        self._volts_gpu_core = HistoryBar(self._configs.volts_gpu_core)
        volts_gpu_core_rect = pygame.Rect(self._positions.volts_gpu_core, self._volts_gpu_core.base_size)
        self._volts_gpu_core.set_direct_draw(self._working_surface, volts_gpu_core_rect)
                                             
        self._volts_gpu_core_min = SimpleText(
            self._positions.volts_gpu_core_min, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)
        self._volts_gpu_core_max = SimpleText(
            self._positions.volts_gpu_core_max, "{}v", text_color=Color.grey_75, direct_surface=self._working_surface)

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
        update_rects.append(self._volts_12_min.draw_update(self._volts_12.min_history_value)[1])
        update_rects.append(self._volts_12_max.draw_update(self._volts_12.max_history_value)[1])

        # PSU 5v
        volts_5_value = DashData.best_attempt_read(aida64_data, DashData.volts_5, "0.0")
        update_rects.append(self._volts_5.draw_update(volts_5_value)[1])
        update_rects.append(self._volts_5_value.draw(" {}v".format(volts_5_value))[1])
        update_rects.append(self._volts_5_label.draw()[1])
        update_rects.append(self._volts_5_min.draw_update(self._volts_5.min_history_value)[1])
        update_rects.append(self._volts_5_max.draw_update(self._volts_5.max_history_value)[1])

        # PSU 3.3v
        volts_3_3_value = DashData.best_attempt_read(aida64_data, DashData.volts_3_3, "0.0")
        update_rects.append(self._volts_3_3.draw_update(volts_3_3_value)[1])
        update_rects.append(self._volts_3_3_value.draw(" {}v".format(volts_3_3_value))[1])
        update_rects.append(self._volts_3_3_label.draw()[1])
        update_rects.append(self._volts_3_3_min.draw_update(self._volts_3_3.min_history_value)[1])
        update_rects.append(self._volts_3_3_max.draw_update(self._volts_3_3.max_history_value)[1])

        # CPU VID
        volts_cpuvid_value = DashData.best_attempt_read(aida64_data, DashData.volts_cpu_vid, "0.0")
        update_rects.append(self._volts_cpuvid.draw_update(volts_cpuvid_value)[1])
        update_rects.append(self._volts_cpuvid_value.draw(" {}v".format(volts_cpuvid_value))[1])
        update_rects.append(self._volts_cpuvid_label.draw()[1])
        update_rects.append(self._volts_cpuvid_min.draw_update(self._volts_cpuvid.min_history_value)[1])
        update_rects.append(self._volts_cpuvid_max.draw_update(self._volts_cpuvid.max_history_value)[1])

        # DIMM V
        volts_dimm_value = DashData.best_attempt_read(aida64_data, DashData.volts_dimm, "0.0")
        update_rects.append(self._volts_dimm.draw_update(volts_dimm_value)[1])
        update_rects.append(self._volts_dimm_value.draw(" {}v".format(volts_dimm_value))[1])
        update_rects.append(self._volts_dimm_label.draw()[1])
        update_rects.append(self._volts_dimm_min.draw_update(self._volts_dimm.min_history_value)[1])
        update_rects.append(self._volts_dimm_max.draw_update(self._volts_dimm.max_history_value)[1])

        # GPU Core
        volts_gpu_core_value = DashData.best_attempt_read(aida64_data, DashData.volts_gpu_core, "0.0")
        update_rects.append(self._volts_gpu_core.draw_update(volts_gpu_core_value)[1])
        update_rects.append(self._volts_gpu_core_value.draw(" {}v".format(volts_gpu_core_value))[1])
        update_rects.append(self._volts_gpu_core_label.draw()[1])
        update_rects.append(self._volts_gpu_core_min.draw_update(self._volts_gpu_core.min_history_value)[1])
        update_rects.append(self._volts_gpu_core_max.draw_update(self._volts_gpu_core.max_history_value)[1])
        
        return self._working_surface, update_rects
