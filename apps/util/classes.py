import sys, traceback
import ac
import math
import configparser
import ctypes
import os.path
import json
from apps.util.func import rgb
from html.parser import HTMLParser


class Window:
    # INITIALIZATION

    def __init__(self, name="defaultAppWindow", title="", icon=False, width=100, height=100, scale=1, texture=""):
        # local variables
        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.scale = scale
        self.x = 0
        self.y = 0
        self.last_x = 0
        self.last_y = 0
        self.is_attached = False
        self.attached_l = -1
        self.attached_r = -1

        # creating the app window
        self.app = ac.newApp(self.name)

        # default settings
        ac.drawBorder(self.app, 0)
        ac.setBackgroundOpacity(self.app, 0)
        if icon is False:
            ac.setIconPosition(self.app, 0, -10000)

        # applying settings
        ac.setTitle(self.app, "")
        ac.setBackgroundTexture(self.app, texture)
        ac.setSize(self.app, math.floor(self.width * scale), math.floor(self.height * scale))

    # PUBLIC METHODS

    def onRenderCallback(self, func):
        ac.addRenderCallback(self.app, func)
        return self

    def setBgOpacity(self, alpha):
        ac.setBackgroundOpacity(self.app, alpha)
        return self

    def showTitle(self, show):
        if show:
            ac.setTitle(self.app, self.name)
        else:
            ac.setTitle(self.app, "")
        return self

    def border(self, value):
        ac.drawBorder(self.app, value)
        return self

    def setBgTexture(self, texture):
        ac.setBackgroundTexture(self.app, texture)
        return self

    def setPos(self, x, y):
        self.x = x
        self.y = y
        ac.setPosition(self.app, self.x, self.y)
        return self

    def setLastPos(self):
        self.x = self.last_x
        self.y = self.last_y
        ac.setPosition(self.app, self.last_x, self.last_y)
        return self

    def getPos(self):
        self.x, self.y = ac.getPosition(self.app)
        return self


# -#####################################################################################################################################-#
class Value:
    def __init__(self, value=0):
        self.value = value
        self.old = value
        self.changed = False

    def setValue(self, value):
        if self.value != value:
            self.old = self.value
            self.value = value
            self.changed = True

    def hasChanged(self):
        if self.changed:
            self.changed = False
            return True
        return False


class raceGaps:
    def __init__(self, sector, time):
        self.sector = sector
        self.time = time


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]


