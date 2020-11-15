#!/usr/bin/env python

import pygame

class AssetPath:
    # No trailing slashes
    fonts = "./assets/fonts"

class Color:
    yellow = "#ffff00"
    green = "#00dc00"
    dark_green = "#173828"
    red = "#dc0000"
    white = "#ffffff"
    grey_20 = "#333333"
    grey_75 = "#c0c0c0"
    black = "#000000"

class Font:
    @staticmethod
    def open_sans():
        return AssetPath.fonts + "/Open_Sans/OpenSans-Regular.ttf"

# TODO: (Adam) 2020-11-14 This is a bit of mess, could use something like Pint for slick unit handling
class Unit:
    name = ""
    symbol = ""
    alt_symbol = ""

    def __init__(self, name = "", symbol = "", alt_symbol = ""):
        self.name = name
        self.symbol = symbol
        self.alt_symbol = alt_symbol

class Units:
    null_unit = Unit()
    celsius = Unit("Celcius", "C")
    percent = Unit("Percent", "%")
    megahertz = Unit("Megahertz", "Mhz")
    megabytes = Unit("Megabytes", "MB")
    megabits = Unit("Megabits", "Mb")
    megabytes_per_second = Unit("Megabytes/sec", "MBps", "MB/s")
    megabits_per_second = Unit("Megabits/sec", "Mbps", "Mb/s")
    kilobytes = Unit("Kilobytes", "KB")
    kilobits = Unit("Kilobits", "Kb")
    kilobytes_per_second = Unit("Kilobytes/sec", "KBps", "KB/s")
    kilobits_per_second = Unit("Kilobits/sec", "Kbps", "Kb/s")
    rpm = Unit("Revolutions Per Second", "RPM")
    fps = Unit("Frames Per Second", "FPS")
    watts = Unit("Watts", "W")

class DataField:
    field_name = ""
    description = ""
    unit = Units.null_unit
    min_value = None
    caution_value = None
    warn_value = None
    max_value = None

    def __init__(
        self, field_name = "", description = "", unit = Units.null_unit,
        min_value = None, caution_value = None, warn_value = None, max_value = None):

        self.field_name = field_name
        self.description = description
        self.unit = unit
        self.min_value = min_value
        self.caution_value = caution_value
        self.warn_value = warn_value
        self.max_value = max_value

