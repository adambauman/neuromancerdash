
#
# disk_visualizer_scratch - messing around with a new disk activity visualizer
# ============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

from time import sleep
import sys
import os
import math

import pygame
import pygame.gfxdraw

from dashboard_painter import Color, FontPath, DataField, DashData, AssetPath, Units

class Helpers:
    @staticmethod
    def calculate_center_align(parent_surface, child_surface):

        parent_center = (parent_surface.get_width() / 2, parent_surface.get_height() / 2)
        child_center = (child_surface.get_width() / 2, child_surface.get_height() / 2)
        
        child_align_x = parent_center[0] - child_center[0]
        child_align_y = parent_center[1] - child_center[1]

        return (child_align_x, child_align_y)

    @staticmethod
    def transpose_ranges(input, input_high, input_low, output_high, output_low):
        #print("transpose, input: {} iHI: {} iLO: {} oHI: {} oLO: {}".format(input, input_high, input_low, output_high, output_low))
        diff_multiplier = (input - input_low) / (input_high - input_low)
        return ((output_high - output_low) * diff_multiplier) + output_low
            
class DiskActivityVisualizer:
    # TODO: Most of this can move to a config class
    __disk_count = 4 # TODO: dynamic count
    __disks_per_row = 2
    __disk_spacing = 4

    __disk_active_bitmap = None
    __disk_bitmap = None
    __letter_font = None

    __last_activity_values = []
    __last_base_surface = None

    def __init__(self, disk_letter_list):
        assert(0 != len(disk_letter_list))

        self.__disk_letter_list = disk_letter_list
        self.__disk_bitmap = pygame.image.load(os.path.join(AssetPath.misc, "disk_02.png"))
        self.__disk_active_bitmap = pygame.image.load(os.path.join(AssetPath.misc, "disk_02_active.png"))
        self.__letter_font = pygame.freetype.Font(FontPath.fira_code_semibold(), 12)

        for _ in range(self.__disk_count):
            self.__last_activity_values.append(False)

    def __draw_activity__(self, is_active, index):
        assert(None != self.__disk_active_bitmap and None != self.__disk_bitmap)

        #disk_center = (int(disk_bitmap.get_width() / 2), int(disk_bitmap.get_height() / 2))

        if False == is_active:
            text = self.__letter_font.render("D{}".format(index), Color.windows_dkgrey_1_highlight)
            #letter_center = (int(text.get_width() / 2), int(text.get_height() / 2))
            disk_status_bitmap = self.__disk_bitmap.copy()
            disk_status_bitmap.blit(text[0], Helpers.calculate_center_align(disk_status_bitmap, text[0]))
            return disk_status_bitmap
        else:
            text = self.__letter_font.render("D{}".format(index), Color.windows_dkgrey_1)
            #letter_center = (int(text.get_width() / 2), int(text.get_height() / 2))
            disk_status_bitmap = self.__disk_bitmap_active.copy()
            disk_status_bitmap.blit(text[0], Helpers.calculate_center_align(disk_status_bitmap, text[0]))
            return disk_status_bitmap

    def update(self, data):
        # TODO: (Adam) 2020-11-25 Add dynamic sizing, disk counts, etc. Right now this is written
        #           to support a specific computer's disk setup
        assert(0 != len(data))

        # Grab data
        activity_values = []
        for index in range(self.__disk_count):
            key = "disk_{}_activity".format(index)
            try:
                activity_values.append(int(data[key]))
            except:
                #if __debug__:
                #    print("Data error: {}".format(key))
                activity_values.append(0)

        assert(0 != len(activity_values))
        assert(len(self.__last_activity_values) == len(activity_values))

        # Don't grind out a new surface if values are static
        values_changed = False
        for index in range(len(activity_values)):
            if self.__last_activity_values[index] == activity_values[index]:
                values_changed = True

        ## But do create one if this is the first run and the last surface is None
        #if False == values_changed and None != self.__last_base_surface: 
        #    return self.__last_base_surface
        
        # TODO: (Adam) 2020-11-25 Move first surface setup into initializer
        # Setup base surface, if values haven't changed we will re-use the base surface
        if None == self.__last_base_surface:
            row_count = int(self.__disk_count / self.__disks_per_row)
            base_surface_x =\
                (self.__disk_bitmap.get_width() * self.__disks_per_row) + (self.__disk_spacing * (self.__disks_per_row - 1))
            base_surface_y =\
                (self.__disk_bitmap.get_height() * row_count) + (self.__disk_spacing * (self.__disks_per_row - 1))

            self.__last_base_surface = pygame.Surface((base_surface_x, base_surface_y), pygame.SRCALPHA)
            self.__last_base_surface.fill(Color.black)

            # TODO: (Adam) 2020-11-25 Kinda all over the place with variable used with ranges,
            #           make more consistent
            base_disk_columns_drawn = 0
            base_rows_drawn = 0
            base_disk_x = 0
            base_disk_y = 0
            for index in range(self.__disk_count):
                # Move to next row, reset column count
                if self.__disks_per_row <= base_disk_columns_drawn:
                    base_rows_drawn += 1
                    base_disk_y += (self.__disk_bitmap.get_height() * base_rows_drawn) + self.__disk_spacing
                    base_disk_columns_drawn = 0

                # Move X up a column or return position to 0 if this is the first in a row
                if 0 != base_disk_columns_drawn:
                    base_disk_x += (self.__disk_bitmap.get_width() * base_disk_columns_drawn) + self.__disk_spacing
                else:
                    base_disk_x = 0

                self.__last_base_surface.blit(self.__draw_activity__(False, index), (base_disk_x, base_disk_y))
                base_disk_columns_drawn += 1

        # Start draw disks, skipping disks that haven't changed
        columns_drawn = 0
        rows_drawn = 0
        disk_x = 0
        disk_y = 0
        for index in range(len(activity_values)):
            # NOTE: (Adam) 2020-11-25 Need to move the "draw cursor" regardless if the value changes
            # Move to next row, reset column count
            if self.__disks_per_row <= columns_drawn:
                rows_drawn += 1
                disk_y += (disk_bitmap.get_height * rows_drawn) + self.__disk_spacing
                columns_drawn = 0

            # Move X up a column or return position to 0 if this is the first in a row
            if 0 != columns_drawn:
                disk_x += (disk_bitmap.get_width() * columns_drawn) + self.__disk_spacing
            else:
                disk_x = 0
            
            # Now check if value has changed, save a blit if it isn't necessary
            if self.__last_activity_values[index] != activity_values[index]:
                self.__last_base_surface.blit(
                    self.__draw_activity__(activity_values[index], index),
                    (base_disk_x, base_disk_y))

        # Store activity and return
        self.__last_activity_values = activity_values
        return self.__last_base_surface

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

    disk_activity = DiskActivityVisualizer(["C", "D", "E", "F"])
    
    data = {
        "disk_0_activity": 0,
        "disk_1_activity": 0,
        "disk_2_activity": 0,
        "disk_3_activity": 0
        }


    while True:
        display_surface.fill(Color.black)

        display_surface.blit(disk_activity.update(data), (20,20))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()

        pygame.event.clear()

        pygame.display.flip()

        sleep(0.100)

    pygame.quit()


