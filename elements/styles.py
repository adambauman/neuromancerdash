#
# styles - various style elements that are uniform across the project
# ===================================================================
#
# Author: Adam J. Bauman (https://gist.github.com/adambauman)
#

class Color:
    yellow = "#ffff00"
    green = "#00dc00"
    dark_green = "#173828"
    red = "#dc0000"
    white = "#ffffff"
    grey_20 = "#333333"
    grey_40 = "#666666"
    grey_75 = "#c0c0c0"
    black = "#000000"
    cyan_dark = "#1c2f2b"
    # Colors pulled from Win10 design doc swatches
    windows_cyan_1 = "#00b693"
    windows_cyan_1_dark = "#015b4a"
    windows_cyan_2 = "#008589"
    windows_red_1 = "#eb2400"
    windows_dkgrey_1_highlight = "#b3aeaa"
    windows_dkgrey_1 = "#4c4a48"
    windows_light_grey_1 = "#7b7574"
    hot_pink = "#f542ce"

class AssetPath:
    # No trailing slashes
    fonts = "assets/fonts"
    gauges = "assets/images/gauges"
    graphs = "assets/images/graphs"
    misc = "assets/images/misc"
    backgrounds = "assets/images/backgrounds"
    icons = "assets/images/icons"

class FontPaths:
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
