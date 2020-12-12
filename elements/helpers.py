#
# helpers - various helper methods to support element drawing
# ===========================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame
from elements.styles import Color

class Helpers:
    def calculate_center_align(parent_surface, child_surface):

        parent_center = (parent_surface.get_width() / 2, parent_surface.get_height() / 2)
        child_center = (child_surface.get_width() / 2, child_surface.get_height() / 2)
        
        child_align_x = parent_center[0] - child_center[0]
        child_align_y = parent_center[1] - child_center[1]

        return (child_align_x, child_align_y)

    def transpose_ranges(input, input_high, input_low, output_high, output_low):
        #print("transpose, input: {} iHI: {} iLO: {} oHI: {} oLO: {}".format(input, input_high, input_low, output_high, output_low))
        diff_multiplier = (input - input_low) / (input_high - input_low)
        return ((output_high - output_low) * diff_multiplier) + output_low

    def clamp_text(text, max_characters, trailing_text="..."):
        trimmed_text = text[0:max_characters]
        return trimmed_text + trailing_text

    def get_centered_origin(parent_size, child_size):
        assert(2 == len(parent_size) and 2 == len(child_size))

        #if this_position[0] > that_position[0] and this_position[1] > that_position[1]:
        #    larger_position = this_position
        #    smaller_position = that_position
        #elif that_position[0] > this_position[0] and that_position[1] > this_position[1]:
        #    larger_position = that_position
        #    smaller_position = this_position
        #else:
        #    # 'ya done messed up
        #    assert(False)

        center_x = (parent_size[0] / 2) - (child_size[0] / 2)
        center_y = (parent_size[1] / 2) - (child_size[1] / 2)

        return (center_x, center_y)

    def get_shadowed_text(font, text, text_color=Color.white, shadow_color=(0,0,0,80), shadow_offset=(2,2)):
        assert(None != font)
        assert(0 != len(text))

        # Draw temp value for sizing
        temp_render = font.render(text)
        base_size = temp_render[0].get_size()
        shadow_text_surface = pygame.Surface(
            (base_size[0] + shadow_offset[0], base_size[1] + shadow_offset[1]), 
            pygame.SRCALPHA)
        font.render_to(shadow_text_surface, shadow_offset, text, shadow_color)
        font.render_to(shadow_text_surface, (0, 0), text, text_color)

        return shadow_text_surface

    # TODO: (Adam) 2020-11-18 Switch to regex for tighter comparisons
    # TODO: (Adam) 2020-11-18 Maybe move this into the DataField class with a count method
    def is_cpu_core_utilization(key):
        # Skip combined cpu_util
        if "cpu_util" == key:
            return False

        is_match = False
        # cpu(n)_util
        if "cpu" == key[0:3] and "_util" == key[-5: ]:
            is_match = True

        return is_match

    def is_disk_activity(key):
        is_match = False
        # disk(n)_activity
        if "disk_" == key[0:3] and "_activity" == key[-9: ]:
            is_match = True
        return is_match
