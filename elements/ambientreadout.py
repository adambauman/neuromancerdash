#
# ambientreadout - displays for ambient environment data
# =============================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

import pygame

from .styles import Color, FontPaths, AssetPath
from .helpers import Helpers

class DynamicField:
    def __init__(self, origin, subsurface, text, text_color, font, value=None):
        # Will be an updatable subsurface of the working surface
        self.__subsurface = subsurface 
        self.__text_color = text_color
        self.__font = font
        self.__origin = origin
        self.__text = text

        self.value = value

    def update(self, new_value):
        # TODO: Find a way to preserve alpha all the way down to the display surface
        #       in case you want a cool background picture or color behind your data
        #       displays.
        self.__subsurface.fill(Color.black)
        render_text = self.__text.format(new_value)
        self.__font.render_to(self.__subsurface, (0,0), render_text, Color.white)
        self.value = new_value
        # No need to return subsurface, it update it's slice of the working surface

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
    __temperature_field = None
    __humidity_field = None

    def __init__(self):
        # TODO: Pass a configuration in, could open sizing, font selection, colors, etc. to 
        #       customization. Also take background surface to handle transparency over anything that
        #       isn't just black fill

        # TODO: Figure out that initial surface sizing
        self.__working_surface = pygame.Surface((70, 60), pygame.SRCALPHA)
        self.__working_surface.fill(Color.black)
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

        # Temperature value and field setup
        origin = self.__get_next_vertical_stack_origin__(origin, self.__fonts.normal, stack_y_offset)
        subsurface_rect = pygame.Rect(origin[0], origin[1], self.__working_surface.get_width(), self.__fonts.normal.get_sized_height())
        text = "{:0.1f}\u00b0F" # TODO also take celcius, do the conversion in here instead of DHT22data
        self.__temperature_field = DynamicField(
            origin, self.__working_surface.subsurface(subsurface_rect),
            text, Color.white, self.__fonts.normal)
        self.__temperature_field.update(dht22_data.temperature)

        ## Humidity static label
        origin = self.__get_next_vertical_stack_origin__(origin, self.__fonts.normal, stack_y_offset)
        self.__fonts.normal.render_to(self.__working_surface, origin, "Humidity", Color.white)

        ## Humidity value and field setup
        origin = self.__get_next_vertical_stack_origin__(origin, self.__fonts.normal, stack_y_offset)
        subsurface_rect = pygame.Rect(origin[0], origin[1], self.__working_surface.get_width(), self.__fonts.normal.get_sized_height())
        text = "{:0.1f}%"
        # Save humidity dynamic area
        # Stretch width of our rendered rect to us the whole "row"
        self.__humidity_field = DynamicField(
            origin, self.__working_surface.subsurface(subsurface_rect),
            text, Color.white, self.__fonts.normal)
        self.__humidity_field.update(dht22_data.humidity)


    def update(self, dht22_data):
        assert(None != dht22_data)

        # On the first update we need to draw the static elements and store information for dynamic areas
        if None == self.__temperature_field or None == self.__humidity_field:
            self.__draw_first__(dht22_data)
            return self.__working_surface

        # Temperature
        if dht22_data.temperature != self.__temperature_field.value:
            if __debug__:
                print("Redrawing ambient temperature...")
            self.__temperature_field.update(dht22_data.temperature)

        if dht22_data.humidity != self.__humidity_field.value:
            if __debug__:
                print("Redrawing ambient humidity...")
            self.__humidity_field.update(dht22_data.humidity)

        return self.__working_surface

            