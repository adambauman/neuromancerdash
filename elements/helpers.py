#
# helpers - various helper methods to support element drawing
# ===========================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

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
