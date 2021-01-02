#
# linegraph - line graph element drawing
# ======================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame
import os
from collections import deque

from .styles import Color, AssetPath
from .helpers import Helpers

# Set true to benchmark the update process
g_benchmark = False

class LineGraphConfig:
    def __init__(self, data_field, size=None):
        self.size = size
        self.plot_vertical_padding = 1
        self.data_field = data_field
        self.steps_per_update = 5
        self.line_color = Color.yellow
        self.line_width = 1
        self.display_background = False
        self.draw_on_zero = True

class LineGraphReverse:
    working_surface = None
    base_rect = None

    def __init__(self, line_graph_config, direct_surface=None, direct_rect=None, surface_flags=0):
        assert((0, 0) != line_graph_config.size)

        self._config = line_graph_config
        self._surface_flags = surface_flags
        if direct_surface and direct_rect:
            self.working_surface = direct_surface.subsurface(direct_rect)
            self.base_rect = direct_rect
        else:
            assert(self._config.size)
            self.working_surface = pygame.Surface(self._config.size, self._surface_flags)
            self.base_rect = pygame.Rect((0, 0), self._config.size)

        self._background = None
        if self._config.display_background:
            self._background = pygame.image.load(os.path.join(AssetPath.graphs, "grid_cyan_dots.png")).convert()

        # Built a plotting area that accounts for padding and the line width
        plot_x = self._config.plot_vertical_padding
        plot_y = self._config.plot_vertical_padding + self._config.line_width
        plot_width = self.working_surface.get_width() - (self._config.plot_vertical_padding * 2)
        plot_height = self.working_surface.get_height() - (self._config.plot_vertical_padding * 2) - (self._config.line_width)
        self._plot_area = pygame.Rect(plot_x, plot_y, plot_width, plot_height)

        plot_queue_length = int(self.working_surface.get_width() / self._config.steps_per_update)
        self._plot_points = deque([], maxlen=plot_queue_length)
        self._plot_points.append((plot_width, plot_height))

    def __shift_plots__(self):
        assert(self._plot_points)

        # Shift each point's X to the left
        for index in range(len(self._plot_points)):
            self._plot_points[index] = (self._plot_points[index][0] - self._config.steps_per_update, self._plot_points[index][1])

        # First point will be out of the working area, pop it
        if 0 > (self._plot_points[0][0] - self._config.steps_per_update):
            self._plot_points.popleft()

    def set_direct_draw(self, direct_surface, direct_rect):
        # Draw element directly to a subsurface of the direct_surface
        assert(direct_surface)
        assert((0, 0) != direct_rect.size)

        self.working_surface = direct_surface.subsurface(direct_rect)
        self.base_rect = direct_rect

    def draw_update(self, value):
        assert(self.working_surface)
        assert(self._config)
        assert(self._plot_area)

        # Clear the working surface
        if self._background:
            self.working_surface.blit(self._background, (0, 0))
        else:
            self.working_surface.fill(0, 0, 0, 0)

        # Prepare plot points by shifting them left by steps_per_update
        self.__shift_plots__()

        # Transpose value into graph space, plot min/max reversed
        data_field = self._config.data_field
        plot_y = self._plot_area[1]
        plot_height = self._plot_area[3]
        transposed_value = Helpers.transpose_ranges(
            float(value), 
            data_field.max_value, data_field.min_value, 
            plot_y, plot_height)

        # Append new plot point with transposed value as Y
        self._plot_points.append((self.working_surface.get_width(), transposed_value))

        # Skip drawing on zero, send None as base_rect to avoid unecessary update
        if 0 == int(value) and not self._config.draw_on_zero:
            return None

        pygame.draw.lines(
            self.working_surface, self._config.line_color, False, self._plot_points, self._config.line_width)

        return self.base_rect
