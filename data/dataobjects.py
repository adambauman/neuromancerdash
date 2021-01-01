#
# dataobjects - contains various classes used to hold dashboard data
# ==================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

from .units import Unit, Units

class DataField:
    def __init__(
        self, field_name="", description="", unit = Units.null_unit,
        min_value=None, caution_value=None, warn_value=None, max_value=None):

        self.field_name = field_name
        self.description = description
        self.unit = unit
        self.min_value = min_value
        self.caution_value = caution_value
        self.warn_value = warn_value
        self.max_value = max_value
#TODO: (Adam) 2020-11-14 AIDA64 layout file is plain text, could write a converter to grab fields names
#           from the client-side export file.

class DashData:
    unknown = DataField("", "Unknown", Units.null_unit)
    cpu_util = DataField("cpu_util", "CPU Utilization", Units.percent, min_value=0, max_value=100)
    cpu_temp = DataField("cpu_temp", "CPU Temperature", Units.celsius, min_value=20, caution_value=81, max_value=80, warn_value=82)
    cpu_clock = DataField("cpu_clock", "CPU Clock", Units.megahertz, min_value=799, max_value=4500)
    cpu_power = DataField("cpu_power", "CPU Power", Units.watts, min_value=0, max_value=91)
    gpu_clock = DataField("gpu_clock", "GPU Clock", Units.megahertz, min_value=300, max_value=1770)
    gpu_util = DataField("gpu_util", "GPU Utilization", Units.percent, min_value=0, max_value=100)
    gpu_ram_used = DataField("gpu_ram_used", "GPU RAM Used", Units.megabytes, min_value=0, max_value=10240)
    gpu_power = DataField("gpu_power", "GPU Power", Units.watts, min_value=0, max_value=215)
    gpu_temp = DataField("gpu_temp", "GPU Temperature", Units.celsius, min_value=20, caution_value=75, max_value=80, warn_value=88)
    gpu_perfcap_reason = DataField("gpu_perfcap_reason", "GPU Performance Cap Reason")
    sys_ram_used = DataField("sys_ram_used", "System RAM Used", Units.megabytes, min_value=0, caution_value=30000, max_value=32768)
    nic1_download_rate = DataField("nic1_download_rate", "NIC1 Download Rate", Units.kilobytes_per_second)
    nic1_upload_rate = DataField("nic1_upload_rate", "NIC2 Upload Rate", Units.kilobytes_per_second, min_value=0, max_value=1000000)
    cpu_fan = DataField("cpu_fan", "CPU Fan Speed", Units.rpm, warn_value=500, min_value=1000, max_value=1460)
    cpu_opt_fan = DataField("cpu_opt_fan", "Forward Exhaust Fan Speed", Units.rpm, warn_value=300, min_value=0, max_value=2410)
    chassis_1_fan = DataField("chassis_1_fan", "Front Intake Fan Speed", Units.rpm, warn_value=300, min_value=0, max_value=1588)
    chassis_2_fan = DataField("chassis_2_fan", "Lower Intake Fan Speed", Units.rpm, warn_value=300, min_value=0, max_value=1900)
    chassis_3_fan = DataField("chassis_3_fan", "Rear Exhaust Fan Speed", Units.rpm, warn_value=300, min_value=0, max_value=2410)
    gpu_fan = DataField("gpu_fan", "GPU Fan Speed", Units.rpm, min_value=0, max_value=3250)
    gpu_2_fan = DataField("gpu_2_fan", "GPU Fan Speed?", Units.rpm, min_value=0, max_value=3250)
    desktop_resolution = DataField("desktop_resolution", "Desktop Display Resolution")
    desktop_refresh_rate = DataField("vertical_refresh_rate", "Display Vertical Refresh Rate")
    motherboard_temp = DataField("motherboard_temp", "Motherboard Temperature", Units.celsius, min_value=15, caution_value=50, max_value=60, warn_value=62)
    rtss_fps = DataField("rtss_fps", "Frames Per Second", Units.fps, min_value=0, max_value=120)
    used_virtual_memory = DataField("used_virtual_memory", "Used Virtual Memory" ,Units.megabytes)
    gpu_used_dynamic_memory = DataField("gpu_used_dynamic_memory", "GPU Dynamic RAM Allocated", Units.megabytes)
    volts_12 = DataField("12v", "12v Rail", Units.volts, min_value=11.4, max_value=12.6)
    volts_5 = DataField("5v", Units.volts, min_value=4.75, max_value=5.25)
    volts_3_3 = DataField("3_3v", "3.3v Rail", Units.volts, min_value=3.135, max_value=3.456)
    volts_dimm = DataField("v_dimm", "Memory Voltage", Units.volts, min_value=0.5, max_value=2.0)
    volts_cpu_vid = DataField("cpu_vid", "CPU VID",Units.volts, min_value=0.60, max_value=1.26)
    volts_cpu_core = DataField("cpu_core_volts", "CPU Core Voltage", Units.volts, min_value=1.2, max_value=1.35)
    volts_gpu_core = DataField("gpu_core_volts", "GPU Core Voltage", Units.volts, min_value=0.7, max_value=1.35)
    pch_temp = DataField("pch_temp", Units.celsius, min_value=20, caution_value=50, max_value=80, warn_value=60)
    unlabeled_temp = DataField("unlabeled_temp", Units.celsius, min_value=20, caution_value=45, max_value=80, warn_value=50)
    drive_c_free = DataField("drive_c_free", "Drive C: Free Space", Units.gigabytes, min_value=0, max_value=465)
    drive_d_free = DataField("drive_d_free", "Drive D: Free Space", Units.gigabytes, min_value=0, max_value=930)
    drive_e_free = DataField("drive_e_free", "Drive E: Free Space", Units.gigabytes, min_value=0, max_value=232)
    drive_f_free = DataField("drive_f_free", "Drive F: Free Space", Units.gigabytes, min_value=0, max_value=1810)
    nvme_temp = DataField("nvme_temp", "NVME Temperature", Units.celsius, min_value=0, max_value=80, warn_value=75)

    # Iterate the following, labels in data source should be setup to be 0-indexed
    disk_activity = DataField("disk_{}_activity", "Disk {} Activity", Units.percent, min_value=0, max_value=100)
    cpu_core_utilization = DataField("cpu{}_util", "CPU Core {} Utilization", Units.percent, min_value=0, max_value=100)

    def best_attempt_read(data, data_field, default_value):
        try:
            value = data[data_field.field_name]
        except:
            value = default_value
            if __debug__:
                print("Data error: {}".format(data_field.field_name))
                #traceback.print_exc()

        return value
