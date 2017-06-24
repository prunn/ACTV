import ac
import acsys
import os.path
import json
import ctypes
from .util.func import rgb
from .util.classes import Window, Label, Value, POINT, Colors, Font
from .configuration import Configuration


class ACTimer:
    # INITIALIZATION

    def __init__(self):
        self.font_offset = 0
        self.finish_labels = []
        self.finish_initialised = False
        self.replay_initialised = False
        self.replay_asc = False
        self.replay_rgb = 255
        self.session = Value()
        self.cursor = Value(False)
        self.session_draw = Value(-1)
        self.ui_row_height = Value(-1)
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
        self.rowHeight = 36
        self.trackName = ""
        self.window = Window(name="ACTV Timer", icon=False, width=228, height=42, texture="")
        self.lbl_session_info = Label(self.window.app, "Loading")\
            .set(w=154, h=self.rowHeight,
                 x=self.rowHeight, y=0,
                 font_size=26,
                 align="center",
                 background=Colors.background(),
                 opacity=Colors.background_opacity())
        self.lbl_session_title = Label(self.window.app, "P")\
            .set(w=self.rowHeight, h=self.rowHeight,
                 x=0, y=0,
                 font_size=26,
                 align="center",
                 background=Colors.theme(bg=True),
                 opacity=Colors.background_opacity())
        self.lbl_session_single = Label(self.window.app, "Loading")\
            .set(w=190, h=self.rowHeight,
                 x=0, y=0,
                 font_size=26,
                 align="center",
                 background=Colors.background(),
                 opacity=Colors.background_opacity(),
                 color=Colors.font_color(),
                 visible=0)
        self.lbl_session_border = Label(self.window.app, "")\
            .set(w=154 + self.rowHeight, h=1,
                 x=0, y=self.rowHeight + 1,
                 background=Colors.theme(bg=True),
                 opacity=Colors.border_opacity(),
                 visible=1)
        self.lbl_pit_window_bg = Label(self.window.app, "")\
            .set(w=0, h=self.rowHeight,
                 x=0, y=-self.rowHeight,
                 font_size=26,
                 background=Colors.background(),
                 opacity=Colors.background_opacity(),
                 visible=0)
        self.lbl_pit_window_text = Label(self.window.app, "Loading")\
            .set(w=160,
                 h=self.rowHeight,
                 x=0,
                 y=-self.rowHeight,
                 font_size=26,
                 align="center",
                 opacity=0,
                 color=Colors.white(),
                 visible=0)

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
        # Load
        self.ui_row_height.setValue(Configuration.ui_row_height)
        # UI
        self.font.setValue(Font.current)
        #if self.ui_row_height.hasChanged() or self.font.hasChanged():
        self.redraw_size()
        self.lbl_session_border.setBgColor(Colors.theme(bg=True, reload=True))
        self.lbl_session_title.setBgColor(Colors.theme(bg=True, reload=True))

    def redraw_size(self):
        # Fonts
        self.font_offset = Font.get_font_offset()
        self.lbl_session_info.update_font()
        self.lbl_session_title.update_font()
        self.lbl_session_single.update_font()
        self.lbl_pit_window_text.update_font()
        # UI
        if Colors.general_theme == 2:
            self.lbl_session_info.set(background=Colors.background_info_position(), opacity=Colors.background_opacity())
            self.lbl_session_single.set(background=Colors.background_info_position(), opacity=Colors.background_opacity())
            self.lbl_pit_window_bg.set(background=Colors.background_info_position(), opacity=Colors.background_opacity())
            self.lbl_session_title.set(background=Colors.background(), opacity=Colors.background_opacity())
        else:
            self.lbl_session_info.set(background=Colors.background(), opacity=Colors.background_opacity())
            self.lbl_session_single.set(background=Colors.background(), opacity=Colors.background_opacity())
            self.lbl_pit_window_bg.set(background=Colors.background(), opacity=Colors.background_opacity())
            self.lbl_session_title.set(background=Colors.theme(bg=True), opacity=Colors.background_opacity())

        self.rowHeight = self.ui_row_height.value
        font_size = Font.get_font_size(self.rowHeight+self.font_offset)
        width = self.rowHeight * 5
        self.lbl_session_info.setSize(self.rowHeight * 4, self.rowHeight).setPos(self.rowHeight, 0).setFontSize(font_size)
        self.lbl_session_title.setSize(self.rowHeight, self.rowHeight).setFontSize(font_size)
        self.lbl_session_single.setSize(width, self.rowHeight).setFontSize(font_size)
        self.lbl_session_border.setSize(width, 1).setPos(0, self.rowHeight + 1)
        #self.lbl_pit_window_text.setPos(width, 2).setSize(self.rowHeight * 3, self.rowHeight).setFontSize(font_size-2)
        self.lbl_pit_window_text.setPos(0, -self.rowHeight+2).setSize(width, self.rowHeight).setFontSize(font_size-2)
        #self.lbl_pit_window_bg.setPos(width, 0)
        self.lbl_pit_window_bg.setPos(0, -self.rowHeight)
        if len(self.finish_labels) > 0:
            i = 0
            j = 0
            height = self.rowHeight / 3
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
        self.lbl_session_info.setVisible(0)
        self.lbl_session_title.setVisible(0)
        self.lbl_session_border.setVisible(0)
        self.lbl_session_single.setVisible(1)
        self.lbl_session_single.setText("").setBgColor(rgb([255, 255, 255], bg=True)).setBgOpacity(0.76).setVisible(1)
        if len(self.finish_labels) > 0:
            for label in self.finish_labels:
                label.setVisible(1)
        else:
            height = self.rowHeight / 3
            for i in range(0, 3):
                for j in range(0, 8):
                    if i % 2 == 1 and j < 7:
                        self.finish_labels.append(Label(self.window.app)
                                                  .setSize(height, height)
                                                  .setPos(height + j * height * 2, i * height)
                                                  .setBgColor(rgb([0, 0, 0], bg=True))
                                                  .setBgOpacity(0.8).setVisible(1))
                    elif i % 2 == 0:
                        self.finish_labels.append(Label(self.window.app)
                                                  .setSize(height, height)
                                                  .setPos(j * height * 2, i * height)
                                                  .setBgColor(rgb([0, 0, 0], bg=True))
                                                  .setBgOpacity(0.8).setVisible(1))

        self.finish_initialised = True

    def destroy_finish(self):
        # Destroy
        self.lbl_session_single.setBgColor(Colors.background()).setBgOpacity(Colors.background_opacity()).setVisible(0)
        for label in self.finish_labels:
            label.setVisible(0)
        self.finish_initialised = False

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

        if self.cursor.hasChanged() or self.session_draw.hasChanged():
            self.numberOfLapsTimedRace = -1
            self.hasExtraLap = -1
            self.numberOfLaps = -1
            self.pitWindowStart = -1
            self.pitWindowEnd = -1
            self.sessionMaxTime = -1
            self.pitWindowVisibleEnd = 0
            self.pitWindowActive = False
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
            else:
                # pin outside
                self.window.setBgOpacity(0).border(0)

    def on_update(self, sim_info):
        self.session_draw.setValue(sim_info.graphics.session)
        self.manage_window()
        sim_info_status = sim_info.graphics.status
        self.lbl_pit_window_text.animate()
        self.lbl_pit_window_bg.animate()
        if sim_info_status == 2:  # LIVE
            if self.replay_initialised:
                self.lbl_session_single.setColor(Colors.font_color())
            self.session.setValue(self.session_draw.value)
            session_time_left = sim_info.graphics.sessionTimeLeft
            if self.session.value < 2:
                self.lbl_pit_window_text.hideText()
                self.lbl_pit_window_bg.setVisible(0)
                # 0 to -5000 show finish
                if 0 > session_time_left > -5000:
                    if not self.finish_initialised:
                        self.init_finish()
                else:
                    if session_time_left < 0:
                        session_time_left = 0
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_info.setVisible(1)
                    self.lbl_session_title.setVisible(1)
                    self.lbl_session_single.setVisible(0)
                    self.lbl_session_border.setVisible(1)
                    if self.session.hasChanged():
                        self.lbl_session_title.setSize(self.rowHeight, self.rowHeight)
                        self.lbl_session_info.setSize(self.rowHeight * 4, self.rowHeight).setPos(self.rowHeight, 0)
                        if self.session.value == 1:
                            self.lbl_session_title.setText("Q")
                        else:
                            self.lbl_session_title.setText("P")
                    self.lbl_session_info.setText(self.time_splitting(session_time_left))
                    if not self.finish_initialised:
                        if sim_info.graphics.flag == 2:
                            self.lbl_session_info.setBgColor(Colors.yellow(True))
                            self.lbl_session_info.setColor(Colors.black(), True)
                            self.lbl_session_border.setBgColor(Colors.black(bg=True), True)
                            self.lbl_session_title.setBgColor(Colors.black(bg=True), True)
                        else:
                            if Colors.general_theme == 2:
                                self.lbl_session_info.setBgColor(Colors.background_info_position())
                            else:
                                self.lbl_session_info.setBgColor(Colors.background())
                            self.lbl_session_info.setColor(Colors.font_color(), True)
                            self.lbl_session_border.setBgColor(Colors.theme(bg=True), True)
                            self.lbl_session_title.setBgColor(Colors.theme(bg=True), True)
                    self.lbl_session_info.animate()
                    self.lbl_session_title.animate()
            elif self.session.value == 2:
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
                    self.lbl_pit_window_bg.setSize(self.rowHeight * 5, self.rowHeight-1, True).setVisible(1)
                    if self.pitWindowVisibleEnd != 0 and self.pitWindowVisibleEnd < session_time_left:
                        self.lbl_pit_window_text.setColor(Colors.green(), True)
                    elif sim_info.graphics.MandatoryPitDone:
                        self.lbl_pit_window_text.setColor(rgb([172, 172, 172]), True)
                    else:
                        self.lbl_pit_window_text.setColor(Colors.font_color(), True)
                    self.lbl_pit_window_text.setText("Pits open")
                    self.lbl_pit_window_text.showText()
                elif self.pitWindowVisibleEnd != 0 and self.pitWindowVisibleEnd < session_time_left:
                    self.lbl_pit_window_bg.setSize(self.rowHeight * 5, self.rowHeight-1, True).setVisible(1)
                    self.lbl_pit_window_text.setText("Pits closed").setColor(Colors.red(), True)
                    self.lbl_pit_window_text.showText()
                else:
                    self.lbl_pit_window_text.hideText()
                    self.lbl_pit_window_bg.setSize(self.rowHeight * 5, 0,  True).setVisible(1)

                if sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0:
                    self.pitWindowVisibleEnd = 0
                    self.pitWindowActive = False
                    self.sessionMaxTime = round(session_time_left, -3)
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_info.setVisible(0)
                    self.lbl_session_title.setVisible(0)
                    self.lbl_session_single.setVisible(1)
                    self.lbl_session_border.setVisible(1)
                    self.lbl_session_single.setText(self.trackName)
                elif race_finished > 0:  # elif self.numberOfLaps > 0 and completed > self.numberOfLaps:
                    if not self.finish_initialised:
                        self.init_finish()
                elif completed == self.numberOfLaps or (self.numberOfLaps == 0 and self.hasExtraLap == 0 and session_time_left < 0) or (self.hasExtraLap == 1 and completed == self.numberOfLapsTimedRace):
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_info.setVisible(0)
                    self.lbl_session_title.setVisible(0)
                    self.lbl_session_single.setVisible(1)
                    self.lbl_session_border.setVisible(1)
                    self.lbl_session_single.setText("Final lap")
                else:
                    if self.finish_initialised:
                        self.destroy_finish()
                    self.lbl_session_info.setVisible(0)
                    self.lbl_session_title.setVisible(0)
                    self.lbl_session_single.setVisible(1)
                    self.lbl_session_border.setVisible(1)
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
                    if sim_info.graphics.flag == 2:
                        self.lbl_session_single.setBgColor(Colors.yellow(True), True)
                        self.lbl_session_single.setColor(Colors.black(), True)
                        self.lbl_session_border.setBgColor(Colors.black(bg=True), True)
                    else:
                        if Colors.general_theme == 2:
                            self.lbl_session_single.setBgColor(Colors.background_info_position(), True)
                        else:
                            self.lbl_session_single.setBgColor(Colors.background(), True)
                        self.lbl_session_single.setColor(Colors.font_color(), True)
                        self.lbl_session_border.setBgColor(Colors.theme(bg=True), True)
                self.lbl_session_border.animate()
                self.lbl_session_single.animate()
            else:
                self.lbl_session_info.setVisible(0)
                self.lbl_session_title.setVisible(0)
                self.lbl_session_single.setVisible(0)
                self.lbl_session_border.setVisible(0)
                self.lbl_pit_window_text.hideText()

        elif sim_info_status == 1:
            replay_time_multiplier = sim_info.graphics.replayTimeMultiplier
            if self.finish_initialised:
                self.destroy_finish()
            self.lbl_session_info.setVisible(0)
            self.lbl_session_title.setVisible(0)
            self.lbl_pit_window_bg.setVisible(0)
            self.lbl_session_border.setVisible(1)
            self.lbl_session_single.setVisible(1)
            self.lbl_pit_window_text.hideText()
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
