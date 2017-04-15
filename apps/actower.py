import ac
import acsys
import math
import functools
import ctypes
import time
from apps.util.func import rgb, getFontSize
from apps.util.classes import Window, Label, Value, POINT, Colors, Config, Log, raceGaps
import http.client
import encodings.idna
import threading
from html.parser import HTMLParser


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


class Laps:
    def __init__(self, lap, valid, time):
        self.lap = lap
        self.valid = valid
        self.time = time


class Driver:
    def __init__(self, app, row_height, font_name, identifier, name, pos, is_lap_label=False):
        self.identifier = identifier
        self.rowHeight = row_height
        self.race = False
        self.hasStartedRace = False
        self.inPitFromPitLane = False
        self.isInPitLane = Value(False)
        self.isInPitLaneOld = False
        self.isInPitBox = Value(False)
        self.fontSize = getFontSize(self.rowHeight)
        str_offset = " "
        self.final_y = 0
        self.isDisplayed = False
        self.firstDraw = False
        self.isAlive = Value(False)
        self.pitBoxMode = False
        self.movingUp = False
        self.isCurrentVehicule = Value(False)
        self.isLapLabel = is_lap_label
        self.qual_mode = Value(0)
        self.race_gaps = []
        self.finished = Value(False)
        self.bestLap = 0
        self.bestLapServer = 0
        self.lapCount = 0
        self.fullName = Value(name)
        self.shortName = name
        self.time = Value()
        self.gap = Value()
        self.raceProgress = 0
        self.race_current_sector = Value(0)
        self.race_standings_sector = Value(0)
        self.isInPit = Value(False)
        self.completedLaps = Value()
        self.completedLapsChanged = False
        self.last_lap_visible_end = 0
        self.time_highlight_end = 0
        self.position_highlight_end = 0
        self.highlight = Value()
        self.pit_highlight_end = 0
        self.pit_highlight = Value()
        self.position = Value()
        self.position_offset = Value()
        self.carName = ac.getCarName(self.identifier)
        # self.gapToFirst=0
        self.num_pos = 0
        self.showingFullNames = False
        if self.isLapLabel:
            self.lbl_name = Label(app, str_offset + name)\
                .set(w=self.rowHeight * 6, h=self.rowHeight,
                     x=0, y=0,
                     font_size=self.fontSize,
                     align="left",
                     background=Colors.background_tower(),
                     opacity=0.6,
                     visible=0)
        else:
            self.lbl_name = Label(app, str_offset + self.format_name_tlc(name))\
                .set(w=self.rowHeight * 5, h=self.rowHeight,
                     x=self.rowHeight, y=0,
                     font_size=self.fontSize,
                     align="left",
                     background=Colors.background_tower(),
                     opacity=0.6,
                     visible=0)
            self.lbl_position = Label(app, str(pos + 1))\
                .set(w=self.rowHeight, h=self.rowHeight,
                     x=0, y=0,
                     font_size=self.fontSize,
                     align="center",
                     background=Colors.background_tower_position_odd(),
                     color=Colors.white(),
                     opacity=1,
                     visible=0)
            self.lbl_pit = Label(app, "P")\
                .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                     x=self.rowHeight * 6, y=self.final_y + 2,
                     font_size=self.fontSize - 3,
                     align="center",
                     opacity=0,
                     visible=0)
            self.lbl_pit.setAnimationSpeed("rgb", 0.08)
            self.lbl_position.setAnimationMode("y", "spring")
            self.lbl_pit.setAnimationMode("y", "spring")
        self.lbl_time = Label(app, "+0.000")\
            .set(w=self.rowHeight * 4.7, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 color=Colors.grey(),
                 font_size=self.fontSize,
                 align="right",
                 opacity=0,
                 visible=0)
        self.lbl_border = Label(app, "")\
            .set(w=self.rowHeight * 2.8, h=1,
                 x=0, y=self.rowHeight - 1,
                 background=Colors.red(bg=True),
                 opacity=Colors.border_opacity(),
                 visible=0)
        self.set_name()
        self.lbl_time.setAnimationSpeed("rgb", 0.08)
        self.lbl_name.setAnimationMode("y", "spring")
        self.lbl_time.setAnimationMode("y", "spring")
        self.lbl_border.setAnimationMode("y", "spring")

        if font_name != "":
            self.lbl_name.setFont(font_name, 0, 0)
            self.lbl_time.setFont(font_name, 0, 0)
            if not self.isLapLabel:
                self.lbl_position.setFont(font_name, 0, 0)
                self.lbl_pit.setFont(font_name, 0, 0)

        if not self.isLapLabel:
            self.partial_func = functools.partial(self.on_click_func, driver=self.identifier)
            ac.addOnClickedListener(self.lbl_position.label, self.partial_func)
            ac.addOnClickedListener(self.lbl_name.label, self.partial_func)

    @classmethod
    def on_click_func(*args, driver=0):
        ac.focusCar(driver)

    def redraw_size(self, height):
        self.rowHeight = height
        font_size = getFontSize(self.rowHeight)
        self.final_y = self.num_pos * self.rowHeight
        if self.isLapLabel:
            self.lbl_name.setSize(self.rowHeight * 6, self.rowHeight).setPos(0, self.final_y).setFontSize(font_size)
        else:
            if self.isInPit.value and not self.race:
                self.lbl_name.setSize(self.rowHeight * 5.6, self.rowHeight)\
                    .setPos(self.rowHeight, self.final_y)\
                    .setFontSize(font_size)
            else:
                self.lbl_name.setSize(self.rowHeight * 5, self.rowHeight)\
                    .setPos(self.rowHeight, self.final_y)\
                    .setFontSize(font_size)
            self.lbl_position.setSize(self.rowHeight, self.rowHeight)\
                .setPos(0, self.final_y).setFontSize(font_size)
            self.lbl_pit.setSize(self.rowHeight * 0.6, self.rowHeight - 2)\
                .setPos(self.rowHeight * 6, self.final_y + 2).setFontSize(font_size - 3)
        self.lbl_time.setSize(self.rowHeight * 4.7, self.rowHeight)\
            .setPos(self.rowHeight, self.final_y).setFontSize(font_size)
        self.lbl_border.setSize(self.rowHeight * 2.8, 1)\
            .setPos(0, self.final_y + self.rowHeight - 1)

    def show(self, needs_tlc=True, race=True):
        self.race = race
        if self.showingFullNames and needs_tlc:
            self.set_name()
        elif not self.showingFullNames and not needs_tlc:
            self.show_full_name()
        if self.pitBoxMode:
            if self.isInPit.value:
                self.lbl_pit.showText()
                self.lbl_name.setSize(self.rowHeight * 15.6, self.rowHeight, True)
            else:
                self.lbl_pit.hideText()
                self.lbl_name.setSize(self.rowHeight * 15, self.rowHeight, True)
        else:
            if not self.isDisplayed:
                if not self.isLapLabel:
                    if self.isInPit.value and not race:
                        self.lbl_pit.showText()
                        self.lbl_name.setSize(self.rowHeight * 5.6, self.rowHeight, True)
                    else:
                        self.lbl_pit.hideText()
                        self.lbl_name.setSize(self.rowHeight * 5, self.rowHeight, True)
                self.isDisplayed = True
        self.lbl_name.show()

        if needs_tlc or self.isLapLabel:
            self.lbl_time.showText()
        self.lbl_border.show()
        if not self.isLapLabel:
            self.lbl_position.show()
            if not self.isAlive.value and not self.finished.value:
                self.lbl_name.setColor(Colors.grey(), True)
            elif self.isInPit.value or ac.getCarState(self.identifier, acsys.CS.SpeedKMH) > 30 or self.finished.value:
                self.lbl_name.setColor(Colors.white(), True)
            else:
                self.lbl_name.setColor(Colors.yellow(), True)

    def update_pit(self, session_time):
        if not self.isLapLabel and self.isInPit.hasChanged():
            if self.isInPit.value:
                self.pit_highlight_end = session_time - 5000
                self.lbl_pit.showText()
                if not self.pitBoxMode:
                    self.lbl_name.setSize(self.rowHeight * 5.6, self.rowHeight, True)
            else:
                self.lbl_pit.hideText()
                if not self.pitBoxMode:
                    self.lbl_name.setSize(self.rowHeight * 5, self.rowHeight, True)
        if self.isInPit.value and (
                self.lbl_name.f_params["w"].value < self.rowHeight * 5.6 or self.lbl_pit.f_params["a"].value < 1):
            self.lbl_pit.showText()
            if not self.pitBoxMode:
                self.lbl_name.setSize(self.rowHeight * 5.6, self.rowHeight, True)
        elif not self.isInPit.value and (
                self.lbl_name.f_params["w"].value > self.rowHeight * 5 or self.lbl_pit.f_params["a"].value == 1):
            self.lbl_pit.hideText()
            if not self.pitBoxMode:
                self.lbl_name.setSize(self.rowHeight * 5, self.rowHeight, True)
                # color
        if session_time == -1:
            self.pit_highlight_end = 0
        self.pit_highlight.setValue(self.pit_highlight_end != 0 and self.pit_highlight_end < session_time)
        if self.pit_highlight.hasChanged():
            if self.pit_highlight.value:
                self.lbl_pit.setColor(Colors.red())
            else:
                self.lbl_pit.setColor(Colors.pitColor(), True)

    def hide(self, reset=False):
        if not self.isLapLabel:
            self.lbl_position.hide()
            self.lbl_pit.hideText()
            if self.isInPit.value:
                self.lbl_name.setSize(self.rowHeight * 5.6, self.rowHeight)
            else:
                self.lbl_name.setSize(self.rowHeight * 5, self.rowHeight)
        self.lbl_time.hideText()
        self.lbl_border.hide()
        self.lbl_name.hide()
        self.isDisplayed = False
        if reset:
            self.finished.setValue(False)
            self.isInPit.setValue(False)
            self.firstDraw = False
            self.set_name()
            self.race_current_sector.setValue(0)
            self.race_standings_sector.setValue(0)
            self.race_gaps = []
            self.completedLaps.setValue(0)
            self.completedLapsChanged = False
            self.last_lap_visible_end = 0
            self.time_highlight_end = 0
            self.bestLap = 0
            self.bestLapServer = 0
            self.position_highlight_end = 0
            self.inPitFromPitLane = False
            self.hasStartedRace = False
            self.isInPitBox.setValue(False)

    def get_best_lap(self, lap=False):
        if lap:
            self.bestLap = lap
        if self.bestLapServer > 0 and self.bestLap > 0:
            if self.bestLapServer > self.bestLap:
                return self.bestLap
            else:
                return self.bestLapServer
        if self.bestLapServer > 0:
            return self.bestLapServer
        if self.bestLap > 0:
            return self.bestLap
        return 0

    def set_name(self):
        self.showingFullNames = False
        offset = " "
        if self.isLapLabel:
            self.lbl_name.setText(offset + self.fullName.value)
        else:
            self.lbl_name.setText(offset + self.format_name_tlc(self.fullName.value))
            self.set_border()

    def set_border(self):
        self.lbl_border.setBgColor(Colors.colorFromCar(self.carName, ACTower.colorsByClass)).setBgOpacity(Colors.border_opacity())

    def show_full_name(self):
        offset = " "
        self.showingFullNames = True
        self.lbl_time.hideText()
        if self.isLapLabel:
            self.lbl_name.setText(offset + self.fullName.value)
        else:
            self.lbl_name.setText(offset + self.format_last_name(self.fullName.value))

    def set_time(self, time, leader, session_time, mode):
        if self.highlight.value:
            if mode == 0:
                mode = 1
        self.qual_mode.setValue(mode)
        self.time.setValue(time)
        self.gap.setValue(time - leader)
        time_changed = self.time.hasChanged()
        if time_changed or self.gap.hasChanged() or self.qual_mode.hasChanged():
            if time_changed:
                self.time_highlight_end = session_time - 5000
            if self.position.value == 1 or mode == 1:
                self.lbl_time.setText(self.format_time(self.time.value))
            else:
                self.lbl_time.setText("+" + self.format_time(self.gap.value))

    def set_time_stint(self, time, valid):
        self.time.setValue(time)
        self.gap.setValue(time)
        if self.time.hasChanged() or self.gap.hasChanged():
            self.lbl_time.setText(self.format_time(self.time.value))  # .setVisible(1)
            self.lbl_time.setColor(Colors.grey())
            if valid:
                self.lbl_time.setColor(Colors.white())
            else:
                self.lbl_time.setColor(Colors.red())
                # self.lbl_time.showText()

    def set_time_race(self, time, leader, session_time):
        if self.position.value == 1:
            self.lbl_time.setText("Lap " + str(time)).setColor(Colors.white())
        else:
            self.lbl_time.setText("+" + self.format_time(leader - session_time)).setColor(Colors.white())

    def set_time_race_battle(self, time, identifier, lap=False):
        if time == "PIT":
            self.lbl_time.setText("PIT").setColor(Colors.yellow(), True)
        elif time == "DNF":
            self.lbl_time.setText("DNF").setColor(Colors.dnf(), True)
        elif time == "UP":
            self.lbl_time.setText(u"\u25B2").setColor(Colors.green(), True)
        elif time == "DOWN":
            self.lbl_time.setText(u"\u25BC").setColor(Colors.red(), True)
        elif self.identifier == identifier or time == 600000:
            self.lbl_time.setText("").setColor(Colors.white(), True)
        elif lap:
            str_time = "+" + str(math.floor(abs(time)))
            if abs(time) >= 2:
                str_time += " Laps"
            else:
                str_time += " Lap"
            self.lbl_time.setText(str_time).setColor(Colors.white(), True)
        elif identifier == -1:
            if time <= ac.getCarState(self.identifier, acsys.CS.BestLap):
                self.lbl_time.setText(self.format_time(time)).setColor(Colors.purple(), True)
            else:
                self.lbl_time.setText(self.format_time(time)).setColor(Colors.red(), True)
        else:
            self.lbl_time.setText(self.format_time(time)).setColor(Colors.white(), True)

    def optimise(self):
        if len(self.race_gaps) > 132:
            del self.race_gaps[0:len(self.race_gaps) - 132]

    def set_position(self, position, offset, battles, qual_mode):
        if not self.isLapLabel:
            self.isInPitLane.setValue(bool(ac.isCarInPitline(self.identifier)))
            self.isInPitBox.setValue(bool(ac.isCarInPit(self.identifier)))
            pit_value = self.isInPitLane.value or self.isInPitBox.value
            self.isInPit.setValue(pit_value)
            if self.race:
                if self.isInPitBox.hasChanged():
                    if self.isInPitBox.value:
                        self.inPitFromPitLane = self.isInPitLaneOld
                    else:
                        self.inPitFromPitLane = False
                self.isInPitLaneOld = self.isInPitLane.value

        self.position.setValue(position)
        self.position_offset.setValue(offset)
        position_changed = self.position.hasChanged()
        if position_changed or self.position_offset.hasChanged() or self.isCurrentVehicule.hasChanged() or self.isAlive.hasChanged():
            if position_changed:
                if self.position.value < self.position.old:
                    self.movingUp = True
                else:
                    self.movingUp = False
                if self.position.old > 0:
                    self.position_highlight_end = True
            # move labels
            self.num_pos = position - 1 - offset
            self.final_y = self.num_pos * self.rowHeight
            # avoid long slide on first draw
            if not self.firstDraw:
                if self.isLapLabel:
                    self.lbl_name.setY(self.final_y)
                else:
                    self.lbl_name.setY(self.final_y)
                    self.lbl_position.setY(self.final_y)
                    self.lbl_pit.setY(self.final_y + 2)
                self.lbl_time.setY(self.final_y)
                self.lbl_border.setY(self.final_y + self.rowHeight - 1)
                self.firstDraw = True

            if self.isLapLabel:
                self.lbl_name.setPos(0, self.final_y, True)
            else:
                self.lbl_position.setText(str(self.position.value))
                self.lbl_name.setPos(self.rowHeight, self.final_y, True)
                self.lbl_position.setPos(0, self.final_y, True)
                self.lbl_pit.setPos(self.rowHeight * 6, self.final_y + 2, True)
            self.lbl_time.setPos(self.rowHeight, self.final_y, True)
            self.lbl_border.setPos(0, self.final_y + self.rowHeight - 1, True)
            if position % 2 == 1:
                if self.isAlive.value:
                    self.lbl_name.setBgOpacity(0.72)
                else:
                    self.lbl_name.setBgOpacity(0.52)
                if position == 1:
                    if not self.isLapLabel:
                        self.lbl_position.setBgColor(Colors.background_first(), True)\
                            .setColor(Colors.white(), True)\
                            .setBgOpacity(0.72)
                    #self.lbl_time.setText(self.format_time(self.time.value))
                elif battles and self.isCurrentVehicule.value:
                    if not self.isLapLabel:
                        self.lbl_position.setBgColor(Colors.background_tower_position_highlight(), True)\
                            .setColor(Colors.red(), True).setBgOpacity(0.72)
                    #self.lbl_time.setText(self.format_time(self.time.value))
                else:
                    if not self.isLapLabel:
                        if self.isAlive.value:
                            self.lbl_position.setBgColor(Colors.background_tower_position_odd(), True)\
                                .setColor(Colors.white(), True)\
                                .setBgOpacity(0.72)
                        else:
                            self.lbl_position.setBgColor(Colors.background_tower_position_odd(), True)\
                                .setColor(Colors.grey(), True)\
                                .setBgOpacity(0.62)
                    '''
                    if qual_mode == 1:
                        self.lbl_time.setText(self.format_time(self.time.value))
                    else:
                        self.lbl_time.setText("+" + self.format_time(self.gap.value))
                    '''
            else:
                if self.isAlive.value:
                    self.lbl_name.setBgOpacity(0.58)
                else:
                    self.lbl_name.setBgOpacity(0.44)
                if battles and self.isCurrentVehicule.value:  # (self.identifier == 0 or)
                    if not self.isLapLabel:
                        self.lbl_position.setBgColor(Colors.background_tower_position_highlight(), True)\
                            .setColor(Colors.red(), True)\
                            .setBgOpacity(0.68)
                    #self.lbl_time.setText(self.format_time(self.time.value))
                else:
                    if not self.isLapLabel:
                        if self.isAlive.value:
                            self.lbl_position.setBgColor(Colors.background_tower_position_even(), True)\
                                .setColor(Colors.white(), True)\
                                .setBgOpacity(0.58)
                        else:
                            self.lbl_position.setBgColor(Colors.background_tower_position_even(), True)\
                                .setColor(Colors.grey(), True)\
                                .setBgOpacity(0.52)
                    '''
                    if qual_mode == 1:
                        self.lbl_time.setText(self.format_time(self.time.value))
                    else:
                        self.lbl_time.setText("+" + self.format_time(self.gap.value))
                    '''
        if not self.isLapLabel:
            self.fullName.setValue(ac.getDriverName(self.identifier))
            if self.fullName.hasChanged():
                # Reset
                self.finished.setValue(False)
                self.set_name()
                self.race_current_sector.setValue(0)
                self.race_standings_sector.setValue(0)
                self.race_gaps = []
                self.completedLaps.setValue(0)
                self.completedLapsChanged = False
                self.last_lap_visible_end = 0
                self.time_highlight_end = 0
                self.bestLap = 0
                self.bestLapServer = 0
                self.position_highlight_end = 0
                self.inPitFromPitLane = False
                self.hasStartedRace = False
                self.isInPitBox.setValue(False)

    def format_name_tlc(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip().upper()
        if len(name) > 2:
            return name[:3]
        return name

    def format_last_name(self, name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name = name.strip().upper()
        if len(name) > 9:
            return name[:10]
        return name

    def format_time(self, ms):
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        d = ms % 1000
        if math.isnan(s) or math.isnan(d) or math.isnan(m) or math.isnan(h):
            return ""
        if h > 0:
            return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
        elif m > 0:
            return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(3))
        else:
            return "{0}.{1}".format(int(s), str(int(d)).zfill(3))

    def animate(self, session_time_left):
        if session_time_left == -1:
            self.time_highlight_end = 0
        # color
        self.highlight.setValue(self.time_highlight_end != 0 and self.time_highlight_end < session_time_left)
        if self.highlight.hasChanged():
            if self.highlight.value:
                self.lbl_time.setColor(Colors.highlight(), True)
            else:
                self.lbl_time.setColor(Colors.white(), True)
        if not self.isLapLabel:
            self.lbl_position.animate()
            self.lbl_pit.animate()
        self.lbl_border.animate()
        self.lbl_time.animate()
        self.lbl_name.animate()


class ACTower:
    colorsByClass = False

    # INITIALIZATION
    def __init__(self):
        self.rowHeight = 36
        self.fontName = ""
        self.drivers = []
        self.stintLabels = []
        self.standings = []
        self.numCars = Value()
        self.session = Value(-1)
        self.sessionTimeLeft = 0
        self.imported = False
        self.TimeLeftUpdate = Value()
        self.lapsCompleted = Value()
        self.currentVehicule = Value(0)
        self.fastestLap = 0
        self.race_show_end = 0
        self.driver_shown = 0
        self.drivers_inited = False
        self.force_hidden = False
        self.pitBoxMode = False
        self.raceStarted = False
        self.leader_time = 0
        self.tick = 0
        self.tick_race_mode = 0
        self.tick_update = 0
        self.cursor = Value(False)
        self.max_num_cars = 18
        self.max_num_laps_stint = 8
        self.numberOfLaps = -1
        self.race_mode = Value(0)
        self.qual_mode = Value(0)
        self.ui_row_height = Value(-1)
        self.numCarsToFinish = 0
        self.window = Window(name="ACTV Tower", icon=False, width=268, height=114, texture="")
        self.minLapCount = 1
        self.curLapCount = Value()
        self.stint_visible_end = 0
        self.title_mode_visible_end = 0
        self.curDriverLaps = []
        self.lastLapInvalidated = -1
        self.minlap_stint = 5
        self.iLastTime = Value()
        self.lbl_title_stint = Label(self.window.app, "Current Stint")\
            .set(w=self.rowHeight * 6, h=self.rowHeight - 4,
                 x=0, y=self.rowHeight * 4 - self.rowHeight - 6,
                 font_size=23,
                 align="center",
                 background=Colors.background_dark(),
                 opacity=0.8,
                 visible=0)
        self.lbl_tire_stint = Label(self.window.app, "")\
            .set(w=self.rowHeight * 6, h=self.rowHeight,
                 x=0, y=self.rowHeight * 4 - (self.rowHeight - 4),
                 font_size=24,
                 align="center",
                 background=Colors.background_tower(),
                 opacity=0.58,
                 visible=0)
        self.lbl_title_mode = Label(self.window.app, "Mode") \
            .set(w=self.rowHeight * 6, h=self.rowHeight - 4,
                 x=0, y=-(self.rowHeight - 4),
                 font_size=23,
                 align="center",
                 background=Colors.theme(bg=True),
                 opacity=0.8,
                 visible=0)
        track = ac.getTrackName(0)
        config = ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife") >= 0 and config.find("touristenfahrten") >= 0:
            self.minLapCount = 0
        elif track.find("drag1000") >= 0 or track.find("drag400") >= 0:
            self.minLapCount = 0
        self.load_cfg()

    # PUBLIC METHODS
    def load_cfg(self):
        cfg = Config("apps/python/prunn/", "config.ini")
        self.max_num_cars = cfg.get("SETTINGS", "num_cars_tower", "int")
        self.max_num_laps_stint = cfg.get("SETTINGS", "num_laps_stint", "int")
        self.race_mode.setValue(cfg.get("SETTINGS", "race_mode", "int"))
        self.qual_mode.setValue(cfg.get("SETTINGS", "qual_mode", "int"))
        self.ui_row_height.setValue(cfg.get("SETTINGS", "ui_row_height", "int"))
        if cfg.get("SETTINGS", "car_colors_by", "int") == 1:
            self.__class__.colorsByClass = True
        else:
            self.__class__.colorsByClass = False
        Colors.highlight(reload=True)
        if self.ui_row_height.hasChanged():
            self.redraw_size()
        else:
            for driver in self.drivers:
                driver.set_border()

    def redraw_size(self):
        self.rowHeight = self.ui_row_height.value
        height = self.rowHeight - 2
        font_size = getFontSize(height)
        font_size2 = getFontSize(height - 2)
        self.lbl_tire_stint.setSize(self.rowHeight * 6, height).setPos(0, self.rowHeight).setFontSize(font_size)
        self.lbl_title_stint.setSize(self.rowHeight * 6, height - 2)\
            .setPos(0, self.rowHeight * 4 - (height - 2))\
            .setFontSize(font_size2)
        self.lbl_title_mode.setBgColor(Colors.theme(bg=True))\
            .setSize(self.rowHeight * 6, height - 2)\
            .setPos(0, -(height - 2))\
            .setFontSize(font_size2)
        for driver in self.drivers:
            driver.redraw_size(self.rowHeight)
            driver.set_border()
        for lbl in self.stintLabels:
            lbl.redraw_size(self.rowHeight)

    def set_font(self, font_name):
        self.lbl_title_stint.setFont(font_name, 0, 0)
        self.lbl_tire_stint.setFont(font_name, 0, 0)
        self.lbl_title_mode.setFont(font_name, 0, 0)
        self.fontName = font_name

    def animate(self, session_time_left):
        self.lbl_title_stint.animate()
        self.lbl_tire_stint.animate()
        self.lbl_title_mode.animate()
        for driver in self.drivers:
            driver.animate(session_time_left)
        for lbl in self.stintLabels:
            lbl.animate(session_time_left)

    def format_tire(self, name):
        space = name.find("(")
        if space > 0:
            name = name[:space]
        name = name.strip()
        if len(name) > 16:
            return name[:17]
        return name

    def init_drivers(self):
        if self.numCars.value > self.numCars.old:
            # init difference
            for i in range(self.numCars.old, self.numCars.value):
                self.drivers.append(Driver(self.window.app, self.rowHeight, self.fontName, i, ac.getDriverName(i), i))
            self.drivers_inited = True

    def next_driver_is_shown(self, pos):
        if pos > 0:
            for d in self.drivers:
                if d.position.value == pos + 1 and d.isDisplayed:
                    return True
        return False

    def update_drivers(self, sim_info):
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
                self.lbl_title_mode.setText("Gaps")
            else:
                self.lbl_title_mode.setText("Times")
            self.title_mode_visible_end = self.sessionTimeLeft - 6000
        if self.title_mode_visible_end != 0 and self.title_mode_visible_end < self.sessionTimeLeft:
            self.lbl_title_mode.show()
        else:
            self.lbl_title_mode.hide()
        # self.minlap_stint = 2255 #disabled for now
        if self.pitBoxMode:
            if self.lbl_title_stint.isVisible.value:
                self.lbl_title_stint.hide()
                self.lbl_tire_stint.hide()
                for l in self.stintLabels:
                    l.hide()
            for driver in self.drivers:
                driver.isAlive.setValue(bool(ac.isConnected(driver.identifier)))
                if driver.isAlive.value:
                    driver.pitBoxMode = True
                    p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                    # check_pos = 0
                    if len(p) > 0:
                        check_pos = p[0] + 1
                    else:
                        check_pos = ac.getCarLeaderboardPosition(driver.identifier)
                    if check_pos <= self.max_num_cars:
                        driver.set_position(check_pos, 0, False, self.qual_mode.value)
                        driver.update_pit(self.sessionTimeLeft)
                    driver.show(False, race=False)

        elif (show_stint_always and len(self.curDriverLaps) >= self.minlap_stint) or (
                self.stint_visible_end != 0 and self.sessionTimeLeft >= self.stint_visible_end):
            # Lap stint mode
            for driver in self.drivers:
                driver.pitBoxMode = False
                if driver.identifier == 0:
                    p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                    if len(p) > 0:
                        driver.set_position(p[0] + 1, p[0], False, self.qual_mode.value)
                    driver.show(False, race=False)
                    self.lbl_title_stint.show()
                    self.lbl_tire_stint.setText(self.format_tire(sim_info.graphics.tyreCompound))
                    self.lbl_tire_stint.show()
                    # self.stintLabels
                    if len(self.curDriverLaps) > len(self.stintLabels):
                        for i in range(len(self.stintLabels), len(self.curDriverLaps)):
                            self.stintLabels.append(
                                Driver(self.window.app, self.rowHeight, self.fontName, 0, "Lap " + str(i + 1), i + 2,
                                       True))
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
                            self.stintLabels[j].set_position(i + 5, 0, True, self.qual_mode.value)
                            self.stintLabels[j].show(False)
                            # i+5,
                            i += 1
                        j += 1

                else:
                    driver.hide()
        else:
            if self.lbl_title_stint.isVisible.value:
                self.lbl_title_stint.hide()
                self.lbl_tire_stint.hide()
                for l in self.stintLabels:
                    l.hide()
            for driver in self.drivers:
                driver.pitBoxMode = False
                c = driver.get_best_lap()
                driver.isAlive.setValue(bool(ac.isConnected(driver.identifier)))
                if not driver.isAlive.value:
                    driver.bestLapServer = 0
                p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                check_pos = 0
                if len(p) > 0:
                    check_pos = p[0] + 1
                if c > 0 and (driver.lapCount > self.minLapCount or self.next_driver_is_shown(check_pos)) and driver.isAlive.value and check_pos <= self.max_num_cars:
                    if len(p) > 0 and len(self.standings) > 0 and len(self.standings[0]) > 1:
                        driver.set_position(p[0] + 1, 0, False, self.qual_mode.value)
                        driver.show(race=False)
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
        if self.race_mode.value == 1:
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

    def get_max_sector(self, driver):
        if driver.race_gaps:
            return driver.race_gaps[-1].sector
        return 0

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

    def update_drivers_race(self, sim_info):
        if self.lbl_title_stint.isVisible.value:
            self.lbl_title_stint.hide()
            self.lbl_tire_stint.hide()
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
        if self.race_mode.hasChanged():
            if self.race_mode.value == 0:
                self.lbl_title_mode.setText("Auto")
            elif self.race_mode.value == 1:
                self.lbl_title_mode.setText("Full-Gaps")
            else:
                self.lbl_title_mode.setText("Full")
            self.title_mode_visible_end = self.sessionTimeLeft - 6000
        if self.title_mode_visible_end != 0 and self.title_mode_visible_end < self.sessionTimeLeft:
            self.lbl_title_mode.show()
        else:
            self.lbl_title_mode.hide()
        for driver in self.drivers:
            driver.isAlive.setValue(bool(ac.isConnected(driver.identifier)))
            if driver.isAlive.value:
                nb_drivers_alive += 1
            p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
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
            if sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0:
                # driver.finished=False
                self.numCarsToFinish = 0
                driver.race_standings_sector.setValue(0)
                driver.race_current_sector.setValue(0)
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
        # if self.lapsCompleted.value >= self.numberOfLaps:
        #    needs_tlc=False
        # memsize=0
        # if mode == 0?
        if self.race_mode.value == 0:
            for driver in self.drivers:
                # memsize += sys.getsizeof(driver.race_gaps)
                gap = self.gap_to_driver(driver, cur_driver, cur_sector)
                if driver.identifier == 0 or (gap < 2500 and cur_sector - self.get_max_sector(driver) < 15):
                    driver_shown += 1
                if driver.identifier == 0 or (gap < 5000 and cur_sector - self.get_max_sector(driver) < 15):
                    driver_shown_max_gap += 1
                driver.optimise()
                # ac.console("Mem size:" + str(memsize/1024) + " ko")
        if not driver_shown > 1:
            driver_shown = driver_shown_max_gap
            max_gap = 5000
        if not driver_shown > 1:
            if self.lapsCompleted.hasChanged():
                self.leader_time = self.sessionTimeLeft
                if self.numCarsToFinish > 0:  # self.lapsCompleted.value >= self.numberOfLaps:
                    self.race_show_end = self.sessionTimeLeft - 720000
                else:
                    self.race_show_end = self.sessionTimeLeft - 12000
        display_offset = 0
        if cur_driver_pos >= self.max_num_cars:
            display_offset = cur_driver_pos - self.max_num_cars
            if nb_drivers_alive > cur_driver_pos:  # showing next driver to user
                display_offset += 1
        if (self.race_mode.value == 1 or self.race_mode.value == 2) and not self.force_hidden:
            # Full tower with gaps(1) or without(2)
            tick_limit = 20
            if self.race_mode.value == 1:
                tick_limit = 40
            if not math.isinf(self.sessionTimeLeft) and int(
                            self.sessionTimeLeft / 100) % 18 == 0 and self.tick_race_mode > tick_limit:
                self.tick_race_mode = 0
                for driver in self.drivers:
                    if self.race_mode.value == 1:
                        gap = self.gap_to_driver(driver, first_driver, first_driver_sector)
                    p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                    if driver.completedLapsChanged and driver.completedLaps.value > 1:
                        driver.last_lap_visible_end = self.sessionTimeLeft - 5000
                    driver_max_sector = self.get_max_sector(driver)
                    if len(p) > 0 and p[
                        0] < self.max_num_cars + display_offset and driver.race_current_sector.value > 5 and (
                            p[0] < 3 or p[0] - 2 > display_offset):
                        if p[0] < 3:
                            driver.set_position(p[0] + 1, best_pos - 1, True, self.qual_mode.value)
                        else:
                            driver.set_position(p[0] + 1, best_pos - 1 + display_offset, True, self.qual_mode.value)
                        if driver.position_highlight_end == True:
                            driver.position_highlight_end = self.sessionTimeLeft - 5000
                        if self.race_mode.value == 1:
                            lapGap = self.get_max_sector(first_driver) - driver_max_sector
                            if driver.finished.value:
                                driver.show(False)
                            elif not driver.isAlive.value:
                                driver.set_time_race_battle("DNF", first_driver.identifier)
                                driver.show()
                            elif bool(ac.isCarInPitline(driver.identifier)) or bool(ac.isCarInPit(driver.identifier)):
                                driver.set_time_race_battle("PIT", first_driver.identifier)
                                driver.show()
                            elif driver.last_lap_visible_end != 0 and driver.last_lap_visible_end < self.sessionTimeLeft:
                                lastlap = ac.getCarState(driver.identifier, acsys.CS.LastLap)
                                driver.set_time_race_battle(lastlap, -1)
                            elif driver.position_highlight_end != 0 and driver.position_highlight_end < self.sessionTimeLeft:
                                if driver.movingUp:
                                    driver.set_time_race_battle("UP", first_driver.identifier)
                                else:
                                    driver.set_time_race_battle("DOWN", first_driver.identifier)
                                driver.show()
                            elif lapGap > 100:
                                driver.set_time_race_battle(lapGap / 100, first_driver.identifier, True)
                                driver.show()
                            else:
                                driver.set_time_race_battle(gap, first_driver.identifier)
                                driver.show()
                        else:
                            driver.show(False)
                    else:
                        driver.hide()
                    driver.optimise()
            elif self.race_mode.value == 1:
                for driver in self.drivers:
                    p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                    if len(p) > 0 and p[0] < self.max_num_cars and driver.isDisplayed:
                        if driver.completedLapsChanged and driver.completedLaps.value > 1:
                            driver.last_lap_visible_end = self.sessionTimeLeft - 5000
                        if driver.finished.value:
                            driver.show(False)
                        elif driver.last_lap_visible_end != 0 and driver.last_lap_visible_end < self.sessionTimeLeft and driver.isAlive.value and not driver.isInPit.value:
                            lastlap = ac.getCarState(driver.identifier, acsys.CS.LastLap)
                            driver.set_time_race_battle(lastlap, -1)
                            # else:
                            #    driver.hide()
            self.tick_race_mode += 1

        elif not self.force_hidden and driver_shown > 1 and (
                self.race_show_end > self.sessionTimeLeft or self.race_show_end == 0):
            # Battles
            self.lapsCompleted.hasChanged()
            if not math.isinf(self.sessionTimeLeft) and int(self.sessionTimeLeft / 100) % 18 == 0 and self.tick > 20:
                self.tick = 0
                for driver in self.drivers:
                    gap = self.gap_to_driver(driver, cur_driver, cur_sector)
                    if len(cur_driver.race_gaps) > 15 and (driver.identifier == cur_driver.identifier or (gap < max_gap and cur_sector - self.get_max_sector(driver) < 12)):
                        p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                        if len(p) > 0:
                            driver.set_position(p[0] + 1, best_pos - 1, True, self.qual_mode.value)
                            if driver.position_highlight_end == True:
                                driver.position_highlight_end = self.sessionTimeLeft - 5000
                            if driver.position_highlight_end != 0 and driver.position_highlight_end < self.sessionTimeLeft:
                                if driver.movingUp:
                                    driver.set_time_race_battle("UP", cur_driver.identifier)
                                else:
                                    driver.set_time_race_battle("DOWN", cur_driver.identifier)
                            else:
                                driver.set_time_race_battle(gap, cur_driver.identifier)
                            driver.show()
                    else:
                        p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
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
                    p = [i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                    if len(p) > 0 and driver.completedLapsChanged:
                        driver.set_position(p[0] + 1, 0, False, self.qual_mode.value)
                        driver.set_time_race(driver.completedLaps.value, self.leader_time, self.sessionTimeLeft)
                        needs_tlc = True
                        if self.numCarsToFinish > 0:  # self.lapsCompleted.value >= self.numberOfLaps:
                            needs_tlc = False
                        driver.show(needs_tlc)
        else:
            for driver in self.drivers:
                driver.hide()

    def get_standings_from_server(self):
        self.imported = True
        try:
            server_ip = ac.getServerIP()
            port = ac.getServerHttpPort()
            if server_ip != '' and port > 0:
                conn = http.client.HTTPConnection(ac.getServerIP(), port=port)
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
            self.raceStarted = False
            self.curDriverLaps = []
            self.stint_visible_end = 0
            self.title_mode_visible_end = 0
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

    def on_update(self, sim_info):
        t_info = time.time()
        t_update_drivers = 0
        t_update_drivers_end = 0
        self.session.setValue(sim_info.graphics.session)
        sim_info_status = sim_info.graphics.status
        if (sim_info_status != 3 and self.sessionTimeLeft != 0 and self.sessionTimeLeft != -1 and self.sessionTimeLeft + 100 < sim_info.graphics.sessionTimeLeft) or sim_info_status == 0:
            self.session.setValue(-1)
            self.session.setValue(sim_info.graphics.session)
        self.manage_window()
        self.numCars.setValue(ac.getCarsCount())
        if self.numCars.hasChanged():
            self.init_drivers()
        self.sessionTimeLeft = sim_info.graphics.sessionTimeLeft
        if sim_info_status != 3:
            self.animate(self.sessionTimeLeft)
        self.currentVehicule.setValue(ac.getFocusedCar())
        if sim_info_status == 2 or (sim_info_status == 1 and self.session.value < 2):
            # LIVE
            if self.session.value < 2:
                # self.pitBoxMode = bool(ac.isCarInPit(self.currentVehicule.value))
                # Qualify - Practise
                if not math.isinf(self.sessionTimeLeft):
                    if not self.imported and self.drivers_inited:
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
                        self.fastestLap = 0
                        for i in range(self.numCars.value):
                            self.drivers[i].bestLap = ac.getCarState(i, acsys.CS.BestLap)
                            bl = self.drivers[i].get_best_lap()
                            self.drivers[i].lapCount = ac.getCarState(i, acsys.CS.LapCount)
                            if bl > 0 and self.drivers[i].lapCount > self.minLapCount and self.drivers[i].isAlive.value:
                                standings.append((i, bl))
                            # fastestLap for info widget
                            if self.fastestLap == 0 or (bl > 0 and bl < self.fastestLap):
                                self.fastestLap = bl
                                # self.fastestLapSectors = ac.getLastSplits(x)

                        self.standings = sorted(standings, key=lambda student: student[1])
                        t_update_drivers = time.time()
                        self.update_drivers(sim_info)
                        t_update_drivers_end = time.time()

            elif self.session.value == 2:
                # RACE
                self.pitBoxMode = False
                if self.numberOfLaps < 0:
                    self.numberOfLaps = sim_info.graphics.numberOfLaps
                completed = 0
                standings = []
                # new standings
                # iTime < 10 lap=0 dont loop direct to backup standings
                if not self.raceStarted and not (
                        sim_info.graphics.iCurrentTime <= 12000 and sim_info.graphics.completedLaps == 0):
                    self.raceStarted = True
                if self.raceStarted:  #
                    for driver in self.drivers:
                        c = ac.getCarState(driver.identifier, acsys.CS.LapCount)
                        driver.completedLaps.setValue(c)
                        driver.completedLapsChanged = driver.completedLaps.hasChanged()
                        driver.finished.setValue(ac.getCarState(driver.identifier, acsys.CS.RaceFinished) == 1)
                        if c > completed:
                            completed = c
                        driver.raceProgress = c + ac.getCarState(driver.identifier, acsys.CS.NormalizedSplinePosition)
                        if self.sector_is_valid(driver.raceProgress, driver):
                            # or lapcount changed and leader finished
                            if driver.finished.hasChanged() and driver.finished.value:
                                # and (driver.race_standings_sector.value >= self.numberOfLaps
                                # or (self.numCarsToFinish > 0 and driver.completedLapsChanged)):
                                driver.race_standings_sector.setValue(
                                    driver.completedLaps.value + (self.numCars.value - self.numCarsToFinish) / 1000)
                                self.numCarsToFinish += 1
                                # driver.finished=True
                            elif not driver.finished.value:
                                driver.race_standings_sector.setValue(driver.raceProgress)
                        if not driver.hasStartedRace and (len(driver.race_gaps) > 2 or driver.race_standings_sector.value > 1):
                            driver.hasStartedRace = True
                        if driver.race_standings_sector.value > 0 and driver.hasStartedRace:
                            standings.append((driver.identifier, driver.race_standings_sector.value))

                self.lapsCompleted.setValue(completed)
                if len(standings) > 0:
                    self.standings = sorted(standings, key=lambda student: student[1], reverse=True)
                    self.force_hidden = False
                else:
                    # backup standings
                    completed = 0
                    standings2 = []
                    for i in range(self.numCars.value):
                        c = ac.getCarState(i, acsys.CS.LapCount)
                        # driver[i].completedLaps.setValue(c)
                        # driver[i].completedLapsChanged=driver[i].completedLaps.hasChanged()
                        if c > completed:
                            completed = c
                        bl = c + ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
                        if bl > 0:
                            standings2.append((i, bl))
                    self.standings = sorted(standings2, key=lambda student: student[1], reverse=True)
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
                '''
                t_update_drivers = time.time()
                self.update_drivers_race(sim_info)
                t_update_drivers_end = time.time()
            elif self.session.value > 2:  # other session                 
                self.pitBoxMode = False
                for driver in self.drivers:
                    driver.hide()
                self.lbl_title_stint.hide()
                self.lbl_tire_stint.hide()
                for l in self.stintLabels:
                    l.hide()
        elif sim_info_status == 1:  # Replay
            self.pitBoxMode = False
            for driver in self.drivers:
                driver.hide()
            self.lbl_title_stint.hide()
            self.lbl_tire_stint.hide()
            for l in self.stintLabels:
                l.hide()

        t_tower = time.time()
        if t_tower - t_info > 0.006:
            t_total = t_tower - t_info
            t_total_d = t_update_drivers_end - t_update_drivers
            # ac.console(str(t_total) + " u_diver:" + str(t_total_d))
            # ac.log(str(t_total) + " u_diver:" + str(t_total_d))
