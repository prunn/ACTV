import ac
import acsys
import ctypes

from apps.util.func import rgb, getFontSize
from apps.util.classes import Window, Label, Value, POINT, Colors, Config


class lapTimeStart:
    def __init__(self, lap, time, lastpit):
        self.lap = lap
        self.time = time
        self.lastpit = lastpit


class ACInfo:
    # INITIALIZATION
    def __init__(self):
        self.rowHeight = 36
        self.lastLapInPit = 0
        self.lastLapInvalidated = 0
        self.isLapVisuallyEnded = True
        self.carsCount = 0
        self.lbl_timing_height = 0
        self.lbl_position_height = 0
        self.lbl_position_text = Value("")
        self.currentVehicle = Value(-1)
        self.ui_row_height = Value(-1)
        self.cursor = Value(False)
        self.fastestLap = Value(0)
        self.fastestLap2 = Value(0)
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
        self.lbl_driver_name2 = Label(self.window.app, "Loading")\
            .set(w=284, h=self.rowHeight,
                 x=14, y=0,
                 font_size=26,
                 align="left",
                 visible=0)
        self.lbl_driver_name_visible = Value()
        self.lbl_driver_name_visible_fin = Value(0)
        self.lbl_driver_name_text = Value("")
        self.lbl_position_visible = Value(0)
        self.lbl_timing_text = Value()
        self.race_fastest_lap = Value(0)
        # self.race_fastest_lap.setValue(0)
        self.race_fastest_lap_driver = Value()
        self.lbl_timing_visible = Value(0)
        self.lbl_timing = Label(self.window.app, "Loading")\
            .set(w=284, h=self.rowHeight,
                 x=0, y=self.rowHeight,
                 font_size=26,
                 align="left",
                 background=Colors.background(),
                 opacity=Colors.background_opacity(),
                 visible=0)
        self.lbl_split = Label(self.window.app, "Loading")\
            .set(w=220, h=self.rowHeight,
                 x=10, y=self.rowHeight,
                 font_size=26,
                 align="right",
                 visible=0)
        self.lbl_fastest_split = Label(self.window.app, "Loading")\
            .set(w=220, h=self.rowHeight,
                 x=48, y=self.rowHeight,
                 font_size=26,
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
        if self.ui_row_height.hasChanged():
            self.redraw_size()
            # self.info_position.setBgColor(Colors.theme(bg = True, reload = True))

    def redraw_size(self):
        self.rowHeight = self.ui_row_height.value + 2
        font_size = getFontSize(self.rowHeight)
        row2_height = self.ui_row_height.value
        font_size2 = getFontSize(row2_height)
        width = self.rowHeight * 7
        self.lbl_driver_name.setSize(width, self.rowHeight).setFontSize(font_size)
        self.lbl_driver_name2.setSize(width, self.rowHeight).setFontSize(font_size)
        self.lbl_timing.setSize(width, row2_height)\
            .setPos(0, self.rowHeight).setFontSize(font_size2)
        self.lbl_split.setSize(self.rowHeight * 4.7, row2_height)\
            .setPos(self.rowHeight, self.rowHeight)\
            .setFontSize(font_size2)
        self.lbl_fastest_split.setSize(self.rowHeight * 5.7, row2_height)\
            .setPos(self.rowHeight, self.rowHeight)\
            .setFontSize(font_size2)
        self.info_position.setSize(self.rowHeight, self.rowHeight)\
            .setFontSize(font_size)
        self.info_position_lead.setSize(row2_height, row2_height)\
            .setPos(width - row2_height, self.rowHeight)\
            .setFontSize(font_size2)
        self.lbl_border.setSize(width, 1).setPos(0, self.rowHeight)

    def set_font(self, font_name):
        self.lbl_driver_name.setFont(font_name, 0, 0)
        self.lbl_driver_name2.setFont(font_name, 0, 0)
        self.lbl_timing.setFont(font_name, 0, 0)
        self.lbl_split.setFont(font_name, 0, 0)
        self.lbl_fastest_split.setFont(font_name, 0, 0)
        self.info_position.setFont(font_name, 0, 0)
        self.info_position_lead.setFont(font_name, 0, 0)

    def format_name(self, name):
        space = name.find(" ")
        if space > 0:
            if len(name) > 14 and space + 1 < len(name):
                return name[space + 1:].upper()
            return name[:space].capitalize() + name[space:].upper()
        if len(name) > 14:
            return name[:15].upper()
        return name.upper()

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

    def animate(self):
        self.lbl_driver_name.animate()
        self.lbl_driver_name2.animate()
        self.lbl_timing.animate()
        self.info_position.animate()
        self.info_position_lead.animate()
        self.lbl_split.animate()
        self.lbl_fastest_split.animate()
        self.lbl_border.animate()

    def reset_visibility(self):
        self.lbl_driver_name_visible.setValue(0)
        self.lbl_driver_name.hide()
        self.lbl_driver_name2.hideText()
        self.lbl_border.hide()
        self.lbl_driver_name_visible_fin.setValue(0)
        self.lbl_timing.hide()
        self.lbl_timing_visible.setValue(0)
        self.lbl_fastest_split.hideText()
        self.lbl_split.hideText()
        self.info_position_lead.hide()
        self.info_position.hide()
        self.visible_end = 0

    def visibility_qualif(self):
        self.lbl_fastest_split.hideText()
        if self.lbl_driver_name_visible.value == 1 and self.lbl_driver_name.isVisible.value == 0:
            self.lbl_driver_name_visible.changed = True
        if self.lbl_timing_visible.value == 1 and self.lbl_timing.isVisible.value == 0:
            self.lbl_timing_visible.changed = True

        self.lbl_driver_name_visible_fin.setValue(self.lbl_driver_name_visible.value)
        self.nameOffsetValue.setValue(self.nameOffset)
        if self.lbl_driver_name_visible_fin.hasChanged():
            if self.lbl_driver_name_visible_fin.value == 0:
                self.lbl_driver_name.hide()
                self.lbl_driver_name2.hideText()
                self.lbl_border.hide()
            else:
                self.lbl_driver_name.show()
                self.lbl_driver_name2.showText()
                self.lbl_border.show()

        if self.lbl_timing_visible.hasChanged():
            if self.lbl_timing_visible.value == 0:
                self.lbl_timing.hide()
            else:
                self.lbl_timing.show()

        if self.lbl_driver_name_text.hasChanged():
            self.lbl_driver_name2.setText(self.lbl_driver_name_text.value.lstrip())
        if self.nameOffsetValue.hasChanged():
            self.lbl_driver_name2.setX(self.nameOffsetValue.value, True)
        if self.lbl_timing_text.hasChanged():
            self.lbl_timing.setText(self.lbl_timing_text.value)

    def visibility_race(self):
        self.nameOffsetValue.setValue(self.nameOffset)
        if self.lbl_driver_name_visible.hasChanged():
            if self.lbl_driver_name_visible.value == 0:
                self.lbl_driver_name.hide()
                self.lbl_driver_name2.hideText()
                self.lbl_border.hide()
            else:
                self.lbl_driver_name.show()
                self.lbl_driver_name2.showText()
                self.lbl_border.show()

        if self.lbl_timing_visible.hasChanged():
            if self.lbl_timing_visible.value == 0:
                self.lbl_timing.hide()
            else:
                self.lbl_timing.show()

        if self.lbl_driver_name_text.hasChanged():
            self.lbl_driver_name2.setText(self.lbl_driver_name_text.value)
        if self.nameOffsetValue.hasChanged():
            self.lbl_driver_name2.setX(self.nameOffsetValue.value, True)
        if self.lbl_timing_text.hasChanged():
            self.lbl_timing.setText(self.lbl_timing_text.value, hidden=bool(self.lbl_timing_height < 30))

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
            self.fastestLapSectors = [0, 0, 0, 0, 0, 0]
        if self.cursor.hasChanged() or session_changed:
            if self.cursor.value and self.lbl_driver_name_visible.value == 0:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)

    def on_update(self, sim_info, fl):
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
            str_offset = "  "
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
                if current_vehicle_changed or self.lbl_driver_name_text.value == "":
                    self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicle.value)))
                # sector_delay = 5000
                # live or info
                if ((self.lastLapStart < 0 and self.minLapCount > 0 and self.isLapVisuallyEnded) or(self.minLapCount == 0 and lap_invalidated)) and self.session.value != 0:
                    self.lbl_driver_name_visible.setValue(0)
                    self.lbl_timing_visible.setValue(0)
                    self.lbl_split.hideText()
                    self.info_position.hide()
                    self.info_position_lead.hide()
                elif (self.lastLapInPit < lap_count or self.minLapCount == 0) and not lap_invalidated and (self.lastTimeInPit == 0 or self.lastTimeInPit > self.lastLapStart or self.minLapCount == 0):
                    if self.currentVehicle.value == 0:
                        sector = sim_info.graphics.currentSectorIndex
                    else:
                        sector = self.get_sector()

                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_timing_visible.setValue(1)

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
                                    .setColor(Colors.white()).showText()
                                self.info_position_lead.show()
                                show_split = True
                            elif fastest_split_fin > 0:
                                self.lbl_split.setText(self.time_splitting(fastest_split_fin, "yes")).setColor(
                                    Colors.white()).showText()
                                self.info_position_lead.show()
                                show_split = True
                            break
                        if sector == s + 1 and s + 1 <= self.sectorCount and cur_lap_time - time_split <= self.sector_delay and fastest_split > 0:
                            # SECTOR_X_FINISHED_BEGIN_SECTOR_Y
                            self.isLapVisuallyEnded = False
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.lbl_timing_text.setValue(str_offset + self.time_splitting(time_split, "yes"))
                            if fastest_split < time_split:
                                self.lbl_split.setText(
                                    "+" + self.time_splitting(time_split - fastest_split, "yes")).setColor(
                                    Colors.yellow()).showText()
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
                            self.lbl_timing_text.setValue(str_offset + self.time_splitting(cur_lap_time))
                            self.info_position.hide()
                            # self.lbl_split.setText(self.time_splitting(self.fastestLap,"yes") + str_offset).setVisible(1)
                        elif self.lastLapInvalidated != lap_count - 1 and ((self.lastLapInPit != lap_count - 1 and sector == 0) or (self.minLapCount == 0)) and cur_lap_time <= self.sector_delay and last_lap > 0:
                            # LAP_FINISHED_BEGIN_NEW_LAP,
                            self.isLapVisuallyEnded = False
                            pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                            if pos == -1:
                                pos = self.get_standings_position(self.currentVehicle.value)

                            if pos > 1:
                                self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(0.8)
                            else:
                                self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(0.8)
                            self.info_position.setText(str(pos))
                            self.info_position.show()

                            self.nameOffset = self.rowHeight * 49 / 36  # 49
                            self.lbl_timing_text.setValue(str_offset + self.time_splitting(last_lap, "yes"))
                            if self.fastestLap.value < last_lap:
                                self.lbl_split.setText("+" + self.time_splitting(last_lap - self.fastestLap.value, "yes"))\
                                    .setColor(Colors.yellow()).showText()
                            else:
                                self.lbl_split.setText("-" + self.time_splitting(self.get_best_lap() - last_lap, "yes"))\
                                    .setColor(Colors.green()).showText()
                            self.info_position_lead.show()

                        else:
                            # OTHER
                            self.isLapVisuallyEnded = True
                            self.nameOffset = self.rowHeight * 14 / 36  # 14
                            self.lbl_timing_text.setValue(str_offset + self.time_splitting(cur_lap_time))
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
                        self.lbl_driver_name_visible.setValue(1)
                        self.nameOffset = self.rowHeight * 14 / 36  # 14
                        self.lbl_timing_visible.setValue(1)
                        self.lbl_split.hideText()
                        self.info_position.hide()
                        self.lbl_timing_text.setValue(str_offset + "0.0")

                    elif lap_invalidated and self.lastLapInPit < lap_count and self.minLapCount > 0:
                        self.lbl_driver_name_visible.setValue(0)
                        self.lbl_timing_visible.setValue(0)
                        self.lbl_split.hideText()
                        self.info_position.hide()
                    elif bestlap > 0:
                        self.lbl_driver_name_visible.setValue(1)
                        self.lbl_timing_visible.setValue(1)

                        if self.fastestLap.value < bestlap:
                            self.lbl_split.setText("+" + self.time_splitting(bestlap - self.fastestLap.value, "yes"))\
                                .setColor(Colors.yellow()).showText()
                        else:
                            self.lbl_split.hideText()

                        self.lbl_timing_text.setValue(str_offset + self.time_splitting(bestlap, "yes"))

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

                    elif is_in_pit:
                        self.lbl_driver_name_visible.setValue(0)
                        self.lbl_timing_visible.setValue(0)
                        self.lbl_split.hideText()
                        self.info_position.hide()
                    else:
                        self.nameOffset = self.rowHeight * 14 / 36  # 14
                        self.lbl_driver_name_visible.setValue(1)
                        self.lbl_timing_visible.setValue(1)
                        if self.currentVehicle.value == 0:
                            self.lbl_timing_text.setValue(str_offset + self.format_tire(sim_info.graphics.tyreCompound))
                        else:
                            self.lbl_timing_text.setValue(str_offset + "Out Lap")
                        self.lbl_split.hideText()
                        self.info_position.hide()

                if cur_lap_time <= self.sector_delay and ac.getCarState(self.currentVehicle.value, acsys.CS.LastLap) > 0 and backup_last_lap_in_pits + 1 < ac.getCarState(x, acsys.CS.LapCount) and session_time_left < 0:
                    self.nameOffset = self.rowHeight * 49 / 36  # 49
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_timing_visible.setValue(1)
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
                    self.visible_end = session_time_left - 8000
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.race_fastest_lap_driver.value)))
                    self.nameOffset = self.rowHeight * 14 / 36  # 14
                    self.lbl_timing_text.setValue(str_offset + "Fastest Lap")
                    self.lbl_timing_visible.setValue(1)
                    self.info_position.hide()
                    self.lbl_fastest_split.setText(self.time_splitting(self.race_fastest_lap.value, "yes")).showText()

                elif current_vehicle_changed or (self.forceViewAlways and not self.fastestLapBorderActive):
                    # driver info
                    if not self.forceViewAlways:
                        self.visible_end = session_time_left - 8000
                    self.lbl_driver_name_visible.setValue(1)
                    # if current_vehicle_changed:
                    self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicle.value)))
                    self.nameOffset = self.rowHeight * 49 / 36  # 49
                    # pos = ac.getCarLeaderboardPosition(self.currentVehicle.value)
                    pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicle.value) + 1
                    if pos > 1:
                        self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(1)
                    else:
                        self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(1)
                    self.info_position.setText(str(pos)).show()
                    self.lbl_timing_visible.setValue(0)
                    self.lbl_fastest_split.hideText()
                elif self.visible_end == 0 or session_time_left < self.visible_end or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                    self.lbl_driver_name_visible.setValue(0)
                    self.info_position.hide()
                    self.lbl_timing_visible.setValue(0)
                    self.lbl_fastest_split.hideText()
                self.visibility_race()
        elif sim_info_status == 1 and self.session.value != 2:
            # Replay Qualif
            str_offset = "  "
            show_split = False
            lap_count = ac.getCarState(self.currentVehicle.value, acsys.CS.LapCount)
            cur_lap_time = ac.getCarState(self.currentVehicle.value, acsys.CS.LapTime)
            is_in_pit = (bool(ac.isCarInPitline(self.currentVehicle.value)) or bool(ac.isCarInPit(self.currentVehicle.value)))
            if current_vehicle_changed or self.lbl_driver_name_text.value == "":
                self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicle.value)))
            if is_in_pit:
                self.lbl_driver_name_visible.setValue(0)
                self.lbl_timing_visible.setValue(0)
                self.lbl_split.hideText()
                self.info_position.hide()
            elif cur_lap_time <= self.sector_delay and lap_count > 1:
                # show last lap
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_timing_visible.setValue(1)
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
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(0.8)
                else:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(0.8)
                self.info_position.setText(str(pos))
                self.info_position.show()
                self.nameOffset = self.rowHeight * 49 / 36  # 49
                self.lbl_timing_text.setValue(str_offset + self.time_splitting(last_lap, "yes"))
                if self.fastestLap.value < last_lap:
                    self.lbl_split.setText("+" + self.time_splitting(last_lap - self.fastestLap.value, "yes"))\
                        .setColor(Colors.yellow()).showText()
                else:
                    self.lbl_split.setText("-" + self.time_splitting(self.fastestLap.old - last_lap, "yes"))\
                        .setColor(Colors.green()).showText()
                self.info_position_lead.show()
                self.fastestLap.changed = False
            elif lap_count > self.minLapCount:
                # showTiming
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_timing_visible.setValue(1)
                self.info_position_lead.hide()
                self.nameOffset = self.rowHeight * 14 / 36  # 14
                self.lbl_timing_text.setValue(str_offset + self.time_splitting(cur_lap_time))
                self.info_position.hide()
                if not show_split:
                    self.lbl_split.hideText()
                    self.info_position_lead.hide()
            else:
                # showTireInfo
                self.info_position_lead.hide()
                self.nameOffset = self.rowHeight * 14 / 36  # 14
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_timing_visible.setValue(1)
                if self.currentVehicle.value == 0:
                    self.lbl_timing_text.setValue(str_offset + self.format_tire(sim_info.graphics.tyreCompound))
                else:
                    self.lbl_timing_text.setValue(str_offset + "Out Lap")
                self.lbl_split.hideText()
                self.info_position.hide()
            self.visibility_qualif()
        elif sim_info_status == 1 and self.session.value == 2:
            # Replay Race
            todo = 1
            '''
            if current_vehicle_changed:
                self.visible_end = session_time_left - 8000
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicle.value)))
                self.nameOffset=self.rowHeight*49/36 #49
                pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicle.value) + 1
                if pos > 1:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.background_info_position()).setBgOpacity(1)
                else:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.background_first()).setBgOpacity(1)
                self.info_position.setText(str(pos)).show() 
                self.lbl_timing_visible.setValue(0)
                self.lbl_fastest_split.hideText()
                
                if self.lbl_driver_name_visible.hasChanged():         
                    if self.lbl_driver_name_visible.value == 0:
                        self.lbl_driver_name.hide()
                        self.lbl_border.hide()
                    else:
                        self.lbl_driver_name.show()
                        self.lbl_border.show()
                    
                if self.lbl_timing_visible.hasChanged():         
                    if self.lbl_timing_visible.value == 0:
                        self.lbl_timing.hide()
                    else:
                        self.lbl_timing.show()
                        
                if self.lbl_driver_name_text.hasChanged():
                    self.lbl_driver_name.setText(self.lbl_driver_name_text.value)  
                if self.lbl_timing_text.hasChanged():
                    self.lbl_timing.setText(self.lbl_timing_text.value,hidden=bool(self.lbl_timing_height < 30)) 
            '''
        else:
            # REPLAY
            self.reset_visibility()
