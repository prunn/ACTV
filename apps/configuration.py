import ac
import acsys
import apps.util.win32con, ctypes, ctypes.wintypes
import threading
from apps.util.classes import Window, Button, Label, Value, Config, Log
from apps.util.func import rgb


class Configuration:
    configChanged = False
    tabChanged = False
    currentTab = 1
    race_mode = 0
    qual_mode = 0
    lapCanBeInvalidated = 1
    forceInfoVisible = 0
    max_num_cars = 18
    max_num_laps_stint = 8
    ui_row_height = 36
    theme_red = 191
    theme_green = 0
    theme_blue = 0
    tower_highlight = 0
    carColorsBy = 0

    # INITIALIZATION
    def __init__(self):
        self.session = Value(-1)
        self.listen_active = True
        self.window = Window(name="ACTV Config", icon=True, width=251, height=480, texture="").setBgOpacity(0.6)

        self.btn_tab1 = Button(self.window.app, self.on_tab1_press)\
            .setPos(0, -22).setSize(126, 22).setText("General")\
            .setAlign("center").setBgColor(rgb([255, 12, 12], bg=True))
        self.btn_tab2 = Button(self.window.app, self.on_tab2_press)\
            .setPos(126, -22).setSize(125, 22).setText("Colors")\
            .setAlign("center").setBgColor(rgb([12, 12, 12], bg=True))

        y = 50
        self.spin_race_mode = ac.addSpinner(self.window.app, "Race tower mode :")
        ac.setRange(self.spin_race_mode, 0, 2)
        ac.setPosition(self.spin_race_mode, 20, y)
        ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        ac.addOnValueChangeListener(self.spin_race_mode, self.on_spin_race_mode_changed)
        self.lbl_race_mode = Label(self.window.app, "Auto")\
            .setSize(120, 26).setPos(186, y - 28)\
            .setFontSize(12).setAlign("left")\
            .setVisible(1)

        y += 70
        self.spin_qual_mode = ac.addSpinner(self.window.app, "Qual tower mode :")
        ac.setRange(self.spin_qual_mode, 0, 1)
        ac.setPosition(self.spin_qual_mode, 20, y)
        ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        ac.addOnValueChangeListener(self.spin_qual_mode, self.on_spin_qual_mode_changed)
        self.lbl_qual_mode = Label(self.window.app, "Gaps")\
            .setSize(120, 26).setPos(186, y - 28)\
            .setFontSize(12).setAlign("left")\
            .setVisible(1)

        y += 70
        self.spin_num_cars = ac.addSpinner(self.window.app, "Number cars tower")
        ac.setRange(self.spin_num_cars, 6, 28)
        ac.setPosition(self.spin_num_cars, 20, y)
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.addOnValueChangeListener(self.spin_num_cars, self.on_spin_num_cars_changed)

        y += 70
        self.spin_num_laps = ac.addSpinner(self.window.app, "Number laps stint mode")
        ac.setRange(self.spin_num_laps, 2, 28)
        ac.setPosition(self.spin_num_laps, 20, y)
        ac.setValue(self.spin_num_laps, self.__class__.max_num_laps_stint)
        ac.addOnValueChangeListener(self.spin_num_laps, self.on_spin_num_laps_changed)

        y += 70
        self.spin_row_height = ac.addSpinner(self.window.app, "Row height")
        ac.setRange(self.spin_row_height, 20, 48)
        ac.setPosition(self.spin_row_height, 20, y)
        ac.setValue(self.spin_row_height, self.__class__.ui_row_height)
        ac.addOnValueChangeListener(self.spin_row_height, self.on_spin_row_height_changed)

        y += 52
        self.chk_invalidated = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_invalidated, 20, y)
        ac.addOnCheckBoxChanged(self.chk_invalidated, self.on_check_invalidated_changed)
        self.lbl_title_invalidated = Label(self.window.app, "Lap can be invalidated")\
            .setSize(200, 26).setPos(65, y + 1)\
            .setFontSize(16).setAlign("left")\
            .setVisible(1)

        y += 36
        self.chk_force_info = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_force_info, 20, y)
        ac.addOnCheckBoxChanged(self.chk_force_info, self.on_check_force_info_changed)
        self.lbl_title_force_info = Label(self.window.app, "Info always visible")\
            .setSize(200, 26).setPos(65, y + 1)\
            .setFontSize(16).setAlign("left")\
            .setVisible(1)

        # RGB
        y = 50
        self.spin_theme_red = ac.addSpinner(self.window.app, "Red")
        ac.setRange(self.spin_theme_red, 0, 255)
        ac.setPosition(self.spin_theme_red, 20, y)
        ac.setValue(self.spin_theme_red, self.__class__.theme_red)
        ac.addOnValueChangeListener(self.spin_theme_red, self.on_red_changed)
        y += 70
        self.spin_theme_green = ac.addSpinner(self.window.app, "Green")
        ac.setRange(self.spin_theme_green, 0, 255)
        ac.setPosition(self.spin_theme_green, 20, y)
        ac.setValue(self.spin_theme_green, self.__class__.theme_green)
        ac.addOnValueChangeListener(self.spin_theme_green, self.on_green_changed)
        y += 70
        self.spin_theme_blue = ac.addSpinner(self.window.app, "Blue")
        ac.setRange(self.spin_theme_blue, 0, 255)
        ac.setPosition(self.spin_theme_blue, 20, y)
        ac.setValue(self.spin_theme_blue, self.__class__.theme_blue)
        ac.addOnValueChangeListener(self.spin_theme_blue, self.on_blue_changed)
        ac.setVisible(self.spin_theme_red, 0)
        ac.setVisible(self.spin_theme_green, 0)
        ac.setVisible(self.spin_theme_blue, 0)

        y += 70
        self.spin_tower_lap = ac.addSpinner(self.window.app, "Tower Highlight :")
        ac.setRange(self.spin_tower_lap, 0, 1)
        ac.setPosition(self.spin_tower_lap, 20, y)
        ac.setValue(self.spin_tower_lap, self.__class__.tower_highlight)
        ac.addOnValueChangeListener(self.spin_tower_lap, self.on_spin_tower_lap_color_changed)
        ac.setVisible(self.spin_tower_lap, 0)
        self.lbl_tower_lap = Label(self.window.app, "Red").setSize(120, 26).setPos(186, y - 28).setFontSize(
            12).setAlign("left").setVisible(0)

        # byClass
        y += 70
        self.spin_colors_by = ac.addSpinner(self.window.app, "Car colors by :")
        ac.setRange(self.spin_colors_by, 0, 1)
        ac.setPosition(self.spin_colors_by, 20, y)
        ac.setValue(self.spin_colors_by, self.__class__.carColorsBy)
        ac.addOnValueChangeListener(self.spin_colors_by, self.on_spin_colors_by_changed)
        ac.setVisible(self.spin_colors_by, 0)
        self.lbl_colors_by = Label(self.window.app, "Brand").setSize(120, 26).setPos(186, y - 28).setFontSize(
            12).setAlign("left").setVisible(0)

        self.cfg_loaded = False
        self.cfg = Config("apps/python/prunn/", "config.ini")
        self.load_cfg()

        # thread
        self.key_listener = threading.Thread(target=self.listen_key)
        self.key_listener.daemon = True
        self.key_listener.start()

    def __del__(self):
        self.listen_active = False

    def load_cfg(self):
        self.__class__.lapCanBeInvalidated = self.cfg.get("SETTINGS", "lap_can_be_invalidated", "int")
        if self.__class__.lapCanBeInvalidated == -1:
            self.__class__.lapCanBeInvalidated = 1
        self.__class__.forceInfoVisible = self.cfg.get("SETTINGS", "force_info_visible", "int")
        if self.__class__.forceInfoVisible == -1:
            self.__class__.forceInfoVisible = 0
        self.__class__.max_num_cars = self.cfg.get("SETTINGS", "num_cars_tower", "int")
        if self.__class__.max_num_cars == -1:
            self.__class__.max_num_cars = 18
        self.__class__.max_num_laps_stint = self.cfg.get("SETTINGS", "num_laps_stint", "int")
        if self.__class__.max_num_laps_stint == -1:
            self.__class__.max_num_laps_stint = 8
        self.__class__.ui_row_height = self.cfg.get("SETTINGS", "ui_row_height", "int")
        if self.__class__.ui_row_height == -1:
            self.__class__.ui_row_height = 36
        self.__class__.race_mode = self.cfg.get("SETTINGS", "race_mode", "int")
        if self.__class__.race_mode == -1:
            self.__class__.race_mode = 0
        self.__class__.qual_mode = self.cfg.get("SETTINGS", "qual_mode", "int")
        if self.__class__.qual_mode == -1:
            self.__class__.qual_mode = 0
            # RGB
        self.__class__.theme_red = self.cfg.get("SETTINGS", "red", "int")
        if self.__class__.theme_red == -1:
            self.__class__.theme_red = 191
        self.__class__.theme_green = self.cfg.get("SETTINGS", "green", "int")
        if self.__class__.theme_green == -1:
            self.__class__.theme_green = 0
        self.__class__.theme_blue = self.cfg.get("SETTINGS", "blue", "int")
        if self.__class__.theme_blue == -1:
            self.__class__.theme_blue = 0
        self.__class__.tower_highlight = self.cfg.get("SETTINGS", "tower_highlight", "int")
        if self.__class__.tower_highlight == -1:
            self.__class__.tower_highlight = 0
        self.__class__.carColorsBy = self.cfg.get("SETTINGS", "car_colors_by", "int")
        if self.__class__.carColorsBy == -1:
            self.__class__.carColorsBy = 0

        ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.setValue(self.spin_num_laps, self.__class__.max_num_laps_stint)
        ac.setValue(self.spin_row_height, self.__class__.ui_row_height)
        ac.setValue(self.chk_invalidated, self.__class__.lapCanBeInvalidated)
        ac.setValue(self.chk_force_info, self.__class__.forceInfoVisible)
        ac.setValue(self.spin_theme_red, self.__class__.theme_red)
        ac.setValue(self.spin_theme_green, self.__class__.theme_green)
        ac.setValue(self.spin_theme_blue, self.__class__.theme_blue)
        ac.setValue(self.spin_tower_lap, self.__class__.tower_highlight)
        ac.setValue(self.spin_colors_by, self.__class__.carColorsBy)
        self.set_labels()
        self.cfg_loaded = True

    def save_cfg(self):
        self.set_labels()
        self.cfg.set("SETTINGS", "race_mode", self.__class__.race_mode)
        self.cfg.set("SETTINGS", "qual_mode", self.__class__.qual_mode)
        self.cfg.set("SETTINGS", "lap_can_be_invalidated", self.__class__.lapCanBeInvalidated)
        self.cfg.set("SETTINGS", "force_info_visible", self.__class__.forceInfoVisible)
        self.cfg.set("SETTINGS", "num_cars_tower", self.__class__.max_num_cars)
        self.cfg.set("SETTINGS", "num_laps_stint", self.__class__.max_num_laps_stint)
        self.cfg.set("SETTINGS", "ui_row_height", self.__class__.ui_row_height)
        self.cfg.set("SETTINGS", "red", self.__class__.theme_red)
        self.cfg.set("SETTINGS", "green", self.__class__.theme_green)
        self.cfg.set("SETTINGS", "blue", self.__class__.theme_blue)
        self.cfg.set("SETTINGS", "tower_highlight", self.__class__.tower_highlight)
        self.cfg.set("SETTINGS", "car_colors_by", self.__class__.carColorsBy)

    def set_labels(self):
        # Qualifying mode
        if self.__class__.qual_mode == 0:
            self.lbl_qual_mode.setText("Gaps")
        else:
            self.lbl_qual_mode.setText("Times")
        # Race mode
        if self.__class__.race_mode == 0:
            self.lbl_race_mode.setText("Auto")
        elif self.__class__.race_mode == 1:
            self.lbl_race_mode.setText("Full-Gaps")
        else:
            self.lbl_race_mode.setText("Full")
        # Tower color
        if self.__class__.tower_highlight == 0:
            self.lbl_tower_lap.setText("Red")
        else:
            self.lbl_tower_lap.setText("Green")
        # Color by class/brand
        if self.__class__.carColorsBy == 0:
            self.lbl_colors_by.setText("Brand")
        else:
            self.lbl_colors_by.setText("Class")

    def change_tab(self):
        if self.__class__.currentTab == 1:
            self.btn_tab1.setBgColor(rgb([255, 12, 12], bg=True)).setBgOpacity(0.6)
            self.btn_tab2.setBgColor(rgb([12, 12, 12], bg=True)).setBgOpacity(0.6)
            ac.setVisible(self.spin_theme_red, 0)
            ac.setVisible(self.spin_theme_green, 0)
            ac.setVisible(self.spin_theme_blue, 0)
            ac.setVisible(self.spin_tower_lap, 0)
            ac.setVisible(self.spin_colors_by, 0)
            self.lbl_tower_lap.setVisible(0)
            self.lbl_colors_by.setVisible(0)
            ac.setVisible(self.spin_race_mode, 1)
            ac.setVisible(self.spin_qual_mode, 1)
            ac.setVisible(self.spin_num_cars, 1)
            ac.setVisible(self.spin_num_laps, 1)
            ac.setVisible(self.spin_row_height, 1)
            ac.setVisible(self.chk_invalidated, 1)
            ac.setVisible(self.chk_force_info, 1)
            self.lbl_title_invalidated.setVisible(1)
            self.lbl_title_force_info.setVisible(1)
            self.lbl_race_mode.setVisible(1)
            self.lbl_qual_mode.setVisible(1)
        else:
            self.btn_tab1.setBgColor(rgb([12, 12, 12], bg=True)).setBgOpacity(0.6)
            self.btn_tab2.setBgColor(rgb([255, 12, 12], bg=True)).setBgOpacity(0.6)
            ac.setVisible(self.spin_theme_red, 1)
            ac.setVisible(self.spin_theme_green, 1)
            ac.setVisible(self.spin_theme_blue, 1)
            ac.setVisible(self.spin_tower_lap, 1)
            ac.setVisible(self.spin_colors_by, 1)
            self.lbl_tower_lap.setVisible(1)
            self.lbl_colors_by.setVisible(1)
            ac.setVisible(self.spin_race_mode, 0)
            ac.setVisible(self.spin_qual_mode, 0)
            ac.setVisible(self.spin_num_cars, 0)
            ac.setVisible(self.spin_num_laps, 0)
            ac.setVisible(self.spin_row_height, 0)
            ac.setVisible(self.chk_invalidated, 0)
            ac.setVisible(self.chk_force_info, 0)
            self.lbl_title_invalidated.setVisible(0)
            self.lbl_title_force_info.setVisible(0)
            self.lbl_race_mode.setVisible(0)
            self.lbl_qual_mode.setVisible(0)

    def on_update(self, sim_info):
        self.window.setBgOpacity(0.6).border(0)
        self.session.setValue(sim_info.graphics.session)
        if self.__class__.tabChanged:
            self.change_tab()
        if self.__class__.configChanged and self.cfg_loaded:
            self.save_cfg()
            self.__class__.configChanged = False
            return True
        elif self.__class__.configChanged and not self.cfg_loaded:
            self.__class__.configChanged = False
        return False

    def listen_key(self):
        try:
            # ctypes.windll.user32.RegisterHotKey(None, 1, 0, apps.util.win32con.VK_F7)
            ctypes.windll.user32.RegisterHotKey(None, 1, apps.util.win32con.MOD_CONTROL, 0x44)  # CTRL+D
            msg = ctypes.wintypes.MSG()
            while self.listen_active:
                if ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == apps.util.win32con.WM_HOTKEY:
                        self.hotkey_pressed()
                    ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                    ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
        except:
            Log.w("Error")
        finally:
            ctypes.windll.user32.UnregisterHotKey(None, 1)

    def hotkey_pressed(self):
        if self.session.value == 2:
            if self.__class__.race_mode >= 2:
                self.__class__.race_mode = 0
            else:
                self.__class__.race_mode += 1
            ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        else:
            if self.__class__.qual_mode >= 1:
                self.__class__.qual_mode = 0
            else:
                self.__class__.qual_mode += 1
            ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        self.__class__.configChanged = True

    @staticmethod
    def on_check_invalidated_changed(name, state):
        Configuration.lapCanBeInvalidated = state
        Configuration.configChanged = True

    @staticmethod
    def on_check_force_info_changed(name, state):
        Configuration.forceInfoVisible = state
        Configuration.configChanged = True

    @staticmethod
    def on_spin_num_cars_changed(value):
        Configuration.max_num_cars = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_num_laps_changed(value):
        Configuration.max_num_laps_stint = value
        Configuration.configChanged = True

    @staticmethod
    def on_red_changed(value):
        Configuration.theme_red = value
        Configuration.configChanged = True

    @staticmethod
    def on_green_changed(value):
        Configuration.theme_green = value
        Configuration.configChanged = True

    @staticmethod
    def on_blue_changed(value):
        Configuration.theme_blue = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_tower_lap_color_changed(value):
        Configuration.tower_highlight = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_colors_by_changed(value):
        Configuration.carColorsBy = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_row_height_changed(value):
        Configuration.ui_row_height = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_race_mode_changed(value):
        Configuration.race_mode = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_qual_mode_changed(value):
        Configuration.qual_mode = value
        Configuration.configChanged = True

    @staticmethod
    def on_tab1_press(a, b):
        if Configuration.currentTab != 1:
            Configuration.currentTab = 1
            Configuration.tabChanged = True

    @staticmethod
    def on_tab2_press(a, b):
        if Configuration.currentTab != 2:
            Configuration.currentTab = 2
            Configuration.tabChanged = True
