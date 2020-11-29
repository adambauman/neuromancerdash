#
# units - contains classes that describe dashboard data units
# ===========================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

# TODO: (Adam) 2020-11-14 This is a bit of mess, could use something like Pint for slick unit handling
class Unit:
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