#TODO: (Adam) 2020-11-14 AIDA64 layout file is plain text, could write a converter to grab fields names
class DashData:
    cpu_util = DataField("cpu_util", "CPU Utilization", Units.percent, min_value=0, max_value=100)
    cpu_temp = DataField("cpu_temp", "CPU Temperature", Units.celsius, min_value=15, caution_value=75, max_value=80, warn_value=82)
    cpu_clock = DataField("cpu_clock", "CPU Clock", Units.megahertz, min_value=799, max_value=4500)
    cpu_power = DataField("cpu_power", "CPU Power", Units.watts, min_value=0, max_value=91)
    gpu_clock = DataField("gpu_clock", "GPU Clock", Units.megahertz, min_value=300, max_value=1770)
    gpu_util = DataField("gpu_util", "GPU Utilization", Units.percent, min_value=0, max_value=100)
    gpu_ram_used = DataField("gpu_ram_used", "GPU RAM Used", Units.megabytes, min_value=0, max_value=8192)
    gpu_power = DataField("gpu_power", "GPU Power", Units.watts, min_value=0, max_value=215)
    gpu_temp = DataField("gpu_temp", "GPU Temperature", Units.celsius, min_value=15, caution_value=75, max_value=80, warn_value=88)
    gpu_perfcap_reason = DataField("gpu_perfcap_reason", "GPU Performance Cap Reason")
    sys_ram_used = DataField("sys_ram_used", "System RAM Used", Units.megabytes, min_value=0, caution_value=30000, max_value=32768)
    nic1_download_rate = DataField("nic1_download_rate", "NIC1 Download Rate", Units.kilobytes_per_second)
    nic1_upload_rate = DataField("nic1_upload_rate", "NIC2 Upload Rate", Units.kilobytes_per_second, min_value=0, max_value=1000000)
    cpu_fan = DataField("cpu_fan", "CPU Fan Speed", Units.rpm, min_value=0, max_value=1500)
    cpu_opt_fan = DataField("cpu_opt_fan", "CPU OPT Fan Speed", Units.rpm, min_value=0, max_value=1500)
    chassis_1_fan = DataField("chassis_1_fan", "Chassis 1 Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    chassis_2_fan = DataField("chassis_2_fan", "Chassis 2 Fan Speed", Units.rpm, warn_value=300,min_value=400, max_value=2000)
    chassis_2_fan = DataField("chassis_3_fan", "Chassis 3 Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    gpu_fan = DataField("gpu_fan", "GPU Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    gpu_2_fan = DataField("gpu_2_fan", "GPU Fan Speed?", Units.rpm, min_value=0, max_value=2000)
    desktop_resolution = DataField("desktop_resolution", "Desktop Display Resolution")
    desktop_refresh_rate = DataField("vertical_refresh_rate", "Display Vertical Refresh Rate")
    motherboard_temp = DataField("motherboard_temp", "Motherboard Temperature", Units.celsius, min_value=15, caution_value=50, max_value=60, warn_value=62)
    rtss_fps = DataField("rtss_fps", "Frames Per Second", Units.fps, min_value=0, max_value=60) #Capping at desired max 'cuz slow monitor
    disk_1_activity = DataField("disk_1_activity", "Disk 1 Activity", Units.percent, min_value=0, max_value=100)
    disk_2_activity = DataField("disk_2_activity", "Disk 2 Activity", Units.percent, min_value=0, max_value=100)
    disk_3_activity = DataField("disk_3_activity", "Disk 3 Activity", Units.percent, min_value=0, max_value=100)
    disk_4_activity = DataField("disk_4_activity", "Disk 4 Activity", Units.percent, min_value=0, max_value=100)
    cpu1_util = DataField("cpu1_util", "CPU Core 1 Utilization", Units.percent, min_value=0, max_value=100)
    cpu2_util = DataField("cpu2_util", "CPU Core 2 Utilization", Units.percent, min_value=0, max_value=100)
    cpu3_util = DataField("cpu3_util", "CPU Core 3 Utilization", Units.percent, min_value=0, max_value=100)
    cpu4_util = DataField("cpu4_util", "CPU Core 4 Utilization", Units.percent, min_value=0, max_value=100)
    cpu5_util = DataField("cpu5_util", "CPU Core 5 Utilization", Units.percent, min_value=0, max_value=100)
    cpu6_util = DataField("cpu6_util", "CPU Core 6 Utilization", Units.percent, min_value=0, max_value=100)
    cpu7_util = DataField("cpu7_util", "CPU Core 7 Utilization", Units.percent, min_value=0, max_value=100)
    cpu8_util = DataField("cpu8_util", "CPU Core 8 Utilization", Units.percent, min_value=0, max_value=100)


class DashboardPainter:

    def paint(data, display_surface):

        display_surface.fill(Color.black)
        
        font_name, font_size = Font.open_sans(), 32
        font = pygame.font.SysFont(font_name, font_size)

        text_surface = font.render(
            DashData.cpu_temp.description + ": {}".format(data[DashData.cpu_temp.field_name]) + DashData.cpu_temp.unit.symbol, 
            True, Color.yellow, None
        )
        display_surface.blit(text_surface, (10, 10))

        text_surface = font.render(
            DashData.cpu_util.description + ": {}".format(data[DashData.cpu_util.field_name]) + DashData.cpu_util.unit.symbol,
            True, Color.yellow, None
        )
        display_surface.blit(text_surface, (10, 40))
