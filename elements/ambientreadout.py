#
# ambientreadout - displays for ambient environment data
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from .styles import Color, FontPaths, AssetPath
from .helpers import Helpers

class DynamicItem:
    previous_value = None

    def __init__(self, origin, rect, color, font, value=None):
        self.origin = origin # Yes, required even with the rect!
        self.rect = rect
        self.color = color
        self.font = font
        self.previous_value = value


class FontCollection:
    def __init__(self):
        # Setup fonts
        self.normal = pygame.freetype.Font(FontPaths.fira_code_semibold(), 12)
        self.normal.kerning = True
        #self.normal.strong = True

        self.large = pygame.freetype.Font(FontPaths.fira_code_semibold(), 24)
        #self.large.strong = True

        self.small = pygame.freetype.Font(FontPaths.fira_code_semibold(), 8)

class TemperatureHumidity:
    __dynamic_items = {}
    __first_update = True

    def __init__(self):
        # TODO: Pass a configuration in, could open sizing, font selection, colors, etc. to 
        #       customization.

        # TODO: Figure out that initial surface sizing
        self.__working_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.__working_surface.fill((0, 0, 0, 0))
        self.__fonts = FontCollection()

    def __get_next_vertical_stack_origin__(self, last_origin, font, padding = 0):
        x = last_origin[0]
        y = last_origin[1] + font.get_sized_height() + padding
        return (x,y)

    def __draw_first__(self, dht22_data):
        assert(None != dht22_data)

        # Fudges spacing a bit for tighter appearance
        stack_y_offset = -2

        # Temperature static label
        origin = (0, 0)
        self.__fonts.normal.render_to(self.__working_surface, origin, "Room Temp", Color.white)

        # Temperature value
        origin = self.__get_next_vertical_stack_origin__(origin, self.__fonts.normal, stack_y_offset)
        text = "{:0.1f}".format(dht22_data.temperature) + u"\u00b0" + "F"
        rendered_rect = self.__fonts.normal.render_to(self.__working_surface, origin, text, Color.white)
        # Save temperature dynamic area
        self.__dynamic_items["temperature"] = DynamicItem(origin, rendered_rect, Color.white, self.__fonts.normal, dht22_data.temperature)

        # Humidity static label
        origin = self.__get_next_vertical_stack_origin__(origin, self.__fonts.normal, stack_y_offset)
        text = "Humidity"
        self.__fonts.normal.render_to(self.__working_surface, origin, text, Color.white)

        # Humidity value
        origin = self.__get_next_vertical_stack_origin__(origin, self.__fonts.normal, stack_y_offset)
        text = "{:0.1f}".format(dht22_data.humidity) + "%"
        rendered_rect = self.__fonts.normal.render_to(self.__working_surface, origin, text, Color.white)
        # Save humidity dynamic area
        self.__dynamic_items["humidity"] = DynamicItem(origin, rendered_rect, Color.white, self.__fonts.normal, dht22_data.humidity)


    def update(self, dht22_data):
        assert(None != dht22_data)

        # On the first update we need to draw the static elements and store information for dynamic areas
        if self.__first_update:
            self.__draw_first__(dht22_data)
            self.__first_update = False
            return self.__working_surface
       
        # After the first run we'll only update the dynamic areas
        assert(0 != len(self.__dynamic_items))

        # Temperature
        dynamic_temp = self.__dynamic_items["temperature"]
        if dht22_data.temperature != dynamic_temp.previous_value:
            if __debug__:
                print("Redrawing ambient temperature...")

            text = "{:0.1f}".format(dht22_data.temperature) + u"\u00b0" + "F"
            rendered_rect = dynamic_temp.font.render_to(self.__working_surface, dynamic_temp.origin, text, dynamic_temp.color)
            # Update so we can erase the old text on the next update
            # TODO: Testing how reference works here, streamline if the debug stuff actually updates
            if __debug__:
                print("Old self dynamic rect: {}".format(self.__dynamic_items["temperature"].rect))
                dynamic_temp.rect = rendered_rect
                print("New self dynamic rect: {}".format(self.__dynamic_items["temperature"].rect))

            self.__dynamic_items["temperature"].rect = rendered_rect
            self.__dynamic_items["temperature"].previous_value = dht22_data.temperature



        return self.__working_surface

            