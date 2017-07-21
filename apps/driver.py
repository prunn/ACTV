import ac
import acsys
import math
import functools
from .util.classes import Label, Value, Colors, Font
from .configuration import Configuration


class Driver:
    def __init__(self, app, row_height, identifier, name, pos, is_lap_label=False, is_results=False):
        self.identifier = identifier
        self.rowHeight = row_height
        self.font_offset = 0
        self.race = False
        self.hasStartedRace = False
        self.inPitFromPitLane = False
        self.isInPitLane = Value(False)
        self.isInPitLaneOld = False
        self.isInPitBox = Value(False)
        self.fontSize = Font.get_font_size(self.rowHeight + self.font_offset)
        str_offset = " "
        self.final_y = 0
        self.isDisplayed = False
        self.firstDraw = False
        self.isAlive = Value(False)
        self.is_results = is_results
        self.movingUp = False
        self.isCurrentVehicule = Value(False)
        self.isLapLabel = is_lap_label
        self.qual_mode = Value(0)
        self.race_gaps = []
        self.finished = Value(False)
        self.bestLap = 0
        self.compact_mode_race = False
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
            self.lbl_name = Label(app, str_offset + name) \
                .set(w=self.rowHeight * 6, h=self.rowHeight,
                     x=0, y=0,
                     font_size=self.fontSize,
                     align="left",
                     background=Colors.background_tower(),
                     opacity=0.6,
                     visible=0)
        elif self.is_results:
            self.lbl_name = Label(app, str_offset + self.format_name_tlc(name)) \
                .set(w=self.rowHeight * 5, h=self.rowHeight,
                     x=self.rowHeight, y=0,
                     font_size=self.fontSize,
                     align="left",
                     opacity=0,
                     visible=0)
            self.lbl_position = Label(app, str(pos + 1)) \
                .set(w=self.rowHeight, h=self.rowHeight,
                     x=0, y=0,
                     font_size=self.fontSize,
                     align="center",
                     background=Colors.background_tower_position_odd(),
                     color=Colors.white(),
                     opacity=1,
                     visible=0)
            self.lbl_pit = Label(app, "P") \
                .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                     x=self.rowHeight * 6, y=self.final_y + 2,
                     font_size=self.fontSize - 3,
                     align="center",
                     opacity=0,
                     visible=0)
            self.lbl_pit.setAnimationSpeed("rgb", 0.08)
            self.lbl_position.setAnimationMode("y", "spring")
            self.lbl_pit.setAnimationMode("y", "spring")
        else:
            self.lbl_name = Label(app, str_offset + self.format_name_tlc(name)) \
                .set(w=self.rowHeight * 5, h=self.rowHeight,
                     x=self.rowHeight, y=0,
                     font_size=self.fontSize,
                     align="left",
                     background=Colors.background_tower(),
                     opacity=0.6,
                     visible=0)
            self.lbl_position = Label(app, str(pos + 1)) \
                .set(w=self.rowHeight, h=self.rowHeight,
                     x=0, y=0,
                     font_size=self.fontSize,
                     align="center",
                     background=Colors.background_tower_position_odd(),
                     color=Colors.white(),
                     opacity=1,
                     visible=0)
            self.lbl_pit = Label(app, "P") \
                .set(w=self.rowHeight * 0.6, h=self.rowHeight - 2,
                     x=self.rowHeight * 6, y=self.final_y + 2,
                     font_size=self.fontSize - 3,
                     align="center",
                     opacity=0,
                     visible=0)
            self.lbl_pit.setAnimationSpeed("rgb", 0.08)
            self.lbl_position.setAnimationMode("y", "spring")
            self.lbl_pit.setAnimationMode("y", "spring")
        self.lbl_time = Label(app, "+0.000") \
            .set(w=self.rowHeight * 4.7, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 color=Colors.grey(),
                 font_size=self.fontSize,
                 align="right",
                 opacity=0,
                 visible=0)
        self.lbl_border = Label(app, "") \
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
        self.redraw_size(row_height)

        if not self.isLapLabel:
            self.partial_func = functools.partial(self.on_click_func, driver=self.identifier)
            ac.addOnClickedListener(self.lbl_position.label, self.partial_func)
            ac.addOnClickedListener(self.lbl_name.label, self.partial_func)

    @classmethod
    def on_click_func(*args, driver=0):
        ac.focusCar(driver)

    def redraw_size(self, height):
        # Fonts
        self.font_offset = Font.get_font_offset()
        self.lbl_name.update_font()
        self.lbl_time.update_font()
        if not self.isLapLabel:
            self.lbl_position.update_font()
            self.lbl_pit.update_font()
        # UI
        if self.isDisplayed:
            self.lbl_name.set(background=Colors.background_tower(), color=Colors.font_color())
            if not self.isLapLabel and not self.race:
                self.lbl_pit.setColor(Colors.pitColor())
            self.lbl_time.setColor(Colors.font_color())
        self.position.setValue(-1)
        self.rowHeight = height
        font_size = Font.get_font_size(self.rowHeight + self.font_offset)
        self.final_y = self.num_pos * self.rowHeight
        if self.isLapLabel:
            if Colors.border_direction == 1:
                self.lbl_name.setSize(self.rowHeight * 6 + 8, self.rowHeight).setPos(0, self.final_y).setFontSize(
                    font_size)
            else:
                self.lbl_name.setSize(self.rowHeight * 6 + 4, self.rowHeight).setPos(0, self.final_y).setFontSize(
                    font_size)
        else:
            if self.is_compact_mode():
                pit_x = 2.9
                name_width = 1.9
            else:
                pit_x = 6
                name_width = 5
            if self.isInPit.value and not self.race:
                if Colors.border_direction == 1:
                    self.lbl_name.setSize(self.rowHeight * (name_width + 0.6) + 8, self.rowHeight) \
                        .setPos(self.rowHeight + 8, self.final_y) \
                        .setFontSize(font_size)
                else:
                    self.lbl_name.setSize(self.rowHeight * (name_width + 0.6) + 4, self.rowHeight) \
                        .setPos(self.rowHeight + 4, self.final_y) \
                        .setFontSize(font_size)
            else:
                if Colors.border_direction == 1:
                    self.lbl_name.setSize(self.rowHeight * name_width, self.rowHeight) \
                        .setPos(self.rowHeight + 8, self.final_y) \
                        .setFontSize(font_size)
                else:
                    self.lbl_name.setSize(self.rowHeight * name_width, self.rowHeight) \
                        .setPos(self.rowHeight + 4, self.final_y) \
                        .setFontSize(font_size)
            self.lbl_position.setSize(self.rowHeight + 4, self.rowHeight) \
                .setPos(0, self.final_y).setFontSize(font_size)
            if Colors.border_direction == 1:
                self.lbl_pit.setSize(self.rowHeight * 0.6, self.rowHeight - 2) \
                    .setPos(self.rowHeight * pit_x + 7, self.final_y + 2).setFontSize(font_size - 3)
            else:
                self.lbl_pit.setSize(self.rowHeight * 0.6, self.rowHeight - 2) \
                    .setPos(self.rowHeight * pit_x + 4, self.final_y + 2).setFontSize(font_size - 3)
        if Colors.border_direction == 1:
            self.lbl_time.setSize(self.rowHeight * 4.7, self.rowHeight) \
                .setPos(self.rowHeight + 8, self.final_y).setFontSize(font_size)
            self.lbl_border.setSize(4, self.rowHeight) \
                .setPos(self.rowHeight + 4, self.final_y)
        else:
            self.lbl_time.setSize(self.rowHeight * 4.7, self.rowHeight) \
                .setPos(self.rowHeight + 4, self.final_y).setFontSize(font_size)
            self.lbl_border.setSize(self.rowHeight * 2.8, 2) \
                .setPos(0, self.final_y + self.rowHeight - 2)

    def show(self, needs_tlc=True, race=True, compact=False):
        self.race = race
        self.compact_mode_race = compact
        #compact = self.is_compact_mode()
        if self.showingFullNames and needs_tlc:
            self.set_name()
        elif not self.showingFullNames and not needs_tlc:
            self.show_full_name()
        if not self.isDisplayed:
            self.lbl_name.set(background=Colors.background_tower())
            if not compact:
                self.lbl_time.setColor(Colors.font_color())
            if not self.isLapLabel:
                #self.lbl_pit.setColor(Colors.pitColor()).setVisible(0)
                if self.isInPit.value and not race:
                    self.lbl_name.setSize(self.rowHeight * 5.6, self.rowHeight, False)
                else:
                    self.lbl_name.setSize(self.rowHeight * 5, self.rowHeight, False)
            self.isDisplayed = True
        self.lbl_name.show()

        if self.isLapLabel or needs_tlc:
            if not compact:
                self.lbl_time.showText()
            else:
                self.lbl_time.hideText()
        else:
            self.lbl_time.hideText()
        if (self.isLapLabel and Colors.border_direction == 0) or not self.isLapLabel:
            self.lbl_border.show()
        else:
            self.lbl_border.hide()
        if not self.isLapLabel:
            self.lbl_position.show()
            if not self.isAlive.value and not self.finished.value:
                self.lbl_name.setColor(Colors.grey(), True)
            elif self.isInPit.value or ac.getCarState(self.identifier, acsys.CS.SpeedKMH) > 30 or self.finished.value:
                self.lbl_name.setColor(Colors.font_color(), True)
            else:
                self.lbl_name.setColor(Colors.yellow_time(), True)

    def update_pit(self, session_time):
        if Colors.border_direction == 1:
            pit_offset = 7
        else:
            pit_offset = 4
        if self.is_compact_mode():
            pit_x = 2.9
            name_width = 1.9
        else:
            pit_x = 6
            name_width = 5
        if not self.isLapLabel and self.isInPit.hasChanged():
            if self.isInPit.value:
                self.pit_highlight_end = session_time - 5000
                self.lbl_pit.showText()
                self.lbl_name.setSize(self.rowHeight * (name_width + 0.6), self.rowHeight, True)
            else:
                self.lbl_pit.hideText()
                self.lbl_name.setSize(self.rowHeight * name_width, self.rowHeight, True)
                self.lbl_pit.setX(self.rowHeight * pit_x + pit_offset)
        if self.isInPit.value and (self.lbl_name.f_params["w"].value < self.rowHeight * 5.6 or self.lbl_pit.f_params["a"].value < 1):
            self.lbl_pit.showText()
            self.lbl_name.setSize(self.rowHeight * (name_width + 0.6), self.rowHeight, True)
            self.lbl_pit.setX(self.rowHeight * pit_x + pit_offset)
        elif not self.isInPit.value and (self.lbl_name.f_params["w"].value > self.rowHeight * 5 or self.lbl_pit.f_params["a"].value == 1):
            self.lbl_pit.hideText()
            self.lbl_name.setSize(self.rowHeight * name_width, self.rowHeight, True)
            self.lbl_pit.setX(self.rowHeight * pit_x + pit_offset)
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
        if Configuration.carColorsBy == 1:
            colors_by_class = True
        else:
            colors_by_class = False
        self.lbl_border.setBgColor(Colors.colorFromCar(self.carName, colors_by_class)).setBgOpacity(
            Colors.border_opacity())

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
                self.lbl_time.change_font_if_needed().setText(self.format_time(self.time.value))
            else:
                self.lbl_time.change_font_if_needed().setText("+" + self.format_time(self.gap.value))

    def set_time_stint(self, time, valid):
        self.time.setValue(time)
        self.gap.setValue(time)
        if self.time.hasChanged() or self.gap.hasChanged():
            self.lbl_time.change_font_if_needed().setText(self.format_time(self.time.value))  # .setVisible(1)
            self.lbl_time.setColor(Colors.grey())
            if valid:
                self.lbl_time.setColor(Colors.font_color())
            else:
                self.lbl_time.setColor(Colors.red())
                # self.lbl_time.showText()

    def set_time_race(self, time, leader, session_time):
        if self.position.value == 1:
            self.lbl_time.change_font_if_needed().setText("Lap " + str(time)).setColor(Colors.font_color())
        else:
            self.lbl_time.change_font_if_needed().setText("+" + self.format_time(leader - session_time)).setColor(
                Colors.font_color())

    def set_time_race_battle(self, time, identifier, lap=False, intervals=False):
        if time == "PIT":
            self.lbl_time.change_font_if_needed().setText("PIT").setColor(Colors.yellow_time(), True)
        elif time == "DNF":
            self.lbl_time.change_font_if_needed().setText("DNF").setColor(Colors.dnf(), True)
        elif time == "UP":
            self.lbl_time.change_font_if_needed(1).setText(u"\u25B2").setColor(Colors.green(), True)
        elif time == "DOWN":
            self.lbl_time.change_font_if_needed(1).setText(u"\u25BC").setColor(Colors.red(), True)
        elif self.identifier == identifier or time == 600000:
            self.lbl_time.change_font_if_needed().setText("").setColor(Colors.font_color(), True)
        elif lap:
            str_time = "+" + str(math.floor(abs(time)))
            if abs(time) >= 2:
                str_time += " Laps"
            else:
                str_time += " Lap"
            self.lbl_time.change_font_if_needed().setText(str_time).setColor(Colors.font_color(), True)
        elif identifier == -1:
            if time <= ac.getCarState(self.identifier, acsys.CS.BestLap):
                self.lbl_time.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.purple(), True)
            else:
                self.lbl_time.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.red(), True)
        else:
            if intervals:
                self.lbl_time.change_font_if_needed().setText("+" + self.format_time(time)).setColor(
                    Colors.font_color(), True)
            else:
                self.lbl_time.change_font_if_needed().setText(self.format_time(time)).setColor(Colors.font_color(),
                                                                                               True)

    def optimise(self):
        if len(self.race_gaps) > 132:
            del self.race_gaps[0:len(self.race_gaps) - 132]

    def set_position(self, position, offset, battles):
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
                if Colors.border_direction == 1:
                    self.lbl_border.setY(self.final_y)
                else:
                    self.lbl_border.setY(self.final_y + self.rowHeight - 2)
                self.firstDraw = True

            if self.isLapLabel:
                self.lbl_name.setPos(0, self.final_y, True)
            else:
                self.lbl_position.setText(str(self.position.value))
                self.lbl_name.setY(self.final_y, True)
                self.lbl_position.setY(self.final_y, True)
                self.lbl_pit.setY(self.final_y + 2, True)

            self.lbl_time.setY(self.final_y, True)
            if Colors.border_direction == 1:
                self.lbl_border.setY(self.final_y, True)
            else:
                self.lbl_border.setY(self.final_y + self.rowHeight - 1, True)
            if position % 2 == 1:
                if self.isAlive.value:
                    self.lbl_name.setBgOpacity(Colors.opacity_tower_odd())
                else:
                    self.lbl_name.setBgOpacity(0.52)
                if position == 1 and Colors.general_theme == 0:
                    if not self.isLapLabel:
                        self.lbl_position.setBgColor(Colors.background_first(), True) \
                            .setColor(Colors.white(), True) \
                            .setBgOpacity(0.72)
                elif battles and self.isCurrentVehicule.value:
                    if not self.isLapLabel:
                        self.lbl_position.setBgColor(Colors.background_tower_position_highlight(), True) \
                            .setColor(Colors.red(), True)  # .setBgOpacity(0.72)
                    if Colors.general_theme == 2:
                        self.lbl_position.setBgOpacity(1)
                    else:
                        self.lbl_position.setBgOpacity(0.72)
                else:
                    if not self.isLapLabel:
                        if self.isAlive.value:
                            self.lbl_position.setBgColor(Colors.background_tower_position_odd(), True) \
                                .setColor(Colors.white(), True)  # .setBgOpacity(0.72)
                            if Colors.general_theme == 2:
                                self.lbl_position.setBgOpacity(1)
                            else:
                                self.lbl_position.setBgOpacity(0.72)
                        else:
                            self.lbl_position.setBgColor(Colors.background_tower_position_odd(), True) \
                                .setColor(Colors.grey(), True) \
                                .setBgOpacity(0.62)
            else:
                if self.isAlive.value:
                    self.lbl_name.setBgOpacity(Colors.opacity_tower_even())
                else:
                    self.lbl_name.setBgOpacity(0.44)
                if battles and self.isCurrentVehicule.value:  # (self.identifier == 0 or)
                    if not self.isLapLabel:
                        self.lbl_position.setBgColor(Colors.background_tower_position_highlight(), True) \
                            .setColor(Colors.red(), True)  # .setBgOpacity(0.68)
                        if Colors.general_theme == 2:
                            self.lbl_position.setBgOpacity(0.96)
                        else:
                            self.lbl_position.setBgOpacity(0.68)
                else:
                    if not self.isLapLabel:
                        if self.isAlive.value:
                            self.lbl_position.setBgColor(Colors.background_tower_position_even(), True) \
                                .setColor(Colors.white(), True)  # .setBgOpacity(0.58)
                            if Colors.general_theme == 2:
                                self.lbl_position.setBgOpacity(0.96)
                            else:
                                self.lbl_position.setBgOpacity(0.58)
                        else:
                            self.lbl_position.setBgColor(Colors.background_tower_position_even(), True) \
                                .setColor(Colors.grey(), True) \
                                .setBgOpacity(0.52)
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

    def is_compact_mode(self):
        if self.isLapLabel:
            return False
        if not self.race and Configuration.qual_mode == 2 and not self.highlight.value:
            return True
        if self.race and self.compact_mode_race:# Configuration.race_mode == 3 and not self.finished.value and not self.isCurrentVehicule.value:
            return True
        return False

    def animate(self, session_time_left):
        if session_time_left == -1:
            self.time_highlight_end = 0
        if not self.isLapLabel:
            # color
            self.highlight.setValue(self.time_highlight_end != 0 and self.time_highlight_end < session_time_left)
            if self.highlight.hasChanged() and not self.race:
                if self.is_compact_mode():
                    name_width = 1.9
                else:
                    name_width = 5
                if self.isInPit.value:
                    name_width += 0.6
                if self.highlight.value:
                    self.lbl_time.setColor(Colors.highlight(), True)
                    self.lbl_time.showText()
                    self.lbl_name.set(w=self.rowHeight * name_width, animated=True)
                else:
                    self.lbl_time.setColor(Colors.font_color(), True)
                    if self.is_compact_mode():
                        self.lbl_time.hideText()
                    else:
                        self.lbl_time.showText()
                    self.lbl_name.set(w=self.rowHeight * name_width, animated=True)
            elif self.race:
                if self.compact_mode_race:
                    name_width = 1.9
                    if self.isInPit.value and self.isDisplayed and self.isAlive.value:
                        if Colors.border_direction == 1:
                            pit_offset = 7
                        else:
                            pit_offset = 4
                        name_width += 0.6
                        pit_x = 2.9
                        self.lbl_pit.setX(self.rowHeight * pit_x + pit_offset)
                        self.lbl_pit.setColor(Colors.pitColor())
                        self.lbl_pit.showText()
                    else:
                        self.lbl_pit.hideText()
                else:
                    name_width = 5
                    self.lbl_pit.hideText()
                self.lbl_name.set(w=self.rowHeight * name_width, animated=True)
            # not isLapLabel
            self.lbl_position.animate()
            self.lbl_pit.animate()
        self.lbl_border.animate()
        self.lbl_time.animate()
        self.lbl_name.animate()
