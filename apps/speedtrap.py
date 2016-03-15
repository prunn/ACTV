import ac
import acsys
import ctypes
import math
import os
from apps.util.func import rgb
from apps.util.classes import Window, Label, Value, POINT, Config

class ACSpeedTrap:

    # INITIALIZATION

    def __init__(self):         
        self.lastLapInPit = 0
        self.lastLapInvalidated = 0
        self.lastLapShown = 0
        self.height = 0
        self.final_height = 0
        self.SpeedKMH=Value()
        self.SpeedMPH=Value()
        self.topSpeed=Value()
        self.userTopSpeed=Value()
        self.curTopSpeed=Value()
        self.curTopSpeedMPH=Value()
        self.currentVehicule=Value()
        self.currentVehicule.setValue(0)
        self.session=Value()
        self.session.setValue(-1)
        self.speedText=""
        self.trap=0
        self.userTrap=0
        self.time_end=0
        self.pinHack=Value(True)
        self.lapCanBeInvalidated=True
        self.relyOnEveryOne=True
        self.widget_visible=Value()
        self.cursor=Value()
        self.cursor.setValue(False)
        self.window = Window(name="ACTV Speed Trap", icon=False, width=250, height=42, texture="")
        self.lbl_title = Label(self.window.app,"").setSize(38, 38).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(rgb([12, 12, 12], bg = True)).setBgOpacity(0.72).setVisible(0)
        self.lbl_time = Label(self.window.app,"").setSize(172, 38).setPos(38, 0).setFontSize(26).setAlign("center").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64).setVisible(0)
        self.lbl_border = Label(self.window.app,"").setSize(210, 1).setPos(0, 39).setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(0.7).setVisible(1)
        self.screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
        self.useMPH = False
        
        user_path = os.path.join(os.path.expanduser("~"), "Documents","Assetto Corsa","cfg")
        if os.path.exists(user_path + "/gameplay.ini"):
            self.checkMPH(user_path)
        else:
            user_path = "cfg"
            if os.path.exists(user_path + "/gameplay.ini"):
                self.checkMPH(user_path)
        self.loadCFG()
    # PUBLIC METHODS
    
    #--------------------------------------------------------------------------------------------------------------------------------------------- 
    def loadCFG(self):        
        cfg = Config("apps/python/prunn/", "config.ini")
        if cfg.get("SETTINGS", "hide_pins", "int") == 1:
            self.pinHack.setValue(True)
        else:
            self.pinHack.setValue(False)
        if cfg.get("SETTINGS", "lap_can_be_invalidated", "int") == 1:
            self.lapCanBeInvalidated = True
        else:
            self.lapCanBeInvalidated = False
            
                                                   
    def checkMPH(self,cfg_path):
        conf  = Config(cfg_path, "/gameplay.ini")
        opt_mph = conf.get("OPTIONS", "USE_MPH",type = "int")
        if opt_mph == 1:
            self.useMPH = True
          
    def animate(self):
        multiplier=2
        if self.final_height != self.height :          
            if self.final_height < self.height :
                self.height-=multiplier   
                #manage z-index with set visible?         
            elif self.final_height > self.height :
                self.height+=multiplier 
            
            self.lbl_title.setSize(38, self.height)
            self.lbl_time.setSize(172, self.height)
            self.lbl_border.setPos(0, self.height+1)
            if self.height < 30:
                self.lbl_title.setText("")
                self.lbl_time.setText("")
            else:
                self.lbl_title.setText("S")
                self.lbl_time.setText(self.speedText)
        elif self.final_height == 0 and self.height == 0 :
            self.lbl_time.setVisible(0)
            self.lbl_border.setVisible(0)
            self.lbl_title.setVisible(0)
    
    def manageWindow(self):
        pt=POINT()
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
        sessionChanged = self.session.hasChanged() 
        if sessionChanged:
            self.lbl_time.setVisible(0)           
            self.lbl_border.setVisible(0)           
            self.lbl_title.setVisible(0)
            self.time_end = 0
        if self.pinHack.hasChanged():
            if self.pinHack.value:
                ac.setSize(self.window.app, self.screenWidth*2, 0)  
            else:   
                ac.setSize(self.window.app, math.floor(self.window.width*self.window.scale), math.floor(self.window.height*self.window.scale))
        if self.cursor.hasChanged() or sessionChanged:
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
                if self.pinHack.value:
                    ac.setSize(self.window.app, math.floor(self.window.width*self.window.scale), math.floor(self.window.height*self.window.scale))   
            else:   
                #pin outside
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)
                if self.pinHack.value:
                    ac.setSize(self.window.app, self.screenWidth*2, 0) 
                    
    def onUpdate(self, deltaT, sim_info):   
        self.session.setValue(sim_info.graphics.session)  
        if (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0) or sim_info.graphics.sessionTimeLeft >= 1800000:  
            self.lbl_time.setVisible(0)           
            self.lbl_border.setVisible(0)           
            self.lbl_title.setVisible(0) 
            self.time_end = 0
        self.manageWindow()
        carsCount = ac.getCarsCount()
        for x in range(carsCount):
            if(ac.isCameraOnBoard(x)):
                self.currentVehicule.setValue(x)  
            c = ac.getCarState(x,acsys.CS.SpeedKMH)
            if x==0 and self.topSpeed.value < c:
                self.userTopSpeed.setValue(c)
                self.userTrap = ac.getCarState(x,acsys.CS.NormalizedSplinePosition)
                
            if self.relyOnEveryOne and self.topSpeed.value < c and ac.getCarState(x,acsys.CS.DriveTrainSpeed) > c/10 and ac.getCarState(x,acsys.CS.Gas) > 0.9 and ac.getCarState(x,acsys.CS.RPM) > 2000:
                if c > 500:
                    self.relyOnEveryOne=False
                    self.topSpeed.setValue(self.userTopSpeed.value)
                    self.trap = self.userTrap 
                    #ac.console("stop rely")
                    #ac.log("stop rely")
                else:
                    self.topSpeed.setValue(c)
                    #ac.console(str(c) + "-"+str(x)+"-rpm:"+str(ac.getCarState(x,acsys.CS.RPM))+"-Gas:"+str(ac.getCarState(x,acsys.CS.Gas))+"-Gear:"+str(ac.getCarState(x,acsys.CS.Gear))+"-DriveTrainSpeed:"+str(ac.getCarState(x,acsys.CS.DriveTrainSpeed))) 
                    self.trap = ac.getCarState(x,acsys.CS.NormalizedSplinePosition) 
            elif not self.relyOnEveryOne and x == 0 and self.topSpeed.value < c:
                self.topSpeed.setValue(c)
                self.trap = ac.getCarState(x,acsys.CS.NormalizedSplinePosition)      
            
        self.SpeedKMH.setValue(ac.getCarState(self.currentVehicule.value,acsys.CS.SpeedKMH))
        self.SpeedMPH.setValue(ac.getCarState(self.currentVehicule.value,acsys.CS.SpeedMPH))
        LapCount = ac.getCarState(self.currentVehicule.value,acsys.CS.LapCount)                   
        
        if self.curTopSpeed.value < self.SpeedKMH.value:
            self.curTopSpeed.setValue(self.SpeedKMH.value) 
            self.curTopSpeedMPH.setValue(self.SpeedMPH.value)         
        if self.currentVehicule.value==0 and sim_info.physics.numberOfTyresOut >= 4 and self.lapCanBeInvalidated:
            self.lastLapInvalidated = LapCount
        self.animate()
        
        if sim_info.graphics.status == 2:
            if sim_info.graphics.session <= 2  :                
                #Qual-Practise every time
                isInPit = self.currentVehicule.value==0 and bool(sim_info.physics.pitLimiterOn)
                                      
                if isInPit :
                    self.lastLapInPit = LapCount
                
                if self.lastLapInPit < LapCount and self.curTopSpeed.value < 500 and self.lastLapShown < LapCount and self.lastLapInvalidated < LapCount and self.widget_visible.value == 0 and self.trap < ac.getCarState(self.currentVehicule.value,acsys.CS.NormalizedSplinePosition) + 0.06 and self.trap > ac.getCarState(self.currentVehicule.value,acsys.CS.NormalizedSplinePosition) - 0.08 and self.SpeedKMH.value < self.SpeedKMH.old - 0.3:
                    #show and set timer 
                    self.lastLapShown=LapCount
                    self.widget_visible.setValue(1)
                    #self.lbl_time.setText("%.1f kph"%(self.curTopSpeed.value))
                    if self.useMPH:
                        self.speedText="%.1f mph"%(self.curTopSpeedMPH.value)
                    else:
                        self.speedText="%.1f kph"%(self.curTopSpeed.value)
                    self.time_end = sim_info.graphics.sessionTimeLeft - 6000
                    self.final_height = 38
                    self.height = 0        
                    self.lbl_time.setVisible(1)
                    self.lbl_border.setVisible(1)
                    self.lbl_title.setVisible(1)
                elif self.time_end == 0 or sim_info.graphics.sessionTimeLeft < self.time_end:
                    #ac.console("hidden : self.time_end == 0  or " + str(sim_info.graphics.sessionTimeLeft) + " < " + str(self.time_end))
                    self.widget_visible.setValue(0)
                    self.time_end=0
                    self.final_height = 0
                    if self.widget_visible.hasChanged():                        
                        self.curTopSpeed.setValue(0)                      
                        self.curTopSpeedMPH.setValue(0)
                    
                #if self.widget_visible.hasChanged:         
                # #   self.lbl_time.setVisible(self.widget_visible.value)
                #    self.lbl_border.setVisible(self.widget_visible.value)
                #   self.lbl_title.setVisible(self.widget_visible.value)
                   
            elif sim_info.graphics.session == 2 :
                #race more randomly          
                self.lbl_time.setVisible(0) 
                self.lbl_border.setVisible(0)  
                self.lbl_title.setVisible(0)    
            else:       
                self.lbl_time.setVisible(0) 
                self.lbl_border.setVisible(0)  
                self.lbl_title.setVisible(0)     
                    
        elif sim_info.graphics.status == 1:  
            self.lbl_time.setVisible(0)           
            self.lbl_border.setVisible(0)           
            self.lbl_title.setVisible(0)
    
    