if __name__ == "__main__":
    main(sys.argv[1:])



# Went a little too nuts here, save this for future updates to GPUTemperature visualizer?

class GPUTemperature:
    _working_surface = None
    _static_elements = None
    _indicator_okay = None
    _indicator_warn = None
    _indicator_origin = None
    _temperature_origin = (44, 42)

    _current_temperature_value = None
    _current_rpm_value = None

    def __init__(self, pump_status_config=GPUTemperatureConfig(), direct_surface=None, direct_rect=None, surface_flags=0):

        self._config = pump_status_config
        self._surface_flags = surface_flags
        self._direct_rect = direct_rect

        if direct_surface and direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
        else:
            self._working_surface = pygame.Surface(size, self._surface_flags)

        self.__prepare_surfaces_()


    def __prepare_surfaces_(self):
        assert(self._working_surface is not None)

        # Base images are much larger than display, scale to fit using heatsink section height to calculate
        heatsink_section_unscaled = pygame.image.load(os.path.join(AssetPath.hardware, "gpu_fins_med.png")).convert_alpha()
        scale_modifier = self._config.size[1] / heatsink_section_unscaled.get_height()

        # Load images
        heatsink_section = pygame.transform.rotozoom(heatsink_section_unscaled, 0, scale_modifier)

        indicator_base = pygame.transform.rotozoom(
            pygame.image.load(os.path.join(AssetPath.hardware, "loose_indicator_housing.png")).convert_alpha(),
            0, scale_modifier)

        indicator_housing = pygame.transform.rotozoom(
            pygame.image.load(os.path.join(AssetPath.hardware, "loose_indicator_housing.png")).convert_alpha(),
            0, scale_modifier)

        self._indicator_okay = indicator_base.copy()
        self._indicator_okay.fill(self._config.indicator_bg_color, special_flags=pygame.BLEND_RGBA_MULT)
        self._indicator_warn = indicator_base.copy()
        self._indicator_warn.fill(self._config.indicator_warning_color, special_flags=pygame.BLEND_RGBA_MULT)

        # Reaching the configured size is a best-effort affair, depends on how many heatsink tiles we can fit
        assert(self._config.size[0] > heatsink_section.get_width())
        heatsink_section_count = int(self._config.size[0] / heatsink_section.get_width()) # python int() on division rounds towards floor

        # Create the heatsink surface and blit out the sections
        assert(self._config.size[1] >= heatsink_section.get_height())
        heatsink_width = heatsink_section_count * heatsink_section.get_width()
        heatsink = pygame.Surface((heatsink_width, heatsink_section.get_height()), self._surface_flags)
        for index in range(heatsink_section_count):

            if heatsink_section_count != index:
                x = index * heatsink_section.get_width()
                heatsink.blit(heatsink_section, (x, 0))
            else:
                # Flip the last element to nicely cap off the heatsink graphic
                cap_section = pygame.transform.flip(heatsink_section, True)
                x = heatsink.get_width() - cap_section.get_width()
                heatsink.blit(cap_section, (x, 0))

        # Create final static elements surface
        # Default is to draw the indicator one surface section from the right
        # TODO: Could add this to config once tested
        indicator_housing_vertical_offset = 4
        indicator_housing_origin = (
            heatsink.get_width() - indicator_housing.get_width() - heatsink_section.get_width(), 
            indicator_housing_vertical_offset)
        # Save origin for update draws, indicator is sized to overlay right on the housing
        self._indicator_origin = indicator_housing_origin
        
        # TODO: Could account for other indicator offsets
        base_width = heatsink.get_width()
        base_height = heatsink.get_height() + indicator_housing_vertical_offset
        self._static_elements = pygame.Surface((base_width, base_height), self._surface_flags)
        self._static_elements.blit(heatsink, (0,0))
        self._static_elements.blit(indicator_housing, indicator_housing_origin)
        
        # All done, blit out to work surface
        self._working_surface.blit(self._static_elements, (0, 0))


    def draw_update(self, temperature_value, fan_rpm_value):
        assert(self._working_surface is not None)
        assert(self._static_elements is not None)
        assert(self._indicator_origin is not None)
        assert(self._indicator_okay is not None and self._indicator_warn is not None)

        self._working_surface.blit(self._static_elements, (0, 0))

        # TODO: Could add GPU fan warning, lots of modern GPUs spin down when idle though
        if self._config.warning_temperature <= int(temperature_value):
            self._working_surface.blit(self._indicator_warn, self._indicator_origin)
        else:
            self._working_surface.blit(self._indicator_okay, self._indicator_origin)

        # TODO: Font coloration based on temperature, if enabled
        # Draw temperature text within the indicator
        shadowed_temperature_text = Helpers.get_shadowed_text(
                self._config.temperature_font, "{}\u00b0".format(temperature_value), 
                self._config.temperature_font_color, self._config.temperature_shadow_color)
        # TODO: Dynamic temperature origin tied to scaled size
        self._working_surface.blit(shadowed_temperature_text, self._temperature_origin)

        # TODO: Update bargraph!

        self._current_temperature_value = temperature_value
        self._current_rpm_value = fan_rpm_value
            
        return self._working_surface, self._direct_rect

