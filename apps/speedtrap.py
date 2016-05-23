import ac
import acsys
import ctypes
import os
from apps.util.func import rgb, getFontSize
from apps.util.classes import Window, Label, Value, POINT, Colors, Config

class ACSpeedTrap:

    # INITIALIZATION

    def __init__(self): 
        self.rowHeight=36         
        self.lastLapInPit = 0
        self.lastLapInvalidated = 0
        self.lastLapShown = 0
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
        self.lapCanBeInvalidated=True
        self.relyOnEveryOne=True
        self.widget_visible=Value()
        self.cursor=Value()
        self.cursor.setValue(False)
        self.ui_row_height = Value(-1)
        self.window = Window(name="ACTV Speed Trap", icon=False, width=250, height=42, texture="")
        self.lbl_title = Label(self.window.app,"").setSize(self.rowHeight, self.rowHeight).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(rgb([12, 12, 12], bg = True)).setBgOpacity(0.72).setVisible(0)
        self.lbl_time = Label(self.window.app,"").setSize(172, self.rowHeight).setPos(38, 0).setFontSize(26).setAlign("center").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64).setVisible(0)
        self.lbl_border = Label(self.window.app,"").setSize(210, 1).setPos(0, 39).setBgColor(Colors.red(bg = True)).setBgOpacity(0.7).setVisible(0)
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
        if cfg.get("SETTINGS", "lap_can_be_invalidated", "int") == 1:
            self.lapCanBeInvalidated = True
        else:
            self.lapCanBeInvalidated = False
        self.ui_row_height.setValue(cfg.get("SETTINGS", "ui_row_height", "int")) 
        if self.ui_row_height.hasChanged():
            self.reDrawSize()
        
    def reDrawSize(self):
        self.rowHeight=self.ui_row_height.value
        fontSize=getFontSize(self.rowHeight)
        self.lbl_title.setSize(self.rowHeight, self.rowHeight).setFontSize(fontSize)
        self.lbl_time.setSize(self.rowHeight*4.8, self.rowHeight).setPos(self.rowHeight, 0).setFontSize(fontSize)
        self.lbl_border.setSize(self.rowHeight*5.8, 1).setPos(0, self.rowHeight+1)
        
            
    def setFont(self,fontName):
        self.lbl_title.setFont(fontName,0,0)
        self.lbl_time.setFont(fontName,0,0)       
                                                   
    def checkMPH(self,cfg_path):
        conf  = Config(cfg_path, "/gameplay.ini")
        opt_mph = conf.get("OPTIONS", "USE_MPH",type = "int")
        if opt_mph == 1:
            self.useMPH = True
          
    def animate(self):
        self.lbl_title.animate()
        self.lbl_time.animate()
        self.lbl_border.animate()
    
    def resetVisibility(self):  
        self.lbl_time.hide()           
        self.lbl_border.hide()           
        self.lbl_title.hide()
    
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
            self.resetVisibility()
            self.time_end = 0
        if self.cursor.hasChanged() or sessionChanged:
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)  
            else:   
                #pin outside
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)
                    
    def onUpdate(self, deltaT, sim_info):   
        self.session.setValue(sim_info.graphics.session)  
        if (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0) or sim_info.graphics.sessionTimeLeft >= 1800000:  
            self.resetVisibility() 
            self.time_end = 0
        self.manageWindow()
        carsCount = ac.getCarsCount()
        for x in range(carsCount):
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
        
        self.currentVehicule.setValue(ac.getFocusedCar())     
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
                #isInPit = self.currentVehicule.value==0 and bool(sim_info.physics.pitLimiterOn)
                isInPit = bool(ac.isCarInPitline(self.currentVehicule.value))
                                      
                if isInPit :
                    self.lastLapInPit = LapCount
                
                if self.lastLapInPit < LapCount and self.curTopSpeed.value < 500 and self.lastLapShown < LapCount and self.lastLapInvalidated < LapCount and self.widget_visible.value == 0 and self.trap < ac.getCarState(self.currentVehicule.value,acsys.CS.NormalizedSplinePosition) + 0.06 and self.trap > ac.getCarState(self.currentVehicule.value,acsys.CS.NormalizedSplinePosition) - 0.08 and self.SpeedKMH.value < self.SpeedKMH.old - 0.6:
                    
                    #show and set timer 0.3
                    self.lastLapShown=LapCount
                    self.widget_visible.setValue(1)
                    if self.useMPH:
                        self.speedText="%.1f mph"%(self.curTopSpeedMPH.value)
                    else:
                        self.speedText="%.1f kph"%(self.curTopSpeed.value)
                    self.time_end = sim_info.graphics.sessionTimeLeft - 6000
                    self.lbl_title.setText("S",hidden=True)
                    self.lbl_time.setText(self.speedText,hidden=True)
                    self.lbl_time.show()
                    self.lbl_border.show()
                    self.lbl_title.show()
                elif self.time_end == 0 or sim_info.graphics.sessionTimeLeft < self.time_end:
                    self.lbl_time.hide()
                    self.lbl_border.hide()
                    self.lbl_title.hide()
                    self.widget_visible.setValue(0)
                    self.time_end=0
                    if self.widget_visible.hasChanged():                        
                        self.curTopSpeed.setValue(0)                      
                        self.curTopSpeedMPH.setValue(0)                   
               
            else:       
                self.resetVisibility()     
                    
        elif sim_info.graphics.status == 1:  
            self.resetVisibility()
    
    