import ac
import acsys
import ctypes
from apps.util.classes import Window, Label, Value, POINT, Colors, Config, Font


class lapTimeStart:
    def __init__(self, lap, time, lastpit):
        self.lap = lap
        self.time = time
        self.lastpit = lastpit


class ACInfo:
    # INITIALIZATION
    def __init__(self):
        self.rowHeight = 36
        self.font_offset = 0
        self.lastLapInPit = 0
        self.lastLapInvalidated = 0
        self.isLapVisuallyEnded = True
        self.raceStarted = False
        self.carsCount = 0
        self.lbl_position_height = 0
        self.lbl_position_text = Value("")
        self.currentVehicle = Value(-1)
        self.ui_row_height = Value(-1)
        self.cursor = Value(False)
        self.fastestLap = Value(0)
        self.fastestLap2 = Value(0)
        self.font = Value(0)
        self.fastestPos = 1
        self.lastLap = 0
        self.lastLapStart = 10000
        self.sector_delay = 5000
        self.lastTimeInPit = 0
        self.visible_end = 0
        self.lastLapTime = 0
        self.nameOffset = 0
        self.nameOffsetValue = Value(0)
        self.lapCanBeInvalidated = True
        self.fastestLapBorderActive = False
        self.firstLapStarted = False
        self.forceViewAlways = False
        self.colorsByClass = Value(False)
        self.minLapCount = 1
        self.sectorCount = -1
        self.lapTimesArray = []
        self.driversLap = []
        self.standings = None
        track = ac.getTrackName(0)
        config = ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife") >= 0 and config.find("touristenfahrten") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        elif track.find("drag1000") >= 0 or track.find("drag400") >= 0:
            self.minLapCount = 0
            self.lastLapInvalidated = -1
        self.fastestLapSectors = [0, 0, 0, 0, 0, 0]
        self.session = Value(-1)
        # self.session.setValue()
        self.window = Window(name="ACTV Info", icon=False, width=332, height=self.rowHeight * 2, texture="")

        self.lbl_driver_name = Label(self.window.app, "")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=0,
                 background=Colors.background_dark(),
                 opacity=0.8,
                 visible=0)
        self.lbl_driver_name_text = Label(self.window.app, "Loading")\
            .set(w=284, h=self.rowHeight,
                 x=14, y=0,
                 font_size=26,
                 align="left",
                 color=Colors.font_color(),
                 visible=0)
        self.driver_name_visible = Value()
        self.driver_name_visible_fin = Value(0)
        self.driver_name_text = Value("")
        self.position_visible = Value(0)
        self.timing_text = Value()
        self.race_fastest_lap = Value(0)
        # self.race_fastest_lap.setValue(0)
        self.race_fastest_lap_driver = Value()
        self.timing_visible = Value(0)
        self.lbl_timing = Label(self.window.app, "")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=self.rowHeight,
                 background=Colors.background(),
                 opacity=Colors.background_opacity(),
                 visible=0)
        self.lbl_timing_text = Label(self.window.app, "Loading")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=self.rowHeight,
                 font_size=26,
                 align="left",
                 visible=0)
        self.lbl_split = Label(self.window.app, "Loading")\
            .set(w=220, h=self.rowHeight,
                 x=10, y=self.rowHeight,
                 font_size=26,
                 align="right",
                 color=Colors.font_color(),
                 visible=0)
        self.lbl_fastest_split = Label(self.window.app, "Loading")\
            .set(w=220, h=self.rowHeight,
                 x=48, y=self.rowHeight,
                 font_size=26,
                 color=Colors.font_color(),
                 align="right",
                 visible=0)
        self.info_position = Label(self.window.app, "0")\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0,
                 font_size=26,
                 align="center",
                 background=Colors.background_first(),
                 opacity=1,
                 visible=0)
        self.info_position_lead = Label(self.window.app, "1")\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=246, y=self.rowHeight,
                 font_size=26,
                 align="center",
                 background=Colors.background_first(),
                 opacity=1,
                 visible=0)
        car = ac.getCarName(0)
        self.lbl_border = Label(self.window.app, "")\
            .set(w=284, h=1,
                 x=0, y=self.rowHeight,
                 background=Colors.colorFromCar(car, self.colorsByClass.value),
                 opacity=Colors.border_opacity(),
                 visible=0)
        self.load_cfg()
        self.info_position.setAnimationSpeed("o", 0.1)
        self.info_position_lead.setAnimationSpeed("o", 0.1)
        self.lbl_split.setAnimationSpeed("a", 0.1)
        self.lbl_fastest_split.setAnimationSpeed("a", 0.1)

    # PUBLIC METHODS
    # ---------------------------------------------------------------------------------------------------------------------------------------------
    def load_cfg(self):
        cfg = Config("apps/python/prunn/", "config.ini")
        if cfg.get("SETTINGS", "lap_can_be_invalidated", "int") == 1:
            self.lapCanBeInvalidated = True
        else:
            self.lapCanBeInvalidated = False
        if cfg.get("SETTINGS", "force_info_visible", "int") == 1:
            self.forceViewAlways = True
        else:
            self.forceViewAlways = False
        if cfg.get("SETTINGS", "car_colors_by", "int") == 1:
            self.colorsByClass.setValue(True)
        else:
            self.colorsByClass.setValue(False)
        self.ui_row_height.setValue(cfg.get("SETTINGS", "ui_row_height", "int"))
        self.font.setValue(Font.current)
        #if self.ui_row_height.hasChanged() or self.font.hasChanged():
        self.redraw_size()
        # self.info_position.setBgColor(Colors.theme(bg = True, reload = True))

    def redraw_size(self):
        # Fonts
        self.font_offset = Font.get_font_offset()
        self.lbl_driver_name_text.update_font()
        self.lbl_timing_text.update_font()
        self.lbl_split.update_font()
        self.lbl_fastest_split.update_font()
        self.info_position.update_font()
        self.info_position_lead.update_font()
        # UI
        if Colors.general_theme == 2:
            self.lbl_timing.set(background=Colors.background_info_position(), opacity=Colors.background_opacity())
        else:
            self.lbl_timing.set(background=Colors.background(), opacity=Colors.background_opacity())
        self.info_position_lead.set(background=Colors.background_first())
        if Colors.themed_info == 1 and self.timing_visible.value == 1:
            self.lbl_driver_name.setBgColor(Colors.theme(bg=True))
            self.lbl_driver_name_text.setColor(Colors.white())
        else:
            self.lbl_driver_name.setBgColor(Colors.background_dark())
            self.lbl_driver_name_text.setColor(Colors.font_color())
        self.lbl_fastest_split.set(color=Colors.font_color())
        self.rowHeight = self.ui_row_height.value + 2
        font_size = Font.get_font_size(self.rowHeight+self.font_offset)
        row2_height = self.ui_row_height.value
        font_size2 = Font.get_font_size(row2_height+self.font_offset)
        width = self.rowHeight * 7
        self.lbl_driver_name.set(w=width, h=self.rowHeight)
        self.lbl_driver_name_text.set(w=width, h=self.rowHeight,
                                      font_size=font_size)
        self.lbl_timing.set(w=width, h=row2_height,
                            x=0, y=self.rowHeight)
        self.lbl_timing_text.set(w=width * 0.6, h=row2_height,
                                 x=self.rowHeight * 14 / 36, y=self.rowHeight,
                                 color=Colors.font_color(),
                                 font_size=font_size2)
        self.lbl_split.set(w=self.rowHeight * 4.7, h=row2_height,
                           x=self.rowHeight, y=self.rowHeight,
                           font_size=font_size2)
        #self.lbl_fastest_split.set(w=self.rowHeight * 5.7, h=row2_height,
        #                           x=self.rowHeight, y=self.rowHeight,
        #                           font_size=font_size2)
        self.lbl_fastest_split.set(w=width, h=row2_height,
                                   x=0, y=self.rowHeight,
                                   font_size=font_size2)
        self.info_position.set(w=self.rowHeight + 4, h=self.rowHeight,
                               font_size=font_size)
        self.info_position_lead.set(w=row2_height, h=row2_height,
                                    x=width - row2_height, y=self.rowHeight,
                                    font_size=font_size2)
        if Colors.border_direction == 1:
            self.lbl_border.set(w=4, h=self.rowHeight, x=self.rowHeight + 4, y=0, opacity=1)
            if not self.lbl_border.isVisible.value:
                self.lbl_border.hide()
        else:
            self.lbl_border.set(w=width, h=1, x=0, y=self.rowHeight)
        self.reset_visibility()

    def format_name(self, name, max_name_length):
        space = name.find(" ")
        if space > 0:
            if len(name) > max_name_length and space + 1 < len(name):
                return name[space + 1:].upper().lstrip()
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

    def get_sector(self):
        splits = ac.getCurrentSplits(self.currentVehicle.value)
        i = 0
        sector = 0
        for c in splits:
            i += 1
            if c > 0:
                sector = i
        return sector

    def get_standings_position(self, vehicle):
        # mainly for replay
        standings = []
        for i in range(self.carsCount):
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
        for i in range(self.carsCount):
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
        self.lbl_driver_name_text.animate()
        self.lbl_timing.animate()
        self.lbl_timing_text.animate()
        self.info_position.animate()
        self.info_position_lead.animate()
        self.lbl_split.animate()
        self.lbl_fastest_split.animate()
        self.lbl_border.animate()

    def reset_visibility(self):
        self.driver_name_visible.setValue(0)
        self.lbl_driver_name.hide()
        self.lbl_driver_name_text.hideText()
        self.lbl_border.hide()
        self.driver_name_visible_fin.setValue(0)
        self.lbl_timing.hide()
        self.lbl_timing_text.hideText()
        self.timing_visible.setValue(0)
        self.lbl_fastest_split.hideText()
        self.lbl_split.hideText()
        self.info_position_lead.hide()
        self.info_position.hide()
        self.visible_end = 0
        self.driver_name_text.setValue("")

    def set_width_and_name(self):
        width = self.rowHeight * 8.9
        name = self.format_name(self.driver_name_text.value, 18)
        if len(name) <= 13:
            width = self.rowHeight * 7.1
        elif len(name) <= 14:
            width = self.rowHeight * 7.4
        elif len(name) <= 15:
            width = self.rowHeight * 7.7
        elif len(name) <= 16:
            width = self.rowHeight * 8.1
        elif len(name) <= 17:
            width = self.rowHeight * 8.5

        self.lbl_driver_name.set(w=width, animated=True)
        self.lbl_driver_name_text.set(w=width, animated=True)
        if Colors.border_direction != 1:
            self.lbl_border.set(w=width, animated=True)
        self.lbl_timing.set(w=width, animated=True)
        self.lbl_fastest_split.set(w=width - self.rowHeight * 14 / 36, animated=True)
        self.info_position_lead.set(x=width - self.ui_row_height.value, animated=True)
        self.lbl_driver_name_text.setText(name)

    def visibility_qualif(self):
        self.lbl_fastest_split.hideText()
        if self.driver_name_visible.value == 1 and self.lbl_driver_name.isVisible.value == 0:
            self.driver_name_visible.changed = True
        if self.timing_visible.value == 1 and self.lbl_timing.isVisible.value == 0:
            self.timing_visible.changed = True

        self.driver_name_visible_fin.setValue(self.driver_name_visible.value)
        self.nameOffsetValue.setValue(self.nameOffset)
        if self.timing_visible.hasChanged():
            if self.timing_visible.value == 0:
                self.lbl_timing.hide()
                self.lbl_timing_text.hideText()
            else:
                self.lbl_timing.show()
                self.lbl_timing_text.showText()
        if Colors.themed_info == 1 and self.driver_name_visible.value == 1:
            if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                self.lbl_border.hide()
            else:
                self.lbl_border.show()
        if self.driver_name_visible_fin.hasChanged():
            if self.driver_name_visible_fin.value == 0:
                self.lbl_driver_name.hide()
                self.lbl_driver_name_text.hideText()
                self.lbl_border.hide()
            else:
                if Colors.themed_info == 1 and self.timing_visible.value == 1:
                    self.lbl_driver_name.setBgColor(Colors.theme(bg=True)).show()
                    self.lbl_driver_name_text.setColor(Colors.white()).showText()
                else:
                    self.lbl_driver_name.setBgColor(Colors.background_dark()).show()
                    self.lbl_driver_name_text.setColor(Colors.font_color()).showText()
                #self.lbl_border.show()
                if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                    self.lbl_border.hide()
                else:
                    self.lbl_border.show()

        if self.driver_name_text.hasChanged():
            self.set_width_and_name()
        if self.nameOffsetValue.hasChanged():
            self.lbl_driver_name_text.setX(self.nameOffsetValue.value, True)
        if self.timing_text.hasChanged():
            self.lbl_timing_text.setText(self.timing_text.value)

    def visibility_race(self):
        if self.timing_visible.hasChanged():
            if self.timing_visible.value == 0:
                self.lbl_timing.hide()
                self.lbl_timing_text.hideText()
            else:
                self.lbl_timing.show()
                self.lbl_timing_text.showText()

        self.nameOffsetValue.setValue(self.nameOffset)
        if Colors.themed_info == 1 and self.driver_name_visible.value == 1:
            if Colors.themed_info == 1 and self.timing_visible.value == 1:
                self.lbl_driver_name.setBgColor(Colors.theme(bg=True))
                self.lbl_driver_name_text.setColor(Colors.white())
            else:
                self.lbl_driver_name.setBgColor(Colors.background_dark())
                self.lbl_driver_name_text.setColor(Colors.font_color())
            if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                self.lbl_border.hide()
            else:
                self.lbl_border.show()

        if self.driver_name_visible.hasChanged():
            if self.driver_name_visible.value == 0:
                self.lbl_driver_name.hide()
                self.lbl_driver_name_text.hideText()
                self.lbl_border.hide()
            else:
                self.lbl_driver_name.show()
                self.lbl_driver_name_text.showText()
                #if dir==1 and lblpos visible ==0:hide
                if Colors.border_direction == 1 and self.info_position.isVisible.value == 0:
                    self.lbl_border.hide()
                else:
                    self.lbl_border.show()

        if self.driver_name_text.hasChanged():
            self.set_width_and_name()
        if self.nameOffsetValue.hasChanged():
            self.lbl_driver_name_text.setX(self.nameOffsetValue.value, True)
        if self.timing_text.hasChanged():
            self.lbl_timing_text.setText(self.timing_text.value, hidden=bool(self.timing_visible.value == 0))

    def get_best_lap(self):
        # old bestLap
        return self.fastestLap2.old

    def manage_window(self):
        pt = POINT()
        result = ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        win_x = self.window.getPos().x
        win_y = self.window.getPos().y
        if win_x > 0:
            self.window.last_x = win_x
            self.window.last_y = win_y
        else:
            self.window.setLastPos()
            win_x = self.window.getPos().x
            win_y = self.window.getPos().y
        if result and pt.x > win_x and pt.x < win_x + self.window.width and pt.y > win_y and pt.y < win_y + self.window.height:
            self.cursor.setValue(True)
        else:
            self.cursor.setValue(False)

        session_changed = self.session.hasChanged()
        if session_changed:
            self.reset_visibility()
            self.raceStarted = False
            self.fastestLapSectors = [0, 0, 0, 0, 0, 0]
        if self.cursor.hasChanged() or session_changed:
            if self.cursor.value and self.driver_name_visible.value == 0:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)

    def on_update(self, sim_info, fl, standings):
        self.standings = standings
        self.session.setValue(sim_info.graphics.session)
        self.manage_window()
        self.animate()
        if self.carsCount == 0:
            self.carsCount = ac.getCarsCount()
        session_time_left = sim_info.graphics.sessionTimeLeft
        sim_info_status = sim_info.graphics.status
        self.currentVehicle.setValue(ac.getFocusedCar())
        backup_laptime = 0
        backup_last_lap_in_pits = 0
        if len(self.lapTimesArray) < self.carsCount:
            for x in range(self.carsCount):
                c = ac.getCarState(x, acsys.CS.LapCount)
                self.driversLap.append(Value(c))
                self.lapTimesArray.append(lapTimeStart(c, session_time_left, 0))
        else:
            for x in range(self.carsCount):
                c = ac.getCarState(x, acsys.CS.LapCount)
                self.driversLap[x].setValue(c)
                if self.driversLap[x].hasChanged():
                    self.lapTimesArray[x].lap = self.driversLap[x].value
                    self.lapTimesArray[x].time = session_time_left
                if bool(ac.isCarInPitline(x)) or bool(ac.isCarInPit(x)):
                    self.lapTimesArray[x].lastpit = c
                if x == self.currentVehicle.value:
                    backup_laptime = self.lapTimesArray[x].time - session_time_left
                    self.lastLapStart = self.lapTimesArray[x].time
                    backup_last_lap_in_pits = self.lapTimesArray[x].lastpit

        current_vehicle_changed = self.currentVehicle.hasChanged()
        if self.colorsByClass.hasChanged() and not self.fastestLapBorderActive:
            car = ac.getCarName(self.currentVehicle.value)
            self.lbl_border.setBgColor(Colors.colorFromCar(car, self.colorsByClass.value))

        if current_vehicle_changed or (self.fastestLapBorderActive and session_time_left < self.visible_end - 2000):
            self.fastestLapBorderActive = False
            car = ac.getCarName(self.currentVehicle.value)
            self.lbl_border.setBgColor(Colors.colorFromCar(car, self.colorsByClass.value))

        if sim_info_status == 2:
            # LIVE
            #str_offset = "  "
            # self.nameOffset=14
            if self.session.value != 2:
                # NOT RACE
                # qtime
                self.fastestLap.setValue(fl)
                bestlap = ac.getCarState(self.currentVehicle.value, acsys.CS.BestLap)
                is_in_pit = (bool(ac.isCarInPitline(self.currentVehicle.value)) or bool(ac.isCarInPit(self.currentVehicle.value)))
                lap_count = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
                if self.lastLap != lap_count:
                    self.lastLap = lap_count
                    self.firstLapStarted = False
                    if self.currentVehicle.value == 0:
                        self.lastLapStart = session_time_left
                cur_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
                if cur_lap_time == 0 and backup_laptime > 0 and self.minLapCount > 0:
                    cur_lap_time = backup_laptime
                if cur_lap_time > 0:
                    self.firstLapStarted = True
                self.lastLapTime = cur_lap_time

                if is_in_pit:
                    self.lastLapInPit = lap_count
                    self.lastTimeInPit = session_time_left
                if self.currentVehicle.value == 0 and sim_info.physics.numberOfTyresOut >= 4 and self.lapCanBeInvalidated:
                    self.lastLapInvalidated = lap_count
                if is_in_pit and self.minLapCount == 0:
                    self.lastLapInvalidated = -1
                if self.sectorCount < 0:
                    self.sectorCount = sim_info.static.sectorCount

                if self.fastestLap.value > 0:
                    for x in range(self.carsCount):
                        c = ac.getCarState(x, acsys.CS.BestLap)
                        if self.fastestLap2.value == 0 or (c > 0 and c < self.fastestLap2.value):
                            self.fastestLap2.setValue(c)
                            self.fastestLapSectors = ac.getLastSplits(x)
                else:
                    self.fastestLapSectors = [0, 0, 0, 0, 0, 0]

                # lap_invalidated = bool(ac.getCarState(0, acsys.CS.LapInvalidated))
                lap_invalidated = bool(self.lastLapInvalidated == lap_count)
                if current_vehicle_changed or self.driver_name_text.value == "":
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                # sector_delay = 5000
                # live or info
                if ((self.lastLapStart < 0 and self.minLapCount > 0 and self.isLapVisuallyEnded) or(self.minLapCount == 0 and lap_invalidated)) and self.session.value != 0:
                    self.driver_name_visible.setValue(0)
                    self.timing_visible.setValue(0)
                    self.lbl_split.hideText()
                    self.info_position.hide()
                    self.info_position_lead.hide()
                elif (self.lastLapInPit < lap_count or self.minLapCount == 0) and not lap_invalidated and (self.lastTimeInPit == 0 or self.lastTimeInPit > self.lastLapStart or self.minLapCount == 0):
                    if self.currentVehicle.value == 0:
                        sector = sim_info.graphics.currentSectorIndex
                    else:
                        sector = self.get_sector()

                    self.driver_name_visible.setValue(1)
                    self.timing_visible.setValue(1)

                    # lapTime = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
                    if self.currentVehicle.value == 0:
                        last_lap = sim_info.graphics.iLastTime
                    else:
                        last_lap = 0
                        last_splits = ac.getLastSplits(self.currentVehicle.value)
                        for c in last_splits:
                            last_lap += c
                        if last_lap == 0:
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
                            fastest_split += self.fastestLapSectors[i]
                            i += 1
                    fastest_split_fin = fastest_split
                    if i < self.sectorCount:
                        fastest_split_fin += self.fastestLapSectors[i]

                    # Situation
                    for s in range(0, self.sectorCount):
                        if self.fastestLap.value > 0 and cur_lap_time > fastest_split_fin - self.sector_delay:
                            # LAST_SECONDS_OF_SECTOR_X, sector == s and
                            self.isLapVisuallyEnded = False
                            self.info_position.hide()
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            if self.sectorCount - 1 == sector:
                                # LAST_SECONDS_OF_SECTOR_LAP,
                                self.lbl_split.setText(self.time_splitting(self.fastestLap.value, "yes"))\
                                    .setColor(Colors.font_color()).showText()
                                self.info_position_lead.show()
                                show_split = True
                            elif fastest_split_fin > 0:
                                self.lbl_split.setText(self.time_splitting(fastest_split_fin, "yes")).setColor(
                                    Colors.font_color()).showText()
                                self.info_position_lead.show()
                                show_split = True
                            break
                        if sector == s + 1 and s + 1 <= self.sectorCount and cur_lap_time - time_split <= self.sector_delay and fastest_split > 0:
                            # SECTOR_X_FINISHED_BEGIN_SECTOR_Y
                            self.isLapVisuallyEnded = False
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.timing_text.setValue(self.time_splitting(time_split, "yes"))
                            if fastest_split < time_split:
                                self.lbl_split.setText(
                                    "+" + self.time_splitting(time_split - fastest_split, "yes")).setColor(
                                    Colors.yellow_time()).showText()
                            else:
                                self.lbl_split.setText(
                                    "-" + self.time_splitting(fastest_split - time_split, "yes")).setColor(
                                    Colors.green()).showText()
                            self.info_position_lead.show()
                            self.info_position.hide()
                            traite = True
                            break

                    if not traite:
                        if self.sectorCount - 1 == sector and self.fastestLap.value > 0 and cur_lap_time > self.fastestLap.value - self.sector_delay:
                            # LAST_SECONDS_OF_SECTOR_LAP,
                            self.isLapVisuallyEnded = False
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.timing_text.setValue(self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            # self.lbl_split.setText(self.time_splitting(self.fastestLap,"yes") + str_offset).setVisible(1)
                        elif self.lastLapInvalidated != lap_count - 1 and ((self.lastLapInPit != lap_count - 1 and sector == 0) or (self.minLapCount == 0)) and cur_lap_time <= self.sector_delay and last_lap > 0:
                            # LAP_FINISHED_BEGIN_NEW_LAP,
                            self.isLapVisuallyEnded = False
                            pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                            if pos == -1:
                                pos = self.get_standings_position(self.currentVehicle.value)

                            if pos > 1:
                                self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(1)
                            else:
                                self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(1)
                            self.info_position.setText(str(pos))
                            self.info_position.show()

                            self.nameOffset = self.rowHeight * 49 / 36  # 49
                            self.timing_text.setValue(self.time_splitting(last_lap, "yes"))
                            if self.fastestLap.value < last_lap:
                                self.lbl_split.setText("+" + self.time_splitting(last_lap - self.fastestLap.value, "yes"))\
                                    .setColor(Colors.yellow_time()).showText()
                            else:
                                self.lbl_split.setText("-" + self.time_splitting(self.get_best_lap() - last_lap, "yes"))\
                                    .setColor(Colors.green()).showText()
                            self.info_position_lead.show()

                        else:
                            # OTHER
                            self.isLapVisuallyEnded = True
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.timing_text.setValue(self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            if not show_split:
                                self.lbl_split.hideText()
                                self.info_position_lead.hide()
                    self.fastestLap.changed = False
                else:
                    self.isLapVisuallyEnded = True
                    self.info_position_lead.hide()
                    spline_position = ac.getCarState(self.currentVehicle.value, acsys.CS.NormalizedSplinePosition)
                    if spline_position <= 0.001:
                        spline_position = 1
                    if session_time_left > 0 and self.minLapCount == 1 and spline_position > 0.95 and not is_in_pit:
                        self.driver_name_visible.setValue(1)
                        self.nameOffset = self.rowHeight * 14 / 36  # 14
                        self.timing_visible.setValue(1)
                        self.lbl_split.hideText()
                        self.info_position.hide()
                        self.timing_text.setValue("0.0")
                        #if Colors.border_direction == 1:
                        #    self.lbl_border.set(x=0)
                    elif lap_invalidated and self.lastLapInPit < lap_count and self.minLapCount > 0:
                        self.driver_name_visible.setValue(0)
                        self.timing_visible.setValue(0)
                        self.lbl_split.hideText()
                        self.info_position.hide()
                    elif bestlap > 0:
                        self.driver_name_visible.setValue(1)
                        self.timing_visible.setValue(1)

                        if self.fastestLap.value < bestlap:
                            self.lbl_split.setText("+" + self.time_splitting(bestlap - self.fastestLap.value, "yes"))\
                                .setColor(Colors.yellow_time()).showText()
                        else:
                            self.lbl_split.hideText()

                        self.timing_text.setValue(self.time_splitting(bestlap, "yes"))

                        self.nameOffset = self.rowHeight * 49 / 36  # 49
                        # pos = sim_info.graphics.position
                        pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                        if pos == -1:
                            pos = self.get_standings_position(self.currentVehicle.value)
                        if pos > 1:
                            self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(1)
                        else:
                            self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(1)
                        self.info_position.setText(str(pos)).show()
                        self.lbl_position_text.setValue(str(pos))
                        #if Colors.border_direction == 1:
                        #    self.lbl_border.set(x=self.rowHeight + 4)
                    elif is_in_pit:
                        self.driver_name_visible.setValue(0)
                        self.timing_visible.setValue(0)
                        self.lbl_split.hideText()
                        self.info_position.hide()
                    else:
                        self.nameOffset = self.rowHeight * 14 / 36  # 14
                        self.driver_name_visible.setValue(1)
                        self.timing_visible.setValue(1)
                        if self.currentVehicle.value == 0:
                            self.timing_text.setValue(self.format_tire(sim_info.graphics.tyreCompound))
                        else:
                            self.timing_text.setValue("Out Lap")
                        self.lbl_split.hideText()
                        self.info_position.hide()
                        #if Colors.border_direction == 1:
                        #    self.lbl_border.set(x=0)
                if cur_lap_time <= self.sector_delay and ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap) > 0 and backup_last_lap_in_pits + 1 < ac.getCarState(x, acsys.CS.LapCount) and session_time_left < 0:
                    self.nameOffset = self.rowHeight * 49 / 36  # 49
                    self.driver_name_visible.setValue(1)
                    self.timing_visible.setValue(1)
                    self.lbl_split.showText()
                    self.info_position.show()
                self.visibility_qualif()

            else:
                # ------------- Race -------------
                self.info_position_lead.hide()
                self.lbl_split.hideText()
                # fastest lap
                completed = 0
                for x in range(self.carsCount):
                    c = ac.getCarState(x, acsys.CS.LapCount)
                    if c > completed:
                        completed = c
                if completed <= 1:
                    self.race_fastest_lap.setValue(0)
                else:
                    for i in range(self.carsCount):
                        bl = ac.getCarState(i, acsys.CS.BestLap)
                        l = ac.getCarState(i, acsys.CS.LapCount)
                        if bl > 0 and l > self.minLapCount and (self.race_fastest_lap.value == 0 or bl < self.race_fastest_lap.value):
                            self.race_fastest_lap.setValue(bl)
                            self.race_fastest_lap_driver.setValue(i)

                if self.race_fastest_lap.hasChanged() and self.race_fastest_lap.value > 0:
                    self.fastestLapBorderActive = True
                    car = ac.getCarName(self.race_fastest_lap_driver.value)
                    self.lbl_border.setBgColor(Colors.colorFromCar(car, self.colorsByClass.value))
                    self.visible_end = session_time_left - 10000
                    self.driver_name_visible.setValue(1)
                    self.driver_name_text.setValue(ac.getDriverName(self.race_fastest_lap_driver.value))
                    self.nameOffset = self.rowHeight * 14 / 36  # 14
                    self.timing_text.setValue("Fastest Lap")
                    self.timing_visible.setValue(1)
                    self.info_position.hide()
                    self.lbl_fastest_split.setText(self.time_splitting(self.race_fastest_lap.value, "yes")).showText()
                    # if Colors.border_direction == 1:
                    #    self.lbl_border.set(x=0)
                elif current_vehicle_changed or (self.forceViewAlways and not self.fastestLapBorderActive):
                    # driver info
                    if not self.forceViewAlways:
                        self.visible_end = session_time_left - 8000
                    self.driver_name_visible.setValue(1)
                    # if current_vehicle_changed:
                    self.driver_name_text.setValue(ac.getDriverName(self.currentVehicle.value))
                    self.nameOffset = self.rowHeight * 49 / 36
                    # pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                    # pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicle.value) + 1
                    if not self.raceStarted:
                        if sim_info.graphics.completedLaps > 0 or sim_info.graphics.iCurrentTime > 20000:
                            self.raceStarted = True
                    if not self.raceStarted:
                        pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicle.value) + 1
                        # pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                    else:
                        pos = self.get_race_standings_position(self.currentVehicle.value)
                    if pos > 1:
                        self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(1)
                    else:
                        self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(1)
                    self.info_position.setText(str(pos)).show()
                    self.timing_visible.setValue(0)
                    self.lbl_fastest_split.hideText()
                    #if Colors.border_direction == 1:
                    #    self.lbl_border.set(x=self.rowHeight + 4)
                elif self.visible_end == 0 or session_time_left < self.visible_end or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                    self.driver_name_visible.setValue(0)
                    self.info_position.hide()
                    self.timing_visible.setValue(0)
                    self.lbl_fastest_split.hideText()
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
                self.lbl_split.hideText()
                self.info_position.hide()
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

                if pos > 1:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(1)
                else:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(1)
                self.info_position.setText(str(pos))
                self.info_position.show()
                self.nameOffset = self.rowHeight * 49 / 36  # 49
                self.timing_text.setValue(self.time_splitting(last_lap, "yes"))
                if self.fastestLap.value < last_lap:
                    self.lbl_split.setText("+" + self.time_splitting(last_lap - self.fastestLap.value, "yes"))\
                        .setColor(Colors.yellow_time()).showText()
                else:
                    self.lbl_split.setText("-" + self.time_splitting(self.fastestLap.old - last_lap, "yes"))\
                        .setColor(Colors.green()).showText()
                self.info_position_lead.show()
                self.fastestLap.changed = False
            elif lap_count > self.minLapCount:
                # showTiming
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(1)
                self.info_position_lead.hide()
                self.nameOffset = self.rowHeight * 14 / 36  # 14
                self.timing_text.setValue(self.time_splitting(cur_lap_time))
                self.info_position.hide()
                if not show_split:
                    self.lbl_split.hideText()
                    self.info_position_lead.hide()
            else:
                # showTireInfo
                self.info_position_lead.hide()
                self.nameOffset = self.rowHeight * 14 / 36  # 14
                self.driver_name_visible.setValue(1)
                self.timing_visible.setValue(1)
                if self.currentVehicle.value == 0:
                    self.timing_text.setValue(self.format_tire(sim_info.graphics.tyreCompound))
                else:
                    self.timing_text.setValue("Out Lap")
                self.lbl_split.hideText()
                self.info_position.hide()
            self.visibility_qualif()
        elif sim_info_status == 1 and self.session.value == 2:
            # Replay Race
            self.info_position_lead.hide()
            self.lbl_split.hideText()
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
                if pos > 1:
                    self.info_position.setColor(Colors.white()).setBgColor(
                        Colors.background_info_position()).setBgOpacity(1)
                else:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(1)
                self.info_position.setText(str(pos)).show()
                self.timing_visible.setValue(0)
                self.lbl_fastest_split.hideText()
                #if Colors.border_direction == 1:
                #    self.lbl_border.set(x=self.rowHeight + 4)
            elif self.visible_end == 0 or session_time_left < self.visible_end or (
                    sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                self.driver_name_visible.setValue(0)
                self.info_position.hide()
                self.timing_visible.setValue(0)
                self.lbl_fastest_split.hideText()
            self.visibility_race()
        else:
            # REPLAY
            self.reset_visibility()
