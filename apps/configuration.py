import ac
import acsys
import apps.util.win32con, ctypes, ctypes.wintypes
import threading
from .util.classes import Window, Button, Label, Value, Config, Log, Font, Colors
from .util.func import rgb


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
        self.window = Window(name="ACTV Config", icon=True, width=251, height=558, texture="").setBgOpacity(0.6)

        self.btn_tab1 = Button(self.window.app, self.on_tab1_press)\
            .setPos(0, -22).setSize(126, 22).setText("General")\
            .setAlign("center").setBgColor(rgb([255, 12, 12], bg=True))
        self.btn_tab2 = Button(self.window.app, self.on_tab2_press)\
            .setPos(126, -22).setSize(125, 22).setText("Colors")\
            .setAlign("center").setBgColor(rgb([12, 12, 12], bg=True))

        y = 50
        self.spin_race_mode = ac.addSpinner(self.window.app, "Race tower mode :")
        ac.setRange(self.spin_race_mode, 0, 4)
        ac.setPosition(self.spin_race_mode, 20, y)
        ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        ac.addOnValueChangeListener(self.spin_race_mode, self.on_spin_race_mode_changed)
        self.lbl_race_mode = Label(self.window.app, "Auto")\
            .setSize(120, 26).setPos(186, y - 28)\
            .setFontSize(12).setAlign("left")\
            .setVisible(1)

        y += 70
        self.spin_qual_mode = ac.addSpinner(self.window.app, "Qual tower mode :")
        ac.setRange(self.spin_qual_mode, 0, 2)
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

        # Font
        y += 70
        self.spin_font = ac.addSpinner(self.window.app, "Font :")
        ac.setRange(self.spin_font, 0, len(Font.fonts) - 1)
        ac.setPosition(self.spin_font, 20, y)
        ac.setValue(self.spin_font, Font.current)
        ac.addOnValueChangeListener(self.spin_font, self.on_spin_font_changed)
        self.lbl_font = Label(self.window.app, "Default").setSize(120, 26).setPos(148, y - 28).setFontSize(
            12).setAlign("left").setVisible(1)

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
        self.lbl_colors_by = Label(self.window.app, "Brand").setSize(120, 26).setPos(178, y - 28).setFontSize(
            12).setAlign("left").setVisible(0)

        # General theme : 0-Dark 1-white 2-electric
        y += 70
        self.spin_general_theme = ac.addSpinner(self.window.app, "Theme :")
        ac.setRange(self.spin_general_theme, 0, 2)
        ac.setPosition(self.spin_general_theme, 20, y)
        ac.setValue(self.spin_general_theme, 0)
        ac.addOnValueChangeListener(self.spin_general_theme, self.on_spin_general_theme_changed)
        ac.setVisible(self.spin_general_theme, 0)
        self.lbl_general_theme = Label(self.window.app, "Dark").setSize(120, 26).setPos(152, y - 28).setFontSize(
            12).setAlign("left").setVisible(0)

        # Border direction - Horizontal vertical none
        y += 70
        self.spin_border_direction = ac.addSpinner(self.window.app, "Border direction :")
        ac.setRange(self.spin_border_direction, 0, 1)
        ac.setPosition(self.spin_border_direction, 20, y)
        ac.setValue(self.spin_border_direction, 0)
        ac.addOnValueChangeListener(self.spin_border_direction, self.on_spin_border_direction_changed)
        ac.setVisible(self.spin_border_direction, 0)
        self.lbl_border_direction = Label(self.window.app, "Horizontal").setSize(120, 26).setPos(192, y - 28).setFontSize(
            12).setAlign("left").setVisible(0)

        # Themed info - checkbox
        y += 52
        self.chk_themed_info = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_themed_info, 20, y)
        ac.addOnCheckBoxChanged(self.chk_themed_info, self.on_check_themed_info_changed)
        ac.setVisible(self.chk_themed_info, 0)
        self.lbl_title_themed_info = Label(self.window.app, "Themed info")\
            .setSize(200, 26).setPos(65, y + 1)\
            .setFontSize(16).setAlign("left")\
            .setVisible(0)

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
        font = self.cfg.get("SETTINGS", "font", "int")
        if font == -1 or font > len(Font.fonts) - 1:
            font = 2  # Open Sans
        Font.set_font(font)

        general_theme = self.cfg.get("SETTINGS", "general_theme", "int")
        if general_theme >= 0:
            Colors.general_theme = general_theme
        border_direction = self.cfg.get("SETTINGS", "border_direction", "int")
        if border_direction >= 0:
            Colors.border_direction = border_direction
        themed_info = self.cfg.get("SETTINGS", "themed_info", "int")
        if themed_info >= 0:
            Colors.themed_info = themed_info

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
        ac.setValue(self.spin_font, font)
        ac.setValue(self.spin_general_theme, Colors.general_theme)
        ac.setValue(self.spin_border_direction, Colors.border_direction)
        ac.setValue(self.chk_themed_info, Colors.themed_info)
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
        self.cfg.set("SETTINGS", "font", Font.current)
        self.cfg.set("SETTINGS", "general_theme", Colors.general_theme)
        self.cfg.set("SETTINGS", "border_direction", Colors.border_direction)
        self.cfg.set("SETTINGS", "themed_info", Colors.themed_info)

    def set_labels(self):
        # Qualifying mode
        if self.__class__.qual_mode == 0:
            self.lbl_qual_mode.setText("Gaps")
        elif self.__class__.qual_mode == 1:
            self.lbl_qual_mode.setText("Times")
        else:
            self.lbl_qual_mode.setText("Compact")
        # Race mode
        if self.__class__.race_mode == 0:
            self.lbl_race_mode.setText("Auto")
        elif self.__class__.race_mode == 1:
            self.lbl_race_mode.setText("Gaps")
        elif self.__class__.race_mode == 2:
            self.lbl_race_mode.setText("Intervals")
        elif self.__class__.race_mode == 3:
            self.lbl_race_mode.setText("Names")
        else:
            self.lbl_race_mode.setText("Compact")
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
        # Font
        self.lbl_font.setText(str(Font.get_font()))
        # Theme
        if Colors.general_theme == 0:
            self.lbl_general_theme.setText("Dark")
        elif Colors.general_theme == 1:
            self.lbl_general_theme.setText("Light")
        elif Colors.general_theme == 2:
            self.lbl_general_theme.setText("Electric")
        # Border direction
        if Colors.border_direction == 0:
            self.lbl_border_direction.setText("Horizontal")
        elif Colors.border_direction == 1:
            self.lbl_border_direction.setText("Vertical")

    def change_tab(self):
        if self.__class__.currentTab == 1:
            self.btn_tab1.setBgColor(rgb([255, 12, 12], bg=True)).setBgOpacity(0.6)
            self.btn_tab2.setBgColor(rgb([12, 12, 12], bg=True)).setBgOpacity(0.6)
            ac.setVisible(self.spin_theme_red, 0)
            ac.setVisible(self.spin_theme_green, 0)
            ac.setVisible(self.spin_theme_blue, 0)
            ac.setVisible(self.spin_tower_lap, 0)
            ac.setVisible(self.spin_colors_by, 0)
            ac.setVisible(self.spin_font, 1)
            self.lbl_tower_lap.setVisible(0)
            self.lbl_colors_by.setVisible(0)
            self.lbl_font.setVisible(1)
            ac.setVisible(self.spin_general_theme, 0)
            self.lbl_general_theme.setVisible(0)
            ac.setVisible(self.spin_border_direction, 0)
            self.lbl_border_direction.setVisible(0)
            ac.setVisible(self.chk_themed_info, 0)
            self.lbl_title_themed_info.setVisible(0)
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
            ac.setVisible(self.spin_font, 0)
            self.lbl_tower_lap.setVisible(1)
            self.lbl_colors_by.setVisible(1)
            self.lbl_font.setVisible(0)
            ac.setVisible(self.spin_general_theme, 1)
            self.lbl_general_theme.setVisible(1)
            ac.setVisible(self.spin_border_direction, 1)
            self.lbl_border_direction.setVisible(1)
            ac.setVisible(self.chk_themed_info, 1)
            self.lbl_title_themed_info.setVisible(1)
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
            if self.__class__.race_mode >= 4:
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
    def on_check_themed_info_changed(name, state):
        Colors.themed_info = state
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
    def on_spin_general_theme_changed(value):
        Colors.general_theme = value
        Configuration.configChanged = True

    @staticmethod
    def on_spin_border_direction_changed(value):
        Colors.border_direction = value
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
    def on_spin_font_changed(value):
        Font.set_font(value)
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
