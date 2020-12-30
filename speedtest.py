import os
import pygame, pygame.freetype
import sys, getopt
#from collections import deque
#import threading

# Set true to benchmark various parts of the update process
g_benchmark = True

from data.aida64lcdsse import AIDA64LCDSSE
from data.dataobjects import DashData, DataField
from elements.styles import Color
from elements.gauge import FlatArcGauge, GaugeConfig

class Hardware:
    screen_size = (480, 320)

def print_usage():
    print("")
    print("Usage: neuromancer_dash.py <options>")
    print("Example: python3 neuromancer_dash.py --aidasse http://localhost:8080/sse")
    print("")
    print("       Required Options:")
    print("           --aidasse <full http address:port to AIDA64 LCD SSE stream>")

def get_command_args(argv):
    aida_sse_server = None
    gpio_enabled = True

    try:
        opts, args = getopt.getopt(argv,"aidasse:",["aidasse=", ])

    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("--aidasse"):
            aida_sse_server = arg

    if (aida_sse_server is None):
        print_usage()
        sys.exit()

    return aida_sse_server


class SimDataItem:
    def __init__(self, starting_value, min_value, max_value, steps_per_update=1, reversible=True):
        assert(min_value < max_value)
        self.current_value = starting_value
        self.min_value = min_value
        self.max_value = max_value
        self._steps_per_update = steps_per_update
        self._reversible = reversible
        self._is_reversing = False

    def step(self):
        next_value = self.current_value
        if self._is_reversing:
            next_value -= self._steps_per_update
            if next_value < self.min_value:
                self._is_reversing = False
                self.current_value = self.min_value
            else:
                self.current_value = next_value
        else:
            next_value += self._steps_per_update
            if next_value > self.max_value:
                if self._reversible:
                    self._is_reversing = True
                    self.current_value = self.max_value
                else:
                    self.current_value = 0
            else:
                self.current_value = next_value

        return self.current_value


class SimulatedAida64Data:
    def __init__(self):
        self.cpu_util = SimDataItem(DashData.cpu_util.min_value, DashData.cpu_util.min_value, DashData.cpu_util.max_value)
        self.cpu_temp = SimDataItem(DashData.cpu_temp.min_value, DashData.cpu_temp.min_value, DashData.cpu_temp.max_value)

    def get_update(self):
        sim_data = {}
        sim_data[DashData.cpu_util.field_name] = self.cpu_util.step()
        sim_data[DashData.cpu_temp.field_name] = self.cpu_temp.step()
        return sim_data


def main(argv):
    aida_sse_server = get_command_args(argv)
    assert(aida_sse_server is not None)

    if __debug__:
        print("Passed arguments:")
        print("    aidasse = {}".format(aida_sse_server))

    pygame.init()
    pygame.freetype.init()
    pygame.mixer.quit() # Mixer not required, avoids ALSA overrun error messages as well
    pygame.mouse.set_visible(False)

    surface_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    display_surface = pygame.display.set_mode(Hardware.screen_size, surface_flags)

    if __debug__:
        display_info = pygame.display.Info()
        print("pygame started display started. driver: {}, display_info: \n{}".format(pygame.display.get_driver(), display_info))

    display_surface.fill(Color.black)
    pygame.display.flip()

    cpu_temp_gauge_config = GaugeConfig(DashData.cpu_temp, 45, value_font_size=16, value_font_origin=(35, 70))
    cpu_temp_gauge_config.draw_unit_symbol = False
    cpu_temp_gauge_rect = pygame.Rect(100, 7, 90, 90)
    cpu_temp_gauge = FlatArcGauge(
        cpu_temp_gauge_config,
        display_surface, cpu_temp_gauge_rect)

    simulated_data = SimulatedAida64Data()

    ############
    ## Main Loop
    ############

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit")
                pygame.quit()
                sys.exit()
            pygame.event.clear()

        aida64_data = simulated_data.get_update()

        if g_benchmark:
            draw_start_ticks = pygame.time.get_ticks()
  
        update_rects = []
        cpu_temperature_value = DashData.best_attempt_read(aida64_data, DashData.cpu_temp, "0")
        update_rects.append(cpu_temp_gauge.draw_update(cpu_temperature_value)[1])

        pygame.display.update(update_rects)

        if g_benchmark:
            # Pre-optimizaiton Arc Guage on Pi zero: ~16ms
            print("BENCHMARK: Draw: {}ms".format(pygame.time.get_ticks() - draw_start_ticks))

        pygame.time.wait(16)

    ############
    ## Main Loop
    ############


    pygame.quit()

if __name__ == "__main__":
    command_arguments = sys.argv[1:]

    # Saves headaches when debugging in VS2019
    if __debug__ and 0 == len(command_arguments):
        print("No command arguments passed and in debug, using http://localhost:8080/sse")
        command_arguments = ['--aidasse', 'http://localhost:8080/sse']

    main(command_arguments)
