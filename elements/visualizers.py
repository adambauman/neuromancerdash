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
    _config = CoreVisualizerConfig

    _working_surface = None
    _direct_rect = None

    # Tracking outside config in case we need to adjust on the fly
    _core_height = 0
    _core_width = 0
    
    _core_count = 0
    _cores_per_row = 0
    _last_core_activity = []

    # TODO: Ditch this, check if surfaces are prepped, last core activity is populated, etc.
    _first_run = True

    def __init__(self, core_visualizer_config, direct_surface=None, direct_rect=None, surface_flags=0):

        self._config = core_visualizer_config

        # NOTE: (Adam) 2020-11-19 Setting for compatability with new config setup
        self._core_count = self._config.core_count

        self._core_width = self._config.core_width
        self._core_height = self._config.core_height
        if self._core_height is None:
            self._core_height = self._core_width

        assert(0 != self._core_height)

        # Rounds up if reminder exists
        self._cores_per_row =\
            int(self._core_count / self._config.core_rows) + (self._core_count % self._config.core_rows > 0)

        # Initialize working surface
        base_width =\
            (self._core_width * self._cores_per_row) + (self._config.core_spacing * (self._cores_per_row -1))
        base_height =\
            (self._core_height * self._config.core_rows) + (self._config.core_spacing * (self._config.core_rows - 1))

        if None != direct_surface and None != direct_rect:
            assert(base_width <= direct_rect[2] and base_height <= direct_rect[3])

            self._working_surface = direct_surface.subsurface(direct_rect)
            self._direct_rect = direct_rect
        else:
            self._working_surface = pygame.Surface((base_width, base_height), surface_flags)

        # Initialize last core activity and do a hack update
        initialize_data = {}
        for index in range(self._core_count):
            key = "cpu{}_util".format(index)
            initialize_data[key] = 0
            self._last_core_activity.append(False)

        self.update(initialize_data)
        self._first_run = False

    def update(self, data):
        assert(self._working_surface is not None)
        assert(0 != len(self._last_core_activity))
        assert(len(data) >= self._core_count)

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # Copy in last core surface, we will only update the altered representations
        #self._base_surface.blit(self._last_base_surface, (0, 0))

        core_origin_x = 0
        core_origin_y = 0
        core_activity_tracking = []
        for index in range(self._core_count):

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
            if core_activity_value >= self._config.activity_threshold_percent:
                #print("Core{} active at {}%".format(index, core_activity_value))
                core_active = True

            # Track activity for the next update call
            core_activity_tracking.append(core_active)

            # No need to re-draw if status hasn't changed
            if self._last_core_activity[index] == core_active and self._first_run is not False:
                continue

            core_color = self._config.inactive_color
            if core_active:
                core_color = self._config.active_color

            pygame.draw.rect(
                self._working_surface, 
                core_color, 
                (core_origin_x, core_origin_y, self._core_width, self._core_width)
            )

            if len(core_activity_tracking) == self._cores_per_row:
                # Move to the next row
                core_origin_y += self._core_width + self._config.core_spacing
                core_columns_drawn = 0
                core_origin_x = 0
            else:
                # Move to the next column
                core_origin_x += self._core_width + self._config.core_spacing

        #assert(len(self._last_core_activity) == len(core_activity_tracking))
        self._last_core_activity = core_activity_tracking

        if g_benchmark:
            print("BENCHMARK: CoreVisualizer: {}ms".format(pygame.time.get_ticks() - start_ticks))

        return self._working_surface, self._direct_rect
