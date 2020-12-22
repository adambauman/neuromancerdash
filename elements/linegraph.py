#
# linegraph - line graph element drawing
# ======================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame
import os

from .styles import Color, AssetPath
from .helpers import Helpers

# Set true to benchmark the update process
g_benchmark = False

class LineGraphConfig:
    def __init__(self, height, width, data_field):
        self.height, self.width = height, width
        self.plot_padding = 0
        self.data_field = data_field
        self.steps_per_update = 6
        self.line_color = Color.yellow
        self.line_width = 1
        self.vertex_color = Color.yellow
        self.vertex_weight = 1
        self.draw_vertices = False
        self.display_background = False
        self. draw_on_zero = True

class LineGraphReverse:
    # Simple line graph that plots data from right to left

    _last_plot_y = 0
    _last_plot_surface = None
    _config = None
    _working_surface = None
    _cropped_background = None
    _direct_rect = None

    def __init__(self, line_graph_config, direct_surface=None, direct_rect=None, surface_flags=0):
        assert(line_graph_config.height != 0 and line_graph_config.width != 0)
        assert(None != line_graph_config.data_field)
        
        self._config = line_graph_config

        if None != direct_surface and None != direct_rect:
            self._working_surface = direct_surface.subsurface(direct_rect)
            self._direct_rect = direct_rect
        else:
            self._working_surface = pygame.Surface((self._config.width, self._config.height), surface_flags)

        plot_width = self._config.width - (self._config.plot_padding * 2)
        plot_height = self._config.height - (self._config.plot_padding * 2)
        self._last_plot_surface = pygame.Surface((self._config.width, self._config.height), surface_flags)
        
        steps_per_update = self._config.steps_per_update
        self._last_plot_y = self._last_plot_surface.get_height()

        if self._config.display_background:
            # Only store what we need for grid
            # TODO: Could probably just tile a slice of the grid BG
            full_background = pygame.image.load(os.path.join(AssetPath.graphs, "grid_cyan_dots.png")).convert_alpha()
            self._cropped_background = pygame.Surface((self._config.width, self._config.height), surface_flags)
            self._cropped_background.blit(full_background, (0, 0))

        # TODO: Fix bug where grid is not fully visible until the updates reach the left-most edge

    # TODO: Go through LineGraphReverse and give it a good scrubbing
    def update(self, value):
        assert(None != self._config)
        assert(None != self._last_plot_surface)
        assert(None != self._working_surface)

        # If provided this function will copy the final element into return_surface instead of returning it

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # Clear working surface
        if self._cropped_background is not None:
            self._working_surface.blit(self._cropped_background, (0, 0))
        else:
            self._working_surface.fill((0,0,0,0))

        # Transform self._previous_plot_surface left by self._steps_per_update
        steps_per_update = self._config.steps_per_update
        last_plot_position = (self._working_surface.get_width() - steps_per_update, self._last_plot_y)

        # Calculate self._previous_plot_position lefy by self._steps_per_update, calculate new plot position
        data_field = self._config.data_field
        transposed_value = Helpers.transpose_ranges(
            float(value), 
            data_field.max_value, data_field.min_value, 
            self._working_surface.get_height(), 0
        )

        plot_padding = self._config.plot_padding
        new_plot_y = int(self._working_surface.get_height() - transposed_value)

        # Clamp the reanges in case something rounds funny
        if self._config.line_width >= new_plot_y:
            new_plot_y = self._config.line_width
        if (self._working_surface.get_height() - self._config.line_width) <= new_plot_y:
            new_plot_y = self._working_surface.get_height() - self._config.line_width

        new_plot_position = (self._working_surface.get_width() - plot_padding, new_plot_y)

        # Save values for the next update
        self._last_plot_y = new_plot_y

        # Blit down self._last_plot_surface and shift to the left by self._steps_per_update, draw the new line segment
        plot_surface_width = self._last_plot_surface.get_width()
        plot_surface_height = self._last_plot_surface.get_height()
        new_plot_surface = pygame.Surface((plot_surface_width, plot_surface_height), pygame.SRCALPHA)

        # Copy down the previous surface but shifted left. TODO: Mess with scroll some more
        new_plot_surface.blit(self._last_plot_surface, (-steps_per_update, 0))

        enable_draw = True
        if 0 == int(value) and self._config.draw_on_zero == False:
            enable_draw = False

        if enable_draw:
            pygame.draw.line(
                new_plot_surface,
                self._config.line_color,
                last_plot_position, new_plot_position,
                self._config.line_width
            )

            # Draw vertex if enabled
            if self._config.draw_vertices:
                pygame.draw.circle(
                    new_plot_surface,
                    self._config.vertex_color,
                    last_plot_position,
                    1 * self._config.vertex_weight
                )

        self._working_surface.blit(new_plot_surface, (plot_padding, plot_padding))

        # Save values for the next update
        self._last_plot_surface = new_plot_surface.copy()

        if g_benchmark:
            print("BENCHMARK: LineGraph {}: {}ms".format(self._config.data_field.field_name, pygame.time.get_ticks() - start_ticks))


        return self._working_surface, self._direct_rect