class Colors:
    general_theme = 1  # 0 : Dark
    border_direction = 1  # 0 : Horizontal, 1 : Vertical
    theme_red = -1
    theme_green = -1
    theme_blue = -1
    theme_highlight = -1
    dataCarsClasses = []
    carsClassesLoaded = False
    theme_files = []
    current_theme = {
        'tower_time_odd_txt': rgb([0, 0, 0]),
        'tower_time_even_txt': rgb([0, 0, 0]),
        'tower_time_highlight_txt': rgb([0, 0, 0]),
        'tower_time_qualification_highlight_txt': rgb([0, 0, 0]),
        'tower_time_retired_txt': rgb([0, 0, 0]),
        'tower_time_best_lap_txt': rgb([0, 0, 0]),
        'tower_time_last_lap_txt': rgb([0, 0, 0]),
        'tower_time_place_gain_txt': rgb([0, 0, 0]),
        'tower_time_place_lost_txt': rgb([0, 0, 0]),
        'tower_time_pit_txt': rgb([0, 0, 0]),
        'tower_driver_odd_bg': rgb([0, 0, 0]),
        'tower_driver_odd_txt': rgb([0, 0, 0]),
        'tower_driver_even_bg': rgb([0, 0, 0]),
        'tower_driver_even_txt': rgb([0, 0, 0]),
        'tower_driver_highlight_odd_bg': rgb([0, 0, 0]),
        'tower_driver_highlight_even_bg': rgb([0, 0, 0]),
        'tower_driver_highlight_odd_txt': rgb([0, 0, 0]),
        'tower_driver_highlight_even_txt': rgb([0, 0, 0]),
        'tower_driver_stopped_txt': rgb([0, 0, 0]),
        'tower_driver_retired_bg': rgb([0, 0, 0]),
        'tower_driver_retired_txt': rgb([0, 0, 0]),
        'tower_position_first_bg': rgb([0, 0, 0]),
        'tower_position_first_txt': rgb([0, 0, 0]),
        'tower_position_odd_bg': rgb([0, 0, 0]),
        'tower_position_odd_txt': rgb([0, 0, 0]),
        'tower_position_even_bg': rgb([0, 0, 0]),
        'tower_position_even_txt': rgb([0, 0, 0]),
        'tower_position_highlight_odd_bg': rgb([0, 0, 0]),
        'tower_position_highlight_even_bg': rgb([0, 0, 0]),
        'tower_position_highlight_odd_txt': rgb([0, 0, 0]),
        'tower_position_highlight_even_txt': rgb([0, 0, 0]),
        'tower_position_retired_txt': rgb([0, 0, 0]),
        'tower_pit_txt': rgb([0, 0, 0]),
        'tower_pit_highlight_txt': rgb([0, 0, 0]),
        'tower_stint_lap_invalid_txt': rgb([0, 0, 0]),
        'tower_p2p_txt': rgb([0, 0, 0]),
        'tower_p2p_cooling': rgb([0, 0, 0]),
        'tower_p2p_active': rgb([0, 0, 0]),
        'tower_border_default_bg': rgb([0, 0, 0]),
        'tower_mode_title_bg': rgb([0, 0, 0]),
        'tower_mode_title_txt': rgb([0, 0, 0]),
        'tower_stint_title_bg': rgb([0, 0, 0]),
        'tower_stint_title_txt': rgb([0, 0, 0]),
        'tower_stint_tire_bg': rgb([0, 0, 0]),
        'tower_stint_tire_txt': rgb([0, 0, 0]),
        'info_driver_bg': rgb([0, 0, 0]),
        'info_driver_txt': rgb([0, 0, 0]),
        'info_driver_single_bg': rgb([0, 0, 0]),
        'info_driver_single_txt': rgb([0, 0, 0]),
        'info_split_txt': rgb([0, 0, 0]),
        'info_split_positive_txt': rgb([0, 0, 0]),
        'info_split_negative_txt': rgb([0, 0, 0]),
        'info_timing_bg': rgb([0, 0, 0]),
        'info_timing_txt': rgb([0, 0, 0]),
        'info_position_first_bg': rgb([0, 0, 0]),
        'info_position_first_txt': rgb([0, 0, 0]),
        'info_position_bg': rgb([0, 0, 0]),
        'info_position_txt': rgb([0, 0, 0]),
        'info_fastest_time_txt': rgb([0, 0, 0]),
        'info_border_default_bg': rgb([0, 0, 0]),
        'timer_title_bg': rgb([0, 0, 0]),
        'timer_title_txt': rgb([0, 0, 0]),
        'timer_title_yellow_flag_bg': rgb([0, 0, 0]),
        'timer_title_yellow_flag_txt': rgb([0, 0, 0]),
        'timer_time_bg': rgb([0, 0, 0]),
        'timer_time_txt': rgb([0, 0, 0]),
        'timer_time_yellow_flag_bg': rgb([0, 0, 0]),
        'timer_time_yellow_flag_txt': rgb([0, 0, 0]),
        'timer_pit_window_bg': rgb([0, 0, 0]),
        'timer_pit_window_txt': rgb([0, 0, 0]),
        'timer_pit_window_open_txt': rgb([0, 0, 0]),
        'timer_pit_window_done_txt': rgb([0, 0, 0]),
        'timer_pit_window_close_txt': rgb([0, 0, 0]),
        'timer_border_bg': rgb([0, 0, 0]),
        'timer_border_yellow_flag_bg': rgb([0, 0, 0]),
        'speedtrap_title_bg': rgb([0, 0, 0]),
        'speedtrap_title_txt': rgb([0, 0, 0]),
        'speedtrap_speed_bg': rgb([0, 0, 0]),
        'speedtrap_speed_txt': rgb([0, 0, 0]),
        'speedtrap_border_bg': rgb([0, 0, 0])
    }

    @staticmethod
    def theme(bg=False, reload=False, a=1):
        #if reload and Colors.general_theme == 0:
        #    Colors.export_theme_values()
        # get theme color
        if reload or Colors.theme_red < 0 or Colors.theme_green < 0 or Colors.theme_blue < 0:
            if reload and Colors.general_theme > 0:
                Colors.load_theme_values()

            cfg = Config("apps/python/prunn/", "config.ini")
            Colors.theme_red = cfg.get("SETTINGS", "red", "int")
            if Colors.theme_red < 0 or Colors.theme_red > 255:
                Colors.theme_red = 191
            Colors.theme_green = cfg.get("SETTINGS", "green", "int")
            if Colors.theme_green < 0 or Colors.theme_green > 255:
                Colors.theme_green = 0
            Colors.theme_blue = cfg.get("SETTINGS", "blue", "int")
            if Colors.theme_blue < 0 or Colors.theme_blue > 255:
                Colors.theme_blue = 0
        # return rgb([40, 152, 211], bg = bg)
        return rgb([Colors.theme_red, Colors.theme_green, Colors.theme_blue], bg=bg, a=a)

    @staticmethod
    def highlight(bg=False, reload=False):
        # get theme color
        if reload or Colors.theme_highlight < 0:
            cfg = Config("apps/python/prunn/", "config.ini")
            Colors.theme_highlight = cfg.get("SETTINGS", "tower_highlight", "int")
            if Colors.theme_highlight != 1:
                Colors.theme_highlight = 0
        if Colors.theme_highlight == 1:
            return Colors.green(bg=bg)
        return Colors.red(bg=bg)

    @staticmethod
    def loadCarClasses():
        Colors.dataCarsClasses = []
        loaded_cars = []
        for i in range(ac.getCarsCount()):
            car_name = ac.getCarName(i)
            if car_name not in loaded_cars:
                loaded_cars.append(car_name)
                file_path = "content/cars/" + car_name + "/ui/ui_car.json"
                try:
                    if os.path.exists(file_path):
                        with open(file_path) as data_file:
                            d = data_file.read().replace('\r', '').replace('\n', '').replace('\t', '')
                            data = json.loads(d)
                            for t in data["tags"]:
                                if t[0] == "#":
                                    Colors.dataCarsClasses.append({"c": car_name, "t": t[1:].lower()})
                except:
                    Log.w("Error color:" + file_path)
        Colors.carsClassesLoaded = True

    @staticmethod
    def getClassForCar(car):
        for c in Colors.dataCarsClasses:
            if c["c"] == car:
                return c["t"]
        return False

    # ------------Theme engine -----------
    @staticmethod
    def load_themes():
        Colors.theme_files = []
        theme_files = [os.path.join(root, name)
                       for root, dirs, files in os.walk("apps/python/prunn/themes/")
                       for name in files
                       if name.endswith(".ini")]
        if len(theme_files):
            for t in theme_files:
                cfg = Config(t, "")
                name = cfg.get('MAIN', 'title', 'string')
                if name == -1:
                    name = ""
                Colors.theme_files.append({"file": t, "name": name})

    @staticmethod
    def load_theme_values():
        if Colors.general_theme > 0 and len(Colors.theme_files):
            cfg = Config(Colors.theme_files[Colors.general_theme - 1]['file'], "")
            for key in Colors.current_theme:
                value = cfg.get('THEME', key, 'string')
                if value != -1:
                    # Translate value to rgba
                    Colors.current_theme[key] = Colors.txt_to_rgba(value)
                    #else default color

    @staticmethod
    def export_theme_values():
        ac.log('----------Start export theme------------')
        ac.log('[THEME]')
        for key in Colors.current_theme:
            val = getattr(Colors, key)()
            if len(val) == 4:
                ac.log(str(key) + "=" + str(round(val[0]*255)) + "," + str(round(val[1]*255)) + "," + str(round(val[2]*255)) + "," + str(val[3]))
            else:
                ac.log(str(key) + "=" + str(round(val[0]*255)) + "," + str(round(val[1]*255)) + "," + str(round(val[2]*255)) + ",1")

    @staticmethod
    def get_color_for_key(key):
        if key in Colors.current_theme:
            if Colors.current_theme[key] == "theme":
                return Colors.theme()
            return Colors.current_theme[key]
        return rgb([0, 0, 0])

    @staticmethod
    def txt_to_rgba(value):
        if value == "theme":
            return "theme"
        value_type = value.find(",")
        if value_type > 0:
            array_values = value.split(',')
            # RGB or RGBA split
            if len(array_values) == 3:
                #RGB
                return rgb([int(array_values[0]),
                            int(array_values[1]),
                            int(array_values[2])])
            if len(array_values) == 4:
                #RGBA
                return rgb([int(array_values[0]),
                            int(array_values[1]),
                            int(array_values[2])],
                           a=float(array_values[3]))
            ac.console('Error loading color :' + str(value))
            ac.log('Error loading color :' + str(value))
        value = value.lstrip('#')
        if len(value) == 6:
            # HEX RGB
            lv = len(value)
            array_values = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
            return rgb([int(array_values[0]),
                        int(array_values[1]),
                        int(array_values[2])])
        if len(value) == 8:
            # HEX ARGB
            lv = len(value)
            array_values = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
            #ac.log("HEX=" + str(array_values[1]) + "," + str(array_values[2]) + "," + str(array_values[3]) + "," + str(array_values[0]/255))
            #ac.console("HEX=" + str(array_values[1]) + "," + str(array_values[2]) + "," + str(array_values[3]) + "," + str(array_values[0]/255))
            return rgb([int(array_values[1]),
                        int(array_values[2]),
                        int(array_values[3])],
                       a=float(array_values[0]/255))
        ac.console('Error loading color :' + str(value))
        ac.log('Error loading color :' + str(value))
        return rgb([0, 0, 0])

    # --------------- Driver -------------
    @staticmethod
    def tower_first_position_different():
        if Colors.general_theme == 0:
            return True
        if Colors.tower_position_first_bg() != Colors.tower_position_odd_bg():
            return True
        return False

    @staticmethod
    def tower_time_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_time_even_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_even_txt')
        return Colors.white()

    @staticmethod
    def tower_time_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_highlight_txt')
        return Colors.white()

    @staticmethod
    def tower_time_qualification_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_qualification_highlight_txt')
        if Colors.theme_highlight == 1:
            return Colors.green()
        return Colors.red()

    @staticmethod
    def tower_time_retired_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_retired_txt')
        return rgb([168, 48, 48])

    @staticmethod
    def tower_time_best_lap_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_best_lap_txt')
        return rgb([135, 31, 144])

    @staticmethod
    def tower_time_last_lap_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_last_lap_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_time_place_gain_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_place_gain_txt')
        return rgb([32, 192, 31])

    @staticmethod
    def tower_time_place_lost_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_place_lost_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_time_pit_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_time_pit_txt')
        return Colors.yellow()

    @staticmethod
    def tower_driver_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_odd_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_driver_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_driver_even_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_even_bg')
        return rgb([32, 32, 32], a=0.58)

    @staticmethod
    def tower_driver_even_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_even_txt')
        return Colors.white()

    @staticmethod
    def tower_driver_highlight_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_highlight_odd_bg')
        return rgb([32, 32, 32], a=0.72)

    @staticmethod
    def tower_driver_highlight_even_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_highlight_even_bg')
        return rgb([32, 32, 32], a=0.58)

    @staticmethod
    def tower_driver_highlight_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_highlight_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_driver_highlight_even_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_highlight_even_txt')
        return Colors.white()

    @staticmethod
    def tower_driver_stopped_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_stopped_txt')
        return Colors.yellow()

    @staticmethod
    def tower_driver_retired_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_retired_bg')
        return Colors.white()

    @staticmethod
    def tower_driver_retired_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_driver_retired_txt')
        return rgb([112, 112, 112])

    @staticmethod
    def tower_position_first_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_first_bg')
        return rgb([192, 0, 0], a=0.62)

    @staticmethod
    def tower_position_first_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_first_txt')
        return Colors.white()

    @staticmethod
    def tower_position_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_odd_bg')
        return rgb([12, 12, 12], a=0.62)

    @staticmethod
    def tower_position_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_odd_txt')
        return Colors.white()

    @staticmethod
    def tower_position_even_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_even_bg')
        return rgb([0, 0, 0], a=0.58)

    @staticmethod
    def tower_position_even_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_even_txt')
        return Colors.white()

    @staticmethod
    def tower_position_highlight_odd_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_odd_bg')
        return rgb([255, 255, 255], a=0.96)

    @staticmethod
    def tower_position_highlight_even_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_even_bg')
        return rgb([255, 255, 255], a=0.96)

    @staticmethod
    def tower_position_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_txt')
        return Colors.red()

    @staticmethod
    def tower_position_highlight_odd_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_odd_txt')
        return Colors.red()

    @staticmethod
    def tower_position_highlight_even_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_highlight_even_txt')
        return Colors.red()

    @staticmethod
    def tower_position_retired_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_position_retired_txt')
        return rgb([112, 112, 112])

    @staticmethod
    def tower_pit_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_pit_txt')
        return rgb([225, 225, 225])

    @staticmethod
    def tower_pit_highlight_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_pit_highlight_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_stint_lap_invalid_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_lap_invalid_txt')
        return rgb([191, 0, 0])

    @staticmethod
    def tower_p2p_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_p2p_txt')
        return rgb([225, 225, 225])

    @staticmethod
    def tower_p2p_cooling():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_p2p_cooling')
        return Colors.yellow()

    @staticmethod
    def tower_p2p_active():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_p2p_active')
        return Colors.red()

    @staticmethod
    def tower_border_default_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_border_default_bg')
        return Colors.theme(a=Colors.border_opacity())

    # --------------- Tower --------------
    @staticmethod
    def tower_mode_title_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_mode_title_bg')
        return Colors.theme()

    @staticmethod
    def tower_mode_title_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_mode_title_txt')
        return Colors.white()

    @staticmethod
    def tower_stint_title_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_title_bg')
        return rgb([20, 20, 20], a=0.8)

    @staticmethod
    def tower_stint_title_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_title_txt')
        return Colors.white()

    @staticmethod
    def tower_stint_tire_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_tire_bg')
        return rgb([32, 32, 32], a=0.58)

    @staticmethod
    def tower_stint_tire_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('tower_stint_tire_txt')
        return Colors.white()

    # --------------- Info ---------------
    @staticmethod
    def info_driver_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_bg')
        #return Colors.theme()
        return rgb([20, 20, 20], a=0.8)

    @staticmethod
    def info_driver_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_txt')
        return Colors.white()

    @staticmethod
    def info_driver_single_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_single_bg')
        return rgb([20, 20, 20], a=0.8)

    @staticmethod
    def info_driver_single_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_driver_single_txt')
        return Colors.white()

    @staticmethod
    def info_split_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_split_txt')
        return Colors.white()

    @staticmethod
    def info_split_positive_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_split_positive_txt')
        return Colors.yellow()

    @staticmethod
    def info_split_negative_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_split_negative_txt')
        return Colors.green()

    @staticmethod
    def info_timing_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_timing_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def info_timing_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_timing_txt')
        return Colors.white()

    @staticmethod
    def info_position_first_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_position_first_bg')
        return rgb([192, 0, 0])

    @staticmethod
    def info_position_first_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_position_first_txt')
        return Colors.white()

    @staticmethod
    def info_position_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_position_bg')
        return rgb([112, 112, 112])

    @staticmethod
    def info_position_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_position_txt')
        return Colors.white()

    @staticmethod
    def info_fastest_time_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_fastest_time_txt')
        return Colors.white()

    @staticmethod
    def info_border_default_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('info_border_default_bg')
        return Colors.theme(a=0.64)

    # --------------- Timer ---------------
    @staticmethod
    def timer_title_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_bg')
        return Colors.theme(a=0.64)

    @staticmethod
    def timer_title_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_txt')
        return Colors.white()

    @staticmethod
    def timer_title_yellow_flag_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_yellow_flag_bg')
        return Colors.black()

    @staticmethod
    def timer_title_yellow_flag_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_title_yellow_flag_txt')
        return Colors.white()

    @staticmethod
    def timer_time_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def timer_time_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_txt')
        return Colors.white()

    @staticmethod
    def timer_time_yellow_flag_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_yellow_flag_bg')
        return Colors.yellow(True)

    @staticmethod
    def timer_time_yellow_flag_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_time_yellow_flag_txt')
        return Colors.black_txt()

    @staticmethod
    def timer_pit_window_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def timer_pit_window_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_txt')
        return Colors.white()

    @staticmethod
    def timer_pit_window_open_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_open_txt')
        return Colors.green()

    @staticmethod
    def timer_pit_window_done_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_done_txt')
        return rgb([172, 172, 172])

    @staticmethod
    def timer_pit_window_close_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_pit_window_close_txt')
        return Colors.red()

    @staticmethod
    def timer_border_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_border_bg')
        return Colors.theme(a=Colors.border_opacity())

    @staticmethod
    def timer_border_yellow_flag_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('timer_border_yellow_flag_bg')
        return Colors.black()

    # --------------- Speedtrap ---------------
    @staticmethod
    def speedtrap_title_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('speedtrap_title_bg')
        return Colors.theme(a=0.64)

    @staticmethod
    def speedtrap_title_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('speedtrap_title_txt')
        return Colors.white()

    @staticmethod
    def speedtrap_speed_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('speedtrap_speed_bg')
        return rgb([55, 55, 55], a=0.64)

    @staticmethod
    def speedtrap_speed_txt():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('speedtrap_speed_txt')
        return Colors.white()

    @staticmethod
    def speedtrap_border_bg():
        if Colors.general_theme > 0:
            return Colors.get_color_for_key('speedtrap_border_bg')
        return Colors.theme(a=0.64)

    # ----------------------------------------

    @staticmethod
    def border_opacity():
        return 0.7

    @staticmethod
    def bmw(a):
        return rgb([40, 152, 211], a=a)

    @staticmethod
    def ford(a):
        return rgb([62, 121, 218], a=a)

    @staticmethod
    def mercedes(a):
        return rgb([0, 161, 156], a=a)

    @staticmethod
    def corvette(a):
        return rgb([240, 171, 1], a=a)

    @staticmethod
    def lamborghini(a):
        return rgb([150, 191, 13], a=a)

    @staticmethod
    def ktm(a):
        return rgb([250, 88, 0], a=a)

    @staticmethod
    def nissan(a):
        return rgb([175, 71, 169], a=a)

    @staticmethod
    def ferrari(a):
        return rgb([191, 0, 0], a=a)

    @staticmethod
    def alfa(a):
        return rgb([54, 172, 68], a=a)

    @staticmethod
    def white(bg=False, a=1):
        return rgb([255, 255, 255], bg=bg, a=a)

    @staticmethod
    def black():
        return rgb([0, 0, 0], a=1)

    @staticmethod
    def black_txt():
        return rgb([12, 12, 12])

    @staticmethod
    def red(bg=False):
        return rgb([191, 0, 0], bg=bg)

    @staticmethod
    def green(bg=False):
        return rgb([32, 192, 31], bg=bg)

    @staticmethod
    def yellow_time(bg=False):
        return Colors.yellow(bg)

    @staticmethod
    def yellow(bg=False):
        return rgb([240, 171, 1], bg=bg)

    @staticmethod
    def grey(bg=False):
        return rgb([112, 112, 112], bg=bg)

    @staticmethod
    def orange(bg=False):
        return rgb([250, 88, 0], bg=bg)

    @staticmethod
    def lmp1(a):
        return rgb([205, 0, 0], a=a)

    @staticmethod
    def gte(a):
        return rgb([0, 150, 54], a=a)

    @staticmethod
    def colorFromCar(car, byclass=False, default=None):
        if default is not None and len(default) > 3:
            #get alpha from default
            alpha = default[3]
        else:
            alpha = 1
        if byclass:
            if not Colors.carsClassesLoaded:
                Colors.loadCarClasses()
            cl = Colors.getClassForCar(car)
            if cl != False:
                if cl == 'lmp1':
                    return Colors.lmp1(alpha)
                if cl == 'lmp3':
                    return Colors.nissan(alpha)
                if cl == 'proto c':
                    return rgb([0, 86, 198], a=alpha)  # blue
                if cl == 'gte-gt3':
                    return Colors.gte(alpha)
                if cl == 'gt4':
                    return Colors.ktm(alpha)
                if cl == 'suv':
                    return rgb([10, 10, 10], a=alpha)
                if cl == 'hypercars':
                    return rgb([240, 212, 0], a=alpha)
                if cl == 'hypercars r':
                    return Colors.lamborghini(alpha)
                if cl == 'supercars':
                    return rgb([97, 168, 219], a=alpha)
                if cl == 'sportscars':
                    return Colors.mercedes(alpha)
                if cl == 'vintage supercars':
                    return rgb([214, 112, 157], a=alpha)
                if cl == 'vintage gt':
                    return rgb([98, 203, 236], a=alpha)
                if cl == 'vintage touring':
                    return Colors.alfa(alpha)
                if cl == 'small sports':
                    return Colors.nissan(alpha)
                if cl == '90s touring':
                    return Colors.gte(alpha)

        if car.find("ferrari") >= 0:
            return Colors.ferrari(alpha)
        if car.find("sauber") >= 0:
            return rgb([8, 110, 250], a=alpha)
        if car.find("india") >= 0:
            return rgb([245, 172, 192], a=alpha)
        if car.find("williams") >= 0:
            return rgb([250, 250, 250], a=alpha)
        if car.find("haas") >= 0:
            return rgb([230, 27, 36], a=alpha)
        if car.find("bull") >= 0:
            return rgb([0, 34, 80], a=alpha)
        if car.find("toro") >= 0:
            return rgb([36, 55, 90], a=alpha)
        if car.find("bmw") >= 0:
            return Colors.bmw(alpha)
        if car.find("ford") >= 0 or car.find("shelby") >= 0:
            return Colors.ford(alpha)
        if car.find("merc") >= 0:
            return Colors.mercedes(alpha)
        if car.find("mazda") >= 0 or car.find("audi") >= 0:
            return rgb([191, 191, 191], a=alpha)
        if car.find("ruf") >= 0 or car.find("corvette") >= 0 or car.find("lotus") >= 0 or car.find("porsche") >= 0:
            return Colors.corvette(alpha)
        if car.find("lamborghini") >= 0 or car.find("pagani") >= 0:
            return Colors.lamborghini(alpha)
        if car.find("ktm") >= 0 or car.find("mclaren") >= 0:
            return Colors.ktm(alpha)
        if car.find("nissan") >= 0:
            return Colors.nissan(alpha)
        if car.find("alfa") >= 0:
            return Colors.alfa(alpha)
        if car.find("honda") >= 0:
            return rgb([214, 112, 157], a=alpha)
        if car.find("renault") >= 0:
            return rgb([255, 204, 49], a=alpha)
        # if car.find("glickenhaus")>=0 or car.find("p4-5_2011")>=0:
        #	return rgb([0, 0, 0], bg = True)
        if default is not None:
            return default
        return Colors.theme(a=alpha)


