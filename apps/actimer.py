import ac
import acsys
import os.path
import json
import ctypes
from .util.func import rgb
from .util.classes import Window, Label, Value, Colors, Font
from .configuration import Configuration


class ACTimer:
    # INITIALIZATION

    def __init__(self):
        self.finish_labels = []
        self.finish_initialised = False
        self.replay_initialised = False
        self.replay_asc = False
        self.replay_rgb = 255
        self.session = Value(-1)
        self.theme = Value(-1)
        self.cursor = Value(False)
        self.row_height = Value(-1)
        self.font = Value(0)
        self.numberOfLaps = -1
        self.hasExtraLap = -1
        self.numberOfLapsTimedRace = -1
        self.sessionMaxTime = -1
        self.pitWindowVisibleEnd = 0
        self.pitWindowStart = -1
        self.pitWindowEnd = -1
        self.pitWindowActive = False
        self.numberOfLapsCompleted = Value(0)
        self.trackName = ""
        self.window = Window(name="ACTV Timer", width=228, height=42)
        self.lbl_session_info = Label(self.window.app, "Loading")\
            .set(w=154, h=36,
                 x=self.row_height.value, y=0,
                 font_size=26,
                 align="center")
        self.lbl_session_title = Label(self.window.app, "P")\
            .set(w=36, h=36,
                 x=0, y=0,
                 font_size=26,
                 align="center")
        self.lbl_session_single = Label(self.window.app, "Loading")\
            .set(w=190, h=36,
                 x=0, y=0,
                 font_size=26,
                 align="center")
        self.lbl_session_border = Label(self.window.app, "")\
            .set(w=154 + 36, h=2,
                 x=0, y=36 + 1)
        self.lbl_pit_window = Label(self.window.app, "")\
            .set(w=160, h=36,
                 x=0, y=-36,
                 align="center",
                 font_size=26)

        track_file_path = "content/tracks/" + ac.getTrackName(0) + "/ui/"
        if ac.getTrackConfiguration(0) != "":
            track_file_path += ac.getTrackConfiguration(0) + "/ui_track.json"
        else:
            track_file_path += "ui_track.json"
        if os.path.exists(track_file_path):
            with open(track_file_path) as data_file:
                data = json.load(data_file)
                self.trackName = data["name"]
                if len(self.trackName) > 12:
                    if self.trackName[12] == " " or self.trackName[12] == "-":
                        self.trackName = self.trackName[:12]
                    else:
                        self.trackName = self.trackName[:12]
                        # cut multi-word
                        space = self.trackName.rfind(" ")
                        dash = self.trackName.rfind("-")
                        if space > 0:
                            self.trackName = self.trackName[:space]
                        elif dash > 0:
                            self.trackName = self.trackName[:dash]

        else:
            self.trackName = ac.getTrackName(0)
        if len(self.trackName) > 12:
            self.trackName = self.trackName[:12]

        self.load_cfg()

    # PUBLIC METHODS
    # ---------------------------------------------------------------------------------------------------------------------------------------------
    def load_cfg(self):
        self.row_height.setValue(Configuration.ui_row_height)
        Colors.theme(reload=True)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.font.setValue(Font.current)
        self.redraw_size()

    def redraw_size(self):
        # Colors
        if self.theme.hasChanged():
            self.lbl_session_border.set(background=Colors.timer_border_bg(),
                                        animated=True, init=True)
            self.lbl_session_single.set(background=Colors.timer_time_bg(),
                                        color=Colors.timer_time_txt(),
                                        animated=True, init=True)
            self.lbl_session_info.set(background=Colors.timer_time_bg(),
                                      color=Colors.timer_time_txt(),
                                      animated=True, init=True)
            self.lbl_session_title.set(background=Colors.timer_title_bg(),
                                       color=Colors.timer_title_txt(),
                                       animated=True, init=True)
            self.lbl_pit_window.set(background=Colors.timer_pit_window_bg(),
                                    color=Colors.timer_pit_window_txt(),
                                    animated=True, init=True)
        if self.row_height.hasChanged() or self.font.hasChanged():
            # Fonts
            self.lbl_session_info.update_font()
            self.lbl_session_title.update_font()
            self.lbl_session_single.update_font()
            self.lbl_pit_window.update_font()
            # Size
            font_size = Font.get_font_size(self.row_height.value+Font.get_font_offset())
            font_size2 = Font.get_font_size(self.row_height.value-7+Font.get_font_offset())
            width = self.row_height.value * 5
            self.lbl_session_info.set(w=self.row_height.value * 4, h=self.row_height.value, x=self.row_height.value,
                                      font_size=font_size)
            self.lbl_session_title.set(w=self.row_height.value, h=self.row_height.value, font_size=font_size)
            self.lbl_session_single.set(w=width, h=self.row_height.value, font_size=font_size)
            self.lbl_session_border.set(w=width, y=self.row_height.value + 1)
            self.lbl_pit_window.set(x=0, y=-self.row_height.value + 3,
                                    w=width, h=self.row_height.value-5,
                                    font_size=font_size2)
            if len(self.finish_labels) > 0:
                i = 0
                j = 0
                height = self.row_height.value / 3
                for label in self.finish_labels:
                    label.setSize(height, height)
                    if i % 2 == 1 and j < 7:
                        label.setPos(height + j * height * 2, i * height)
                    elif i % 2 == 0:
                        label.setPos(j * height * 2, i * height)
                    j += 1
                    if (i % 2 == 0 and j >= 8) or (i % 2 == 1 and j >= 7):
                        i += 1
                        j = 0

    def time_splitting(self, ms):
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        # d,h=divmod(h,24)
        if h > 0:
            return "{0}:{1}:{2}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2))
        else:
            return "{0}:{1}".format(int(m), str(int(s)).zfill(2))

    def init_finish(self):
        self.lbl_session_info.hide()
        self.lbl_session_title.hide()
        self.lbl_session_border.hide()
        self.lbl_session_single.setText("").setBgColor(rgb([255, 255, 255], bg=True)).setBgOpacity(0.76).show()
        if len(self.finish_labels) > 0:
            for label in self.finish_labels:
                label.show()
        else:
            height = self.row_height.value / 3
            for i in range(0, 3):
                for j in range(0, 8):
                    if i % 2 == 1 and j < 7:
                        self.finish_labels.append(Label(self.window.app)
                                                  .setSize(height, height)
                                                  .setPos(height + j * height * 2, i * height)
                                                  .setBgColor(rgb([0, 0, 0], bg=True), init=True)
                                                  .setBgOpacity(0.8, init=True).show())
                    elif i % 2 == 0:
                        self.finish_labels.append(Label(self.window.app)
                                                  .setSize(height, height)
                                                  .setPos(j * height * 2, i * height)
                                                  .setBgColor(rgb([0, 0, 0], bg=True), init=True)
                                                  .setBgOpacity(0.8, init=True).show())

        self.finish_initialised = True

    def destroy_finish(self):
        # Destroy
        self.lbl_session_single.setBgColor(Colors.timer_time_bg()).hide()
        for label in self.finish_labels:
            label.hide()
        self.finish_initialised = False

    def animate(self):
        self.lbl_session_info.animate()
        self.lbl_session_title.animate()
        self.lbl_session_border.animate()
        self.lbl_session_single.animate()
        self.lbl_pit_window.animate()
        if len(self.finish_labels) > 0:
            for label in self.finish_labels:
                label.animate()

    def manage_window(self):
        if self.session.hasChanged():
            self.numberOfLapsTimedRace = -1
            self.hasExtraLap = -1
            self.numberOfLaps = -1
            self.pitWindowStart = -1
            self.pitWindowEnd = -1
            self.sessionMaxTime = -1
            self.pitWindowVisibleEnd = 0
            self.pitWindowActive = False
            if self.session.value == 1:
                self.lbl_session_title.setText("Q")
            else:
                self.lbl_session_title.setText("P")
            self.window.setBgOpacity(0).border(0)

    def on_update(self, sim_info):
        self.session.setValue(sim_info.graphics.session)
        self.manage_window()
        sim_info_status = sim_info.graphics.status
        self.animate()
        if sim_info_status == 2:  # LIVE
            if self.replay_initialised:
                self.lbl_session_single.setColor(Colors.timer_time_txt())
            session_time_left = sim_info.graphics.sessionTimeLeft
            if self.session.value < 2:
                self.lbl_pit_window.hide()
                # 0 to -5000 show finish
                if 0 > session_time_left > -5000:
                    if not self.finish_initialised:
                        self.init_finish()
                else:
                    if session_time_left < 0:
                        session_time_left = 0
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_title.show()
                    self.lbl_session_single.hide()
                    self.lbl_session_border.show()
                    self.lbl_session_info.setText(self.time_splitting(session_time_left)).show()
                    if not self.finish_initialised:
                        if sim_info.graphics.flag == 2:
                            # Yellow Flag
                            self.lbl_session_info.set(background=Colors.timer_time_yellow_flag_bg(),
                                                      color=Colors.timer_time_yellow_flag_txt(),
                                                      animated=True)
                            self.lbl_session_title.set(background=Colors.timer_title_yellow_flag_bg(),
                                                       color=Colors.timer_title_yellow_flag_txt(),
                                                       animated=True)
                            self.lbl_session_border.set(background=Colors.timer_border_yellow_flag_bg(),
                                                        animated=True)
                        else:
                            self.lbl_session_info.set(background=Colors.timer_time_bg(),
                                                      color=Colors.timer_time_txt(),
                                                      animated=True)
                            self.lbl_session_title.set(background=Colors.timer_title_bg(),
                                                       color=Colors.timer_title_txt(),
                                                       animated=True)
                            self.lbl_session_border.set(background=Colors.timer_border_bg(),
                                                        animated=True)
            elif self.session.value == 2:
                # Race
                completed = 0
                race_finished = 0
                for x in range(ac.getCarsCount()):
                    c = ac.getCarState(x, acsys.CS.LapCount)
                    if c > completed:
                        completed = c
                    if ac.getCarState(x, acsys.CS.RaceFinished):
                        race_finished = 1
                completed += 1
                if self.numberOfLaps < 0:
                    self.numberOfLaps = sim_info.graphics.numberOfLaps
                if self.hasExtraLap < 0:
                    self.hasExtraLap = sim_info.static.hasExtraLap
                if self.hasExtraLap == 1 and session_time_left < 0 and self.numberOfLapsTimedRace < 0:
                    self.numberOfLapsTimedRace = completed + 1

                # PitWindow
                pit_window_remain = ""
                if self.pitWindowStart < 0:
                    self.pitWindowStart = sim_info.static.PitWindowStart
                    self.pitWindowEnd = sim_info.static.PitWindowEnd
                if self.numberOfLaps > 0:
                    self.numberOfLapsCompleted.setValue(completed)
                    if self.numberOfLapsCompleted.hasChanged():
                        if self.numberOfLapsCompleted.value == self.pitWindowStart:
                            self.pitWindowVisibleEnd = session_time_left - 8000
                            self.pitWindowActive = True
                        elif self.numberOfLapsCompleted.value == self.pitWindowEnd:
                            self.pitWindowVisibleEnd = session_time_left - 8000
                            self.pitWindowActive = False
                    if self.pitWindowActive:
                        if self.pitWindowEnd - completed > 1:
                            pit_window_remain = " {0} Laps".format(self.pitWindowEnd - completed)
                        else:
                            pit_window_remain = " {0} Lap".format(self.pitWindowEnd - completed)
                else:
                    if self.sessionMaxTime < 0:
                        self.sessionMaxTime = round(session_time_left, -3)
                    if not self.pitWindowActive and session_time_left <= self.sessionMaxTime - self.pitWindowStart * 60 * 1000 and session_time_left >= self.sessionMaxTime - self.pitWindowEnd * 60 * 1000:
                        self.pitWindowVisibleEnd = session_time_left - 8000
                        self.pitWindowActive = True
                    elif self.pitWindowActive and session_time_left < self.sessionMaxTime - self.pitWindowEnd * 60 * 1000:
                        self.pitWindowVisibleEnd = session_time_left - 8000
                        self.pitWindowActive = False
                    if self.pitWindowActive:
                        pit_window_remain = " " + self.time_splitting(session_time_left - (self.sessionMaxTime - self.pitWindowEnd * 60 * 1000))
                if self.pitWindowActive:
                    self.lbl_pit_window.show()
                    if self.pitWindowVisibleEnd != 0 and self.pitWindowVisibleEnd < session_time_left:
                        self.lbl_pit_window.setColor(Colors.timer_pit_window_open_txt())
                    elif sim_info.graphics.MandatoryPitDone:
                        self.lbl_pit_window.setColor(Colors.timer_pit_window_done_txt(), True)
                    else:
                        self.lbl_pit_window.setColor(Colors.timer_pit_window_txt(), True)
                    self.lbl_pit_window.setText("Pits open" + pit_window_remain)
                elif self.pitWindowVisibleEnd != 0 and self.pitWindowVisibleEnd < session_time_left:
                    self.lbl_pit_window.show()
                    self.lbl_pit_window.setText("Pits closed").setColor(Colors.timer_pit_window_close_txt(), True)
                else:
                    self.lbl_pit_window.hide()

                if sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0:
                    self.pitWindowVisibleEnd = 0
                    self.pitWindowActive = False
                    self.sessionMaxTime = round(session_time_left, -3)
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_info.hide()
                    self.lbl_session_title.hide()
                    self.lbl_session_single.show()
                    self.lbl_session_border.show()
                    self.lbl_session_single.setText(self.trackName)
                elif race_finished > 0:
                    if not self.finish_initialised:
                        self.init_finish()
                elif completed == self.numberOfLaps or (self.numberOfLaps == 0 and self.hasExtraLap == 0 and session_time_left < 0) or (self.hasExtraLap == 1 and completed == self.numberOfLapsTimedRace):
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_info.hide()
                    self.lbl_session_title.hide()
                    self.lbl_session_single.show()
                    self.lbl_session_border.show()
                    self.lbl_session_single.setText("Final lap")
                else:
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_info.hide()
                    self.lbl_session_title.hide()
                    self.lbl_session_single.show()
                    self.lbl_session_border.show()
                    if self.hasExtraLap > 0:
                        txt_extra_lap = " +1 Lap"
                    else:
                        txt_extra_lap = ""
                    if self.numberOfLaps > 0:
                        self.lbl_session_single.setText("{0} / {1}".format(completed, self.numberOfLaps))
                    elif session_time_left > 0:
                        self.lbl_session_single.setText(self.time_splitting(session_time_left) + txt_extra_lap)
                    else:
                        self.lbl_session_single.setText("0:00" + txt_extra_lap)
                if not self.finish_initialised:
                    if sim_info.graphics.flag == 2:  # Yellow flag
                        self.lbl_session_single.set(background=Colors.timer_time_yellow_flag_bg(),
                                                    color=Colors.timer_time_yellow_flag_txt(),
                                                    animated=True)
                        self.lbl_session_border.set(background=Colors.timer_border_yellow_flag_bg(),
                                                    animated=True)
                    else:
                        self.lbl_session_single.set(background=Colors.timer_time_bg(),
                                                    color=Colors.timer_time_txt(),
                                                    animated=True)
                        self.lbl_session_border.set(background=Colors.timer_border_bg(),
                                                    animated=True)
            else:
                self.lbl_session_info.hide()
                self.lbl_session_title.hide()
                self.lbl_session_single.hide()
                self.lbl_session_border.hide()
                self.lbl_pit_window.hide()

        elif sim_info_status == 1:
            replay_time_multiplier = sim_info.graphics.replayTimeMultiplier
            if self.finish_initialised:
                self.destroy_finish()
            self.lbl_session_info.hide()
            self.lbl_session_title.hide()
            self.lbl_session_border.show()
            self.lbl_session_single.show()
            self.lbl_pit_window.hide()
            self.replay_initialised = True
            self.lbl_session_single.setColor(rgb([self.replay_rgb, self.replay_rgb, self.replay_rgb]))
            if self.replay_asc and replay_time_multiplier > 0:
                self.replay_rgb += 2
            elif replay_time_multiplier > 0:
                self.replay_rgb -= 2
            if Colors.general_theme == 1:
                if self.replay_rgb <= 2:
                    self.replay_asc = True
                elif self.replay_rgb > 168:
                    self.replay_rgb = 168
                    self.replay_asc = False
            else:
                if self.replay_rgb < 100:
                    self.replay_asc = True
                elif self.replay_rgb >= 246:
                    self.replay_rgb = 246
                    self.replay_asc = False
            self.lbl_session_single.setText("REPLAY")
