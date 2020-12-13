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

    __last_plot_y = 0
    __last_plot_surface = None
    __config = None
    __working_surface = None
    __background = None

    def __init__(self, line_graph_config, surface_flags=0):
        assert(line_graph_config.height != 0 and line_graph_config.width != 0)
        assert(None != line_graph_config.data_field)
        
        self.__config = line_graph_config

        self.__working_surface = pygame.Surface((self.__config.width, self.__config.height), surface_flags)

        plot_width = self.__config.width - (self.__config.plot_padding * 2)
        plot_height = self.__config.height - (self.__config.plot_padding * 2)
        self.__last_plot_surface = pygame.Surface((self.__config.width, self.__config.height), surface_flags)
        
        steps_per_update = self.__config.steps_per_update
        self.__last_plot_y = self.__last_plot_surface.get_height()

        if self.__config.display_background:
            self.__background = pygame.image.load(os.path.join(AssetPath.graphs, "grid_8px_dkcyan.png"))
            self.__working_surface.blit(self.__background, (0, 0))

        # TODO: Fix bug where grid is not fully visible until the updates reach the left-most edge


    def update(self, value):
        assert(None != self.__config)
        assert(None != self.__last_plot_surface)
        assert(None != self.__working_surface)

        if g_benchmark:
            start_ticks = pygame.time.get_ticks()

        # Clear working surface
        if None != self.__background:
            self.__working_surface.blit(self.__background, (0, 0))
        else:
            self.__working_surface.fill(Color.black)

        # Transform self.__previous_plot_surface left by self.__steps_per_update
        steps_per_update = self.__config.steps_per_update
        last_plot_position = (self.__working_surface.get_width() - steps_per_update, self.__last_plot_y)

        # Calculate self.__previous_plot_position lefy by self.__steps_per_update, calculate new plot position
        data_field = self.__config.data_field
        transposed_value = Helpers.transpose_ranges(
            float(value), 
            data_field.max_value, data_field.min_value, 
            self.__working_surface.get_height(), 0
        )

        plot_padding = self.__config.plot_padding
        new_plot_y = int(self.__working_surface.get_height() - transposed_value)

        # Clamp the reanges in case something rounds funny
        if self.__config.line_width >= new_plot_y:
            new_plot_y = self.__config.line_width
        if (self.__working_surface.get_height() - self.__config.line_width) <= new_plot_y:
            new_plot_y = self.__working_surface.get_height() - self.__config.line_width

        new_plot_position = (self.__working_surface.get_width() - plot_padding, new_plot_y)

        # Save values for the next update
        self.__last_plot_y = new_plot_y

        # Blit down self.__last_plot_surface and shift to the left by self.__steps_per_update, draw the new line segment
        plot_surface_width = self.__last_plot_surface.get_width()
        plot_surface_height = self.__last_plot_surface.get_height()
        new_plot_surface = pygame.Surface((plot_surface_width, plot_surface_height), pygame.SRCALPHA)

        # Copy down the previous surface but shifted left. TODO: Mess with scroll some more
        new_plot_surface.blit(self.__last_plot_surface, (-steps_per_update, 0))

        enable_draw = True
        if 0 == int(value) and self.__config.draw_on_zero == False:
            enable_draw = False

        if enable_draw:
            pygame.draw.line(
                new_plot_surface,
                self.__config.line_color,
                last_plot_position, new_plot_position,
                self.__config.line_width
            )

            # Draw vertex if enabled
            if self.__config.draw_vertices:
                pygame.draw.circle(
                    new_plot_surface,
                    self.__config.vertex_color,
                    last_plot_position,
                    1 * self.__config.vertex_weight
                )

        self.__working_surface.blit(new_plot_surface, (plot_padding, plot_padding))

        # Save values for the next update
        self.__last_plot_surface = new_plot_surface.copy()

        if g_benchmark:
            print("BENCHMARK: LineGraph {}: {}ms".format(self.__config.data_field.field_name, pygame.time.get_ticks() - start_ticks))

        # Return completed working surface
        return self.__working_surface
