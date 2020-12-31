#
# styles - various style elements that are uniform across the project
# ===================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

class Color:
    yellow = (255, 255, 0, 255)
    green = (0, 220, 0, 255)
    dark_green = (23, 56, 40, 255)
    red = (220, 0, 0, 255)
    white = (255, 255, 255, 255)
    grey_20 = (51, 51, 51, 255)
    grey_40 = (102, 102, 102, 255)
    grey_75 = (192, 192, 192, 255)
    black = (0, 0, 0, 255)
    cyan_dark = (28, 47, 43, 255)
    # Colors pulled from Win10 design doc swatches
    windows_cyan_1 = (0, 182, 147, 255)
    windows_cyan_1_medium = (0, 165, 133, 255)
    windows_cyan_1_dark = (1, 91, 74, 255)
    windows_cyan_2 = (0, 133, 137, 255)
    windows_red_1 = (235, 36, 0, 255)
    windows_red_1_bright = (255, 39, 0, 255)
    windows_red_1_medium = (197, 30, 0, 255)
    windows_red_1_dark = (165, 25, 0, 255)
    windows_dkgrey_1_highlight = (179, 174, 170, 255)
    windows_dkgrey_1 = (76, 74, 72, 255)
    windows_light_grey_1 = (123, 117, 116, 255)
    hot_pink = (245, 66, 206, 255)

class AssetPath:
    # No trailing slashes
    fonts = "assets/fonts"
    gauges = "assets/images/gauges"
    graphs = "assets/images/graphs"
    misc = "assets/images/misc"
    backgrounds = "assets/images/backgrounds"
    icons = "assets/images/icons"
    hardware = "assets/images/hardware"

class FontPath:
    # TODO: (Adam) 2020-11-15 Use os.path.join instead of string concact
    @staticmethod
    def open_sans_regular():
        return AssetPath.fonts + "/Open_Sans/OpenSans-Regular.ttf"
    def open_sans_semibold():
        return AssetPath.fonts + "/Open_Sans/OpenSans-SemiBold.ttf"
    def dm_sans_medium():
        return AssetPath.fonts + "/DM_Sans/DMSans-Medium.ttf"
    def goldman_regular():
        return AssetPath.fonts + "/Goldman/Goldman-Regular.ttf"
    def fira_code_variable():
        return AssetPath.fonts + "/Fira_Code/FiraCode-VariableFont_wght.ttf"
    def fira_code_semibold():
        return AssetPath.fonts + "/Fira_Code/static/FiraCode-SemiBold.ttf"
