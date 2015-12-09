import ac
import acsys
import ctypes
import math

from apps.util.func import rgb
from apps.util.classes import Window, Label, Value, POINT, Colors
       
class ACInfo:

    # INITIALIZATION

    def __init__(self):        
        self.lastLapInPit = 0
        self.lastLapInvalidated = 0
        self.situation = 0
        self.lbl_name_final_height = 0
        self.lbl_name_height = 0
        self.lbl_timing_final_height = 0
        self.lbl_timing_height = 0
        self.lbl_position_final_height = 0
        self.lbl_position_height = 0
        self.lbl_position_text=Value()
        self.currentVehicule=Value()
        self.currentVehicule.setValue(0)
        self.cursor=Value()
        self.cursor.setValue(False)
        self.fastestLap=Value()
        self.fastestPos=1
        self.lastLap=0
        self.lastLapStart=10000
        self.lastTimeInPit=0
        self.visible_end = 0
        self.lastLapTime = 0
        self.fastestLapBorderActive = False
        self.firstLapStarted=False
        self.minLapCount=1
        track=ac.getTrackName(0)
        config=ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife")>=0 and config.find("touristenfahrten")>=0:
            self.minLapCount=0
            self.lastLapInvalidated = -1
        elif track.find("drag1000")>=0 or track.find("drag400")>=0:
            self.minLapCount=0
            self.lastLapInvalidated = -1
        self.fastestLapSectors = [0,0,0,0,0,0]
        self.screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
        self.session=Value()
        self.session.setValue(-1)    
        self.window = Window(name="ACTV Info", icon=False, width=332, height=114, texture="")
        
        self.lbl_driver_name=Label(self.window.app,"Loading").setSize(284, 38).setPos(0, 38).setFontSize(26).setAlign("left").setBgColor(rgb([20, 20, 20], bg = True)).setBgOpacity(0.8).setVisible(1)
        self.lbl_driver_name_visible=Value()
        self.lbl_driver_name_text=Value()
        self.lbl_position_visible=Value()
        self.lbl_position_visible.setValue(0)
        self.lbl_timing_text=Value()
        self.race_fastest_lap=Value()
        self.race_fastest_lap.setValue(0)
        self.race_fastest_lap_driver=Value()
        self.lbl_timing_visible=Value()
        self.lbl_timing=Label(self.window.app,"Loading").setSize(284, 38).setPos(0, 76).setFontSize(26).setAlign("left").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64).setVisible(1)
        self.lbl_split=Label(self.window.app,"Loading").setSize(220, 38).setPos(10, 76).setFontSize(26).setAlign("right").setVisible(0)
        self.lbl_fastest_split=Label(self.window.app,"Loading").setSize(220, 38).setPos(48, 76).setFontSize(26).setAlign("right").setVisible(0)
        self.info_position=Label(self.window.app,"0").setSize(38, 38).setPos(0, 38).setFontSize(26).setAlign("center").setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(1).setVisible(0)
        self.info_position_lead=Label(self.window.app,"1").setSize(38, 38).setPos(246, 76).setFontSize(26).setAlign("center").setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(1).setVisible(0)
        car = ac.getCarName(0)        
        self.lbl_border=Label(self.window.app,"").setSize(284, 1).setPos(0, 75).setBgColor(Colors.colorFromCar(car)).setBgOpacity(0.7).setVisible(0)
                
        
    # PUBLIC METHODS
        
    def format_name(self,name):
        space = name.find(" ")
        if space > 0:
            return name[:space].capitalize() + name[space:].upper()
        return name.upper()
        
    #---------------------------------------------------------------------------------------------------------------------------------------------                                        
    def time_splitting(self, ms, full = "no"):        
        s=ms/1000 
        m,s=divmod(s,60) 
        h,m=divmod(m,60) 
        #d,h=divmod(h,24) 
        if full == "yes":
            d=ms % 1000
            if h > 0:
                return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
            elif m > 0:  
                return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(3))
            else:
                return "{0}.{1}".format(int(s), str(int(d)).zfill(3))
        else:
            d=ms / 100 % 10 
            if h > 0:
                return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), int(d))
            elif m > 0:  
                return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), int(d))
            else:
                return "{0}.{1}".format(int(s), int(d))
    
    def getSector(self):
        splits=ac.getCurrentSplits(self.currentVehicule.value)
        i=0 
        sector=0  
        for c in splits: 
            i+=1
            if c > 0: 
                sector=i
        return sector
        
    def animate(self):
        multiplier=2
        if self.lbl_name_final_height != self.lbl_name_height :          
            if self.lbl_name_final_height < self.lbl_name_height :
                self.lbl_name_height-=multiplier   
                #manage z-index with set visible?         
            elif self.lbl_name_final_height > self.lbl_name_height :
                self.lbl_name_height+=multiplier 
            
            self.lbl_driver_name.setSize(284, self.lbl_name_height)
            self.lbl_border.setPos(0, self.lbl_name_height+38)
            if self.lbl_name_height < 30:
                self.lbl_driver_name.setText("")
            else:
                self.lbl_driver_name.setText(self.lbl_driver_name_text.value)
        elif self.lbl_name_final_height == 0 and self.lbl_name_height == 0 :
            self.lbl_driver_name.setVisible(0)
            self.lbl_border.setVisible(0)
         
        if self.lbl_position_final_height != self.lbl_position_height :     
            if self.lbl_position_final_height < self.lbl_position_height :
                self.lbl_position_height-=multiplier        
            elif self.lbl_position_final_height > self.lbl_position_height :
                self.lbl_position_height+=multiplier 
                
            self.info_position.setSize(38, self.lbl_position_height)
            if self.lbl_position_height < 30:
                self.info_position.setText("")
            else:
                self.info_position.setText(self.lbl_position_text.value)
                
        elif self.lbl_position_final_height == 0 and self.lbl_position_height == 0 :
            self.info_position.setVisible(0)
            
        if self.lbl_name_final_height == self.lbl_name_height and self.lbl_timing_final_height != self.lbl_timing_height : 
            if self.lbl_timing_final_height < self.lbl_timing_height :
                self.lbl_timing_height-=multiplier   
                #manage z-index with set visible?         
            elif self.lbl_timing_final_height > self.lbl_timing_height :
                self.lbl_timing_height+=multiplier 
            self.lbl_timing.setSize(284, self.lbl_timing_height)
            if self.lbl_timing_height < 30:
                self.lbl_timing.setText("")
                self.lbl_fastest_split.hideText()
            else:
                self.lbl_timing.setText(self.lbl_timing_text.value)
                self.lbl_fastest_split.showText()
        elif self.lbl_timing_final_height == 0 and self.lbl_timing_height == 0 :
            self.lbl_timing.setVisible(0)
            
    
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
        
        if self.cursor.hasChanged() or self.session.hasChanged():
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
                ac.setSize(self.window.app, math.floor(self.window.width*self.window.scale), math.floor(self.window.height*self.window.scale))   
            else:   
                #pin outside
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)
                ac.setSize(self.window.app, self.screenWidth*2, 0) 
        
    def onUpdate(self, deltaT, sim_info):
        self.session.setValue(sim_info.graphics.session)
        self.manageWindow()
        self.animate()
        
        for x in range(ac.getCarsCount()):
            if(ac.isCameraOnBoard(x)):
                self.currentVehicule.setValue(x)
        currentVehiculeChanged=self.currentVehicule.hasChanged()
        if currentVehiculeChanged or (self.fastestLapBorderActive and sim_info.graphics.sessionTimeLeft < self.visible_end):
            self.fastestLapBorderActive = False
            car = ac.getCarName(self.currentVehicule.value)        
            self.lbl_border.setBgColor(Colors.colorFromCar(car)).setBgOpacity(0.7)       
            
        if sim_info.graphics.status == 2 :
            #LIVE
            strOffset = "  "
            if sim_info.graphics.session != 2 :
                #NOT RACE
                #qtime          
                bestlap = ac.getCarState(self.currentVehicule.value,acsys.CS.BestLap)
    
                isInPit = self.currentVehicule.value==0 and bool(sim_info.graphics.isInPit)
                #isInPit = self.currentVehicule.value==0 and bool(sim_info.physics.pitLimiterOn)
                LapCount = ac.getCarState(self.currentVehicule.value,acsys.CS.LapCount)
                if self.lastLap != LapCount:
                    self.lastLap = LapCount
                    self.firstLapStarted=False
                    self.lastLapStart = sim_info.graphics.sessionTimeLeft
                curLapTime = ac.getCarState(self.currentVehicule.value, acsys.CS.LapTime)
                if curLapTime > 0:
                    self.firstLapStarted=True
                if self.minLapCount == 0 and self.firstLapStarted and ((self.lastLapTime > curLapTime and curLapTime < 1000) or self.lastLapStart==10000):
                    self.lastLapStart = sim_info.graphics.sessionTimeLeft                    
                self.lastLapTime = curLapTime
                                  
                if isInPit :
                    self.lastLapInPit = LapCount
                    self.lastTimeInPit = sim_info.graphics.sessionTimeLeft
                if self.currentVehicule.value==0 and sim_info.physics.numberOfTyresOut >= 4 :
                    self.lastLapInvalidated = LapCount
                if isInPit and self.minLapCount == 0:
                    self.lastLapInvalidated = -1
                
                sectorCount = sim_info.static.sectorCount    
                #save fastest lap as it comes - online need to be there
                online_fast_test=0
                online_fast_sect = [0,0,0,0,0,0]
                for x in range(ac.getCarsCount()): 
                    c = ac.getCarState(x,acsys.CS.BestLap)
                    if online_fast_test == 0 or (c > 0 and c < online_fast_test):
                        online_fast_test=c
                        online_fast_sect=ac.getCarState(x,acsys.CS.BestLap)
                    if self.fastestLap.value == 0 or (c > 0 and c < self.fastestLap.value): #and  self.fastestLapSectors[sectorCount - 1] > 0 :               
                        self.fastestLap.setValue(c)
                        self.fastestLapSectors = ac.getLastSplits(x)
                     
                #self.lbl_test.setText(str(self.fastestLap.value) + " " + str(self.fastestLapSectors) + ">"+str(online_fast_test))        
                #lapInvalidated = bool(ac.getCarState(0, acsys.CS.LapInvalidated))
                lapInvalidated = bool(self.lastLapInvalidated==LapCount)
                # live ou passif                
                if ((self.lastLapStart < 0 and self.minLapCount > 0) or (self.minLapCount == 0 and lapInvalidated)) and sim_info.graphics.session != 0:                    
                    self.lbl_driver_name_visible.setValue(0)
                    self.lbl_timing_visible.setValue(0)  
                    self.lbl_split.setVisible(0)  
                    self.info_position.setVisible(0)
                    self.info_position_lead.setVisible(0)          
                elif (self.lastLapInPit < LapCount or self.minLapCount==0) and not lapInvalidated and (self.lastTimeInPit==0 or self.lastTimeInPit > self.lastLapStart) :
                    
                    sector_delay = 5000
                    if self.currentVehicule.value == 0:
                        sector = sim_info.graphics.currentSectorIndex
                    else:
                        sector = self.getSector()
                    
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_timing_visible.setValue(1)  
                    
                    lapTime = ac.getCarState(self.currentVehicule.value, acsys.CS.LapTime)
                    if self.currentVehicule.value == 0:
                        lastLap = sim_info.graphics.iLastTime
                    else: 
                        lastLap=0                       
                        lastSplits = ac.getLastSplits(self.currentVehicule.value)
                        for c in lastSplits:
                            lastLap+=c
                            
                    
                    traite=False
                    cur_splits = ac.getCurrentSplits(self.currentVehicule.value)
                    timeSplit=0
                    fastestSplit=0
                    i=0
                    showSplit=False
                    for c in cur_splits: 
                        if c > 0:
                            timeSplit+=c 
                            fastestSplit+=self.fastestLapSectors[i]
                            i+=1
                    fastestSplit_fin=fastestSplit
                    if i < sectorCount:
                        fastestSplit_fin+=self.fastestLapSectors[i]
                         
                    #Situation
                    for s in range(0,sectorCount):                    
                        if self.fastestLap.value > 0 and lapTime > fastestSplit_fin - sector_delay:
                            #LAST_SECONDS_OF_SECTOR_X, sector == s and
                            self.info_position.setVisible(0) 
                            self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                            if sectorCount-1 == sector:
                                #LAST_SECONDS_OF_SECTOR_LAP,
                                self.lbl_split.setText(self.time_splitting(self.fastestLap.value,"yes")).setColor(rgb([255, 255, 255])).setVisible(1)
                                self.info_position_lead.setVisible(1) 
                                
                                showSplit=True
                            elif fastestSplit_fin > 0:
                                self.lbl_split.setText(self.time_splitting(fastestSplit_fin,"yes")).setColor(rgb([255, 255, 255])).setVisible(1)
                                self.info_position_lead.setVisible(1) 
                                showSplit=True
                            break
                        if sector == s + 1 and s + 1 <= sectorCount and lapTime - timeSplit <= sector_delay and fastestSplit > 0 :
                            #SECTOR_X_FINISHED_BEGIN_SECTOR_Y  
                            self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(self.currentVehicule.value)))                  
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(timeSplit,"yes")) 
                            if fastestSplit < timeSplit:
                                self.lbl_split.setText("+"+self.time_splitting(timeSplit-fastestSplit,"yes")).setColor(rgb([240, 171, 1])).setVisible(1)
                            else:
                                self.lbl_split.setText("-"+self.time_splitting(fastestSplit-timeSplit,"yes")).setColor(rgb([32, 192, 31])).setVisible(1)
                            self.info_position_lead.setVisible(1) 
                            self.info_position.setVisible(0)
                            traite=True
                            break
                    
                    if not traite:
                        if sectorCount-1 == sector and self.fastestLap.value > 0 and lapTime > self.fastestLap.value - sector_delay:
                            #LAST_SECONDS_OF_SECTOR_LAP,
                            self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(lapTime)) 
                            self.info_position.setVisible(0)
                            #self.lbl_split.setText(self.time_splitting(self.fastestLap,"yes") + strOffset).setVisible(1)
                        elif self.lastLapInvalidated!=LapCount-1 and ((self.lastLapInPit!=LapCount-1 and sector == 0) or (self.minLapCount==0)) and lapTime <= sector_delay and lastLap > 0:
                            #LAP_FINISHED_BEGIN_NEW_LAP,                        
                            #pos = sim_info.graphics.position                   
                            pos = ac.getCarLeaderboardPosition(self.currentVehicule.value)
                            if pos > 1:
                                self.info_position.setColor(rgb([255, 255, 255])).setBgColor(rgb([112, 112, 112], bg = True)).setBgOpacity(0.8)
                            else:
                                self.info_position.setColor(rgb([255, 255, 255])).setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(0.8)
                            self.info_position.setText(str(pos))
                            self.info_position.setVisible(1)
                            
                            self.lbl_driver_name_text.setValue(strOffset + "     " + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(lastLap,"yes")) 
                            if self.fastestLap.value < lastLap:
                                self.lbl_split.setText("+"+self.time_splitting(lastLap-self.fastestLap.value,"yes")).setColor(rgb([240, 171, 1])).setVisible(1)
                            else:                            
                                self.lbl_split.setText("-"+self.time_splitting(self.fastestLap.old-lastLap,"yes")).setColor(rgb([32, 192, 31])).setVisible(1)
                            self.info_position_lead.setVisible(1) 
                            
                        else:
                            #OTHER
                            self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(lapTime))  
                            self.info_position.setVisible(0)
                            if not showSplit:
                                self.lbl_split.setVisible(0)
                                self.info_position_lead.setVisible(0)
                else :                    
                    self.info_position_lead.setVisible(0)
                    #self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(0)))                        
                    normalizedSplinePosition = ac.getCarState(self.currentVehicule.value,acsys.CS.NormalizedSplinePosition)
                    if normalizedSplinePosition <= 0.001:
                        normalizedSplinePosition=1
                    if sim_info.graphics.sessionTimeLeft > 0 and self.minLapCount==1 and normalizedSplinePosition > 0.95 and not isInPit :                         
                        self.lbl_driver_name_visible.setValue(1)                    
                        self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                        self.lbl_timing_visible.setValue(1)  
                        self.lbl_split.setVisible(0)  
                        self.info_position.setVisible(0)
                        self.lbl_timing_text.setValue(strOffset + "0.0") 
                        #if bestlap > 0 :
                        #    self.info_position.setVisible(1)
                        #else:
                        #self.info_position.setVisible(0)
                    elif lapInvalidated and self.lastLapInPit < LapCount and self.minLapCount > 0 :
                        self.lbl_driver_name_visible.setValue(0)
                        self.lbl_timing_visible.setValue(0)  
                        self.lbl_split.setVisible(0)  
                        self.info_position.setVisible(0)  
                    elif bestlap > 0 :                
                        self.lbl_driver_name_visible.setValue(1)
                        self.lbl_timing_visible.setValue(1)  
                         
                        if self.fastestLap.value < bestlap:
                            self.lbl_split.setText("+"+self.time_splitting(bestlap-self.fastestLap.value,"yes")).setColor(rgb([240, 171, 1])).setVisible(1) 
                            #self.lbl_split.setVisible(1) 
                        else:                            
                            self.lbl_split.setVisible(0)
                        
                        self.info_position.setVisible(1)
                        self.lbl_timing_text.setValue(strOffset + self.time_splitting(bestlap,"yes")) 
                                            
                        self.lbl_driver_name_text.setValue(strOffset + "     " + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                        #pos = sim_info.graphics.position
                        pos = ac.getCarLeaderboardPosition(self.currentVehicule.value)
                        if pos > 1:
                            self.info_position.setColor(rgb([255, 255, 255])).setBgColor(rgb([112, 112, 112], bg = True)).setBgOpacity(1)
                        else:
                            self.info_position.setColor(rgb([255, 255, 255])).setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(1)
                        self.info_position.setText(str(pos)).setVisible(1)   
                        self.lbl_position_text.setValue(str(pos))                
                            
                    elif isInPit :     
                        self.lbl_driver_name_visible.setValue(0)
                        self.lbl_timing_visible.setValue(0)  
                        self.lbl_split.setVisible(0)  
                        self.info_position.setVisible(0)
                    else :  
                        self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                        self.lbl_driver_name_visible.setValue(1)
                        self.lbl_timing_visible.setValue(1)
                        self.lbl_timing_text.setValue(strOffset + "Out Lap")
                        self.lbl_split.setVisible(0)
                        self.info_position.setVisible(0)  
                
                self.lbl_fastest_split.setVisible(0)
                if self.lbl_driver_name_visible.value == 1 and self.lbl_driver_name.visible==0:
                    self.lbl_driver_name_visible.changed=True
                if self.lbl_timing_visible.value == 1 and self.lbl_timing.visible==0:
                    self.lbl_timing_visible.changed=True
                if self.lbl_driver_name_visible.hasChanged():         
                    if self.lbl_driver_name_visible.value == 0:
                        self.lbl_name_final_height = 0
                    else:
                        self.lbl_name_final_height = 38
                        self.lbl_driver_name.setVisible(1)
                        self.lbl_border.setVisible(1)
                        
                if self.lbl_timing_visible.hasChanged():         
                    if self.lbl_timing_visible.value == 0:
                        self.lbl_timing_final_height = 0
                    else:
                        self.lbl_timing_final_height = 38
                        self.lbl_timing.setVisible(1)
                        
                if self.lbl_driver_name_text.hasChanged():
                    self.lbl_driver_name.setText(self.lbl_driver_name_text.value)   
                if self.lbl_timing_text.hasChanged() and self.lbl_timing_final_height == self.lbl_timing_height:
                    self.lbl_timing.setText(self.lbl_timing_text.value) 
            else:
                self.info_position_lead.setVisible(0) 
                self.lbl_split.setVisible(0)
                #fastest lap
                completed=0
                for x in range(ac.getCarsCount()): 
                    c = ac.getCarState(x,acsys.CS.LapCount)
                    if c > completed:
                        completed=c
                if completed <=1:
                    self.race_fastest_lap.setValue(0)
                else:
                    for i in range(ac.getCarsCount()): 
                        bl=ac.getCarState(i,acsys.CS.BestLap)
                        l = ac.getCarState(i,acsys.CS.LapCount)
                        if bl > 0 and l > self.minLapCount and (self.race_fastest_lap.value == 0 or bl < self.race_fastest_lap.value):
                            self.race_fastest_lap.setValue(bl)
                            self.race_fastest_lap_driver.setValue(i)
                if self.race_fastest_lap.hasChanged() and self.race_fastest_lap.value > 0:
                    self.fastestLapBorderActive = True
                    car = ac.getCarName(self.race_fastest_lap_driver.value)        
                    self.lbl_border.setBgColor(Colors.colorFromCar(car)).setBgOpacity(0.7) 
                    self.visible_end = sim_info.graphics.sessionTimeLeft - 8000
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_driver_name_text.setValue(strOffset + self.format_name(ac.getDriverName(self.race_fastest_lap_driver.value)))
                    self.lbl_timing_text.setValue(strOffset + "Fastest Lap")
                    self.lbl_timing_visible.setValue(1)
                    self.lbl_fastest_split.setText(self.time_splitting(self.race_fastest_lap.value,"yes"),hidden=bool(self.lbl_timing_height < 30)).setVisible(1)
                    
                elif currentVehiculeChanged:  
                    #driver info                  
                    self.visible_end = sim_info.graphics.sessionTimeLeft - 8000
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_driver_name_text.setValue(strOffset + "     " + self.format_name(ac.getDriverName(self.currentVehicule.value)))
                    #pos = ac.getCarLeaderboardPosition(self.currentVehicule.value)
                    pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicule.value) + 1
                    if pos > 1:
                        self.info_position.setColor(rgb([255, 255, 255])).setBgColor(rgb([112, 112, 112], bg = True)).setBgOpacity(1)
                    else:
                        self.info_position.setColor(rgb([255, 255, 255])).setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(1)
                    self.info_position.setText(str(pos)).setVisible(1)   
                    self.lbl_position_final_height = 38
                    self.lbl_timing_visible.setValue(0)
                    self.lbl_fastest_split.setVisible(0)
                elif self.visible_end == 0 or sim_info.graphics.sessionTimeLeft < self.visible_end:
                    self.lbl_driver_name_visible.setValue(0)
                    self.info_position.setVisible(0)
                    self.lbl_timing_visible.setValue(0)
                    self.lbl_fastest_split.setVisible(0)
                    
                if self.lbl_driver_name_visible.hasChanged():         
                    if self.lbl_driver_name_visible.value == 0:
                        self.lbl_name_final_height = 0
                    else:
                        self.lbl_name_final_height = 38
                        self.lbl_driver_name.setVisible(1)
                        self.lbl_border.setVisible(1)
                    
                if self.lbl_timing_visible.hasChanged():         
                    if self.lbl_timing_visible.value == 0:
                        self.lbl_timing_final_height = 0
                    else:
                        self.lbl_timing_final_height = 38
                        self.lbl_timing.setVisible(self.lbl_timing_visible.value)
                        
                if self.lbl_driver_name_text.hasChanged():
                    self.lbl_driver_name.setText(self.lbl_driver_name_text.value)   
                if self.lbl_timing_text.hasChanged():
                    self.lbl_timing.setText(self.lbl_timing_text.value,hidden=bool(self.lbl_timing_height < 30)) 
                    
        else:
            #REPLAY
            self.lbl_driver_name.setVisible(0)
            self.lbl_fastest_split.setVisible(0)
            self.lbl_border.setVisible(0)
            self.lbl_timing.setVisible(0)
            self.lbl_split.setVisible(0)
            self.info_position_lead.setVisible(0) 
            self.info_position.setVisible(0)
        
    
    