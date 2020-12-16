#
# visualizers - visualizer display elements
# =========================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from .styles import Color

# Set true to benchmark the update process
g_benchmark = False

class CoreVisualizerConfig:
    def __init__(self, core_count):
        self.core_count = core_count
        self.core_width = 13
        self.core_spacing = 2
        self.core_rows = 2
        self.core_height = None
        self.active_color = Color.windows_cyan_1
        self.inactive_color = Color.windows_cyan_1_dark
        # Percentage of activity required to light up core representation
        self.activity_threshold_percent = 12

class SimpleCoreVisualizer:
    __config = CoreVisualizerConfig

    __working_surface = None
    __using_direct_surface = False
    __direct_rect = None

    # Tracking outside config in case we need to adjust on the fly
    __core_height = 0
    __core_width = 0
    
    __core_count = 0
    __cores_per_row = 0
    __last_core_activity = []

    __first_run = True

    def __init__(self, core_visualizer_config, direct_surface=None, direct_rect=None, surface_flags=0):

        self.__config = core_visualizer_config

        # NOTE: (Adam) 2020-11-19 Setting for compatability with new config setup
        self.__core_count = self.__config.core_count

        self.__core_width = self.__config.core_width
        self.__core_height = self.__config.core_height
        if None == self.__core_height:
            self.__core_height = self.__core_width

        assert(0 != self.__core_height)

        # Rounds up if reminder exists
        self.__cores_per_row =\
            int(self.__core_count / self.__config.core_rows) + (self.__core_count % self.__config.core_rows > 0)

        # Initialize working surface
        base_width =\
            (self.__core_width * self.__cores_per_row) + (self.__config.core_spacing * (self.__cores_per_row -1))
        base_height =\
            (self.__core_height * self.__config.core_rows) + (self.__config.core_spacing * (self.__config.core_rows - 1))

        if None != direct_surface and None != direct_rect:
            assert(base_width <= direct_rect[2] and base_height <= direct_rect[3])

            self.__using_direct_surface = True
            self.__working_surface = direct_surface.subsurface(direct_rect)
            self.__direct_rect = direct_rect
        else:
            self.__using_direct_surface = False
            self.__working_surface = pygame.Surface((base_width, base_height), surface_flags)

        # Initialize last core activity and do a hack update
        initialize_data = {}
        for index in range(self.__core_count):
            key = "cpu{}_util".format(index)
            initialize_data[key] = 0
            self.__last_core_activity.append(False)

        self.update(initialize_data)
        self.__first_run = False

    def update(self, data):
        assert(None != self.__working_surface and 0 != len(self.__last_core_activity))
        assert(len(data) >= self.__core_count)

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # Copy in last core surface, we will only update the altered representations
        #self.__base_surface.blit(self.__last_base_surface, (0, 0))

        core_origin_x = 0
        core_origin_y = 0
        core_activity_tracking = []
        for index in range(self.__core_count):

            key_name = "cpu{}_util".format(index)
            core_activity_value = 0
            try:
                core_activity_value = int(data[key_name])
            except:
                core_activity_value = 0
                if __debug__:
                    print("Data error: core {}".format(index))
                    #traceback.print_exc()

            core_active = False
            if core_activity_value >= self.__config.activity_threshold_percent:
                #print("Core{} active at {}%".format(index, core_activity_value))
                core_active = True

            # Track activity for the next update call
            core_activity_tracking.append(core_active)

            # No need to re-draw if status hasn't changed
            if self.__last_core_activity[index] == core_active and self.__first_run != False:
                continue

            core_color = self.__config.inactive_color
            if core_active:
                core_color = self.__config.active_color

            pygame.draw.rect(
                self.__working_surface, 
                core_color, 
                (core_origin_x, core_origin_y, self.__core_width, self.__core_width)
            )

            if len(core_activity_tracking) == self.__cores_per_row:
                # Move to the next row
                core_origin_y += self.__core_width + self.__config.core_spacing
                core_columns_drawn = 0
                core_origin_x = 0
            else:
                # Move to the next column
                core_origin_x += self.__core_width + self.__config.core_spacing


        #assert(len(self.__last_core_activity) == len(core_activity_tracking))
        self.__last_core_activity = core_activity_tracking


        if g_benchmark:
            print("BENCHMARK: CoreVisualizer: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self.__working_surface, self.__direct_rect


