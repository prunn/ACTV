import ac
import acsys
import math
import ctypes
import time
import http.client
import os.path
import json
import encodings.idna
import threading
from .util.classes import Window, Label, Value, Colors, Log, raceGaps, Font, Laps, MyHTMLParser, Config, CarClass
from .configuration import Configuration
from .driver import Driver


class ACTower:

    # INITIALIZATION
    def __init__(self, sim_info):
        rowHeight = 36
        self.fontName = ""
        self.is_multiplayer = ac.getServerIP() != ''
        self.drivers = []
        self.stintLabels = []
        self.standings = []
        self.realtime_standings = []
        self.standings_start_race = []
        self.standings_replay = []
        self.cars_count = ac.getCarsCount()
        self.session = Value(-1)
        self.sessionTimeLeft = 0
        self.imported = False
        self.drivers_info_updating = False
        self.drivers_info_updated = False
        self.TimeLeftUpdate = Value()
        self.lapsCompleted = Value()
        self.currentVehicule = Value(0)
        self.font = Value(0)
        self.theme = Value(-1)
        self.fastestLap = 0
        self.race_show_end = 0
        self.driver_shown = 0
        self.ping_updater = None
        self.ping_updater_active = False
        self.force_hidden = False
        self.raceStarted = False
        self.leader_time = 0
        self.tick = 0
        self.tick_race_mode = 0
        self.tick_update = 0
        self.cursor = Value(False)
        self.max_num_cars = 18
        self.max_num_laps_stint = 8
        self.race_mode = Value(0)
        self.qual_mode = Value(0)
        self.ui_row_height = Value(-1)
        self.border_direction = Value(-1)
        self.numCarsToFinish = 0
        self.window = Window(name="ACTV Tower", width=268, height=60)
        self.minLapCount = 1
        self.is_touristenfahrten = False
        self.track_length = sim_info.static.trackSPlineLength
        self.curLapCount = Value()
        self.stint_visible_end = 0
        self.title_mode_visible_end = 0
        self.title_mode_visible_end_replay = 0
        self.curDriverLaps = []
        self.lastLapInvalidated = -1
        self.minlap_stint = 5
        self.iLastTime = Value()
        self.cars_classes_count = Value(0)
        self.cars_classes_mouse = Value(-1)
        self.cars_classes_current = Value(-1)
        self.cars_classes_timeout = None
        self.cars_classes_triggered = False
        self.cars_classes = []
        self.cars_classes_labels_init = False
        self.lbl_title_stint = Label(self.window.app)\
            .set(w=rowHeight * 6, h=rowHeight - 4,
                 x=0, y=rowHeight * 4 - rowHeight - 6,
                 opacity=0)
        self.lbl_title_stint_txt = Label(self.window.app, "Current Stint")\
            .set(w=rowHeight * 6, h=rowHeight - 4,
                 x=0, y=rowHeight * 4 - rowHeight - 6,
                 font_size=23,
                 opacity=0,
                 align="center")
        self.lbl_tire_stint = Label(self.window.app)\
            .set(w=rowHeight * 6, h=rowHeight,
                 x=0, y=rowHeight * 4 - (rowHeight - 4),
                 opacity=0.58)
        self.lbl_tire_stint_txt = Label(self.window.app)\
            .set(w=rowHeight * 6, h=rowHeight,
                 x=0, y=rowHeight * 4 - (rowHeight - 4),
                 font_size=24,
                 opacity=0,
                 align="center")
        self.lbl_title_mode = Label(self.window.app) \
            .set(w=rowHeight * 6, h=rowHeight - 4,
                 x=0, y=-(rowHeight - 4),
                 opacity=0)
        self.lbl_title_mode_txt = Label(self.window.app, "Mode") \
            .set(w=rowHeight * 6, h=rowHeight - 4,
                 x=0, y=-(rowHeight - 4),
                 opacity=0,
                 font_size=23,
                 align="center")
        track = ac.getTrackName(0)
        config = ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife") >= 0 and config.find("touristenfahrten") >= 0:
            self.minLapCount = 0
            self.is_touristenfahrten = True
        elif track.find("drag1000") >= 0 or track.find("drag400") >= 0:
            self.minLapCount = 0
        self.init_drivers(sim_info)
        self.load_cfg()

    def __del__(self):
        self.ping_updater_active = False

    # PUBLIC METHODS
    def load_cfg(self):
        self.max_num_cars = Configuration.max_num_cars
        self.max_num_laps_stint = Configuration.max_num_laps_stint
        self.race_mode.setValue(Configuration.race_mode)
        self.qual_mode.setValue(Configuration.qual_mode)
        self.ui_row_height.setValue(Configuration.ui_row_height)
        self.border_direction.setValue(Colors.border_direction)
        Colors.highlight(reload=True)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.font.setValue(Font.current)
        self.redraw_size()
        for driver in self.drivers:
            driver.set_border()

    def redraw_size(self):
        # Colors
        if self.theme.hasChanged():
            self.lbl_title_stint.set(background=Colors.tower_stint_title_bg(), animated=True, init=True)
            self.lbl_title_stint_txt.set(color=Colors.tower_stint_title_txt(), animated=True, init=True)
            self.lbl_tire_stint.set(background=Colors.tower_stint_tire_bg(), animated=True, init=True)
            self.lbl_tire_stint_txt.set(color=Colors.tower_stint_tire_txt(), animated=True, init=True)
            self.lbl_title_mode.set(background=Colors.tower_mode_title_bg(), animated=True, init=True)
            self.lbl_title_mode_txt.set(color=Colors.tower_mode_title_txt(), animated=True, init=True)
        if self.ui_row_height.hasChanged() or self.font.hasChanged() or self.border_direction.hasChanged():
            # Fonts
            self.lbl_title_stint_txt.update_font()
            self.lbl_tire_stint_txt.update_font()
            self.lbl_title_mode_txt.update_font()
            # UI
            font_offset = Font.get_font_offset()
            height = self.ui_row_height.value - 2
            font_size = Font.get_font_size(height + font_offset)
            font_size2 = Font.get_font_size(height - 2 + font_offset)

            if Colors.border_direction == 1:
                border_offset = 8
            else:
                border_offset = 4
            width = self.ui_row_height.value * 6.2 + border_offset
            self.window.setSize(width, self.ui_row_height.value * 2)
            self.lbl_title_stint.set(w=width, h=height - 2, y=self.ui_row_height.value * 4 - (height - 2))
            self.lbl_title_stint_txt.set(w=width, h=height - 2,
                                         y=self.ui_row_height.value * 4 - (height - 2) + Font.get_font_x_offset(),
                                         font_size=font_size2)
            self.lbl_tire_stint.set(w=width, h=height, y=self.ui_row_height.value)
            self.lbl_tire_stint_txt.set(w=width, h=height,
                                        y=self.ui_row_height.value + Font.get_font_x_offset(),
                                        font_size=font_size)
            self.lbl_title_mode.set(w=width, h=height - 2, y=-(height - 2))
            self.lbl_title_mode_txt.set(w=width, h=height - 2,
                                        y=-(height - 2) + Font.get_font_x_offset(),
                                        font_size=font_size2)
        for driver in self.drivers:
            driver.redraw_size()
            driver.set_border()
        for lbl in self.stintLabels:
            lbl.redraw_size()
        offset=0
        for i, lbl in enumerate(self.cars_classes):
            if i <= Colors.cars_classes_current:
                offset -= lbl.w + (Configuration.ui_row_height - 2) * 10 / 36
        for lbl in self.cars_classes:
            lbl.redraw_size(Configuration.ui_row_height-2, offset)
            offset+=lbl.w + (Configuration.ui_row_height - 2) * 10 / 36

    def animate(self):
        self.lbl_title_stint.animate()
        self.lbl_title_stint_txt.animate()
        self.lbl_tire_stint.animate()
        self.lbl_tire_stint_txt.animate()
        self.lbl_title_mode.animate()
        self.lbl_title_mode_txt.animate()
        for driver in self.drivers:
            driver.animate(self.sessionTimeLeft)
        for lbl in self.stintLabels:
            lbl.animate(self.sessionTimeLeft)
        for lbl in self.cars_classes:
            lbl.animate()

    def format_tire(self, name):
        space = name.find("(")
        if space > 0:
            name = name[:space]
        name = name.strip()
        if len(name) > 16:
            return name[:17]
        return name

    def init_drivers(self, sim_info):
        for i in range(self.cars_count):
            self.drivers.append(Driver(self.window.app, i, ac.getDriverName(i), is_touristenfahrten=self.is_touristenfahrten))
        self.load_drivers_info(sim_info)

    def init_car_classes(self):
        if Colors.multiCarsClasses:
            if not self.cars_classes_labels_init:
                self.cars_classes.append(CarClass(self.window.app ,-1, 'Overall',Configuration.ui_row_height-2,0, Colors.theme(bg=True))) # no filter
                self.cars_classes_labels_init=True
            self.cars_classes_count.setValue(len(Colors.car_classes_list))
            if self.cars_classes_count.hasChanged():
                offset=0
                for lbl in self.cars_classes:
                    offset += lbl.w + Configuration.ui_row_height*10/36
                for i in range(self.cars_classes_count.old, self.cars_classes_count.value):
                    title = Colors.car_classes_list[i]
                    color=Colors.car_classes['default_bg']
                    if title != "" and title + '_bg' in Colors.car_classes:
                        color = Colors.car_classes[title + "_bg"]
                    if title != "" and title + '_title' in Colors.car_classes:
                        title = Colors.car_classes[title + "_title"]
                    title = title[:1].upper() + title[1:]
                    self.cars_classes.append(CarClass(self.window.app , i, title, Configuration.ui_row_height-2,offset,color))
                    offset += self.cars_classes[-1].w + Configuration.ui_row_height*10/36
            # place current on top of standings
            self.cars_classes_current.setValue(Colors.cars_classes_current)
            if self.cars_classes_current.hasChanged():
                # timeout 5 sec when changed
                self.cars_classes_timeout = self.sessionTimeLeft - 5000
                offset = 0
                ct = 0
                for i, lbl in enumerate(self.cars_classes):
                    # update active filter
                    if i > 0:
                        cur_class = Colors.car_classes_list[i - 1]
                        lbl.active = False
                        for s in self.standings:
                            if cur_class == s[2]:
                                lbl.active = True
                                ct += 1
                                break

                    if lbl.active and i <= Colors.cars_classes_current:
                        offset -= lbl.w + (Configuration.ui_row_height - 2) * 10 / 36
                for lbl in self.cars_classes:
                    lbl.setX(offset)
                    if lbl.active:
                        offset+=lbl.w + (Configuration.ui_row_height - 2) * 10 / 36
                Colors.multiCarsClasses = (ct > 1)

    def next_driver_is_shown(self, pos):
        if pos > 0:
            for d in self.drivers:
                if d.position.value == pos + 1 and d.isDisplayed:
                    return True
        return False

    def update_drivers(self, sim_info):
        cur_driver = 0
        self.minlap_stint = 5
        show_stint_always = False
        if len(self.standings) <= 1:
            self.minlap_stint = 3
            show_stint_always = True
        elif self.minLapCount == 0:
            self.minlap_stint = 3
        if self.minLapCount > 0 and (bool(sim_info.graphics.isInPit) or bool(sim_info.physics.pitLimiterOn)):
            self.curDriverLaps = []
            self.stint_visible_end = 0
        # mode_changed = self.qual_mode.hasChanged()
        if self.qual_mode.hasChanged():
            if self.qual_mode.value == 0:
                self.lbl_title_mode_txt.setText("Gaps")
            elif self.qual_mode.value == 1:
                self.lbl_title_mode_txt.setText("Times")
            elif self.qual_mode.value == 2:
                self.lbl_title_mode_txt.setText("Sectors")
            elif self.qual_mode.value == 3:
                self.lbl_title_mode_txt.setText("Compact")
            else:
                self.lbl_title_mode_txt.setText("Relative")
            self.title_mode_visible_end = self.sessionTimeLeft - 6000
        if self.title_mode_visible_end != 0 and self.title_mode_visible_end < self.sessionTimeLeft:
            self.lbl_title_mode.show()
            self.lbl_title_mode_txt.show()
            for lbl in self.cars_classes:
                lbl.setY((Configuration.ui_row_height - 2)*-2)
        else:
            self.lbl_title_mode.hide()
            self.lbl_title_mode_txt.hide()
            for lbl in self.cars_classes:
                lbl.setY(-(Configuration.ui_row_height - 2))

        current_standings = self.standings
        if Colors.cars_classes_current >= 0:
            cur_class = Colors.car_classes_list[Colors.cars_classes_current]
            # filter current_standings
            current_standings = []
            for s in self.standings:
                if cur_class == s[2]:
                    current_standings.append((s[0], s[1], s[2]))
        needs_tlc = True
        if Configuration.names >= 2:
            needs_tlc = False

        ##########################################
        display_offset = cur_driver_pos = 0
        cur_car_shown=False
        fastest_driver_sectors = []
        for driver in self.drivers:
            driver.isAlive.setValue(bool(ac.isConnected(driver.identifier)))
            if len(current_standings) > 0 and driver.identifier == current_standings[0][0]:
                fastest_driver_sectors = driver.bestLap_sectors
            if driver.identifier == self.currentVehicule.value:
                driver.isCurrentVehicule.setValue(True)
                cur_driver = driver
                p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                if len(p) > 0:
                    cur_driver_pos = p[0] + 1
                    c = driver.get_best_lap()
                    if c > 0 and driver.completedLaps.value > self.minLapCount:
                        cur_car_shown=True
            else:
                driver.isCurrentVehicule.setValue(False)
        if cur_driver_pos >= self.max_num_cars:
            display_offset = cur_driver_pos - self.max_num_cars
            if len(current_standings) > cur_driver_pos:  # showing next driver to user
                display_offset += 1

        if self.qual_mode.value == 4:
            # Realtime
            realtime_target = [i for i, v in enumerate(self.realtime_standings) if v[0] == self.currentVehicule.value]
            if len(realtime_target) > 0:
                max_num_cars = min(self.max_num_cars, len(self.standings) * 2)
                if max_num_cars % 2 == 1:
                    # 5 % 2 = 1 - perfect 2 up,driver, 2 down
                    display_offset = max_down = math.ceil(max_num_cars / 2)
                else:
                    # 6 = 3 up, driver, 2 down
                    display_offset = math.ceil(max_num_cars / 2) + 1
                    max_down = math.ceil(max_num_cars / 2)

                for driver in self.drivers:
                    r = [i for i, v in enumerate(self.realtime_standings) if v[0] == driver.identifier]
                    if len(r) > 0 and -max_down < realtime_target[0] - r[0] < display_offset:
                        p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                        if driver.last_lap_visible_end != 0 and driver.last_lap_visible_end < self.sessionTimeLeft and driver.isAlive.value and not driver.isInPit.value:
                            lastlap = ac.getCarState(driver.identifier, acsys.CS.LastLap)
                            driver.set_time_race_battle(lastlap, -1)
                        else:
                            gap = self.realtime_to_driver(driver, cur_driver)
                            driver.set_time_race_battle(gap, cur_driver.identifier, realtime=True)
                        if len(p) > 0:
                            driver.set_position(p[0] + 1, r[0] - realtime_target[0] + display_offset - 1, True, True)
                        else:
                            driver.set_position(0, r[0] - realtime_target[0] + display_offset - 1, True, True)
                        driver.show(needs_tlc=needs_tlc, race=False)
                        driver.update_pit(self.sessionTimeLeft)
                    else:
                        driver.hide()
        elif Configuration.max_num_laps_stint > 0 and ((show_stint_always and len(self.curDriverLaps) >= self.minlap_stint) or (self.stint_visible_end != 0 and self.sessionTimeLeft >= self.stint_visible_end)):
            # Lap stint mode
            for driver in self.drivers:
                if driver.identifier == 0:
                    p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                    if len(p) > 0:
                        driver.set_position(p[0] + 1, p[0], False)
                    driver.show(needs_tlc=False, race=False, compact=True)
                    driver.update_pit(self.sessionTimeLeft)
                    self.lbl_title_stint.show()
                    self.lbl_title_stint_txt.show()
                    self.lbl_tire_stint_txt.setText(self.format_tire(sim_info.graphics.tyreCompound))
                    self.lbl_tire_stint.show()
                    self.lbl_tire_stint_txt.show()
                    # self.stintLabels
                    if len(self.curDriverLaps) > len(self.stintLabels):
                        for i in range(len(self.stintLabels), len(self.curDriverLaps)):
                            self.stintLabels.append(
                                Driver(self.window.app, 0, "Lap " + str(i + 1),True))
                    i = 0
                    j = 0
                    # for lbl in self.stintLabels:
                    lap_offset = len(self.curDriverLaps) - self.max_num_laps_stint
                    for l in self.curDriverLaps:
                        if j < lap_offset:
                            self.stintLabels[j].hide()
                        else:
                            # lbl.final_y = 38 * (i+3)
                            self.stintLabels[j].set_time_stint(l.time, l.valid)
                            self.stintLabels[j].set_position(i + 5, 0, True)
                            self.stintLabels[j].show(False)
                            # i+5,
                            i += 1
                        j += 1

                else:
                    driver.hide()
        else:
            if self.lbl_title_stint.isVisible.value:
                self.lbl_title_stint.hide()
                self.lbl_title_stint_txt.hide()
                self.lbl_tire_stint.hide()
                self.lbl_tire_stint_txt.hide()
                for l in self.stintLabels:
                    l.hide()
            if not cur_car_shown:
                display_offset=0

            for driver in self.drivers:
                driver.isAlive.setValue(bool(ac.isConnected(driver.identifier)))
                p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                #if len(p) > 0:
                c = driver.get_best_lap()
                if not driver.isAlive.value:
                    driver.bestLapServer = 0
                if len(p) > 0 and p[0] < self.max_num_cars + display_offset and (p[0] == 0 or p[0] > display_offset):
                    check_pos = p[0] + 1
                    if c > 0 and (driver.completedLaps.value > self.minLapCount or self.next_driver_is_shown(check_pos)) and driver.isAlive.value:# and check_pos <= self.max_num_cars:
                        if len(current_standings) > 0 and len(current_standings[0]) > 1:
                            if p[0] == 0:
                                driver.set_position(p[0] + 1, 0, False)
                            else:
                                driver.set_position(p[0] + 1, display_offset, False)
                            #driver.set_position(p[0] + 1, 0, True)
                            driver.show(needs_tlc=needs_tlc, race=False, compact=Configuration.qual_mode == 3)
                            driver.set_time(c, current_standings[0][1], self.sessionTimeLeft, Configuration.qual_mode, fastest_driver_sectors)
                            driver.update_pit(self.sessionTimeLeft)
                    else:
                        driver.hide()
                else:
                    driver.hide()

    def update_drivers_replay(self):
        if self.qual_mode.hasChanged():
            if self.qual_mode.value == 0:
                self.lbl_title_mode_txt.setText("Gaps")
            elif self.qual_mode.value == 1:
                self.lbl_title_mode_txt.setText("Times")
            elif self.qual_mode.value == 2:
                self.lbl_title_mode_txt.setText("Compact")
            else:
                self.lbl_title_mode_txt.setText("Relative")
            self.title_mode_visible_end = self.sessionTimeLeft - 6000
        if self.title_mode_visible_end != 0 and self.title_mode_visible_end < self.sessionTimeLeft:
            self.lbl_title_mode.show()
            self.lbl_title_mode_txt.show()
            for lbl in self.cars_classes:
                lbl.setY((Configuration.ui_row_height - 2)*-2)
        else:
            self.lbl_title_mode.hide()
            self.lbl_title_mode_txt.hide()
            for lbl in self.cars_classes:
                lbl.setY(-(Configuration.ui_row_height - 2))

        if self.lbl_title_stint.isVisible.value:
            self.lbl_title_stint.hide()
            self.lbl_title_stint_txt.hide()
            self.lbl_tire_stint.hide()
            self.lbl_tire_stint_txt.hide()
            for l in self.stintLabels:
                l.hide()

        needs_tlc = True
        if Configuration.names >= 2:
            needs_tlc = False

        for driver in self.drivers:
            driver.isCurrentVehicule.setValue(driver.identifier == self.currentVehicule.value)
            c = 0
            p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
            check_pos = 0
            if len(p) > 0:
                check_pos = p[0] + 1
            for v in self.standings:
                if v[0] == driver.identifier:
                    c = v[1]
                    break
            lap_count = ac.getCarState(driver.identifier, acsys.CS.LapCount)
            if c > 0 and (lap_count > self.minLapCount or self.next_driver_is_shown(check_pos)) and driver.isAlive.value and check_pos <= self.max_num_cars:
                if len(p) > 0 and len(self.standings) > 0 and len(self.standings[0]) > 1:
                    driver.set_position(p[0] + 1, 0, False)
                    driver.show(needs_tlc=needs_tlc, race=False, compact=Configuration.qual_mode == 3)
                    driver.set_time(c, self.standings[0][1], self.sessionTimeLeft, self.qual_mode.value)
                    driver.update_pit(self.sessionTimeLeft)
            else:
                driver.hide()

    def gap_to_driver(self, d1, d2, sector):
        t1 = 0
        t2 = 0
        found1 = False
        found2 = False
        max_offset = 25
        if self.race_mode.value == 1 or self.race_mode.value == 2 or self.race_mode.value == 3:
            max_offset = 125
        if abs(sector - self.get_max_sector(d1)) > max_offset:
            return 600000
        if abs(sector - self.get_max_sector(d2)) > max_offset:
            return 600000
        for g in reversed(d1.race_gaps):
            if g.sector == sector:
                t1 = g.time
                found1 = True
                break
        for g in reversed(d2.race_gaps):
            if g.sector == sector:
                t2 = g.time
                found2 = True
                break
        if (not found1 or not found2) and sector > 0:
            return self.gap_to_driver(d1, d2, sector - 1)
        return abs(t1 - t2)

    def realtime_to_driver(self, d1, d2):
        if self.session.value != 2:
            max_d1 = d1.raceProgress
            max_d2 = d2.raceProgress

            if max_d2 - max_d1 > 0.5:
                gap = max_d1 + 1 - max_d2
            elif max_d2 - max_d1 < -0.5:
                gap = max_d1 - 1 - max_d2
            else:
                gap = max_d1 - max_d2

            # if behind get his time as ref else your best time
            if gap > 0:
                ref = d2.get_best_lap() # d2 best
            else:
                ref = d1.get_best_lap() # d1 best

            if ref <= 0:
                # about realistic time based on track length
                ref = 60000 * (self.track_length / 2600)
            return gap * ref

        ##################### Race ##################
        max_sector1 = self.get_max_sector(d1)
        max_sector2 = self.get_max_sector(d2)
        max_d1 = max_sector1 % 100 # gap to
        max_d2 = max_sector2 % 100 # current
        #return (max_d1 % 100 - max_d2 % 100) * 1000
        if abs(max_d2 - max_d1) > 50:
            sector = max(max_d1, max_d2)
            t1 = d1.realtime_gaps[sector]
            t2 = d2.realtime_gaps[sector]
            return t1 - t2
        # Same lap
        sector=min(max_d1,max_d2)
        if d1.realtime_gaps[sector] == 0 or d2.realtime_gaps[sector] == 0 or max_sector1 < 20 or max_sector2 < 20:
            max_d1 = (d1.raceProgress * 100) % 100
            max_d2 = (d2.raceProgress * 100) % 100
            # if behind get his time as ref else your best time
            # about realistic time based on track length
            ref = 60000 * (self.track_length / 2600)
            if max_d2 - max_d1 > 50:
                gap = (max_d1 + 100 - max_d2) / 100
            elif max_d2 - max_d1 < -50:
                gap = (max_d1 - 100 - max_d2) / 100
            else:
                gap = (max_d1 - max_d2) / 100
            return gap * ref
        t1 = d1.realtime_gaps[sector]
        t2 = d2.realtime_gaps[sector]
        return t1 - t2

    def get_max_sector(self, driver):
        if driver.race_gaps:
            return driver.race_gaps[-1].sector
        return 0

    def generate_standings_pos_before_race(self):
        # Generate standings from -0.5 to 0.5 for the start of race
        standings = []
        for i in range(self.cars_count):
            bl = ac.getCarLeaderboardPosition(i)
            standings.append((i, bl))
        self.standings_start_race = sorted(standings, key=lambda student: student[1], reverse=False)

    def get_standings_pos_before_race(self, driver):
        # Get position
        p = [i for i, v in enumerate(self.standings_start_race) if v[0] == driver.identifier]
        if len(p) > 0:
            return p[0]
        return ac.getCarRealTimeLeaderboardPosition(driver.identifier)

    def sector_is_valid(self, new_sector, driver):
        if len(driver.race_gaps) == 0 and self.sessionTimeLeft < 1760000 and not bool(ac.isCarInPitline(driver.identifier)) and not bool(ac.isCarInPit(driver.identifier)):
            return True
        if new_sector * 100 < driver.race_current_sector.value:
            return False
        if (new_sector * 100) % 100 > 88 and len(driver.race_gaps) < 15:
            return False
        if ac.getCarState(driver.identifier, acsys.CS.SpeedKMH) <= 1:
            return False
        if new_sector * 100 > driver.race_current_sector.value + 25:
            return False
        # other checks
        return True

    def update_drivers_race(self, game_data, replay=False):
        if self.lbl_title_stint.isVisible.value:
            self.lbl_title_stint.hide()
            self.lbl_title_stint_txt.hide()
            self.lbl_tire_stint.hide()
            self.lbl_tire_stint_txt.hide()
            for l in self.stintLabels:
                l.hide()
        self.driver_shown = 0
        nb_drivers_alive = 0
        cur_driver = 0
        cur_driver_pos = 0
        first_driver = 0
        first_driver_sector = 0
        cur_sector = 0
        best_pos = 0
        # if not replay:  Would need real timing
        if self.race_mode.hasChanged():
            if self.race_mode.value == 0:
                self.lbl_title_mode_txt.setText("Auto")
            elif self.race_mode.value == 1:
                self.lbl_title_mode_txt.setText("Gaps")
            elif self.race_mode.value == 2:
                self.lbl_title_mode_txt.setText("Intervals")
            elif self.race_mode.value == 3:
                self.lbl_title_mode_txt.setText("Compact")
            elif self.race_mode.value == 4:
                self.lbl_title_mode_txt.setText("Progress")
            elif self.race_mode.value == 5:
                self.lbl_title_mode_txt.setText("Pit Stops")
            elif self.race_mode.value == 6:
                self.lbl_title_mode_txt.setText("Tires")
            elif self.race_mode.value == 7:
                self.lbl_title_mode_txt.setText("Off")
            else:
                self.lbl_title_mode_txt.setText("Relative")
            if replay:
                self.title_mode_visible_end_replay = time.time() + 6
            else:
                self.title_mode_visible_end = self.sessionTimeLeft - 6000
        if not replay and self.title_mode_visible_end != 0 \
                and self.title_mode_visible_end < self.sessionTimeLeft:
            self.lbl_title_mode.show()
            self.lbl_title_mode_txt.show()
            for lbl in self.cars_classes:
                lbl.setY((Configuration.ui_row_height - 2)*-2)
        elif replay and self.title_mode_visible_end_replay != 0 \
                and self.title_mode_visible_end_replay > time.time():
            self.lbl_title_mode.show()
            self.lbl_title_mode_txt.show()
            for lbl in self.cars_classes:
                lbl.setY((Configuration.ui_row_height - 2)*-2)
        else:
            self.lbl_title_mode.hide()
            self.lbl_title_mode_txt.hide()
            for lbl in self.cars_classes:
                lbl.setY(-(Configuration.ui_row_height - 2))
        if replay:
            current_standings = self.standings_replay
        else:
            current_standings = self.standings
        if Colors.cars_classes_current >= 0:
            cur_class = Colors.car_classes_list[Colors.cars_classes_current]
            # filter current_standings
            unfiltered = current_standings
            current_standings = []
            for s in unfiltered:
                if cur_class == s[2]:
                    current_standings.append((s[0], s[1], s[2]))

        for driver in self.drivers:
            if replay:
                p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                if len(p) > 0 and p[0] == 0:
                    first_driver = driver
                    first_driver_sector = driver.race_current_sector.value
                if driver.isDisplayed:
                    self.driver_shown += 1
                    if len(p) > 0 and (best_pos == 0 or best_pos > p[0] + 1):
                        best_pos = p[0] + 1

                '''            
                bl = driver.raceProgress
                if bl >= 0.06 and not driver.finished.value and self.sector_is_valid(bl, driver):
                    driver.race_current_sector.setValue(math.floor(bl * 100))
                elif bl < 0.06 and len(driver.race_gaps) < 30:
                    t=0
                    #driver.race_gaps = []
                    #driver.race_standings_sector.setValue(0)
                    #driver.race_current_sector.setValue(0)
                #if driver.race_current_sector.hasChanged():
                #    driver.race_gaps.append(raceGaps(driver.race_current_sector.value, self.sessionTimeLeft))
                '''
            else:
                driver.isAlive.setValue(bool(ac.isConnected(driver.identifier)))
                if driver.isAlive.value:
                    nb_drivers_alive += 1
                p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                if len(p) > 0 and p[0] == 0:
                    first_driver = driver
                    first_driver_sector = driver.race_current_sector.value
                if driver.isDisplayed:
                    self.driver_shown += 1
                    if len(p) > 0 and (best_pos == 0 or best_pos > p[0] + 1):
                        best_pos = p[0] + 1
                if driver.isInPitBox.value and not driver.finished.value and not driver.inPitFromPitLane:
                    driver.race_gaps = []
                    if driver.race_standings_sector.value < 1:
                        driver.race_standings_sector.setValue(0)
                        driver.race_current_sector.setValue(0)
                if game_data.beforeRaceStart:
                    # driver.finished=False
                    self.numCarsToFinish = 0
                    driver.race_standings_sector.setValue(0)
                    driver.race_current_sector.setValue(0)
                    #Starting positions
                    self.generate_standings_pos_before_race()
                    driver.race_start_position = self.get_standings_pos_before_race(driver)
                else:
                    bl = driver.raceProgress
                    if bl >= 0.06 and not driver.finished.value and self.sector_is_valid(bl, driver):
                        driver.race_current_sector.setValue(math.floor(bl * 100))
                    elif bl < 0.06 and len(driver.race_gaps) < 30:
                        driver.race_gaps = []
                        driver.race_standings_sector.setValue(0)
                        driver.race_current_sector.setValue(0)

                if driver.race_current_sector.hasChanged():
                    driver.race_gaps.append(raceGaps(driver.race_current_sector.value, self.sessionTimeLeft))
                    driver.realtime_gaps[driver.race_current_sector.value%100] = self.sessionTimeLeft
            if driver.identifier == self.currentVehicule.value:
                driver.isCurrentVehicule.setValue(True)
                cur_driver = driver
                cur_sector = driver.race_current_sector.value
                if len(p) > 0:
                    cur_driver_pos = p[0] + 1
            else:
                driver.isCurrentVehicule.setValue(False)
        driver_shown = 0
        driver_shown_max_gap = 0
        max_gap = 2500
        # needs_tlc=True
        # memsize=0
        if self.race_mode.value == 0:
            for driver in self.drivers:
                # memsize += sys.getsizeof(driver.race_gaps)
                gap = self.gap_to_driver(driver, cur_driver, cur_sector)
                if driver.identifier == 0 or (gap < 2500 and cur_sector - self.get_max_sector(driver) < 15):
                    driver_shown += 1
                if driver.identifier == 0 or (gap < 5000 and cur_sector - self.get_max_sector(driver) < 15):
                    driver_shown_max_gap += 1
                if not replay:
                    driver.optimise()
                    # ac.console("Mem size:" + str(memsize/1024) + " ko")
        if not driver_shown > 1:
            driver_shown = driver_shown_max_gap
            max_gap = 5000
        if not driver_shown > 1:
            if self.lapsCompleted.hasChanged():
                self.leader_time = self.sessionTimeLeft
                if self.numCarsToFinish > 0:
                    self.race_show_end = self.sessionTimeLeft - 720000
                else:
                    self.race_show_end = self.sessionTimeLeft - 12000
        display_offset = 0
        ##########################################
        if cur_driver_pos >= self.max_num_cars:
            display_offset = cur_driver_pos - self.max_num_cars
            if nb_drivers_alive > cur_driver_pos:  # showing next driver to user
                display_offset += 1
        needs_tlc = True
        if Configuration.names >= 2:
            needs_tlc = False
        if 0 < self.race_mode.value < 8 and not self.force_hidden:
            # Full tower
            tick_limit = 40
            if self.sessionTimeLeft != 0 and int(self.sessionTimeLeft / 100) % 18 == 0 and self.tick_race_mode > tick_limit:
                self.tick_race_mode = 0
                for driver in self.drivers:
                    if driver.position_highlight_end == True:
                        driver.position_highlight_end = self.sessionTimeLeft - 5000
                    if driver.completedLapsChanged and driver.completedLaps.value > 1:
                        driver.last_lap_visible_end = self.sessionTimeLeft - 5000
                    p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                    if len(p) > 0 and p[0] < self.max_num_cars + display_offset and driver.race_current_sector.value > 5 and (p[0] < 3 or p[0] - 2 > display_offset):
                        if p[0] < 3:
                            driver.set_position(p[0] + 1, best_pos - 1, True)
                        else:
                            driver.set_position(p[0] + 1, best_pos - 1 + display_offset, True)
                        if self.race_mode.value == 1 or self.race_mode.value == 2 or (self.race_mode.value == 3 and (driver.isCurrentVehicule.value or cur_driver_pos - 2 == p[0] or cur_driver_pos == p[0] or driver.finished.value)):
                            gap = lap_gap = 0
                            if self.race_mode.value == 1:
                                gap = self.gap_to_driver(driver, first_driver, first_driver_sector)
                                lap_gap = self.get_max_sector(first_driver) - self.get_max_sector(driver)
                            elif self.race_mode.value == 2 or self.race_mode.value == 3:
                                if p[0] > 0:
                                    id_compare = current_standings[p[0]-1][0]
                                    for d in self.drivers:
                                        if id_compare == d.identifier:
                                            gap = self.gap_to_driver(driver, d, d.race_current_sector.value)
                                            lap_gap = self.get_max_sector(d) - self.get_max_sector(driver)
                                            break
                            if not replay and driver.finished.value:
                                driver.show(needs_tlc=False, compact=True)
                            elif not driver.isAlive.value:
                                driver.set_time_race_battle("DNF", first_driver.identifier)
                                driver.show(needs_tlc)
                            elif driver.isInPitLane.value or driver.isInPitBox.value:
                                driver.set_time_race_battle("PIT", first_driver.identifier)
                                driver.show(needs_tlc)
                            elif driver.last_lap_visible_end != 0 and driver.last_lap_visible_end < self.sessionTimeLeft:
                                lastlap = ac.getCarState(driver.identifier, acsys.CS.LastLap)
                                driver.set_time_race_battle(lastlap, -1)
                            elif driver.position_highlight_end != 0 and driver.position_highlight_end < self.sessionTimeLeft:
                                if driver.movingUp:
                                    driver.set_time_race_battle("UP", first_driver.identifier)
                                else:
                                    driver.set_time_race_battle("DOWN", first_driver.identifier)
                                driver.show(needs_tlc)
                            elif lap_gap > 100:
                                driver.set_time_race_battle(lap_gap / 100, first_driver.identifier, True)
                                driver.show(needs_tlc)
                            else:
                                driver.set_time_race_battle(gap, first_driver.identifier, False, self.race_mode.value == 2)
                                driver.show(needs_tlc)
                        elif Configuration.race_mode == 4:  # Progress
                            p2 = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                            if driver.race_start_position > p2[0]:
                                driver.set_time_race_battle("{0} UP".format(driver.race_start_position - p2[0]), -1)
                            elif driver.race_start_position < p2[0]:
                                driver.set_time_race_battle("{0} DOWN".format(p2[0] - driver.race_start_position), -1)
                            else:
                                driver.set_time_race_battle("0 NEUTRAL", -1)
                            driver.show(needs_tlc)
                        elif Configuration.race_mode == 5:  # pit stops
                            driver.set_time_race_battle(driver.pit_stops_count, -1)
                            driver.show(needs_tlc)
                            driver.update_pit(self.sessionTimeLeft)
                        elif Configuration.race_mode == 6:  # Tires
                            age = driver.completedLaps.value - max(driver.last_lap_in_pit, 0)
                            lastlap = ac.getCarTyreCompound(driver.identifier) + ' (' + str(age) + ' L)'
                            driver.set_time_race_battle(lastlap, -1)
                            driver.show(needs_tlc)
                            driver.update_pit(self.sessionTimeLeft)
                        elif Configuration.race_mode == 7:  # Timing off
                            driver.show(needs_tlc, compact=True)
                        else:
                            driver.show(needs_tlc=needs_tlc, compact=True)
                    else:
                        driver.hide()
                    driver.optimise()
            elif self.race_mode.value == 1 or self.race_mode.value == 2 or self.race_mode.value == 3:
                for driver in self.drivers:
                    p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                    if len(p) > 0 and p[0] < self.max_num_cars and driver.isDisplayed:
                        if self.race_mode.value == 1 or self.race_mode.value == 2 or (self.race_mode.value == 3 and (driver.isCurrentVehicule.value or cur_driver_pos - 2 == p[0] or cur_driver_pos == p[0])):
                            if driver.completedLapsChanged and driver.completedLaps.value > 1:
                                driver.last_lap_visible_end = self.sessionTimeLeft - 5000
                            if driver.finished.value:
                                driver.show(needs_tlc=False, compact=True)
                            elif driver.last_lap_visible_end != 0 and driver.last_lap_visible_end < self.sessionTimeLeft and driver.isAlive.value and not driver.isInPit.value:
                                lastlap = ac.getCarState(driver.identifier, acsys.CS.LastLap)
                                driver.set_time_race_battle(lastlap, -1)
                                # else:
                                #    driver.hide()
            self.tick_race_mode += 1
        elif self.race_mode.value == 8:# and not self.force_hidden
            # Realtime
            realtime_target = [i for i, v in enumerate(self.realtime_standings) if v[0] == self.currentVehicule.value]
            if len(realtime_target) > 0:
                max_num_cars = min(self.max_num_cars,len(self.standings) * 2)
                if max_num_cars % 2 == 1:
                    #5 % 2 = 1 - perfect 2 up,driver, 2 down
                    display_offset = max_down = math.ceil(max_num_cars / 2)
                else:
                    #6 = 3 up, driver, 2 down
                    display_offset = math.ceil(max_num_cars / 2) + 1
                    max_down = math.ceil(max_num_cars / 2)

                for driver in self.drivers:
                    r = [i for i, v in enumerate(self.realtime_standings) if v[0] == driver.identifier]
                    #ac.console("---"+str(-max_down) + " < " + str(realtime_target[0]) + " - " + str(r[0]) + " < " + str(display_offset))
                    if len(r) > 0 and -max_down < realtime_target[0] - r[0] < display_offset:
                        if replay:
                            p = [i for i, v in enumerate(self.standings_replay) if v[0] == driver.identifier]
                        else:
                            p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                        if driver.position_highlight_end == True:
                            driver.position_highlight_end = self.sessionTimeLeft - 5000
                        if driver.completedLapsChanged and driver.completedLaps.value > 1:
                            driver.last_lap_visible_end = self.sessionTimeLeft - 5000
                        if driver.last_lap_visible_end != 0 and driver.last_lap_visible_end < self.sessionTimeLeft and driver.isAlive.value and not driver.isInPit.value:
                            lastlap = ac.getCarState(driver.identifier, acsys.CS.LastLap)
                            driver.set_time_race_battle(lastlap, -1)
                        elif driver.position_highlight_end != 0 and driver.position_highlight_end < self.sessionTimeLeft:
                            if driver.movingUp:
                                driver.set_time_race_battle("UP", first_driver.identifier)
                            else:
                                driver.set_time_race_battle("DOWN", first_driver.identifier)
                        #elif driver.identifier == self.currentVehicule.value:
                        #    driver.set_time_race_battle("--.-", first_driver.identifier)
                        else:
                            # gap=0 realtime gap
                            gap = self.realtime_to_driver(driver, cur_driver)
                            driver.set_time_race_battle(gap, cur_driver.identifier,realtime=True)
                        if len(p) > 0:
                            driver.set_position(p[0] + 1, r[0] - realtime_target[0] + display_offset - 1, True, True)
                        else:
                            driver.set_position(0, r[0] - realtime_target[0] + display_offset - 1, True, True)
                        driver.show(needs_tlc=needs_tlc, realtime_target_laps=cur_sector)
                        driver.update_pit(self.sessionTimeLeft)
                    else:
                        driver.hide()
        elif not self.force_hidden and driver_shown > 1 and (
                self.race_show_end > self.sessionTimeLeft or self.race_show_end == 0):
            # Battles
            self.lapsCompleted.hasChanged()
            if self.sessionTimeLeft != 0 and int(self.sessionTimeLeft / 100) % 18 == 0 and self.tick > 20:
                self.tick = 0
                for driver in self.drivers:
                    gap = self.gap_to_driver(driver, cur_driver, cur_sector)
                    if len(cur_driver.race_gaps) > 15 and (driver.identifier == cur_driver.identifier or (gap < max_gap and cur_sector - self.get_max_sector(driver) < 12)):
                        p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                        if len(p) > 0:
                            driver.set_position(p[0] + 1, best_pos - 1, True)
                            if driver.position_highlight_end == True:
                                driver.position_highlight_end = self.sessionTimeLeft - 5000
                            if driver.position_highlight_end != 0 and driver.position_highlight_end < self.sessionTimeLeft:
                                if driver.movingUp:
                                    driver.set_time_race_battle("UP", cur_driver.identifier)
                                else:
                                    driver.set_time_race_battle("DOWN", cur_driver.identifier)
                            else:
                                driver.set_time_race_battle(gap, cur_driver.identifier)
                            driver.show(needs_tlc)
                    else:
                        p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                        if len(p) > 0:
                            driver.position.setValue(p[0] + 1)
                            # driver.position.hasChanged()
                        driver.hide()
            self.tick += 1

        elif self.race_show_end != 0 and self.race_show_end < self.sessionTimeLeft and not self.force_hidden:
            # Show full standings as they cross the finish line
            self.driver_shown = 0
            for driver in self.drivers:
                if driver.isDisplayed:
                    self.driver_shown += 1
            for driver in self.drivers:
                if driver.completedLaps.value == self.lapsCompleted.value:
                    p = [i for i, v in enumerate(current_standings) if v[0] == driver.identifier]
                    if len(p) > 0 and driver.completedLapsChanged:
                        driver.set_position(p[0] + 1, 0, False)
                        driver.set_time_race(driver.completedLaps.value, self.leader_time, self.sessionTimeLeft)
                        needs_tlc = True
                        if self.numCarsToFinish > 0:
                            needs_tlc = False
                        driver.show(needs_tlc)
        else:
            for driver in self.drivers:
                driver.hide()

    def get_drivers_info(self):
        info = []
        for driver in self.drivers:
            info.append({
                'id': driver.identifier,
                'number': driver.car_number,
                'team': driver.team_name
            })
        return info

    def drivers_info_is_updated(self):
        if self.drivers_info_updated:
            self.drivers_info_updated = False
            return True
        return False

    def load_drivers_info(self, sim_info):
        # Offline only
        if ac.getServerIP() == '':
            # Open race.ini
            conf = Config(Config.get_user_documents_path() + "cfg/", "race.ini")

            # loop config CAR_0 get
            for driver in self.drivers:
                model = ac.getCarName(driver.identifier)
                skin = conf.get("CAR_" + str(driver.identifier), "SKIN")
                if model != "" and skin != -1:
                    # Open skin file:
                    skin_path = os.path.join("content", "cars", model, "skins", skin) + "/ui_skin.json"
                    try:
                        if os.path.exists(skin_path):
                            with open(skin_path) as data_file:
                                # get number and team
                                data = json.load(data_file)
                                driver.car_number = data["number"]
                                driver.team_name = data["team"]
                    except:
                        Log.w("Error loading ui_skin")
        else:
            # Online Car 0
            model = ac.getCarName(0)
            skin = sim_info.static.carSkin
            if model != "" and skin != -1:
                # Open skin file:
                skin_path = os.path.join("content", "cars", model, "skins", skin) + "/ui_skin.json"
                try:
                    if os.path.exists(skin_path):
                        with open(skin_path) as data_file:
                            # get number and team
                            data = json.load(data_file)
                            self.drivers[0].car_number = data["number"]
                            self.drivers[0].team_name = data["team"]
                except:
                    Log.w("Error loading ui_skin")

    def get_standings_from_server(self):
        self.imported = True
        try:
            server_ip = ac.getServerIP()
            port = ac.getServerHttpPort()
            if server_ip != '' and port > 0:
                conn = http.client.HTTPConnection(server_ip, port=port)
                conn.request("GET", "/ENTRY")
                response = conn.getresponse()
                data1 = response.read()
                conn.close()

                parser = MyHTMLParser()
                parser.feed(data1.decode('utf-8', errors='ignore'))
                data2 = parser.data
                data2.pop(0)

                for d in data2:
                    bl = self.convert_time(d[5])
                    if bl > 0:
                        for driver in self.drivers:
                            norm_d1 = self.normalize_string(d[1])
                            if norm_d1 == self.normalize_string(driver.fullName.value) and str(d[2]) == driver.carName and bool(ac.isConnected(driver.identifier)):
                                driver.bestLapServer = bl
                                break
        except:
            Log.w("Error tower")

    def convert_time(self, time):
        t = str(time).split(':')
        if len(t) == 3 and int(t[0]) < 16000:  # != "16666":#16666:39:999
            return int(t[2]) + int(t[1]) * 1000 + int(t[0]) * 60000
        return 0

    def normalize_string(self, s):
        return s.encode('ascii', errors='ignore').decode('utf-8')

    def get_fastest_lap(self):
        return self.fastestLap

    def get_standings(self):
        return self.standings

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
            self.cars_classes_triggered=True
        else:
            self.cursor.setValue(False)
        session_changed = self.session.hasChanged()
        if session_changed:
            self.raceStarted = False
            self.curDriverLaps = []
            self.stint_visible_end = 0
            self.title_mode_visible_end = 0
            self.cars_classes_timeout = None
            for driver in self.drivers:
                driver.hide(True)

        if self.cursor.hasChanged() or session_changed:
            show = True
            for driver in self.drivers:
                if driver.isDisplayed:
                    show = False
                    break
            if self.cursor.value and show:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)
        # Classes swap
        self.cars_classes_mouse.setValue(game_data.cursor_x + game_data.cursor_y)
        if self.cars_classes_mouse.hasChanged() and self.cars_classes_triggered:
            self.cars_classes_timeout = self.sessionTimeLeft - 5000
        for i, lbl in enumerate(self.cars_classes):
            if (self.session.value == 2 and Configuration.race_mode == 8) or (self.session.value < 2 and Configuration.qual_mode==3):# realtime
                lbl.hide()
            elif i > 0 and i == Colors.cars_classes_current + 1: # current not overall
                lbl.show()
            elif self.cars_classes_timeout is not None and self.cars_classes_timeout < self.sessionTimeLeft:
                lbl.show()
            else:
                lbl.hide()
        if self.cars_classes_timeout is None or self.cars_classes_timeout >= self.sessionTimeLeft:
            self.cars_classes_triggered=False



    def on_update(self, sim_info, game_data):
        '''
        t_info = time.time()
        t_update_drivers = 0
        t_update_drivers_end = 0
        '''
        self.session.setValue(game_data.session)
        sim_info_status = game_data.status
        if (sim_info_status != 1 and sim_info_status != 3 and self.sessionTimeLeft != 0 and self.sessionTimeLeft != -1 and self.sessionTimeLeft + 100 < game_data.sessionTimeLeft) or sim_info_status == 0:
            self.session.setValue(-1)
            self.session.setValue(game_data.session)
        self.manage_window(game_data)
        self.init_car_classes()
        self.sessionTimeLeft = game_data.sessionTimeLeft
        if sim_info_status != 3:
            self.animate()
        self.currentVehicule.setValue(game_data.focusedCar)
        if sim_info_status == 2:# or (sim_info_status == 1 and self.session.value < 2):
            # LIVE
            realtime_target = ac.getCarState(self.currentVehicule.value, acsys.CS.NormalizedSplinePosition)
            if self.session.value < 2:
                # Qualify - Practise
                realtime_target_in_pit = bool(ac.isCarInPitline(self.currentVehicule.value)) or bool(ac.isCarInPit(self.currentVehicule.value))
                for driver in self.drivers:
                    driver.update_mandatory_pitstop(False)
                    c = ac.getCarState(driver.identifier, acsys.CS.LapCount)
                    driver.completedLaps.setValue(c)
                    driver.completedLapsChanged = driver.completedLaps.hasChanged()
                    if driver.completedLapsChanged:
                        driver.last_lap_visible_end = self.sessionTimeLeft - 6000
                        if self.sessionTimeLeft < 0:
                            driver.finished.setValue(True)
                    elif self.sessionTimeLeft < 0 and driver.isInPit.value:
                        driver.finished.setValue(True)
                    spline = ac.getCarState(driver.identifier, acsys.CS.NormalizedSplinePosition)
                    driver.raceProgress = spline

                if self.sessionTimeLeft != 0:
                    if not self.imported and self.is_multiplayer:
                        thread_standings = threading.Thread(target=self.get_standings_from_server)
                        thread_standings.daemon = True
                        thread_standings.start()

                    self.TimeLeftUpdate.setValue(int(self.sessionTimeLeft / 500))
                    if self.TimeLeftUpdate.hasChanged():
                        # stint view
                        lap_count = ac.getCarState(0, acsys.CS.LapCount)
                        self.curLapCount.setValue(lap_count)
                        if sim_info.physics.numberOfTyresOut >= 4:
                            self.lastLapInvalidated = lap_count
                        if self.curLapCount.hasChanged():
                            self.iLastTime.setValue(ac.getCarState(0, acsys.CS.LastLap))
                            if self.iLastTime.hasChanged():
                                self.curDriverLaps.append(
                                    Laps(self.curLapCount.value - 1, self.lastLapInvalidated != lap_count - 1,
                                         sim_info.graphics.iLastTime))
                                if len(self.curDriverLaps) > 5 and len(self.curDriverLaps) % 2 == 0:
                                    self.minlap_stint = len(self.curDriverLaps) + 5
                                if len(self.curDriverLaps) >= self.minlap_stint:
                                    self.stint_visible_end = self.sessionTimeLeft - 30000
                                    if self.stint_visible_end > 0 and self.stint_visible_end < 90000:
                                        if self.sessionTimeLeft - 90000 < 5000:
                                            self.stint_visible_end = 0
                                        else:
                                            self.stint_visible_end = 90000
                            else:
                                self.curLapCount.changed = True

                        standings = []
                        realtime_standings = []
                        self.fastestLap = 0
                        for i in range(self.cars_count):
                            self.drivers[i].bestLap = ac.getCarState(i, acsys.CS.BestLap)
                            bl = self.drivers[i].get_best_lap()
                            self.drivers[i].bestLap_value.setValue(bl)
                            if self.drivers[i].bestLap_value.hasChanged():
                                self.drivers[i].bestLap_sectors = ac.getLastSplits(i)
                            if bl > 0 and self.drivers[i].isAlive.value:  # and self.drivers[i].completedLaps.value > self.minLapCount
                                standings.append((i, bl, self.drivers[i].car_class_name))
                            elif self.is_touristenfahrten and (self.drivers[i].isAlive.value or (not self.drivers[i].isAlive.value and bl > 0)):
                                pro = 3600000 - (self.cars_count - self.drivers[i].identifier)
                                standings.append((i, pro, self.drivers[i].car_class_name))
                            elif self.drivers[i].isAlive.value or (not self.drivers[i].isAlive.value and bl > 0):
                                pro = 3600000 - self.drivers[i].completedLaps.value * 100
                                if not self.drivers[i].isInPit.value:
                                    pro -= ac.getCarState(i, acsys.CS.NormalizedSplinePosition) * 100
                                standings.append((i, pro, self.drivers[i].car_class_name))

                            #self.drivers[i].lapCount = ac.getCarState(i, acsys.CS.LapCount)
                            #if bl > 0 and self.drivers[i].lapCount > self.minLapCount and self.drivers[i].isAlive.value:
                            #    standings.append((i, bl))
                            # fastestLap for info widget
                            if self.fastestLap == 0 or (0 < bl < self.fastestLap):
                                self.fastestLap = bl
                                # self.fastestLapSectors = ac.getLastSplits(x)
                            # realtime
                            if self.drivers[i].isAlive.value and \
                                    ((realtime_target_in_pit) or
                                     (not realtime_target_in_pit and not self.drivers[i].isInPit.value)):
                                spline = ac.getCarState(self.drivers[i].identifier, acsys.CS.NormalizedSplinePosition)
                                if realtime_target - spline > 0.5:
                                    realtime_standings.append((self.drivers[i].identifier, spline + 1))
                                elif realtime_target - spline < -0.5:
                                    realtime_standings.append((self.drivers[i].identifier, spline - 1))
                                else:
                                    realtime_standings.append((self.drivers[i].identifier, spline))

                        self.standings = sorted(standings, key=lambda student: student[1])
                        self.realtime_standings = sorted(realtime_standings, key=lambda student: student[1], reverse=True)
                        #t_update_drivers = time.time()
                        self.update_drivers(sim_info)
                        #t_update_drivers_end = time.time()

            elif self.session.value == 2:
                # RACE
                completed = 0
                standings = []
                realtime_standings = []
                # new standings
                # iTime < 10 lap=0 dont loop direct to backup standings
                if not self.raceStarted and not (
                        sim_info.graphics.iCurrentTime <= 12000 and sim_info.graphics.completedLaps == 0):
                    self.raceStarted = True
                if self.raceStarted:  #
                    for driver in self.drivers:
                        driver.update_mandatory_pitstop(False)
                        c = ac.getCarState(driver.identifier, acsys.CS.LapCount)
                        driver.completedLaps.setValue(c)
                        driver.completedLapsChanged = driver.completedLaps.hasChanged()
                        driver.finished.setValue(ac.getCarState(driver.identifier, acsys.CS.RaceFinished) == 1)
                        if c > completed:
                            completed = c
                        spline = ac.getCarState(driver.identifier, acsys.CS.NormalizedSplinePosition)
                        driver.raceProgress = c + spline
                        if self.sector_is_valid(driver.raceProgress, driver):
                            # or lapcount changed and leader finished
                            if driver.finished.hasChanged() and driver.finished.value:
                                # or (self.numCarsToFinish > 0 and driver.completedLapsChanged)):
                                driver.race_standings_sector.setValue(
                                    driver.completedLaps.value + (self.cars_count - self.numCarsToFinish) / 1000)
                                self.numCarsToFinish += 1
                                # driver.finished=True
                            elif not driver.finished.value:
                                driver.race_standings_sector.setValue(driver.raceProgress)
                        if not driver.hasStartedRace and (len(driver.race_gaps) > 2 or driver.race_standings_sector.value > 1):
                            driver.hasStartedRace = True
                        if driver.race_standings_sector.value > 0 and driver.hasStartedRace:
                            standings.append((driver.identifier, driver.race_standings_sector.value, driver.car_class_name))
                            # realtime
                            if driver.isAlive.value:
                                if realtime_target - spline > 0.5:
                                    realtime_standings.append((driver.identifier, spline + 1))
                                elif realtime_target - spline < -0.5:
                                    realtime_standings.append((driver.identifier, spline - 1))
                                else:
                                    realtime_standings.append((driver.identifier, spline))

                self.lapsCompleted.setValue(completed)
                if len(standings) > 0:
                    self.standings = sorted(standings, key=lambda student: student[1], reverse=True)
                    self.realtime_standings = sorted(realtime_standings, key=lambda student: student[1], reverse=True)
                    self.force_hidden = False
                else:
                    # backup standings
                    completed = 0
                    standings2 = []
                    for i in range(self.cars_count):
                        c = ac.getCarState(i, acsys.CS.LapCount)
                        # driver[i].completedLaps.setValue(c)
                        # driver[i].completedLapsChanged=driver[i].completedLaps.hasChanged()
                        if c > completed:
                            completed = c
                        #bl = c + ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
                        #if bl > 0:
                        #    standings2.append((i, bl))
                        if self.drivers[i].isAlive.value:
                            spline = ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
                            if c == 0 and spline > 0.6:
                                spline -= 1
                            bl = c + spline
                            standings2.append((i, bl, self.drivers[i].car_class_name))
                            if realtime_target - spline > 0.5:
                                realtime_standings.append((self.drivers[i].identifier, spline + 1))
                            elif realtime_target - spline < -0.5:
                                realtime_standings.append((self.drivers[i].identifier, spline - 1))
                            else:
                                realtime_standings.append((self.drivers[i].identifier, spline))

                    self.standings = sorted(standings2, key=lambda student: student[1], reverse=True)
                    self.realtime_standings = sorted(realtime_standings, key=lambda student: student[1], reverse=True)
                    self.force_hidden = True
                    self.lapsCompleted.setValue(completed)
                '''
                # Debug code
                o = 1
                for i, s in self.standings:
                    if o <= 10:
                        ac.console("standings:" + str(o) + "-" + ac.getDriverName(i) + " id:" + str(i) + " sector:" + str(s))
                    o = o + 1
                ac.console("---------------------------------") 
                
                for driver in self.drivers:
                    if not driver.hasStartedRace:
                        ac.log("standings:" + str(len(driver.race_gaps)) + "-" + driver.fullName.value + " pro:" + str(driver.raceProgress) + " s:" + str(driver.hasStartedRace))
                        ac.console("standings:" + str(len(driver.race_gaps)) + "-" + driver.fullName.value + " pro:" + str(driver.raceProgress) + " s:" + str(driver.hasStartedRace))
                for driver in self.drivers:
                    ac.log(
                        "1standings:" + "-" + driver.fullName.value + " id:" + str(
                            driver.finished.value) + " sector:" + str(driver.race_standings_sector.value))
                '''
                #t_update_drivers = time.time()
                self.update_drivers_race(game_data)
                #t_update_drivers_end = time.time()
            elif self.session.value > 2:  # other session
                for driver in self.drivers:
                    driver.hide()
                self.lbl_title_stint.hide()
                self.lbl_title_stint_txt.hide()
                self.lbl_tire_stint.hide()
                self.lbl_tire_stint_txt.hide()
                self.lbl_title_mode.hide()
                self.lbl_title_mode_txt.hide()
                for l in self.stintLabels:
                    l.hide()
        elif sim_info_status == 1:  # Replay
            if self.session.value < 2:  # Qual
                standings = []
                for i in range(self.cars_count):
                    bl = ac.getCarState(i, acsys.CS.BestLap)
                    if bl > 0:
                        standings.append((i, bl, self.drivers[i].car_class_name))
                self.standings = sorted(standings, key=lambda student: student[1])
                self.update_drivers_replay()
            elif self.session.value == 2:  # Race
                #completed = 0
                standings = []
                for i in range(self.cars_count):
                    #c = ac.getCarState(i, acsys.CS.LapCount)
                    # driver[i].completedLaps.setValue(c)
                    # driver[i].completedLapsChanged=driver[i].completedLaps.hasChanged()
                    #if c > completed:
                    #    completed = c
                    #bl = c + ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
                    #pos = ac.getCarRealTimeLeaderboardPosition(i)
                    #if bl > 0:
                    #standings.append((i, pos, pos))
                    #standings.append((i, bl, pos))
                    bl = ac.getCarState(i, acsys.CS.LapCount) + ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
                    #if bl > 0:
                    standings.append((i, bl, self.drivers[i].car_class_name))

                #self.standings_replay = sorted(standings, key=lambda student: student[1], reverse=False)
                self.standings_replay = sorted(standings, key=lambda student: student[1], reverse=True)
                #Sort by place
                self.force_hidden = False
                #self.lapsCompleted.setValue(completed)
                self.update_drivers_race(game_data, replay=True)

                # Debug code
                '''

                o = 1
                for i, s in self.standings_replay:
                    if o <= 10:
                        ac.console("standings:" + str(o) + "-" + ac.getDriverName(i) + " id:" + str(i) + " sector:" + str(s))
                    o = o + 1
                ac.console("---------------------------------")
                p = [i for i, v in enumerate(standings) if v[0] == vehicle]
                if len(p) > 0:
                    return p[0] + 1
                return 0
                for driver in self.drivers:
                    if not driver.hasStartedRace:
                        ac.log("standings:" + str(len(driver.race_gaps)) + "-" + driver.fullName.value + " pro:" + str(driver.raceProgress) + " s:" + str(driver.hasStartedRace))
                        ac.console("standings:" + str(len(driver.race_gaps)) + "-" + driver.fullName.value + " pro:" + str(driver.raceProgress) + " s:" + str(driver.hasStartedRace))
                for driver in self.drivers:
                    ac.log(
                        "1standings:" + "-" + driver.fullName.value + " id:" + str(
                            driver.finished.value) + " sector:" + str(driver.race_standings_sector.value))
                '''

        else:
            # Paused-OFF
            self.lbl_title_mode.hide()
            self.lbl_title_mode_txt.hide()
        '''
        t_tower = time.time()
        if t_tower - t_info > 0.006:
            t_total = t_tower - t_info
            t_total_d = t_update_drivers_end - t_update_drivers
            # ac.console(str(t_total) + " u_diver:" + str(t_total_d))
            # ac.log(str(t_total) + " u_diver:" + str(t_total_d))
        '''