import ac
import acsys
import ctypes
import os
from .util.classes import Window, Label, Value, POINT, Colors, Config, Font
from .configuration import Configuration


class ACSpeedTrap:
    # INITIALIZATION
    def __init__(self):
        self.lastLapInvalidated = 0
        self.lastLapShown = 0
        self.SpeedKMH = Value(0)
        self.SpeedMPH = Value(0)
        self.topSpeed = Value(0)
        self.topSpeedMPH = Value(0)
        self.theme = Value(-1)
        self.userTopSpeed = Value(0)
        self.userTopSpeedMPH = Value(0)
        self.curTopSpeed = Value(0)
        self.curTopSpeedMPH = Value(0)
        self.current_vehicle = Value(0)
        self.session = Value(-1)
        self.font = Value(0)
        self.trap = 0
        self.userTrap = 0
        self.time_start = 0
        self.time_end = 0
        self.carsCount = 0
        self.relyOnEveryOne = True
        self.widget_visible = Value(0)
        self.cursor = Value(False)
        self.row_height = Value(-1)
        self.window = Window(name="ACTV Speed Trap", width=250, height=60)
        self.lbl_title = Label(self.window.app)\
            .set(w=36, h=36,
                 x=0, y=0,
                 font_size=26,
                 align="center")
        self.lbl_title_txt = Label(self.window.app, "Speed Trap")\
            .set(w=36, h=36,
                 x=0, y=0,
                 font_size=26,
                 opacity=0,
                 align="center")
        self.lbl_time = Label(self.window.app)\
            .set(w=172, h=36,
                 x=38, y=0,
                 font_size=26,
                 align="center")
        self.lbl_time_txt = Label(self.window.app)\
            .set(w=172, h=36,
                 x=38, y=0,
                 opacity=0,
                 font_size=26,
                 align="center")
        self.lbl_border = Label(self.window.app)\
            .set(w=210, h=2,
                 x=0, y=39)
        self.useMPH = False
        self.check_mph()
        self.load_cfg()

    # ----------------------- PUBLIC METHODS ------------------------- #

    def load_cfg(self):
        self.row_height.setValue(Configuration.ui_row_height)
        self.font.setValue(Font.current)
        self.theme.setValue(Colors.general_theme + Colors.theme_red + Colors.theme_green + Colors.theme_blue)
        self.redraw_size()

    def redraw_size(self):
        # Colors
        if self.theme.hasChanged():
            self.lbl_title.set(background=Colors.speedtrap_title_bg(), animated=True, init=True)
            self.lbl_title_txt.set(color=Colors.speedtrap_title_txt(), animated=True, init=True)
            self.lbl_time.set(background=Colors.speedtrap_speed_bg(), animated=True, init=True)
            self.lbl_time_txt.set(color=Colors.speedtrap_speed_txt(), animated=True, init=True)
            self.lbl_border.set(background=Colors.speedtrap_border_bg(), animated=True, init=True)

        if self.row_height.hasChanged() or self.font.hasChanged():
            # Fonts
            self.lbl_title_txt.update_font()
            self.lbl_time_txt.update_font()
            # Size
            font_size = Font.get_font_size(self.row_height.value+Font.get_font_offset())
            self.lbl_title.set(w=self.row_height.value*4.7, h=self.row_height.value,
                               x=self.row_height.value*3.3)
            self.lbl_title_txt.set(w=self.row_height.value*4.7, h=self.row_height.value,
                                   x=self.row_height.value*3.3, y=Font.get_font_x_offset(),
                                   font_size=font_size)
            self.lbl_time.set(w=self.row_height.value * 8, h=self.row_height.value,
                              x=0, y=self.row_height.value)
            self.lbl_time_txt.set(w=self.row_height.value * 8, h=self.row_height.value,
                                  x=0, y=self.row_height.value + Font.get_font_x_offset(),
                                  font_size=font_size)
            self.lbl_border.set(w=self.row_height.value * 8, y=self.row_height.value*2 + 1)
            # v1.4
            # self.lbl_title.set(w=self.row_height.value, h=self.row_height.value,
            #                   font_size=font_size)
            # self.lbl_time.set(w=self.row_height.value * 6.6, h=self.row_height.value,
            #                  x=self.row_height.value, font_size=font_size)
            # v1
            # self.lbl_time.set(w=self.row_height.value * 4.8, h=self.row_height.value,
            #                  x=self.row_height.value, font_size=font_size)
            # self.lbl_border.set(w=self.row_height.value * 5.8, y=self.row_height.value + 1)
            # self.lbl_border.set(w=self.row_height.value * 7.6, y=self.row_height.value + 1)

    def check_mph(self):
        cfg_path = None
        user_path = os.path.join(os.path.expanduser("~"), "Documents", "Assetto Corsa", "cfg")
        if os.path.exists(user_path + "/gameplay.ini"):
            cfg_path = user_path
        else:
            user_path = "cfg"
            if os.path.exists(user_path + "/gameplay.ini"):
                cfg_path = user_path
        if cfg_path is not None:
            conf = Config(cfg_path, "/gameplay.ini")
            opt_mph = conf.get("OPTIONS", "USE_MPH", type="int")
            if opt_mph == 1:
                self.useMPH = True

    def animate(self):
        self.lbl_title.animate()
        self.lbl_title_txt.animate()
        self.lbl_time.animate()
        self.lbl_time_txt.animate()
        self.lbl_border.animate()

    def reset_visibility(self):
        self.lbl_time.hide()
        self.lbl_time_txt.hide()
        self.lbl_border.hide()
        self.lbl_title.hide()
        self.lbl_title_txt.hide()

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
        # if result and pt.x > win_x and pt.x < win_x + self.window.width
        # and pt.y > win_y and pt.y < win_y + self.window.height:
        if result and win_x < pt.x < win_x + self.window.width and win_y < pt.y < win_y + self.window.height:
            self.cursor.setValue(True)
        else:
            self.cursor.setValue(False)
        session_changed = self.session.hasChanged()
        if session_changed:
            self.reset_visibility()
            self.time_end = 0
            self.time_start = 0
        if self.cursor.hasChanged() or session_changed:
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)

    def on_update(self, sim_info):
        self.session.setValue(sim_info.graphics.session)
        session_time_left = sim_info.graphics.sessionTimeLeft
        sim_info_status = sim_info.graphics.status
        if sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0:
            self.session.setValue(-1)
            self.session.setValue(sim_info.graphics.session)
        self.manage_window()
        if self.carsCount == 0:
            self.carsCount = ac.getCarsCount()
        for x in range(self.carsCount):
            c = ac.getCarState(x, acsys.CS.SpeedKMH)
            if self.useMPH:
                mph = ac.getCarState(x, acsys.CS.SpeedMPH)
            if x == 0 and self.topSpeed.value < c:
                self.userTopSpeed.setValue(c)
                if self.useMPH:
                    self.userTopSpeedMPH.setValue(mph)
                self.userTrap = ac.getCarState(x, acsys.CS.NormalizedSplinePosition)

            if self.relyOnEveryOne and self.topSpeed.value < c \
                    and ac.getCarState(x, acsys.CS.DriveTrainSpeed) > c / 10 \
                    and ac.getCarState(x, acsys.CS.Gas) > 0.9 \
                    and ac.getCarState(x, acsys.CS.RPM) > 2000:
                if c > 500:
                    self.relyOnEveryOne = False
                    self.topSpeed.setValue(self.userTopSpeed.value)
                    if self.useMPH:
                        self.topSpeedMPH.setValue(self.userTopSpeedMPH.value)
                    self.trap = self.userTrap
                    # ac.console("stop rely")
                else:
                    self.topSpeed.setValue(c)
                    if self.useMPH:
                        self.topSpeedMPH.setValue(mph)
                    self.trap = ac.getCarState(x, acsys.CS.NormalizedSplinePosition)
            elif not self.relyOnEveryOne and x == 0 and self.topSpeed.value < c:
                self.topSpeed.setValue(c)
                if self.useMPH:
                    self.topSpeedMPH.setValue(mph)
                self.trap = ac.getCarState(x, acsys.CS.NormalizedSplinePosition)

        self.current_vehicle.setValue(ac.getFocusedCar())
        self.SpeedKMH.setValue(ac.getCarState(self.current_vehicle.value, acsys.CS.SpeedKMH))
        if self.useMPH:
            self.SpeedMPH.setValue(ac.getCarState(self.current_vehicle.value, acsys.CS.SpeedMPH))
        lap_count = ac.getCarState(self.current_vehicle.value, acsys.CS.LapCount)

        if self.curTopSpeed.value < self.SpeedKMH.value:
            self.curTopSpeed.setValue(self.SpeedKMH.value)
            if self.useMPH:
                self.curTopSpeedMPH.setValue(self.SpeedMPH.value)
        if self.current_vehicle.value == 0 and sim_info.physics.numberOfTyresOut >= 4:
            self.lastLapInvalidated = lap_count
        self.animate()

        if sim_info_status == 2:  # Live
            is_in_pit = (bool(ac.isCarInPitline(self.current_vehicle.value)) or
                         bool(ac.isCarInPit(self.current_vehicle.value)))
            if is_in_pit:
                self.lastLapInvalidated = lap_count
            position = ac.getCarState(self.current_vehicle.value, acsys.CS.NormalizedSplinePosition)
            if self.curTopSpeed.value < 500 and self.lastLapShown < lap_count \
                    and self.lastLapInvalidated < lap_count and self.widget_visible.value == 0 \
                    and position + 0.06 > self.trap > position - 0.08 \
                    and self.SpeedKMH.value < self.SpeedKMH.old - 0.6:
                # show and set timer 0.3
                self.lastLapShown = lap_count
                self.widget_visible.setValue(1)
                if self.useMPH:
                    speed_text = "%.1f mph | %.1f mph" % (self.curTopSpeedMPH.value, self.topSpeedMPH.value)
                else:
                    speed_text = "%.1f kph | %.1f kph" % (self.curTopSpeed.value, self.topSpeed.value)
                self.time_start = session_time_left - 800
                self.time_end = session_time_left - 14800
                self.lbl_time_txt.setText(speed_text) #  , hidden=True)
                self.lbl_title.set(y=self.row_height.value).show()
                self.lbl_title_txt.set(y=self.row_height.value + Font.get_font_x_offset()).show()
            elif self.time_start != 0 and self.time_start > session_time_left > self.time_end:
                self.lbl_title.set(y=0, animated=True).show()
                self.lbl_title_txt.set(y=0 + Font.get_font_x_offset(), animated=True).show()
                self.lbl_time.show()
                self.lbl_time_txt.show()
                self.lbl_border.show()
            elif self.time_end == 0 or session_time_left < self.time_end:
                self.reset_visibility()
                self.widget_visible.setValue(0)
                self.time_start = 0
                self.time_end = 0
                if self.widget_visible.hasChanged():
                    self.curTopSpeed.setValue(0)
                    self.curTopSpeedMPH.setValue(0)
            # else:
            #   self.reset_visibility()
        elif sim_info_status == 1:
            self.reset_visibility()
