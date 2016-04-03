import ac
import acsys
import math
import sys
import ctypes
from apps.util.func import rgb
from apps.util.classes import Window, Label, Value, POINT, Colors, Config

class Laps:
    def __init__(self,lap,valid,time):
        self.lap = lap
        self.valid = valid
        self.time = time
        
class Driver:
    def __init__(self,app,identifier,name,pos,isLapLabel=False):
        self.identifier=identifier
        strOffset = " "
        self.y = 0
        self.final_y = 0
        self.isDisplayed = False
        self.isAlive = False
        self.isLapLabel = isLapLabel
        self.gas=Value()
        self.wheelSpeed=Value()
        self.race_mode = Value(0)
        self.qual_mode = Value(0)
        self.race_gaps = []
        self.keepAlive=0
        self.finished=False
        self.fullName = Value(name)
        self.shortName = name
        self.driver_shown=0
        self.time = Value()
        self.gap = Value()
        self.race_current_sector = Value()
        self.race_standings_sector = Value(0)
        self.isInPit = Value(False)
        self.completedLaps = Value()
        self.time_highlight_end = 0
        self.highlight = Value()
        self.position = Value()
        self.position_offset = Value()
        self.gapToFirst=0
        self.showingFullNames=False
        if isLapLabel:            
            self.lbl_name = Label(app,strOffset+name).setSize(218, 38).setPos(0, 0).setFontSize(26).setAlign("left").setBgColor(rgb([32, 32, 32], bg = True)).setBgOpacity(0.6).setVisible(0)
        else:    
            self.lbl_name = Label(app,strOffset+self.format_name_tlc(name)).setSize(180, 38).setPos(38, 0).setFontSize(26).setAlign("left").setBgColor(rgb([32, 32, 32], bg = True)).setBgOpacity(0.6).setVisible(0)
        self.lbl_position = Label(app,str(pos+1)).setSize(38, 38).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(rgb([112, 112, 112], bg = True)).setColor(rgb([255,255,255])).setBgOpacity(1).setVisible(0)
        self.lbl_time = Label(app,"+0.000").setSize(60, 38).setPos(148, 0).setFontSize(26).setAlign("right").setBgOpacity(0).setVisible(0)
        self.lbl_border=Label(app,"").setSize(104, 1).setPos(0, 38).setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(0.7).setVisible(0)
        self.lbl_pit = Label(app,"P").setSize(24, 36).setPos(218, 0).setFontSize(23).setAlign("center").setBgOpacity(0).setVisible(0)
        self.setName()
    
    def show(self,start,needsTLC=True):
        if self.showingFullNames and needsTLC:
            self.setName()
        if not self.isDisplayed: 
            self.lbl_name.setVisible(1)
            if self.isLapLabel:
                self.lbl_position.setVisible(0)
            else:
                self.lbl_position.setVisible(1)
            self.lbl_time.setVisible(1)
            self.lbl_border.setVisible(1)
            if start > 1:
                self.y=(start-2)*38
                if self.isLapLabel:
                    self.lbl_name.setPos(0, (start-2)*38)
                else:
                    self.lbl_name.setPos(38, (start-2)*38)
                self.lbl_position.setPos(0, (start-2)*38)
                self.lbl_time.setPos(148, (start-2)*38) 
                self.lbl_pit.setPos(218, (start-2)*38 + 2)   
                self.lbl_border.setPos(0, (start-2)*38 + 37)
            else:
                self.y=38
                if self.isLapLabel:
                    self.lbl_name.setPos(0, 38)
                else:
                    self.lbl_name.setPos(38, 38)
                self.lbl_position.setPos(0, 38)
                self.lbl_time.setPos(148, 38)  
                self.lbl_pit.setPos(218, 42)  
                self.lbl_border.setPos(0, 37)        
            self.isDisplayed = True
            
    def updatePit(self):
        self.isInPit.setValue(bool(ac.isCarInPitline(self.identifier)))
        if self.isInPit.hasChanged():
            if self.isInPit.value:
                self.lbl_pit.setVisible(1)
                self.lbl_name.setSize(204, 38)
            else:
                self.lbl_pit.setVisible(0)  
                self.lbl_name.setSize(180, 38)                  
           
    def hide(self): 
        if self.isDisplayed: 
            self.lbl_name.setVisible(0)
            self.lbl_name.setSize(218, 38) 
            self.lbl_position.setVisible(0)
            self.lbl_time.setVisible(0)
            self.lbl_border.setVisible(0)  
            self.lbl_pit.setVisible(0)  
            self.isDisplayed = False    
            
    def setName(self):
        strOffset = " "
        if self.isLapLabel:
            self.lbl_name.setText(strOffset+self.fullName.value)
        else:
            self.lbl_name.setText(strOffset+self.format_name_tlc(self.fullName.value))        
            car = ac.getCarName(self.identifier) 
            self.lbl_border.setBgColor(Colors.colorFromCar(car)).setBgOpacity(0.7)
    
    def showFullName(self):
        strOffset = " "
        self.showingFullNames=True   
        self.lbl_time.setText("")
        self.lbl_name.setText(strOffset+self.format_last_name(self.fullName.value))
            
    def setTime(self,time,leader,session_time,mode):
        self.qual_mode.setValue(mode)
        self.time.setValue(time)
        self.gap.setValue(time-leader)
        time_changed=self.time.hasChanged()
        if time_changed or self.gap.hasChanged() or self.qual_mode.hasChanged():
            if time_changed:
                self.time_highlight_end = session_time - 5000
            #self.highlight.setValue(True)
            if self.position.value==1 or mode==1:
                self.lbl_time.setText(self.format_time(self.time.value))
            else:
                self.lbl_time.setText("+"+self.format_time(self.gap.value))
                
    def setTimeStint(self,time,valid):
        self.time.setValue(time)
        self.gap.setValue(time)
        time_changed=self.time.hasChanged()
        if time_changed or self.gap.hasChanged():            
            if self.isLapLabel:
                self.lbl_time.setText(self.format_time(self.time.value))
        if valid:            
            self.lbl_time.setColor(rgb([255,255,255]))
        else:
            self.lbl_time.setColor(rgb([192,0,0]))
                
    def setTimeRace(self,time,leader,session_time):
        if self.position.value==1:
            self.lbl_time.setText("Lap " + str(time)).setColor(rgb([255,255,255]))
        else:
            self.lbl_time.setText("+"+self.format_time(leader-session_time)).setColor(rgb([255,255,255]))
            
    def setTimeRaceBattle(self,time,identifier):
        if self.identifier==identifier:           
            self.lbl_time.setText("")
        else:
            self.lbl_time.setText(""+self.format_time(time)).setColor(rgb([255,255,255]))
            
    def optimise(self,sector):
        if self.race_gaps:
            result = []
            for g in self.race_gaps:
                if g.sector + 75 > sector:
                    result.append(g)
            self.race_gaps = result
               
    def setPosition(self,position,leader,offset,battles,qual_mode):
        self.position.setValue(position)
        self.position_offset.setValue(offset)
        if self.position.hasChanged() or self.position_offset.hasChanged():
            self.lbl_position.setText(str(self.position.value))
            #move labels
            #ac.console("offset:" + str(offset))
            pos=position-1-offset
            self.final_y=pos*38
            if position % 2 == 1:
                self.lbl_name.setBgOpacity(0.72)
                #self.lbl_pit.setBgOpacity(0.72)           
                if position==1:
                    self.lbl_position.setBgColor(rgb([192, 0, 0], bg = True)).setColor(rgb([255,255,255])).setBgOpacity(0.72)
                    #self.lbl_position.setBgColor(rgb([0, 0, 0], bg = True)).setBgOpacity(0.76)
                    self.lbl_time.setText(self.format_time(self.time.value))
                elif battles and self.identifier == 0:
                    self.lbl_position.setBgColor(rgb([255, 255, 255], bg = True)).setColor(rgb([192,0,0])).setBgOpacity(0.72)
                    #self.lbl_position.setBgColor(rgb([0, 0, 0], bg = True)).setBgOpacity(0.76)
                    self.lbl_time.setText(self.format_time(self.time.value))
                else:
                    #self.lbl_position.setBgColor(rgb([112, 112, 112], bg = True)).setBgOpacity(0.76)
                    self.lbl_position.setBgColor(rgb([12, 12, 12], bg = True)).setColor(rgb([255,255,255])).setBgOpacity(0.72)
                    if qual_mode == 1:
                        self.lbl_time.setText(self.format_time(self.time.value))
                    else:
                        self.lbl_time.setText("+"+self.format_time(self.gap.value))
            else:
                self.lbl_name.setBgOpacity(0.58)
                #self.lbl_pit.setBgOpacity(0.58)
                if battles and self.identifier == 0:
                    self.lbl_position.setBgColor(rgb([255, 255, 255], bg = True)).setColor(rgb([192,0,0])).setBgOpacity(0.68)
                    self.lbl_time.setText(self.format_time(self.time.value))
                else:
                    self.lbl_position.setBgColor(rgb([0, 0, 0], bg = True)).setColor(rgb([255,255,255])).setBgOpacity(0.58)
                    if qual_mode == 1:
                        self.lbl_time.setText(self.format_time(self.time.value))
                    else:
                        self.lbl_time.setText("+"+self.format_time(self.gap.value))
        if not self.isLapLabel:
            self.fullName.setValue(ac.getDriverName(self.identifier))
            if self.fullName.hasChanged():
                self.setName()
                
            
    def format_name_tlc(self,name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name=name.strip().upper()
        if len(name) > 2:
            return name[:3]
        return name
    
    def format_last_name(self,name):
        space = name.find(" ")
        if space > 0:
            name = name[space:]
        name=name.strip().upper()
        if len(name) > 9:
            return name[:10]
        return name
        
            
    def format_time(self, ms):        
        s=ms/1000 
        m,s=divmod(s,60) 
        h,m=divmod(m,60) 
        #d,h=divmod(h,24) 
        d=ms % 1000
        if h > 0:
            return "{0}:{1}:{2}.{3}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2), str(int(d)).zfill(3))
        elif m > 0:  
            return "{0}:{1}.{2}".format(int(m), str(int(s)).zfill(2), str(int(d)).zfill(3))
        else:
            return "{0}.{1}".format(int(s), str(int(d)).zfill(3))
     
    def animate(self,sessionTimeLeft):
        if self.final_y != self.y :
            multiplier=3
            if abs(self.final_y - self.y) == 1:
                multiplier=1
            elif abs(self.final_y - self.y) > 38*3:
                multiplier=round(abs(self.final_y - self.y)/38)        
            if self.final_y < self.y :
                self.y-=multiplier   
                #manage z-index with set visible?         
            elif self.final_y > self.y :
                self.y+=multiplier 
            if self.isLapLabel:                
                self.lbl_name.setPos(0, self.y)
            else:
                self.lbl_name.setPos(38, self.y)
            self.lbl_position.setPos(0, self.y)
            self.lbl_time.setPos(148, self.y)
            self.lbl_pit.setPos(218, self.y+2)
            self.lbl_border.setPos(0, self.y+37)
        
        #color
        self.highlight.setValue(self.time_highlight_end != 0 and self.time_highlight_end < sessionTimeLeft)
        
        if self.highlight.hasChanged() :          
            if self.highlight.value:
                self.lbl_time.setColor(rgb([192,0,0]))
            else:
                self.lbl_time.setColor(rgb([255,255,255]))
             
class raceGaps:
    def __init__(self,sector,time):
        self.sector = sector
        self.time = time
        
class ACTower:

    # INITIALIZATION
    def __init__(self): 
        self.drivers = []
        self.stintLabels = []
        self.standings = []
        self.numCars = Value()
        self.session=Value(-1)
        self.lapsCompleted=Value()
        self.currentVehicule=Value(0)
        self.race_show_end = 0
        self.drivers_inited=False
        self.leader_time=0
        self.tick=0  
        self.tick_race_mode=0
        self.pinHack=Value(True)
        self.cursor=Value(False)
        self.max_num_cars = 18
        self.max_num_laps_stint = 8
        self.race_mode = Value(0)
        self.qual_mode = Value(0)
        self.numCarsToFinish=0
        #self.cursor.setValue(False)      
        self.window = Window(name="ACTV Tower", icon=False, width=268, height=114, texture="")
        self.screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
        self.minLapCount=1
        self.curLapCount=Value()
        self.stint_visible_end=0
        self.curDriverLaps=[]
        self.lastLapInvalidated=-1
        self.minlap_stint = 5
        self.iLastTime=Value()
        self.lbl_title_stint = Label(self.window.app,"Current Stint").setSize(218, 34).setPos(0, 118).setFontSize(23).setAlign("center").setBgColor(rgb([12, 12, 12], bg = True)).setBgOpacity(0.8).setVisible(0)
        self.lbl_tire_stint = Label(self.window.app,"").setSize(218, 38).setPos(0, 38).setFontSize(24).setAlign("center").setBgColor(rgb([32, 32, 32], bg = True)).setBgOpacity(0.58).setVisible(0)
        
        track=ac.getTrackName(0)
        config=ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife")>=0 and config.find("touristenfahrten")>=0:
            self.minLapCount=0
        elif track.find("drag1000")>=0 or track.find("drag400")>=0:
            self.minLapCount=0
        self.loadCFG()
        
    # PUBLIC METHODS
    def loadCFG(self):        
        cfg = Config("apps/python/prunn/", "config.ini")
        if cfg.get("SETTINGS", "hide_pins", "int") == 1:
            self.pinHack.setValue(True)
        else:
            self.pinHack.setValue(False)  
        self.max_num_cars = cfg.get("SETTINGS", "num_cars_tower", "int") 
        self.max_num_laps_stint = cfg.get("SETTINGS", "num_laps_stint", "int")
        self.race_mode.setValue(cfg.get("SETTINGS", "race_mode", "int"))
        self.qual_mode.setValue(cfg.get("SETTINGS", "qual_mode", "int")) 
     
    def animate(self,sessionTimeLeft):
        for driver in self.drivers:
            #if driver.final_y != driver.y :
            driver.animate(sessionTimeLeft)
        for lbl in self.stintLabels:
            lbl.animate(sessionTimeLeft)
            
    def format_tire(self,name):
        space = name.find("(")
        if space > 0:
            name = name[:space]
        name=name.strip()
        if len(name) > 16:
            return name[:17]
        return name
    
    def init_drivers(self):
        if self.numCars.value > self.numCars.old:
            #init difference
            for i in range(self.numCars.old,self.numCars.value): 
                self.drivers.append(Driver(self.window.app,i,ac.getDriverName(i),i))                      
            self.drivers_inited=True
    
    def nextDriverIsShown(self,pos):
        if pos > 0:
            for d in self.drivers: 
                if d.position.value == pos+1 and d.isDisplayed:
                    return True
        return False          
        
    
    def update_drivers(self,sim_info):
        if self.numCars.hasChanged():
            self.init_drivers()
        self.minlap_stint = 5
        show_stint_always = False
        if len(self.standings) <= 1:
            self.minlap_stint = 3  
            show_stint_always = True
        elif self.minLapCount == 0:
            self.minlap_stint = 3           
        if self.minLapCount > 0 and (bool(sim_info.graphics.isInPit) or bool(sim_info.physics.pitLimiterOn)):
            self.curDriverLaps=[]
            self.stint_visible_end=0
        #mode_changed = self.qual_mode.hasChanged()
        if (show_stint_always and len(self.curDriverLaps) >= self.minlap_stint) or (self.stint_visible_end != 0 and sim_info.graphics.sessionTimeLeft >= self.stint_visible_end):
            #ac.console(str(show_stint_always) + " and " + str(len(self.curDriverLaps)) + " >= " + str(self.minlap_stint) + " or " + str(self.stint_visible_end != 0) + " and " + str(sim_info.graphics.sessionTimeLeft) + " >= " + str(self.stint_visible_end))
            #if (sim_info.graphics.sessionTimeLeft > 90000 or sim_info.graphics.session == 0) and len(self.curDriverLaps) >= minlap_stint:
            #visible end
            for driver in self.drivers: 
                if driver.identifier == 0:
                    driver.show(0,False)
                    driver.final_y = 0
                    driver.showFullName()
                    p=[i for i, v in enumerate(self.standings) if v[0] == driver.identifier]                        
                    if len(p) > 0:
                        driver.setPosition(p[0] + 1,self.standings[0][1],p[0] + 1,False,self.qual_mode.value)                        
                    #self.stintLabels                    
                    if len(self.curDriverLaps) > len(self.stintLabels):                        
                        for i in range(len(self.stintLabels),len(self.curDriverLaps)): 
                            self.stintLabels.append(Driver(self.window.app,0,"Lap " + str(i+1),i+2,True))
                    i=0
                    j=0
                    self.lbl_title_stint.setVisible(1)
                    self.lbl_tire_stint.setText(self.format_tire(sim_info.graphics.tyreCompound))
                    self.lbl_tire_stint.setVisible(1)
                    #for lbl in self.stintLabels:
                    lapOffset=len(self.curDriverLaps)-self.max_num_laps_stint
                    for l in self.curDriverLaps:
                        if j < lapOffset:
                            self.stintLabels[j].hide()
                        else:
                            #lbl.final_y = 38 * (i+3)
                            self.stintLabels[j].setTimeStint(l.time,l.valid)
                            self.stintLabels[j].setPosition(i+5,1,0,True,self.qual_mode.value) 
                            self.stintLabels[j].show(i+5,False)
                            i+=1    
                        j+=1          
                
                else:
                    driver.hide()
        else:            
            if self.lbl_title_stint.visible != 0:
                self.lbl_title_stint.setVisible(0)
                self.lbl_tire_stint.setVisible(0)
                for l in self.stintLabels:
                    l.hide()
            for driver in self.drivers: 
                c = ac.getCarState(driver.identifier,acsys.CS.BestLap)
                l = ac.getCarState(driver.identifier,acsys.CS.LapCount)
                driver.gas.setValue(ac.getCarState(driver.identifier,acsys.CS.Gas))
                s=ac.getCarState(driver.identifier,acsys.CS.WheelAngularSpeed)
                wheelSpeed=0
                for w in s:
                    wheelSpeed+=w
                driver.wheelSpeed.setValue(wheelSpeed)
                if driver.identifier > 0 and not driver.gas.hasChanged() and not driver.wheelSpeed.hasChanged():
                    #todo last time alive from time
                    #if driver.aliveMissed > 180:
                    if driver.keepAlive - int(sim_info.graphics.sessionTimeLeft) > 2000:
                        driver.isAlive=False 
                    #else:
                    #    driver.aliveMissed += 1                   
                else:
                    #driver.aliveMissed = 0
                    driver.keepAlive=int(sim_info.graphics.sessionTimeLeft)
                    driver.isAlive=True
                p=[i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                checkPos=0
                if len(p) > 0:
                    checkPos=p[0] + 1
                if c > 0 and (l > self.minLapCount or self.nextDriverIsShown(checkPos)) and driver.isAlive and checkPos <= self.max_num_cars:
                    driver.show(self.driver_shown)
                    driver.updatePit()
                    if len(p) > 0 and len(self.standings) > 0 and len(self.standings[0]) > 1:
                        driver.setPosition(p[0] + 1,self.standings[0][1],0,False,self.qual_mode.value) 
                        driver.setTime(c,self.standings[0][1],sim_info.graphics.sessionTimeLeft,self.qual_mode.value)                           
                else:
                    driver.hide() 
                
    def gapToDriver(self,d1,d2,sector):
        t1=0
        t2=0
        found1=False
        found2=False
        if abs(sector - self.getMaxSector(d1)) > 25:
            return 100000
        if abs(sector - self.getMaxSector(d2)) > 25:
            return 100000
        for g in reversed(d1.race_gaps):
            if g.sector==sector:
                t1=g.time
                found1=True
                break
        for g in reversed(d2.race_gaps):
            if g.sector==sector:
                t2=g.time
                found2=True
                break
        if (not found1 or not found2) and sector > 0:
            return self.gapToDriver(d1,d2,sector-1)
        return abs(t1-t2)
        
    def getMaxSector(self,driver):       
        if driver.race_gaps:
            return driver.race_gaps[-1].sector        
        return 0  
    
    def sectorIsValid(self,newSector,driver):
        if newSector*100 < driver.race_current_sector.value:
            return False
        if (newSector*100) % 100 > 88 and len(driver.race_gaps) < 15:
            return False
        if ac.getCarState(driver.identifier,acsys.CS.SpeedKMH) <= 1:
            return False
        if newSector*100 > driver.race_current_sector.value + 25:
            return False
        #other checks
        return True                  
                
    def update_drivers_race(self,sim_info): 
        if self.lbl_title_stint.visible != 0:
            self.lbl_title_stint.setVisible(0)
            self.lbl_tire_stint.setVisible(0)
            for l in self.stintLabels:
                l.hide()
        if self.numCars.hasChanged():
            self.init_drivers()        
        self.driver_shown=0
        cur_driver=0
        cur_sector=0
        best_pos=0
        isInPit = self.currentVehicule.value==0 and (bool(sim_info.graphics.isInPit) or bool(sim_info.physics.pitLimiterOn))
        for driver in self.drivers:
            if driver.isDisplayed:
                self.driver_shown+=1
                p=[i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                if len(p) > 0 and (best_pos == 0 or best_pos > p[0]+1):
                    best_pos=p[0]+1            
            if sim_info.graphics.sessionTimeLeft >= 1800000 or isInPit or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):                               
                driver.race_gaps = []
                self.curDriverLaps=[]
                self.stint_visible_end=0
                if (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0) or sim_info.graphics.sessionTimeLeft >= 1800000:                    
                    driver.finished=False
                    self.numCarsToFinish=0
                    driver.race_standings_sector.setValue(0)
                    driver.race_current_sector.setValue(0)
            else:                    
                bl=ac.getCarState(driver.identifier,acsys.CS.LapCount) + ac.getCarState(driver.identifier,acsys.CS.NormalizedSplinePosition)
                if bl <= sim_info.graphics.numberOfLaps and self.sectorIsValid(bl,driver):
                    driver.race_current_sector.setValue(math.floor(bl*100))
                
            if driver.race_current_sector.hasChanged():
                driver.race_gaps.append(raceGaps(driver.race_current_sector.value, sim_info.graphics.sessionTimeLeft))                
                
            if driver.identifier == self.currentVehicule.value:
                cur_driver=driver
                cur_sector=driver.race_current_sector.value
        driverShown=0
        driverShownMaxGap=0
        maxGap=2500
        needsTLC=True
        if self.lapsCompleted.value >= sim_info.graphics.numberOfLaps:
            needsTLC=False
        #memsize=0
        for driver in self.drivers: 
            #memsize += sys.getsizeof(driver.race_gaps)
            gap = self.gapToDriver(driver,cur_driver,cur_sector) 
            if driver.identifier == 0 or (gap < 2500 and cur_sector - self.getMaxSector(driver) < 15):  
                driverShown+=1
            if driver.identifier == 0 or (gap < 5000 and cur_sector - self.getMaxSector(driver) < 15):  
                driverShownMaxGap+=1 
            driver.optimise(cur_sector) 
        #ac.console("Mem size:" + str(memsize/1024) + " ko")
        if not driverShown > 1:
            driverShown=driverShownMaxGap
            maxGap=5000
        if not driverShown > 1:
            if self.lapsCompleted.hasChanged():  
                self.leader_time = sim_info.graphics.sessionTimeLeft     
                if self.lapsCompleted.value >= sim_info.graphics.numberOfLaps:
                    self.race_show_end = sim_info.graphics.sessionTimeLeft - 360000                    
                else:     
                    self.race_show_end = sim_info.graphics.sessionTimeLeft - 12000
                    
        if self.race_mode.value == 1:
            if not math.isinf(sim_info.graphics.sessionTimeLeft) and int(sim_info.graphics.sessionTimeLeft/100) % 18 == 0 and self.tick_race_mode > 20:
                self.tick_race_mode = 0 
                for driver in self.drivers:                
                    p=[i for i, v in enumerate(self.standings) if v[0] == driver.identifier]
                    driver.gas.setValue(ac.getCarState(driver.identifier,acsys.CS.Gas))
                    s=ac.getCarState(driver.identifier,acsys.CS.WheelAngularSpeed)
                    wheelSpeed=0
                    for w in s:
                        wheelSpeed+=w
                    driver.wheelSpeed.setValue(wheelSpeed)
                    if driver.identifier > 0 and not driver.gas.hasChanged() and not driver.wheelSpeed.hasChanged():                        
                        if not math.isinf(sim_info.graphics.sessionTimeLeft) and driver.keepAlive - int(sim_info.graphics.sessionTimeLeft) > 2000:
                            driver.isAlive=False                                          
                    elif not math.isinf(sim_info.graphics.sessionTimeLeft):
                        driver.keepAlive=int(sim_info.graphics.sessionTimeLeft)
                        driver.x=True
                    # and driver.isAlive               
                    if len(p) > 0  and p[0] < self.max_num_cars:
                        driver.setPosition(p[0] + 1,self.standings[0][1],best_pos-1,True,self.qual_mode.value) 
                        driver.setTimeRaceBattle(gap,cur_driver.identifier) 
                        driver.showFullName()                        
                        driver.show(self.driver_shown,False)
                    else:
                        driver.hide()
            self.tick_race_mode+=1
                
        elif driverShown > 1 and (self.race_show_end > sim_info.graphics.sessionTimeLeft or self.race_show_end == 0):
            self.lapsCompleted.hasChanged()
           
            if not math.isinf(sim_info.graphics.sessionTimeLeft) and int(sim_info.graphics.sessionTimeLeft/100) % 18 == 0 and self.tick > 20:  
                #ac.console("updating gaps" + str(self.tick))
                self.tick = 0                        
                for driver in self.drivers: 
                    gap = self.gapToDriver(driver,cur_driver,cur_sector)
                    #self.lapsCompleted.value > 0 and 
                    if len(cur_driver.race_gaps) > 15 and (driver.identifier == cur_driver.identifier or (gap < maxGap and cur_sector - self.getMaxSector(driver) < 12)):
                        p=[i for i, v in enumerate(self.standings) if v[0] == driver.identifier] 
                        if len(p) > 0:
                            driver.setPosition(p[0] + 1,self.standings[0][1],best_pos-1,True,self.qual_mode.value) 
                            driver.setTimeRaceBattle(gap,cur_driver.identifier) 
                            if p[0] <= best_pos+1:
                                driver.show(0)
                            else:
                                driver.show(self.driver_shown)
                    else:
                        driver.hide()
            self.tick+=1
                    
        elif self.race_show_end != 0 and self.race_show_end < sim_info.graphics.sessionTimeLeft: 
            self.driver_shown=0
            for driver in self.drivers:
                if driver.isDisplayed:
                    self.driver_shown+=1
            for driver in self.drivers: 
                c = ac.getCarState(driver.identifier,acsys.CS.LapCount)
                driver.completedLaps.setValue(c)             
                if c == self.lapsCompleted.value:
                    p=[i for i, v in enumerate(self.standings) if v[0] == driver.identifier] 
                    if len(p) > 0 and driver.completedLaps.hasChanged():
                        driver.setPosition(p[0] + 1,self.standings[0][1],0,False,self.qual_mode.value) 
                        driver.setTimeRace(c,self.leader_time,sim_info.graphics.sessionTimeLeft)  
                    if self.lapsCompleted.value == sim_info.graphics.numberOfLaps:
                        driver.showFullName()                  
                    driver.show(self.driver_shown,needsTLC)
        else:   
            for driver in self.drivers: 
                driver.hide()   
               
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
            self.curDriverLaps=[]
            self.stint_visible_end=0
            for driver in self.drivers:
                driver.hide()
                driver.race_standings_sector.setValue(0)
                driver.race_gaps = []
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
        self.manageWindow()
        self.numCars.setValue(ac.getCarsCount()) 
        sessionTimeLeft=sim_info.graphics.sessionTimeLeft
        self.animate(sessionTimeLeft)
           
        #stint view
        LapCount=ac.getCarState(0,acsys.CS.LapCount)
        self.curLapCount.setValue(LapCount)
        if sim_info.physics.numberOfTyresOut >= 4 :
            self.lastLapInvalidated = LapCount
        if self.curLapCount.hasChanged():
            self.iLastTime.setValue(ac.getCarState(0,acsys.CS.LastLap))
            if self.iLastTime.hasChanged():                
                #self.curDriverLaps.append(Laps(self.curLapCount.value-1, ac.getCarState(0,acsys.CS.LastLap)==sim_info.graphics.iLastTime, sim_info.graphics.iLastTime))  
                self.curDriverLaps.append(Laps(self.curLapCount.value-1, self.lastLapInvalidated!=LapCount-1, sim_info.graphics.iLastTime))  
                if len(self.curDriverLaps) >= self.minlap_stint:
                    self.stint_visible_end = sessionTimeLeft - 30000 
                    if self.stint_visible_end > 0 and self.stint_visible_end < 90000:                        
                        if sessionTimeLeft - 90000 < 5000:
                            self.stint_visible_end=0
                        else:
                            self.stint_visible_end=90000   
            else: 
                self.curLapCount.changed = True 
        
        if sim_info.graphics.status == 2:
            #LIVE             
            if self.session.value < 2  :                
                #Qualify - Practise
                standings = []
                self.driver_shown=0
                for i in range(self.numCars.value): 
                    bl=ac.getCarState(i,acsys.CS.BestLap)
                    l = ac.getCarState(i,acsys.CS.LapCount)
                    if bl > 0 and l > self.minLapCount and self.drivers[i].isAlive:
                        standings.append((i,bl))                        
                        self.driver_shown+=1
                self.standings = sorted(standings, key=lambda student: student[1])                
                self.update_drivers(sim_info)
                               
            elif self.session.value == 2 :               
                #RACE
                completed=0
                standings = []
                standings2 = []
                #new standings
                for driver in self.drivers:
                    bl=ac.getCarState(driver.identifier,acsys.CS.LapCount) + ac.getCarState(driver.identifier,acsys.CS.NormalizedSplinePosition)
                    #bl <= sim_info.graphics.numberOfLaps and
                    if self.sectorIsValid(bl,driver):  
                        if not driver.finished and driver.race_standings_sector.value >= sim_info.graphics.numberOfLaps:
                            driver.race_standings_sector.setValue(sim_info.graphics.numberOfLaps + (self.numCars.value - self.numCarsToFinish)/100)
                            self.numCarsToFinish+=1
                            driver.finished=True
                        elif not driver.finished:                  
                            driver.race_standings_sector.setValue(bl)
                            
                    if driver.race_standings_sector.value > 0:
                        standings.append((driver.identifier,driver.race_standings_sector.value))     
                        
                for i in range(self.numCars.value):  
                    c = ac.getCarState(i,acsys.CS.LapCount)
                    if c > completed:
                        completed=c  
                    #if(ac.isCameraOnBoard(i)):
                    #    self.currentVehicule.setValue(i)  
                    bl=c + ac.getCarState(i,acsys.CS.NormalizedSplinePosition)
                    if bl > 0:
                        standings2.append((i,bl)) 
                
                self.currentVehicule.setValue(ac.getFocusedCar()) 
                self.lapsCompleted.setValue(completed) 
                if len(standings) > 0:       
                    self.standings = sorted(standings, key=lambda student: student[1], reverse=True)
                else:       
                    self.standings = sorted(standings2, key=lambda student: student[1], reverse=True)
                
                #Debug code
                '''
                o=1
                for i,s in self.standings:
                    if o <= 10:
                        ac.console("standings:" + str(o) + "-" + ac.getDriverName(i) + " id:" + str(i) + " sector:" + str(s))
                    o=o+1
                ac.console("---------------------------------") 
                '''
                self.update_drivers_race(sim_info)
                    
        elif sim_info.graphics.status == 1:
            #REPLAY
            test=1
        
    
    