class Label:
    # INITIALIZATION

    def __init__(self, window, text=""):
        self.text = text
        self.debug = False
        self.is_hiding = True
        self.label = ac.addLabel(window, self.text)
        self.params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(0), "bg": Value(0),
                       "bb": Value(0), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(0)}
        self.f_params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(0), "bg": Value(0),
                         "bb": Value(0), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(0)}
        self.o_params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(0), "bg": Value(0),
                         "bb": Value(0), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(1)}
        self.multiplier = {"x": Value(3), "y": Value(3), "w": Value(1), "h": Value(1), "br": Value(0.06),
                           "bg": Value(0.06), "bb": Value(0.06), "o": Value(0.02), "r": Value(0.06), "g": Value(0.06),
                           "b": Value(0.06), "a": Value(0.02)}
        self.multiplier_mode = {"x": "", "y": "", "w": "", "h": "", "br": "", "bg": "", "bb": "", "o": "", "r": "",
                                "g": "", "b": "", "a": ""}
        self.fontSize = 12
        self.spring_multiplier = 36
        self.align = "left"
        self.bgTexture = ""
        self.fontName = ""
        self.cur_fontName = ""
        self.visible = 0
        self.isVisible = Value(False)
        self.isTextVisible = Value(False)
        self.setVisible(0)

    # PUBLIC METHODS
    def set(self, text=None, align=None, color=None, font_size=None, font=None, w=None, h=None, x=None, y=None, texture=None, background=None, opacity=None, visible=None, animated=False, text_hidden=False, init=False):
        # Text
        if text is not None:
            self.setText(text, text_hidden)
        # Text alignment
        if align is not None:
            self.setAlign(align)
        # Size
        if w is not None and h is not None:
            self.setSize(w, h, animated)
        elif w is not None:
            self.setSize(w, self.params["h"].value, animated)
        elif h is not None:
            self.setSize(self.params["w"].value, h, animated)
        # Position
        if x is not None and y is not None:
            self.setPos(x, y, animated)
        elif x is not None:
            self.setX(x, animated)
        elif y is not None:
            self.setY(y, animated)
        # Font color
        if color is not None:
            self.setColor(color, animated, init)
        # Font
        if font is not None:
            self.setFont(font, 0, 0)
        # Font size
        if font_size is not None:
            self.setFontSize(font_size)
        # Background texture
        if texture is not None:
            self.setBgTexture(texture)
        # Background color
        if background is not None:
            self.setBgColor(background, animated, init)
        # Background opacity
        if opacity is not None:
            self.setBgOpacity(opacity, animated, init)
        # Visibility
        if visible is not None:
            self.setVisible(visible)
        return self

    def setText(self, text, hidden=False):
        self.text = text
        if hidden:
            ac.setText(self.label, "")
            self.isTextVisible.setValue(False)
        else:
            ac.setText(self.label, self.text)
            self.isTextVisible.setValue(True)
        return self

    def setSize(self, w, h, animated=False):
        self.f_params["w"].setValue(w)
        self.f_params["h"].setValue(h)
        if not animated:
            self.o_params["w"].setValue(w)
            self.o_params["h"].setValue(h)
            self.params["w"].setValue(w)
            self.params["h"].setValue(h)
            if self.params["w"].hasChanged() or self.params["h"].hasChanged():
                ac.setSize(self.label, self.params["w"].value, self.params["h"].value)
        return self

    def setPos(self, x, y, animated=False):
        self.f_params["x"].setValue(x)
        self.f_params["y"].setValue(y)
        if not animated:
            self.o_params["x"].setValue(x)
            self.o_params["y"].setValue(y)
            self.params["x"].setValue(x)
            self.params["y"].setValue(y)
            if self.params["x"].hasChanged() or self.params["y"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setY(self, y, animated=False):
        self.f_params["y"].setValue(y)
        if not animated:
            self.o_params["y"].setValue(y)
            self.params["y"].setValue(y)
            if self.params["y"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setX(self, x, animated=False):
        self.f_params["x"].setValue(x)
        if not animated:
            self.o_params["x"].setValue(x)
            self.params["x"].setValue(x)
            if self.params["x"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setColor(self, color, animated=False, init=False):
        self.f_params["r"].setValue(color[0])
        self.f_params["g"].setValue(color[1])
        self.f_params["b"].setValue(color[2])
        if init or not animated:
            self.o_params["r"].setValue(color[0])
            self.o_params["g"].setValue(color[1])
            self.o_params["b"].setValue(color[2])
            self.o_params["a"].setValue(color[3])
        if self.isVisible.value:
            self.f_params["a"].setValue(color[3])
        if not animated:
            self.params["r"].setValue(color[0])
            self.params["g"].setValue(color[1])
            self.params["b"].setValue(color[2])
            if self.isVisible.value:
                self.params["a"].setValue(color[3])
                ac.setFontColor(self.label, *color)
        return self

    def setFont(self, fontName, italic, bold):
        self.fontName = fontName
        self.cur_fontName = fontName
        ac.setCustomFont(self.label, self.fontName, italic, bold)
        return self

    def update_font(self):
        self.setFont(Font.get_font(), 0, 0)
        return self

    def change_font_if_needed(self, support=None):
        if support is not None:
            self.cur_fontName = Font.get_support_font()
            ac.setCustomFont(self.label, self.cur_fontName, 0, 0)
        elif self.fontName != self.cur_fontName:
            self.setFont(Font.get_font(), 0, 0)
        return self

    def setFontSize(self, fontSize):
        self.fontSize = fontSize
        ac.setFontSize(self.label, self.fontSize)
        return self

    def setAlign(self, align="left"):
        self.align = align
        ac.setFontAlignment(self.label, self.align)
        return self

    def setBgTexture(self, texture):
        self.bgTexture = texture
        ac.setBackgroundTexture(self.label, self.bgTexture)
        return self

    def setBgColor(self, color, animated=False, init=False):
        if self.debug:
            #self.debug_param("A", "a")
            #self.debug_param("O", "o")
            self.debug_param("setBgColor" + str(color[0]), "br")
        self.f_params["br"].setValue(color[0])
        self.f_params["bg"].setValue(color[1])
        self.f_params["bb"].setValue(color[2])
        if init or not animated:
            self.o_params["br"].setValue(color[0])
            self.o_params["bg"].setValue(color[1])
            self.o_params["bb"].setValue(color[2])
        if not animated:
            self.params["br"].setValue(color[0])
            self.params["bg"].setValue(color[1])
            self.params["bb"].setValue(color[2])
            ac.setBackgroundColor(self.label, color[0], color[1], color[2])
            if self.isVisible.value:
                ac.setBackgroundOpacity(self.label, self.params["o"].value)
            else:
                ac.setBackgroundOpacity(self.label, 0)
        if len(color) > 3:
            self.setBgOpacity(color[3], animated, init)
        return self

    def setBgOpacity(self, opacity, animated=False, init=False):
        if init or not animated:
            self.o_params["o"].setValue(opacity)
        if self.isVisible.value:
            self.f_params["o"].setValue(opacity)
        if not animated:
            if self.isVisible.value:
                self.params["o"].setValue(opacity)
                ac.setBackgroundOpacity(self.label, self.params["o"].value)
        return self

    ############################## Animations ##############################

    def debug_param(self, title="", param="o"):
        ac.console(title + ": current:" + str(self.params[param].value) + " final:" + str(self.f_params[param].value) + " origin:" + str(
            self.o_params[param].value))
        ac.log(title + ": current:" + str(self.params[param].value) + " final:" + str(self.f_params[param].value) + " origin:" + str(
            self.o_params[param].value))
        return self

    def setVisible(self, value):
        self.visible = value
        self.isVisible.setValue(bool(value))
        ac.setVisible(self.label, value)
        if self.isVisible.value:
            self.is_hiding = False
        else:
            self.is_hiding = True
        return self

    def setAnimationSpeed(self, param, value):
        for p in param:
            self.multiplier[p].setValue(value)
        return self

    def setAnimationMode(self, param, value):
        for p in param:
            self.multiplier_mode[p] = value
        return self

    def hide(self):
        self.is_hiding = True
        if self.o_params["o"].value == 0:
            self.hideText()
        else:
            #self.setBgOpacity(0, True)
            self.f_params["o"].setValue(0)
        return self

    def slide_up(self):
        self.f_params["h"].setValue(0)
        return self

    def show(self):
        self.is_hiding = False
        if self.o_params["o"].value == 0:
            self.showText()
        else:
            self.f_params["o"].setValue(self.o_params["o"].value)
            self.f_params["a"].setValue(self.o_params["a"].value)
        return self

    def slide_down(self):
        self.f_params["h"].setValue(self.o_params["h"].value)
        return self

    def showText(self):
        self.is_hiding = False
        self.f_params["a"].setValue(self.o_params["a"].value)
        return self

    def hideText(self):
        self.is_hiding = True
        self.f_params["a"].setValue(0)
        return self

    def adjustParam(self, p):
        if self.params[p].value != self.f_params[p].value:
            if self.multiplier_mode[p] == "spring":
                multiplier = self.multiplier[p].value
                spring_multi = self.spring_multiplier
                if p == "y":
                    spring_multi = self.f_params["h"].value - 1
                    if not spring_multi > 0:
                        spring_multi = 36
                if abs(self.f_params[p].value - self.params[p].value) > spring_multi * self.multiplier[p].value:
                    multiplier = round(abs(self.f_params[p].value - self.params[p].value) / spring_multi)
            else:
                multiplier = self.multiplier[p].value
            if abs(self.f_params[p].value - self.params[p].value) < multiplier:
                multiplier = abs(self.f_params[p].value - self.params[p].value)
            if self.params[p].value < self.f_params[p].value:
                self.params[p].setValue(self.params[p].value + multiplier)
            else:
                self.params[p].setValue(self.params[p].value - multiplier)
        return self

    def animate(self):
        if self.debug:
            #self.debug_param("A", "a")
            #self.debug_param("O", "o")
            self.debug_param("br", "br")
            #self.debug_param("g", "g")
            #self.debug_param("b", "b")
        # adjust size +1
        self.adjustParam("w").adjustParam("h")
        # adjust position +3
        self.adjustParam("x").adjustParam("y")
        # adjust background
        self.adjustParam("br").adjustParam("bg").adjustParam("bb").adjustParam("o")
        # adjust colors + 0.02
        self.adjustParam("r").adjustParam("g").adjustParam("b").adjustParam("a")

        # commit changes
        if self.params["x"].hasChanged() or self.params["y"].hasChanged():
            ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        param_h_changed = self.params["h"].hasChanged()
        if self.params["w"].hasChanged() or param_h_changed:
            ac.setSize(self.label, self.params["w"].value, self.params["h"].value)
            #if param_h_changed:
            #    if self.params["h"].value == 0:
            #        self.isVisible.setValue(False)
            #    else:
            #        self.isVisible.setValue(True)
        if self.params["br"].hasChanged() or self.params["bg"].hasChanged() or self.params["bb"].hasChanged():
            ac.setBackgroundColor(self.label, self.params["br"].value, self.params["bg"].value, self.params["bb"].value)
            ac.setBackgroundOpacity(self.label, self.params["o"].value)

        opacity_changed = self.params["o"].hasChanged()
        if opacity_changed:
            # fg opacity
            ac.setBackgroundOpacity(self.label, self.params["o"].value)
            # TODO : hide by alpha
            if not self.is_hiding and (self.params["o"].value >= 0.4 or self.f_params["o"].value < 0.4):
                self.isTextVisible.setValue(True)
            elif self.is_hiding:
                self.isTextVisible.setValue(False)
            if self.isTextVisible.hasChanged():
                if self.isTextVisible.value:
                    ac.setText(self.label, self.text)
                    ac.setFontColor(self.label, self.params["r"].value,
                                    self.params["g"].value,
                                    self.params["b"].value,
                                    self.params["a"].value)
                else:
                    ac.setText(self.label, "")
                    if self.debug:
                        self.debug_param("setText", "a")
                        self.debug_param("setText", "o")

        alpha_changed = self.params["a"].hasChanged()
        if self.params["r"].hasChanged() or self.params["g"].hasChanged() \
                or self.params["b"].hasChanged() or alpha_changed:
            ac.setFontColor(self.label,
                            self.params["r"].value,
                            self.params["g"].value,
                            self.params["b"].value,
                            self.params["a"].value)

        if opacity_changed or alpha_changed:
            if self.is_hiding and ((opacity_changed and self.params["o"].value == 0)
                                   or (alpha_changed and self.params["a"].value == 0)):
                self.setVisible(0)
            elif not self.is_hiding:
                self.setVisible(1)

# -#####################################################################################################################################-#


class Button:
    # INITIALIZATION

    def __init__(self, window, clickFunc, width=60, height=20, x=0, y=0, text="", texture=""):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.button = ac.addButton(window, text)

        # adding default settings
        self.setSize(width, height)
        self.setPos(x, y)
        if texture != "":
            self.setBgTexture(texture)

        # default settings
        ac.drawBorder(self.button, 0)
        ac.setBackgroundOpacity(self.button, 0)

        # adding a click event
        ac.addOnClickedListener(self.button, clickFunc)

    # PUBLIC METHODS

    def setSize(self, width, height):
        self.width = width
        self.height = height
        ac.setSize(self.button, self.width, self.height)
        return self

    def setFontSize(self, fontSize):
        self.fontSize = fontSize
        ac.setFontSize(self.button, self.fontSize)
        return self

    def setPos(self, x, y):
        self.x = x
        self.y = y
        ac.setPosition(self.button, self.x, self.y)
        return self

    def setBgTexture(self, texture):
        ac.setBackgroundTexture(self.button, texture)
        return self

    def setText(self, text, hidden=False):
        ac.setText(self.button, text)
        return self

    def setAlign(self, align="left"):
        ac.setFontAlignment(self.button, align)
        return self

    def setBgColor(self, color, animated=False):
        ac.setBackgroundColor(self.button, *color)
        # ac.setBackgroundOpacity(self.label, self.params["o"].value)
        return self

    def setBgOpacity(self, opacity, animated=False):
        ac.setBackgroundOpacity(self.button, opacity)
        return self

    def setVisible(self, value):
        ac.setVisible(self.button, value)
        return self


# -#####################################################################################################################################-#

class Log:
    @staticmethod
    def w(message):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        ac.console(message + ":")
        for line in lines:
            ac.log(line)
        for line in lines:
            if line.find("Traceback") >= 0:
                continue
            s = line.replace("\n", " -> ")
            s = s.replace("  ", "")
            if s[-4:] == " -> ":
                s = s[:-4]
            ac.console(s)


class Config:
    # INITIALIZATION

    def __init__(self, path, filename):
        self.file = path + filename
        self.parser = 0

        try:
            self.parser = configparser.RawConfigParser()
        except:
            ac.console("Prunn: Config -- Failed to initialize ConfigParser.")

        # read the file
        self._read()

    # LOCAL METHODS

    def _read(self):
        self.parser.read(self.file)

    def _write(self):
        with open(self.file, "w") as cfgFile:
            self.parser.write(cfgFile)

    # PUBLIC METHODS

    def has(self, section=None, option=None):
        if section is not None:
            # if option is not specified, search only for the section
            if option is None:
                return self.parser.has_section(section)
            # else, search for the option within the specified section
            else:
                return self.parser.has_option(section, option)
        # if section is not specified
        else:
            ac.console("Prunn: Config.has -- section must be specified.")

    def set(self, section=None, option=None, value=None):
        if section is not None:
            # if option is not specified, add the specified section
            if option is None:
                self.parser.add_section(section)
                self._write()
            # else, add the option within the specified section
            else:
                if not self.has(section, option) and value is None:
                    ac.console("Prunn: Config.set -- a value must be passed.")
                else:
                    if not self.has(section):
                        self.parser.add_section(section)
                    self.parser.set(section, option, value)
                    self._write()
        # if sections is not specified
        else:
            ac.console("Prunn: Config.set -- section must be specified.")

    def get(self, section, option, type=""):
        if self.has(section) and self.has(section, option):
            # if option request is an integer
            if type == "int":
                return self.parser.getint(section, option)
            # if option request is a float
            elif type == "float":
                return self.parser.getfloat(section, option)
            # if option request is boolean
            elif type == "bool":
                return self.parser.getboolean(section, option)
            # it must be a string then!
            else:
                return self.parser.get(section, option)
        else:
            return -1

    def remSection(self, section):
        if self.has(section):
            self.parser.remove_section(section)
            self._write()
        else:
            ac.console("Prunn: Config.remSection -- section not found.")

    def remOption(self, section, option):
        if self.has(section) and self.has(section, option):
            self.parser.remove_option(section, option)
            self._write()
        else:
            ac.console("Prunn: Config.remOption -- option not found.")


class Font:
    # Name, offset, support, width
    fonts = [["Segoe UI", 0, None, 1.2],
             ["Noto Sans", 0, None, 1.26],
             ["Open Sans", 0, 0, 1.5],
             ["Yantramanav", 5, 0, 1.18],
             ["Signika Negative", 3, 0, 1.2],
             ["Strait", 7, 0, 1.1],
             ["Overlock", 4, 1, 1.1]]
    init = []
    current = 0

    @staticmethod
    def set_font(font):
        Font.current = font
        if not len(Font.init):
            i = 0
            for _ in Font.fonts:
                Font.init.append(False)
                i += 1
        if not Font.init[Font.current]:
            if ac.initFont(0, Font.fonts[Font.current][0], 0, 0) > 0:
                Font.init[Font.current] = True

    @staticmethod
    def get_font():
        return Font.fonts[Font.current][0]

    @staticmethod
    def get_font_width_adjust():
        return Font.fonts[Font.current][3]

    @staticmethod
    def get_support_font():
        if Font.fonts[Font.current][2] is not None:
            return Font.fonts[Font.fonts[Font.current][2]][0]
        return Font.fonts[Font.current][0]

    @staticmethod
    def get_font_offset():
        return Font.fonts[Font.current][1]

    @staticmethod
    def get_text_dimensions(text, height):
        class SIZE(ctypes.Structure):
            _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]
        points = Font.get_font_size(height+Font.get_font_offset())

        hdc = ctypes.windll.user32.GetDC(0)
        hfont = ctypes.windll.gdi32.CreateFontA(-32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Arial")
        #hfont = ctypes.windll.gdi32.CreateFontA(-points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, Font.get_font())
        hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)
        size = SIZE(0, 0)
        ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))
        ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
        ctypes.windll.gdi32.DeleteObject(hfont)
        #ac.console("Name :" + str(points) + " : " + str(Font.get_font()) + " : " + str(size.cx) + " = " + str(size.cx / 32 * points * Font.get_font_width_adjust()))
        #ac.console("Name :" + str(points) + " : " + str(Font.get_font()) + " : " + str(size.cx) + " = " + str(size.cx / 32 * points * Font.get_font_width_adjust()))
        #ac.log("Name :" + str(points) + " : " + str(Font.get_font()) + " : " + str(size.cx) + " = " + str(size.cx / 32 * points * Font.get_font_width_adjust()))
        #return size.cx
        #return size.cx * Font.get_font_width_adjust()
        return size.cx / 32 * points * Font.get_font_width_adjust()

    @staticmethod
    def get_font_size(row_height):
        if row_height == 57 or row_height == 56:
            return 38
        if row_height == 55 or row_height == 54:
            return 37
        if row_height == 53 or row_height == 52:
            return 36
        if row_height == 52 or row_height == 51:
            return 35
        if row_height == 50 or row_height == 49:
            return 34
        if row_height == 48 or row_height == 47:
            return 33
        if row_height == 46 or row_height == 45:
            return 32
        if row_height == 44 or row_height == 43:
            return 31
        if row_height == 42:
            return 30
        if row_height == 41:
            return 29
        if row_height == 40:
            return 28
        if row_height == 39:
            return 27
        if row_height == 38 or row_height == 37:
            return 26
        if row_height == 36 or row_height == 35:
            return 25
        if row_height == 34:
            return 24
        if row_height == 33:
            return 23
        if row_height == 32 or row_height == 31:
            return 22
        if row_height == 30 or row_height == 29:
            return 21
        if row_height == 28:
            return 19
        if row_height == 27:
            return 19
        if row_height == 26:
            return 19
        if row_height == 25:
            return 18
        if row_height == 24 or row_height == 23:
            return 17
        if row_height == 22:
            return 16
        if row_height == 21:
            return 15
        if row_height == 20:
            return 14
        if row_height < 30:
            return row_height - 6
        return 26


class Laps:
    def __init__(self, lap, valid, time):
        self.lap = lap
        self.valid = valid
        self.time = time


class lapTimeStart:
    def __init__(self, lap, time, lastpit):
        self.lap = lap
        self.time = time
        self.lastpit = lastpit


class MyHTMLParser(HTMLParser):
    html_table = 0
    logging_html = False
    line = []
    data = []
    tmp_data = ""
    b = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.__class__.html_table += 1
            if self.__class__.html_table > 1:
                self.__class__.logging_html = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.__class__.logging_html = False
        elif self.__class__.logging_html and tag == "tr" and len(self.__class__.line) > 0:
            self.__class__.data.append(self.__class__.line)
            self.__class__.line = []
            self.__class__.tmp_data = ""
        elif self.__class__.logging_html and tag == "td":
            self.__class__.line.append(self.__class__.tmp_data)
            self.__class__.tmp_data = ""

    def handle_data(self, data):
        if self.__class__.logging_html:
            self.__class__.tmp_data = data
