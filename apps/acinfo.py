import ac
import acsys
import ctypes
import math
from .util.classes import Window, Label, Value, Colors, Font, lapTimeStart, Config
from .configuration import Configuration


class ACInfo:
    # INITIALIZATION
    def __init__(self, sim_info):
        self.rowHeight = 36
        self.lastLapInvalidated = 0
        self.isLapVisuallyEnded = True
        self.raceStarted = False
        self.cars_count = ac.getCarsCount()
        self.pos = 0
        self.driver_name_width = 0
        self.lbl_position_text = Value("")
        self.currentVehicle = Value(-1)
        self.row_height = Value(-1)
        self.cursor = Value(False)
        self.border_direction = Value(-1)
        self.fastestLap = Value(0)
        self.fastest_lap_old = 0
        self.current_car_class=Value("")
        self.font = Value(0)
        self.theme = Value(-1)
        self.sector_delay = 5000
        self.visible_end = 0
        self.nameOffset = 0
        self.lapCanBeInvalidated = True
        self.fastestLapBorderActive = False
        self.driver_in_pit_active = False
        self.forceViewAlways = False
        self.colorsByClass = Value(False)
        self.minLapCount = 1
        self.sectorCount = sim_info.static.sectorCount
        self.lapTimesArray = []
        self.driversLap = []
        for i in range(self.cars_count):
            self.lapTimesArray.append(lapTimeStart(0, 0, 0))
            self.driversLap.append(Value(0))
        self.drivers_info = []
        self.standings = None
        self.track_name = ac.getTrackName(0)
        self.track_config = ac.getTrackConfiguration(0)
        if self.track_config == "":
            self.track_config= "main"
        if self.track_name.find("ks_nordschleife") >= 0 and self.track_config.find("touristenfahrten") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        elif self.track_name.find("drag1000") >= 0 or self.track_name.find("drag400") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        self.session = Value(-1)
        self.window = Window(name="ACTV Info", width=332, height=self.rowHeight * 2)

        self.lbl_driver_name = Label(self.window.app, "")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=0,
                 opacity=0.8)
        self.lbl_fl_driver_name = Label(self.window.app, "")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=0,
                 opacity=0.8)
        self.lbl_driver_name_text = Label(self.window.app, "Loading")\
            .set(w=284, h=self.rowHeight,
                 x=14, y=0,
                 font_size=26,
                 align="left",
                 opacity=0)
        self.driver_name_visible = Value()
        self.driver_name_visible_fin = Value(0)
        self.driver_name_text = Value("")
        self.position_visible = Value(0)
        self.timing_text = Value()
        self.race_fastest_lap = Value(0)
        self.race_fastest_lap_driver = Value()

        self.driver_old_fastest_sectors = []
        self.drivers_lap_count = []
        self.drivers_sector = []
        self.drivers_best_lap_splits = []
        self.drivers_is_in_pit = []
        for _ in range(self.cars_count):
            self.drivers_lap_count.append(Value(0))
            self.drivers_sector.append(Value(0))
            self.drivers_best_lap_splits.append([])
            self.drivers_is_in_pit.append(Value(0))
        self.last_lap_start = [-1] * self.cars_count
        self.last_sector_start = [-1] * self.cars_count
        self.drivers_last_lap_pit = [0] * self.cars_count
        self.drivers_pit_lane_start_time = [0] * self.cars_count
        self.drivers_pit_stop_start_time = [0] * self.cars_count

        self.timing_visible = Value(0)
        self.lbl_timing = Label(self.window.app)\
            .set(w=284, h=self.rowHeight,
                 x=0, y=self.rowHeight)
        self.lbl_timing_text = Label(self.window.app, "Loading")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=self.rowHeight,
                 opacity=0,
                 font_size=26,
                 align="left")
        self.lbl_split = Label(self.window.app, "Loading")\
            .set(w=220, h=self.rowHeight,
                 x=10, y=self.rowHeight,
                 opacity=0,
                 font_size=26,
                 align="right")
        self.lbl_fastest_split = Label(self.window.app, "Loading")\
            .set(w=220, h=self.rowHeight,
                 x=48, y=self.rowHeight,
                 opacity=0,
                 font_size=26,
                 align="right")
        self.info_position = Label(self.window.app)\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0)
        self.info_position_txt = Label(self.window.app, "0")\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0,
                 opacity=0,
                 font_size=26,
                 align="center")
        self.info_position_lead = Label(self.window.app)\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=246, y=self.rowHeight,
                 opacity=1)
        self.info_position_lead_txt = Label(self.window.app, "1")\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=246, y=self.rowHeight,
                 font_size=26,
                 opacity=0,
                 align="center")
        self.lbl_border = Label(self.window.app)\
            .set(w=284, h=2,
                 x=0, y=self.rowHeight)
        self.load_cfg()
        self.info_position.setAnimationSpeed("o", 0.1)
        self.info_position_lead.setAnimationSpeed("o", 0.1)
        self.lbl_split.setAnimationSpeed("a", 0.1)
        self.lbl_fastest_split.setAnimationSpeed("a", 0.1)

    # PUBLIC METHODS
    # ---------------------------------------------------------------------------------------------------------------------------------------------
    def load_cfg(self):
        if Configuration.lapCanBeInvalidated == 1:
            self.lapCanBeInvalidated = True
        else:
            self.lapCanBeInvalidated = False
        if Configuration.forceInfoVisible == 1:
            self.forceViewAlways = True
        else:
            self.forceViewAlways = False
        if Configuration.carColorsBy == 1:
            self.colorsByClass.setValue(True)
        else:
            self.colorsByClass.setValue(False)
        self.row_height.setValue(Configuration.ui_row_height)
        self.font.setValue(Font.current)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.border_direction.setValue(Colors.border_direction)
        self.redraw_size()

    def redraw_size(self):
        # Colors
        if self.theme.hasChanged():
            if self.currentVehicle.value >= 0:
                car_name = ac.getCarName(self.currentVehicle.value)
            else:
                car_name = ac.getCarName(0)
            self.lbl_timing.set(background=Colors.info_timing_bg(),
                                animated=True, init=True)
            self.info_position_lead.set(background=Colors.info_position_first_bg(), animated=True, init=True)
            self.info_position_lead_txt.set(color=Colors.info_position_first_txt(), animated=True, init=True)
            if self.timing_visible.value == 1:
                self.lbl_driver_name.set(background=Colors.info_driver_single_bg(), animated=True, init=True)
                self.lbl_driver_name_text.set(color=Colors.info_driver_single_txt(), animated=True, init=True)
            else:
                self.lbl_driver_name.set(background=Colors.info_driver_bg(), animated=True, init=True)
                self.lbl_driver_name_text.set(color=Colors.info_driver_txt(), animated=True, init=True)
            self.lbl_fastest_split.set(color=Colors.info_fastest_time_txt(), animated=True, init=True)
            self.lbl_timing_text.set(color=Colors.info_timing_txt(), animated=True, init=True)
            self.lbl_fl_driver_name.set(background=Colors.info_driver_bg(), animated=True, init=True)
            class_id = self.get_class_id(self.currentVehicle.value)
            if Colors.border_direction == 1:
                self.lbl_border.set(background=Colors.colorFromCar(car_name, self.colorsByClass.value, Colors.info_border_default_bg(),class_id),
                                    opacity=1, animated=True, init=True)
            else:
                self.lbl_border.set(background=Colors.colorFromCar(car_name, self.colorsByClass.value, Colors.info_border_default_bg(),class_id),
                                    opacity=Colors.border_opacity(), animated=True, init=True)
            if self.pos > 1:
                self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
            else:
                self.info_position.set(background=Colors.info_position_first_bg(), animated=True, init=True)
                self.info_position_txt.set(color=Colors.info_position_first_txt(), animated=True, init=True)

        if self.row_height.hasChanged() or self.font.hasChanged() or self.border_direction.hasChanged():
            # Fonts
            font_offset = Font.get_font_offset()
            self.lbl_driver_name_text.update_font()
            self.lbl_timing_text.update_font()
            self.lbl_split.update_font()
            self.lbl_fastest_split.update_font()
            self.info_position_txt.update_font()
            self.info_position_lead_txt.update_font()
            # UI
            self.rowHeight = self.row_height.value + 2
            font_size = Font.get_font_size(self.rowHeight+font_offset)
            font_size2 = Font.get_font_size(self.row_height.value+font_offset)
            width = self.rowHeight * 7
            self.lbl_driver_name.set(h=self.rowHeight)  # w=width,
            self.lbl_fl_driver_name.set(h=self.rowHeight)  # w=width,
            self.lbl_driver_name_text.set(w=width, h=self.rowHeight, y=Font.get_font_x_offset(),
                                          font_size=font_size)
            self.lbl_timing.set(h=self.row_height.value,
                                y=self.rowHeight)#w=width,
            self.lbl_timing_text.set(w=width * 0.6, h=self.row_height.value,
                                     x=self.rowHeight * 14 / 36, y=self.rowHeight + Font.get_font_x_offset(),
                                     font_size=font_size2)
            self.lbl_split.set(w=self.rowHeight * 4.7, h=self.row_height.value,
                               x=self.rowHeight, y=self.rowHeight + Font.get_font_x_offset(),
                               font_size=font_size2)
            self.lbl_fastest_split.set(w=width, h=self.row_height.value,
                                       x=0, y=self.rowHeight + Font.get_font_x_offset(),
                                       font_size=font_size2)
            self.info_position.set(w=self.rowHeight + 4, h=self.rowHeight)
            self.info_position_txt.set(w=self.rowHeight + 4, h=self.rowHeight,
                                       font_size=font_size, y=Font.get_font_x_offset())
            self.info_position_lead.set(w=self.row_height.value, h=self.row_height.value,
                                        x=width - self.row_height.value, y=self.rowHeight)
            self.info_position_lead_txt.set(w=self.row_height.value, h=self.row_height.value,
                                            x=width - self.row_height.value,
                                            y=self.rowHeight + Font.get_font_x_offset(),
                                            font_size=font_size2)
            if Colors.border_direction == 1:
                self.lbl_border.set(w=4, h=self.rowHeight, x=self.rowHeight + 4, y=0)
            else:
                self.lbl_border.set(w=self.rowHeight * 7, h=2, x=0, y=self.rowHeight)
            self.set_width_and_name()

    def set_drivers_info(self, info):
        self.drivers_info = info

    def get_team(self, currentVehicle):
        if currentVehicle >= 0:
            for driver in self.drivers_info:
                if driver['id'] == currentVehicle:  # or fastest...
                    return str(driver['team'])
        return currentVehicle

    def format_name(self, name, max_name_length):
        space = name.find(" ")
        if space > 0:
            if len(name) > max_name_length and space + 1 < len(name):
                first = ""
                if len(name) > 0:
                    first = name[0].upper() + "."
                name = first + name[space + 1:].upper().lstrip()
                if len(name) > max_name_length:
                    return name[:max_name_length + 1]
                return name
            return name[:space].capitalize().lstrip() + name[space:].upper()
        if len(name) > max_name_length:
            return name[:max_name_length+1].upper().lstrip()
        return name.upper().lstrip()

    def format_tire(self, name):
        space = name.find("(")
        if space > 0:
            name = name[:space]
        name = name.strip()
        if len(name) > 16:
            return name[:17]
        return name

    def time_splitting(self, ms, full="no"):
        ms=abs(ms)
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        if full == "yes":
            d = ms % 1000
            if h > 0:
                return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2),
                                                str(int(d)).zfill(3))
            elif m > 0:
                return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(3))
            else:
                return "{0}.{1}".format(int(s), str(int(d)).zfill(3))
        else:
            d = ms / 100 % 10
            if h > 0:
                return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), int(d))
            elif m > 0:
                return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), int(d))
            else:
                return "{0}.{1}".format(int(s), int(d))

    def get_sector(self,vehicle):
        splits = ac.getCurrentSplits(vehicle)
        sector = 0
        for c in splits:
            if c > 0:
                sector += 1
        return sector

    def get_standings_position(self, vehicle):
        # mainly for replay
        standings = []
        for i in range(self.cars_count):
            bl = ac.getCarState(i, acsys.CS.BestLap)
            if bl > 0 and bool(ac.isConnected(vehicle)):
                standings.append((i, bl))
        standings = sorted(standings, key=lambda student: student[1])
        p = [i for i, v in enumerate(standings) if v[0] == vehicle]
        if len(p) > 0:
            return p[0] + 1
        return 0

    def get_race_standings_position(self, identifier):
        if len(self.standings):
            p = [i for i, v in enumerate(self.standings) if v[0] == identifier]
            if len(p) > 0:
                return p[0] + 1
        return ac.getCarRealTimeLeaderboardPosition(identifier) + 1

    def get_race_standings_position_replay(self, vehicle):
        standings = []
        for i in range(self.cars_count):
            bl = ac.getCarState(i, acsys.CS.LapCount) + ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
            if bl > 0:
                standings.append((i, bl))
        standings = sorted(standings, key=lambda student: student[1], reverse=True)
        p = [i for i, v in enumerate(standings) if v[0] == vehicle]
        if len(p) > 0:
            return p[0] + 1
        return 0

    def animate(self):
        self.lbl_driver_name.animate()
        self.lbl_fl_driver_name.animate()
        self.lbl_driver_name_text.animate()
        self.lbl_timing.animate()
        self.lbl_timing_text.animate()
        self.info_position.animate()
        self.info_position_txt.animate()
        self.info_position_lead.animate()
        self.info_position_lead_txt.animate()
        self.lbl_split.animate()
        self.lbl_fastest_split.animate()
        self.lbl_border.animate()

    def reset_visibility(self):
        self.driver_name_visible.setValue(0)
        self.lbl_driver_name.hide()
        self.lbl_fl_driver_name.hide()
        self.lbl_driver_name_text.hide()
        self.lbl_border.hide()
        self.driver_name_visible_fin.setValue(0)
        self.lbl_timing.hide()
        self.lbl_timing_text.hide()
        self.timing_visible.setValue(0)
        self.lbl_fastest_split.hide()
        self.lbl_split.hide()
        self.info_position_lead.hide()
        self.info_position_lead_txt.hide()
        self.info_position.hide()
        self.info_position_txt.hide()
        self.visible_end = 0
        self.driver_name_text.setValue("")

    def set_width_and_name(self):
        name = self.format_name(self.driver_name_text.value, 17)
        width = (self.rowHeight * 49 / 36) + Font.get_text_dimensions(name, self.rowHeight)
        if width < self.rowHeight * 7.2:
            width = self.rowHeight * 7.2

        '''
        width = Font.get_text_dimensions("WWWWWWWWW", self.rowHeight)
        ac.console("Name length:" + str(width))
        ac.log("Name length:" + str(width))
        width1 = self.get_text_dimensions(name,
                                          Font.get_font_size(self.rowHeight+Font.get_font_offset()),
                                          Font.get_font())

        width = self.rowHeight * 8.6
        name = self.format_name(self.driver_name_text.value, 17)
        if len(name) <= 13:
            width = self.rowHeight * 7.2
        elif len(name) <= 14:
            width = self.rowHeight * 7.5
        elif len(name) <= 15:
            width = self.rowHeight * 7.8
        elif len(name) <= 16:
            width = self.rowHeight * 8.2
        
        '''
        self.driver_name_width = width
        #self.lbl_driver_name.set(w=width, animated=True)
        self.lbl_fl_driver_name.set(w=width, animated=True)
        #self.lbl_driver_name_text.set(w=width, animated=True)
        if Colors.border_direction != 1:
            self.lbl_border.set(w=width, animated=True)
        self.lbl_timing.set(w=width, animated=True)
        self.lbl_fastest_split.set(w=width - self.rowHeight * 14 / 36, animated=True)
        self.info_position_lead.set(x=width - self.row_height.value, animated=True)
        self.info_position_lead_txt.set(x=width - self.row_height.value, animated=True)
        self.lbl_driver_name_text.setText(name)

    def set_driver_name_width(self):
        if Colors.border_direction == 1 and self.info_position.isVisible.value == 1:
            self.lbl_driver_name.set(x=self.rowHeight + 8, w=self.driver_name_width-(self.rowHeight + 8), animated=True)
        elif self.info_position.isVisible.value == 1:
            self.lbl_driver_name.set(x=self.rowHeight + 4, w=self.driver_name_width-(self.rowHeight + 4), animated=True)
        else:
            self.lbl_driver_name.set(x=0, w=self.driver_name_width, animated=True)

    def visibility_qualif(self):
        self.lbl_fastest_split.hide()
        self.lbl_fl_driver_name.hide()
        #if self.driver_name_visible.value == 1 and self.lbl_driver_name.isVisible.value == 0:
        #    self.driver_name_visible.changed = True

        self.driver_name_visible_fin.setValue(self.driver_name_visible.value)
        if self.timing_visible.value == 0:
            self.lbl_timing.hide()
            self.lbl_timing_text.hide()
        else:
            self.lbl_timing.show()
            self.lbl_timing_text.show()
        if self.driver_name_visible.value == 1:
            if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                self.lbl_border.hide()
            else:
                self.lbl_border.show()
        if self.driver_name_visible_fin.hasChanged():
            if self.driver_name_visible_fin.value == 0:
                self.lbl_driver_name.hide()
                self.lbl_driver_name_text.hide()
                self.lbl_border.hide()
            else:
                #if self.timing_visible.value == 1:
                self.lbl_driver_name.set(background=Colors.info_driver_bg()).show()
                self.lbl_driver_name_text.set(color=Colors.info_driver_txt()).show()
                #else: never happening
                #    self.lbl_driver_name.setBgColor(Colors.info_driver_single_bg()).show()
                #    self.lbl_driver_name_text.setColor(Colors.info_driver_single_txt()).show()
                if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                    self.lbl_border.hide()
                else:
                    self.lbl_border.show()
        if Colors.border_direction == 1 and self.info_position.isVisible.value == 1:
            self.nameOffset += 4
        self.lbl_driver_name_text.set(x=self.nameOffset, animated=True)
        if self.driver_name_text.hasChanged():
            self.set_width_and_name()
        self.set_driver_name_width()
        if self.timing_text.hasChanged():
            self.lbl_timing_text.setText(self.timing_text.value)

    def visibility_race(self):
        if self.timing_visible.value == 0:
            self.lbl_timing.hide()
            self.lbl_timing_text.hide()
        else:
            self.lbl_timing.show()
            self.lbl_timing_text.show()

        if self.driver_name_visible.value == 1:
            if self.timing_visible.value == 1:
                #self.lbl_driver_name.set(background=Colors.info_driver_bg())
                self.lbl_driver_name_text.set(color=Colors.info_driver_txt())
            else:
                self.lbl_driver_name.setBgColor(Colors.info_driver_single_bg())
                self.lbl_driver_name_text.setColor(Colors.info_driver_single_txt())
            if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                self.lbl_border.hide()
            else:
                self.lbl_border.show()

        if self.driver_name_visible.value == 0:
            self.lbl_driver_name.hide()
            self.lbl_fl_driver_name.hide()
            self.lbl_driver_name_text.hide()
            self.lbl_border.hide()
        else:
            if self.fastestLapBorderActive:
                self.lbl_fl_driver_name.show()
                self.lbl_driver_name.hide()
            else:
                self.lbl_driver_name.show()
                self.lbl_fl_driver_name.hide()
            self.lbl_driver_name_text.show()
            if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                self.lbl_border.hide()
            else:
                self.lbl_border.show()

        self.lbl_driver_name_text.set(x=self.nameOffset, animated=True)
        if self.driver_name_text.hasChanged():
            self.set_width_and_name()
        if not self.fastestLapBorderActive:
            self.set_driver_name_width()
        if self.timing_text.hasChanged():
            self.lbl_timing_text.setText(self.timing_text.value, hidden=bool(self.timing_visible.value == 0))

    def get_class_id(self, identifier):
        if self.standings is not None and len(self.standings):
            for s in self.standings:
                if s[0] == identifier:
                    return s[2]
        return Colors.getClassForCar(ac.getCarName(identifier))

    def manage_window(self, game_data):
        win_x = self.window.getPos().x
        win_y = self.window.getPos().y
        if win_x > 0:
            self.window.last_x = win_x
            self.window.last_y = win_y
        else:
            self.window.setLastPos()
            win_x = self.window.getPos().x
            win_y = self.window.getPos().y
        if win_x < game_data.cursor_x < win_x + self.window.width and win_y < game_data.cursor_y < win_y + self.window.height:
            self.cursor.setValue(True)
        else:
            self.cursor.setValue(False)

        session_changed = self.session.hasChanged()
        if session_changed:
            self.reset_visibility()
            self.raceStarted = False
            self.driver_in_pit_active = False
            self.driver_old_fastest_sectors = []
            self.drivers_lap_count = []
            self.drivers_sector = []
            self.drivers_best_lap_splits = []
            self.drivers_is_in_pit = []
            self.last_sector_start = [-1] * self.cars_count
            for i in range(self.cars_count):
                self.drivers_lap_count.append(Value(0))
                self.drivers_sector.append(Value(0))
                self.drivers_best_lap_splits.append([])
                self.drivers_is_in_pit.append(Value(0))
                self.last_sector_start[i] = game_data.sessionTimeLeft
            self.last_lap_start = [-1] * self.cars_count
            self.drivers_last_lap_pit = [0] * self.cars_count
            self.drivers_pit_lane_start_time = [0] * self.cars_count
            self.drivers_pit_stop_start_time = [0] * self.cars_count
        if self.cursor.hasChanged() or session_changed:
            if self.cursor.value and self.driver_name_visible.value == 0:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)

    def on_update(self, sim_info, fl, standings, game_data):
        self.standings = standings
        self.session.setValue(game_data.session)
        sim_info_status = game_data.status
        session_time_left = game_data.sessionTimeLeft
        if (sim_info_status != 1 and sim_info_status != 3 and session_time_left != 0 and session_time_left != -1 and session_time_left + 100 < game_data.sessionTimeLeft) or sim_info_status == 0:
            self.session.setValue(-1)
            self.session.setValue(game_data.session)
        self.manage_window(game_data)
        self.animate()
        self.currentVehicle.setValue(game_data.focusedCar)

        for x in range(self.cars_count):
            c = ac.getCarState(x, acsys.CS.LapCount)
            self.driversLap[x].setValue(c)
            if self.driversLap[x].hasChanged():
                self.lapTimesArray[x].lap = self.driversLap[x].value
                self.lapTimesArray[x].time = session_time_left
            if bool(ac.isCarInPitline(x)) or bool(ac.isCarInPit(x)):
                self.lapTimesArray[x].lastpit = c

        backup_laptime = self.lapTimesArray[self.currentVehicle.value].time - session_time_left
        backup_last_lap_in_pits = self.lapTimesArray[self.currentVehicle.value].lastpit
        current_vehicle_changed = self.currentVehicle.hasChanged()
        self.current_car_class.setValue(self.get_class_id(self.currentVehicle.value))
        if self.colorsByClass.hasChanged() and not self.fastestLapBorderActive:
            car = ac.getCarName(self.currentVehicle.value)
            self.lbl_border.setBgColor(Colors.colorFromCar(car, self.colorsByClass.value, Colors.info_border_default_bg(),self.current_car_class.value))

        if current_vehicle_changed or self.current_car_class.hasChanged() or (self.fastestLapBorderActive and session_time_left < self.visible_end - 2000):
            self.fastestLapBorderActive = False
            car = ac.getCarName(self.currentVehicle.value)
            self.lbl_border.setBgColor(Colors.colorFromCar(car, self.colorsByClass.value, Colors.info_border_default_bg(),self.current_car_class.value))
            self.driver_in_pit_active = False

        if sim_info_status == 2:
            # LIVE
            #str_offset = "  "
            # self.nameOffset=14
            if self.session.value != 2:
                # NOT RACE
                # qtime
                # check sector/laps changes
                chk_fl=0
                fastest_lap_driver_id=0
                for i in range(self.cars_count):
                    if ac.isConnected(i) > 0:
                        c = ac.getCarState(i, acsys.CS.BestLap)
                        if chk_fl==0 or 0 < c < chk_fl:
                            chk_fl=c
                            fastest_lap_driver_id=i

                        self.drivers_lap_count[i].setValue(ac.getCarState(i, acsys.CS.LapCount))
                        self.drivers_sector[i].setValue(self.get_sector(i))
                        if self.drivers_sector[i].hasChanged():
                            self.last_sector_start[i] = session_time_left

                        if self.last_lap_start[i] == -1 and not math.isinf(session_time_left) and session_time_left != 0:
                            self.last_lap_start[i] = self.last_sector_start[i] = session_time_left
                        if self.drivers_lap_count[i].hasChanged() and not math.isinf(session_time_left):
                            self.last_lap_start[i] = self.last_sector_start[i] = session_time_left
                            # if PB save delta
                            if ac.getCarState(i, acsys.CS.LastLap) <= ac.getCarState(i, acsys.CS.BestLap):
                                # save fastest lap sectors
                                self.drivers_best_lap_splits[i] = ac.getLastSplits(i)
                        if ac.isCarInPit(i) or ac.isCarInPitline(i):
                            self.drivers_last_lap_pit[i] = self.drivers_lap_count[i].value

                self.fastestLap.setValue(fl)
                is_in_pit = bool(ac.isCarInPitline(self.currentVehicle.value)) or \
                            bool(ac.isCarInPit(self.currentVehicle.value))
                lap_count = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
                cur_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
                if cur_lap_time == 0 and backup_laptime > 0 and self.minLapCount > 0:
                    cur_lap_time = backup_laptime

                if self.currentVehicle.value == 0 and sim_info.physics.numberOfTyresOut >= 4 and self.lapCanBeInvalidated:
                    self.lastLapInvalidated = lap_count
                if is_in_pit and self.minLapCount == 0:
                    self.lastLapInvalidated = -1

                lap_invalidated = bool(self.lastLapInvalidated == lap_count)
                if current_vehicle_changed or self.driver_name_text.value == "":
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                # sector_delay = 5000
                # live or info
                if self.drivers_last_lap_pit[self.currentVehicle.value] + self.minLapCount <= self.drivers_lap_count[self.currentVehicle.value].value and (self.currentVehicle.value != 0 or (self.currentVehicle.value == 0 and not lap_invalidated)):
                    sector = self.get_sector(self.currentVehicle.value)
                    self.driver_name_visible.setValue(1)
                    self.timing_visible.setValue(1)

                    last_lap = ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap)

                    traite = False
                    self.isLapVisuallyEnded = True
                    cur_splits = ac.getCurrentSplits(self.currentVehicle.value)
                    time_split = 0
                    fastest_split = 0
                    i = 0
                    show_split = False
                    for c in cur_splits:
                        if c > 0:
                            time_split += c
                            if len(self.drivers_best_lap_splits[fastest_lap_driver_id]) > i:
                                fastest_split+=self.drivers_best_lap_splits[fastest_lap_driver_id][i]
                            i += 1
                    fastest_split_fin = fastest_split
                    if len(self.drivers_best_lap_splits[fastest_lap_driver_id]) > i:
                        fastest_split_fin += self.drivers_best_lap_splits[fastest_lap_driver_id][i]

                    # Situation
                    for s in range(0, self.sectorCount):
                        if self.fastestLap.value > 0 and cur_lap_time > fastest_split_fin - self.sector_delay:
                            # LAST_SECONDS_OF_SECTOR_X, sector == s and
                            self.isLapVisuallyEnded = False
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            if self.sectorCount - 1 == sector:
                                # LAST_SECONDS_OF_SECTOR_LAP,
                                self.lbl_split.setText(self.time_splitting(self.fastestLap.value, "yes"))\
                                    .setColor(Colors.info_split_txt()).show()
                                self.info_position_lead.show()
                                self.info_position_lead_txt.show()
                                self.fastest_lap_old = self.fastestLap.value
                                show_split = True
                            elif fastest_split_fin > 0:
                                self.lbl_split.setText(self.time_splitting(fastest_split_fin, "yes")).setColor(
                                    Colors.info_split_txt()).show()
                                self.info_position_lead.show()
                                self.info_position_lead_txt.show()
                                show_split = True
                            break
                        #if sector == s + 1 and s + 1 <= self.sectorCount and cur_lap_time - time_split <= self.sector_delay and fastest_split > 0:
                        if sector == s + 1 and s + 1 <= self.sectorCount and cur_lap_time - time_split <= self.sector_delay:
                            # SECTOR_X_FINISHED_BEGIN_SECTOR_Y
                            self.isLapVisuallyEnded = False
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.timing_text.setValue(self.time_splitting(time_split, "yes"))
                            if fastest_split < time_split:
                                self.lbl_split.setText(
                                    "+" + self.time_splitting(time_split - fastest_split, "yes")).setColor(
                                    Colors.info_split_positive_txt()).show()
                            else:
                                self.lbl_split.setText(
                                    "-" + self.time_splitting(fastest_split - time_split, "yes")).setColor(
                                    Colors.info_split_negative_txt()).show()
                            self.info_position_lead.show()
                            self.info_position_lead_txt.show()
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            traite = True
                            break

                    if not traite:
                        if self.sectorCount - 1 == sector and self.fastestLap.value > 0 and cur_lap_time > self.fastestLap.value - self.sector_delay:
                            # LAST_SECONDS_OF_SECTOR_LAP,
                            self.isLapVisuallyEnded = False
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.timing_text.setValue(self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            # self.lbl_split.setText(self.time_splitting(self.fastestLap,"yes") + str_offset).setVisible(1)
                        elif self.lastLapInvalidated != lap_count - 1 and ((self.drivers_last_lap_pit[self.currentVehicle.value] != self.drivers_lap_count[self.currentVehicle.value].value - 1 and sector == 0) or (self.minLapCount == 0)) and cur_lap_time <= self.sector_delay and last_lap > 0:
                            #elif self.lastLapInvalidated != lap_count - 1 and ((self.lastLapInPit != lap_count - 1 and sector == 0) or (self.minLapCount == 0)) and cur_lap_time <= self.sector_delay and last_lap > 0:
                            # LAP_FINISHED_BEGIN_NEW_LAP,
                            self.isLapVisuallyEnded = False
                            pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                            if pos == -1:
                                pos = self.get_standings_position(self.currentVehicle.value)
                            self.pos = pos
                            if pos > 1:
                                self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                                self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                            else:
                                self.info_position.set(background=Colors.info_position_first_bg(), animated=True, init=True)
                                self.info_position_txt.set(color=Colors.info_position_first_txt(), animated=True, init=True)
                            self.info_position_txt.setText(str(pos)).show()
                            self.info_position.show()

                            self.nameOffset = self.rowHeight * 49 / 36  # 49
                            self.timing_text.setValue(self.time_splitting(last_lap, "yes"))
                            if self.fastestLap.value < last_lap:
                                self.lbl_split.setText("+" + self.time_splitting(last_lap - self.fastestLap.value, "yes"))\
                                    .setColor(Colors.info_split_positive_txt()).show()
                            else:
                                self.lbl_split.setText("-" + self.time_splitting(self.fastest_lap_old - last_lap, "yes"))\
                                    .setColor(Colors.info_split_negative_txt()).show()
                            self.info_position_lead.show()
                            self.info_position_lead_txt.show()

                        else:
                            # OTHER
                            self.isLapVisuallyEnded = True
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.timing_text.setValue(self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            self.info_position_txt.hide()
                            if not show_split:
                                self.lbl_split.hide()
                                self.info_position_lead.hide()
                                self.info_position_lead_txt.hide()
                    self.fastestLap.changed = False
                else:
                    bestlap = ac.getCarState(self.currentVehicle.value, acsys.CS.BestLap)
                    self.isLapVisuallyEnded = True
                    self.info_position_lead.hide()
                    self.info_position_lead_txt.hide()
                    spline_position = ac.getCarState(self.currentVehicle.value, acsys.CS.NormalizedSplinePosition)
                    if spline_position <= 0.001:
                        spline_position = 1
                    if session_time_left > 0 and self.minLapCount == 1 and spline_position > 0.95 and not is_in_pit:
                        self.driver_name_visible.setValue(1)
                        self.nameOffset = self.rowHeight * 14 / 36
                        self.timing_visible.setValue(1)
                        self.lbl_split.hide()
                        self.info_position.hide()
                        self.info_position_txt.hide()
                        self.timing_text.setValue("0.0")
                    elif (self.currentVehicle.value != 0 or (self.currentVehicle.value == 0 and not lap_invalidated)) and self.drivers_last_lap_pit[self.currentVehicle.value] < self.drivers_lap_count[self.currentVehicle.value].value and self.minLapCount > 0:
                        self.driver_name_visible.setValue(Configuration.forceInfoVisible)
                        self.timing_visible.setValue(0)
                        self.lbl_split.hide()
                        self.info_position.hide()
                        self.info_position_txt.hide()
                    elif bestlap > 0:
                        if Configuration.forceInfoVisible == 1:
                            self.driver_name_visible.setValue(1)
                            self.timing_visible.setValue(1)
                            if self.fastestLap.value < bestlap:
                                self.lbl_split.setText("+" + self.time_splitting(bestlap - self.fastestLap.value, "yes"))\
                                    .setColor(Colors.info_split_positive_txt()).show()
                            else:
                                self.lbl_split.hide()
                            self.timing_text.setValue(self.time_splitting(bestlap, "yes"))
                            self.nameOffset = self.rowHeight * 49 / 36
                            pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                            if pos == -1:
                                pos = self.get_standings_position(self.currentVehicle.value)
                            self.pos = pos
                            if pos > 1:
                                self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                                self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                            else:
                                self.info_position.set(background=Colors.info_position_first_bg(), animated=True, init=True)
                                self.info_position_txt.set(color=Colors.info_position_first_txt(), animated=True, init=True)
                            self.info_position.show()
                            self.info_position_txt.setText(str(pos)).show()
                            self.lbl_position_text.setValue(str(pos))
                        else:
                            self.driver_name_visible.setValue(0)
                            self.timing_visible.setValue(0)
                            self.lbl_split.hide()
                            self.info_position.hide()
                            self.info_position_txt.hide()

                    elif is_in_pit:
                        self.nameOffset = self.rowHeight * 14 / 36
                        self.driver_name_visible.setValue(Configuration.forceInfoVisible)
                        self.timing_visible.setValue(0)
                        self.lbl_split.hide()
                        self.info_position.hide()
                        self.info_position_txt.hide()
                    else:
                        self.nameOffset = self.rowHeight * 14 / 36  # 14
                        self.driver_name_visible.setValue(1)
                        self.timing_visible.setValue(1)
                        if self.currentVehicle.value == 0:
                            self.timing_text.setValue(self.format_tire(sim_info.graphics.tyreCompound))
                        else:
                            self.timing_text.setValue("Out Lap")
                        self.lbl_split.hide()
                        self.info_position.hide()
                        self.info_position_txt.hide()
                if cur_lap_time <= self.sector_delay and ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap) > 0 and backup_last_lap_in_pits + 1 < ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount) and session_time_left < 0:
                    self.nameOffset = self.rowHeight * 49 / 36  # 49
                    self.driver_name_visible.setValue(1)
                    self.timing_visible.setValue(1)
                    self.lbl_split.show()
                    self.info_position.show()
                    self.info_position_txt.show()
                self.visibility_qualif()

            else:
                # ------------- Race -------------
                self.info_position_lead.hide()
                self.info_position_lead_txt.hide()
                self.lbl_split.hide()
                # fastest lap
                completed = 0
                for x in range(self.cars_count):
                    pit_lane = bool(ac.isCarInPitline(x))
                    pit_box = bool(ac.isCarInPit(x))
                    self.drivers_is_in_pit[x].setValue(pit_lane or pit_box)
                    if self.drivers_is_in_pit[x].hasChanged():
                        if self.drivers_is_in_pit[x].value:
                            self.drivers_pit_lane_start_time[x] = session_time_left

                    c = ac.getCarState(x, acsys.CS.LapCount)
                    if c > completed:
                        completed = c
                if completed <= 1:
                    self.race_fastest_lap.setValue(0)
                else:
                    for i in range(self.cars_count):
                        bl = ac.getCarState(i, acsys.CS.BestLap)
                        l = ac.getCarState(i, acsys.CS.LapCount)
                        if bl > 0 and l > self.minLapCount and (self.race_fastest_lap.value == 0 or bl < self.race_fastest_lap.value):
                            self.race_fastest_lap.setValue(bl)
                            self.race_fastest_lap_driver.setValue(i)

                is_in_pit = self.drivers_is_in_pit[self.currentVehicle.value].value
                if self.race_fastest_lap.hasChanged() and self.race_fastest_lap.value > 0 and not is_in_pit:
                    self.fastestLapBorderActive = True
                    car = ac.getCarName(self.race_fastest_lap_driver.value)
                    class_id = self.get_class_id(self.race_fastest_lap_driver.value)
                    self.lbl_border.setBgColor(Colors.colorFromCar(car, self.colorsByClass.value, Colors.info_border_default_bg(),class_id))
                    self.visible_end = session_time_left - 10000
                    self.driver_name_visible.setValue(1)
                    self.driver_name_text.setValue(ac.getDriverName(self.race_fastest_lap_driver.value))
                    self.nameOffset = self.rowHeight * 14 / 36  # 14
                    self.timing_text.setValue("Fastest Lap")
                    self.timing_visible.setValue(1)
                    self.info_position.hide()
                    self.info_position_txt.hide()
                    self.lbl_fastest_split.setText(self.time_splitting(self.race_fastest_lap.value, "yes")).show()
                elif current_vehicle_changed or (self.forceViewAlways and not self.fastestLapBorderActive) or is_in_pit:
                    # driver info
                    if is_in_pit and not ac.getCarState(self.currentVehicle.value, acsys.CS.RaceFinished) and not math.isinf(session_time_left):
                        self.driver_in_pit_active = True
                        self.timing_text.setValue("Pit Lane")
                        self.timing_visible.setValue(1)
                        pit_lane_time = self.drivers_pit_lane_start_time[self.currentVehicle.value] - session_time_left
                        self.lbl_fastest_split.setText(self.time_splitting(pit_lane_time)).show()
                    elif session_time_left < self.visible_end or self.visible_end == 0:
                        self.lbl_fastest_split.hide()

                    if not self.forceViewAlways or is_in_pit:
                        self.visible_end = session_time_left - 8000
                    self.driver_name_visible.setValue(1)
                    # if current_vehicle_changed:
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                    self.nameOffset = self.rowHeight * 49 / 36
                    if Colors.border_direction == 1:
                        self.nameOffset += 4
                    if not self.raceStarted:
                        if sim_info.graphics.completedLaps > 0 or sim_info.graphics.iCurrentTime > 20000:
                            self.raceStarted = True
                        # Generate standings from -0.5 to 0.5 for the start of race
                        standings = []
                        for i in range(self.cars_count):
                            bl = ac.getCarState(i, acsys.CS.LapCount) + ac.getCarState(i,acsys.CS.NormalizedSplinePosition)
                            if bl < 0.5:
                                bl += 0.5  # 0.1 = 0.6
                            elif 0.5 <= bl < 1:
                                bl -= 0.5  # 0.9 = 0.4
                            standings.append((i, bl))
                        standings = sorted(standings, key=lambda student: student[1], reverse=True)
                        p = [i for i, v in enumerate(standings) if v[0] == self.currentVehicle.value]
                        if len(p) > 0:
                            pos = p[0] + 1
                        else:
                            pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicle.value) + 1
                    else:
                        if game_data.beforeRaceStart:
                            self.raceStarted = False
                        pos = self.get_race_standings_position(self.currentVehicle.value)
                    self.pos = pos
                    if pos > 1:
                        self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                        self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                    else:
                        self.info_position.set(background=Colors.info_position_first_bg(), animated=True, init=True)
                        self.info_position_txt.set(color=Colors.info_position_first_txt(), animated=True, init=True)
                    self.info_position.show()
                    self.info_position_txt.setText(str(pos)).show()
                    self.timing_visible.setValue(0)
                    self.lbl_fastest_split.hide()
                elif self.visible_end == 0 or session_time_left < self.visible_end or game_data.beforeRaceStart:
                    self.driver_name_visible.setValue(0)
                    self.info_position.hide()
                    self.info_position_txt.hide()
                    self.timing_visible.setValue(0)
                    self.lbl_fastest_split.hide()
                if session_time_left < self.visible_end and self.visible_end != 0:
                    self.driver_in_pit_active = False
                self.visibility_race()
        elif sim_info_status == 1 and self.session.value != 2:
            # Replay Qualif
            show_split = False
            lap_count = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
            cur_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
            is_in_pit = (bool(ac.isCarInPitline(self.currentVehicle.value)) or bool(ac.isCarInPit(self.currentVehicle.value)))
            if current_vehicle_changed or self.driver_name_text.value == "":
                self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
            if is_in_pit:
                self.driver_name_visible.setValue(0)
                self.timing_visible.setValue(0)
                self.lbl_split.hide()
                self.info_position.hide()
                self.info_position_txt.hide()
            elif cur_lap_time <= self.sector_delay and lap_count > 1:
                # show last lap
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(1)
                if self.currentVehicle.value == 0:
                    last_lap = sim_info.graphics.iLastTime
                else:
                    last_lap = 0
                    last_splits = ac.getLastSplits(self.currentVehicle.value)
                    for c in last_splits:
                        last_lap += c
                    if last_lap == 0:
                        last_lap = ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap)
                pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                if pos == -1:
                    pos = self.get_standings_position(self.currentVehicle.value)
                self.pos = pos
                if pos > 1:
                    self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                    self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                else:
                    self.info_position.set(background=Colors.info_position_first_bg(), animated=True, init=True)
                    self.info_position_txt.set(color=Colors.info_position_first_txt(), animated=True, init=True)
                self.info_position_txt.setText(str(pos)).show()
                self.info_position.show()
                self.nameOffset = self.rowHeight * 49 / 36  # 49
                self.timing_text.setValue(self.time_splitting(last_lap, "yes"))
                if self.fastestLap.value < last_lap:
                    self.lbl_split.setText("+" + self.time_splitting(last_lap - self.fastestLap.value, "yes"))\
                        .setColor(Colors.info_split_positive_txt()).show()
                else:
                    self.lbl_split.setText("-" + self.time_splitting(self.fastestLap.old - last_lap, "yes"))\
                        .setColor(Colors.info_split_negative_txt()).show()
                self.info_position_lead.show()
                self.info_position_lead_txt.show()
                self.fastestLap.changed = False
            elif lap_count > self.minLapCount:
                # showTiming
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(1)
                self.info_position_lead.hide()
                self.info_position_lead_txt.hide()
                self.nameOffset = self.rowHeight * 14 / 36  # 14
                self.timing_text.setValue(self.time_splitting(cur_lap_time))
                self.info_position.hide()
                self.info_position_txt.hide()
                if not show_split:
                    self.lbl_split.hide()
                    self.info_position_lead.hide()
                    self.info_position_lead_txt.hide()
            else:
                # showTireInfo
                self.info_position_lead.hide()
                self.info_position_lead_txt.hide()
                self.nameOffset = self.rowHeight * 14 / 36  # 14
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(1)
                if self.currentVehicle.value == 0:
                    self.timing_text.setValue(self.format_tire(sim_info.graphics.tyreCompound))
                else:
                    self.timing_text.setValue("Out Lap")
                self.lbl_split.hide()
                self.info_position.hide()
                self.info_position_txt.hide()
            self.visibility_qualif()
        elif sim_info_status == 1 and self.session.value == 2:
            # Replay Race
            self.info_position_lead.hide()
            self.info_position_lead_txt.hide()
            self.lbl_split.hide()
            if current_vehicle_changed or (self.forceViewAlways and not self.fastestLapBorderActive):
                # driver info
                if not self.forceViewAlways:
                    self.visible_end = session_time_left - 8000
                self.driver_name_visible.setValue(1)
                # if current_vehicle_changed:
                self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                self.nameOffset = self.rowHeight * 49 / 36
                # pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicle.value) + 1
                # pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                pos = self.get_race_standings_position_replay(self.currentVehicle.value)
                self.pos = pos
                if pos > 1:
                    self.info_position.set(background=Colors.info_position_bg(), animated=True, init=True)
                    self.info_position_txt.set(color=Colors.info_position_txt(), animated=True, init=True)
                else:
                    self.info_position.set(background=Colors.info_position_first_bg(), animated=True, init=True)
                    self.info_position_txt.set(color=Colors.info_position_first_txt(), animated=True, init=True)
                self.info_position.show()
                self.info_position_txt.setText(str(pos)).show()
                self.timing_visible.setValue(0)
                self.lbl_fastest_split.hide()
            elif self.visible_end == 0 or session_time_left < self.visible_end or game_data.beforeRaceStart:
                self.driver_name_visible.setValue(0)
                self.info_position.hide()
                self.info_position_txt.hide()
                self.timing_visible.setValue(0)
                self.lbl_fastest_split.hide()
            self.visibility_race()
        else:
            # REPLAY
            self.reset_visibility()
