#!/usr/bin/env python

import sys, getopt

from sseclient import SSEClient

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

class AIDAField:
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
    cpu_util = AIDAField("cpu_util", "CPU Utilization", Units.percent, min_value=0, max_value=100)
    cpu_temp = AIDAField("cpu_temp", "CPU Temperature", Units.celsius, min_value=15, caution_value=75, max_value=80, warn_value=82)
    cpu_clock = AIDAField("cpu_clock", "CPU Clock", Units.megahertz, min_value=799, max_value=4500)
    cpu_power = AIDAField("cpu_power", "CPU Power", Units.watts, min_value=0, max_value=91)
    gpu_clock = AIDAField("gpu_clock", "GPU Clock", Units.megahertz, min_value=300, max_value=1770)
    gpu_util = AIDAField("gpu_util", "GPU Utilization", Units.percent, min_value=0, max_value=100)
    gpu_ram_used = AIDAField("gpu_ram_used", "GPU RAM Used", Units.megabytes, min_value=0, max_value=8192)
    gpu_power = AIDAField("gpu_power", "GPU Power", Units.watts, min_value=0, max_value=215)
    gpu_temp = AIDAField("gpu_temp", "GPU Temperature", Units.celsius, min_value=15, caution_value=75, max_value=80, warn_value=88)
    gpu_perfcap_reason = AIDAField("gpu_perfcap_reason", "GPU Performance Cap Reason")
    sys_ram_used = AIDAField("sys_ram_used", "System RAM Used", Units.megabytes, min_value=0, caution_value=30000, max_value=32768)
    nic1_download_rate = AIDAField("nic1_download_rate", "NIC1 Download Rate", Units.kilobytes_per_second)
    nic1_upload_rate = AIDAField("nic1_upload_rate", "NIC2 Upload Rate", Units.kilobytes_per_second, min_value=0, max_value=1000000)
    cpu_fan = AIDAField("cpu_fan", "CPU Fan Speed", Units.rpm, min_value=0, max_value=1500)
    cpu_opt_fan = AIDAField("cpu_opt_fan", "CPU OPT Fan Speed", Units.rpm, min_value=0, max_value=1500)
    chassis_1_fan = AIDAField("chassis_1_fan", "Chassis 1 Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    chassis_2_fan = AIDAField("chassis_2_fan", "Chassis 2 Fan Speed", Units.rpm, warn_value=300,min_value=400, max_value=2000)
    chassis_2_fan = AIDAField("chassis_3_fan", "Chassis 3 Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    gpu_fan = AIDAField("gpu_fan", "GPU Fan Speed", Units.rpm, warn_value=300, min_value=400, max_value=2000)
    gpu_2_fan = AIDAField("gpu_2_fan", "GPU Fan Speed?", Units.rpm, min_value=0, max_value=2000)
    desktop_resolution = AIDAField("desktop_resolution", "Desktop Display Resolution")
    desktop_refresh_rate = AIDAField("vertical_refresh_rate", "Display Vertical Refresh Rate")
    motherboard_temp = AIDAField("motherboard_temp", "Motherboard Temperature", Units.celsius, min_value=15, caution_value=50, max_value=60, warn_value=62)
    rtss_fps = AIDAField("rtss_fps", "Frames Per Second", Units.fps, min_value=0, max_value=60) #Capping at desired max 'cuz slow monitor
    disk_1_activity = AIDAField("disk_1_activity", "Disk 1 Activity", Units.percent, min_value=0, max_value=100)
    disk_2_activity = AIDAField("disk_2_activity", "Disk 2 Activity", Units.percent, min_value=0, max_value=100)
    disk_3_activity = AIDAField("disk_3_activity", "Disk 3 Activity", Units.percent, min_value=0, max_value=100)
    disk_4_activity = AIDAField("disk_4_activity", "Disk 4 Activity", Units.percent, min_value=0, max_value=100)
    cpu1_util = AIDAField("cpu1_util", "CPU Core 1 Utilization", Units.percent, min_value=0, max_value=100)
    cpu2_util = AIDAField("cpu2_util", "CPU Core 2 Utilization", Units.percent, min_value=0, max_value=100)
    cpu3_util = AIDAField("cpu3_util", "CPU Core 3 Utilization", Units.percent, min_value=0, max_value=100)
    cpu4_util = AIDAField("cpu4_util", "CPU Core 4 Utilization", Units.percent, min_value=0, max_value=100)
    cpu5_util = AIDAField("cpu5_util", "CPU Core 5 Utilization", Units.percent, min_value=0, max_value=100)
    cpu6_util = AIDAField("cpu6_util", "CPU Core 6 Utilization", Units.percent, min_value=0, max_value=100)
    cpu7_util = AIDAField("cpu7_util", "CPU Core 7 Utilization", Units.percent, min_value=0, max_value=100)
    cpu8_util = AIDAField("cpu8_util", "CPU Core 8 Utilization", Units.percent, min_value=0, max_value=100)


class AIDA64SSEData:

    # TODO: (Adam) 2020-11-14 Very simple static class right now, could definitely tighten things up, use
    #       user-specified callbacks to send out data, etc.

    @staticmethod
    def __extract_single_item_data__(data):
        assert(0 != len(data))

        # Data is initially combined with the gauge type like so: Simple1|cpu_util 6
        split_type_and_item_data = data.split("|")
        assert(2 == len(split_type_and_item_data))
        assert(-1 != split_type_and_item_data[0].find("Simple")) # Derp check that we setup AIDA64 fields correctly

        # Second index will contain the actual data which is space delimited
        split_item_data = split_type_and_item_data[1].split()
        item_value = ""
        if DashData.desktop_resolution.field_name == split_item_data[0]:
            # Desktop resultion is "key, width, 'x', height"
            assert(4 == len(split_item_data)) 
            item_value = split_item_data[1] + split_item_data[2] + split_item_data[3]
        else:
            assert(2 == len(split_item_data)) # Should be key, value
            item_value = split_item_data[1]

        assert(0 != len(split_item_data[0]) and 0 !=len(item_value))

        # Return key, value
        return split_item_data[0], item_value

    @staticmethod
    def connect(server_address):
        assert(0 != len(server_address))

        print("Connecting to SSEClient \'" + server_address + "\'...")
        messages = SSEClient(server_address)
        print("Connected!")

        return messages

    @staticmethod
    def parse_data(message_data):
        assert(0 != len(message_data))

        #if __debug__:
            #print("Message data: " + message_data)

        split_message_data = message_data.split("{|}")
        assert(0 != len(split_message_data))

        # TODO: (Adam) 2020-11-14 Multi-page handling? Right now one page can fit a ton of data but it
        #       could be split into multiple pages to decrease the size of the stream packet.

        # First item should be the page name, process it seperatly
        page_name = split_message_data.pop(0)
        assert('|' == page_name[-1])
        assert(-1 != page_name.find("Page"))

        #if __debug__:
            #print("Page name: " + page_name)

        # The last item should be empty after the split, pop it
        last_item = split_message_data.pop(-1)
        assert(0 == len(last_item))

        parsed_datas = {}
        for data in split_message_data:
            key, value = AIDA64SSEData.__extract_single_item_data__(data)

            # Don't add incomplete data
            if 0 != len(key) and 0 != len(value):
                parsed_datas[key] = value
            else:
                assert(False)
                continue;

        return parsed_datas


def print_usage():
    print("\nUsage: aida64_sse_data.py --server <full http address to sse stream>\n")


def get_command_args(argv):
    server_address = None
    try:
        opts, args = getopt.getopt(argv,"server:",["server="])

    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("--server"):
            server_address = arg

    if (None == server_address):
        print_usage()
        sys.exit()

    return server_address


def main(argv):
	server_address = get_command_args(argv)
	assert(None != server_address)

	# Example usage
	messages = AIDA64SSEData.connect(server_address)
	for message in messages:
	
		# Example data response: 'Page0 | {|}Simple1|cpu_util 6 {|} Simple2|cpu_temp 32 {|}'
		# NOTE: (Adam) 2020-11-14 Message data isn't always in sync with the message? Continue looping
		#		if it wasn't receieved.
		if 0 == len(message.data) or None == message.data:
			continue

		parsed_datas = AIDA64SSEData.parse_data(message.data)

		# Draw your dashboard, process the message data, etc. 
		for key in parsed_datas:
			print(key + ": " + parsed_datas[key])

		print("\n")

	
if __name__ == "__main__":
	main(sys.argv[1:])
	