import ac
import acsys
import ctypes

from apps.util.func import rgb, getFontSize
from apps.util.classes import Window, Label, Value, POINT, Colors, Config

class lapTimeStart:
    def __init__(self,lap,time,lastpit):
        self.lap = lap
        self.time = time 
        self.lastpit = lastpit   
         
class ACInfo:

    # INITIALIZATION
    def __init__(self):   
        self.rowHeight=36     
        self.lastLapInPit = 0
        self.lastLapInvalidated = 0
        self.situation = 0
        self.carsCount=0
        self.lbl_timing_height = 0
        self.lbl_position_height = 0
        self.lbl_position_text=Value("")
        self.currentVehicule=Value(-1)
        self.ui_row_height = Value(-1)
        self.cursor=Value(False)
        self.fastestLap=Value(0)
        self.fastestLap2=Value(0)
        self.fastestPos=1
        self.lastLap=0
        self.lastLapStart=10000
        self.sector_delay = 5000
        self.lastTimeInPit=0
        self.visible_end = 0
        self.lastLapTime = 0
        self.nameOffset=0
        self.nameOffsetValue=Value(0)
        self.lapCanBeInvalidated=True
        self.fastestLapBorderActive = False
        self.firstLapStarted=False
        self.colorsByClass=Value(False)
        self.minLapCount=1
        self.sectorCount=-1
        self.lapTimesArray = []
        self.driversLap = []
        track=ac.getTrackName(0)
        config=ac.getTrackConfiguration(0)
        if track.find("ks_nordschleife")>=0 and config.find("touristenfahrten")>=0:
            self.minLapCount=0
            self.lastLapInvalidated = -1
        elif track.find("drag1000")>=0 or track.find("drag400")>=0:
            self.minLapCount=0
            self.lastLapInvalidated = -1
        self.fastestLapSectors = [0,0,0,0,0,0]
        self.session=Value(-1)
        #self.session.setValue()    
        self.window = Window(name="ACTV Info", icon=False, width=332, height=self.rowHeight*2, texture="")
        
        self.lbl_driver_name=Label(self.window.app,"").setSize(284, self.rowHeight).setPos(0, 0).setBgColor(rgb([20, 20, 20], bg = True)).setBgOpacity(0.8).setVisible(0)
        self.lbl_driver_name2=Label(self.window.app,"Loading").setSize(284, self.rowHeight).setPos(14, 0).setFontSize(26).setAlign("left").setVisible(0)
        self.lbl_driver_name_visible=Value()
        self.lbl_driver_name_visible_fin=Value(0)
        self.lbl_driver_name_text=Value("")
        self.lbl_position_visible=Value(0)
        self.lbl_timing_text=Value()
        self.race_fastest_lap=Value(0)
        #self.race_fastest_lap.setValue(0)
        self.race_fastest_lap_driver=Value()
        self.lbl_timing_visible=Value(0)
        self.lbl_timing=Label(self.window.app,"Loading").setSize(284, self.rowHeight).setPos(0, self.rowHeight).setFontSize(26).setAlign("left").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64).setVisible(0)
        self.lbl_split=Label(self.window.app,"Loading").setSize(220, self.rowHeight).setPos(10, self.rowHeight).setFontSize(26).setAlign("right").setVisible(0)
        self.lbl_fastest_split=Label(self.window.app,"Loading").setSize(220, self.rowHeight).setPos(48, self.rowHeight).setFontSize(26).setAlign("right").setVisible(0)
        self.info_position=Label(self.window.app,"0").setSize(self.rowHeight, self.rowHeight).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(Colors.red(bg = True)).setBgOpacity(1).setVisible(0)
        self.info_position_lead=Label(self.window.app,"1").setSize(self.rowHeight, self.rowHeight).setPos(246, self.rowHeight).setFontSize(26).setAlign("center").setBgColor(Colors.red(bg = True)).setBgOpacity(1).setVisible(0)
        car = ac.getCarName(0)        
        self.lbl_border=Label(self.window.app,"").setSize(284, 1).setPos(0, self.rowHeight).setBgColor(Colors.colorFromCar(car,self.colorsByClass.value)).setBgOpacity(0.7).setVisible(0)
        self.loadCFG()
        self.info_position.setAnimationSpeed("o", 0.1)
        self.info_position_lead.setAnimationSpeed("o", 0.1)
        self.lbl_split.setAnimationSpeed("a", 0.1)
        self.lbl_fastest_split.setAnimationSpeed("a", 0.1)
                
        
    # PUBLIC METHODS
    #---------------------------------------------------------------------------------------------------------------------------------------------       
    def loadCFG(self):        
        cfg = Config("apps/python/prunn/", "config.ini") 
        if cfg.get("SETTINGS", "lap_can_be_invalidated", "int") == 1:
            self.lapCanBeInvalidated = True
        else:
            self.lapCanBeInvalidated = False
        if cfg.get("SETTINGS", "car_colors_by", "int") == 1:
            self.colorsByClass.setValue(True)
        else:
            self.colorsByClass.setValue(False)
        self.ui_row_height.setValue(cfg.get("SETTINGS", "ui_row_height", "int")) 
        if self.ui_row_height.hasChanged():
            self.reDrawSize()
        #self.info_position.setBgColor(Colors.theme(bg = True, reload = True))
        
    def reDrawSize(self):
        self.rowHeight=self.ui_row_height.value+2
        fontSize=getFontSize(self.rowHeight)
        self.row2Height=self.ui_row_height.value
        fontSize2=getFontSize(self.row2Height)
        width=self.rowHeight*7
        self.lbl_driver_name.setSize(width, self.rowHeight).setFontSize(fontSize)
        self.lbl_driver_name2.setSize(width, self.rowHeight).setFontSize(fontSize)
        self.lbl_timing.setSize(width, self.row2Height).setPos(0, self.rowHeight).setFontSize(fontSize2)
        self.lbl_split.setSize(self.rowHeight*4.7, self.row2Height).setPos(self.rowHeight, self.rowHeight).setFontSize(fontSize2)
        self.lbl_fastest_split.setSize(self.rowHeight*5.7, self.row2Height).setPos(self.rowHeight, self.rowHeight).setFontSize(fontSize2)
        self.info_position.setSize(self.rowHeight, self.rowHeight).setFontSize(fontSize)
        self.info_position_lead.setSize(self.row2Height, self.row2Height).setPos(width-self.row2Height, self.rowHeight).setFontSize(fontSize2)      
        self.lbl_border.setSize(width, 1).setPos(0, self.rowHeight)
        
            
    def setFont(self,fontName):
        self.lbl_driver_name.setFont(fontName,0,0)
        self.lbl_driver_name2.setFont(fontName,0,0)
        self.lbl_timing.setFont(fontName,0,0)
        self.lbl_split.setFont(fontName,0,0)
        self.lbl_fastest_split.setFont(fontName,0,0)
        self.info_position.setFont(fontName,0,0)
        self.info_position_lead.setFont(fontName,0,0)
           
    def format_name(self,name):        
        space = name.find(" ")
        if space > 0:
            if len(name) > 14 and space+1 < len(name):
                return name[space+1:].upper()
            return name[:space].capitalize() + name[space:].upper()
        if len(name) > 14:
            return name[:15].upper()
        return name.upper()
            
     
            
    def format_tire(self,name):
        space = name.find("(")
        if space > 0:
            name = name[:space]
        name=name.strip()
        if len(name) > 16:
            return name[:17]
        return name   
                                          
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
    
    def getStandingsPosition(self,vehicule):
        #mainly for replay
        standings = []
        for i in range(self.carsCount): 
            bl=ac.getCarState(i,acsys.CS.BestLap)
            if bl > 0  and bool(ac.isConnected(vehicule)):
                standings.append((i,bl))  
        standings = sorted(standings, key=lambda student: student[1]) 
        p=[i for i, v in enumerate(standings) if v[0] == vehicule] 
        if len(p) > 0:
            return p[0]+1
        return 0
        
        
    def animate(self):
        self.lbl_driver_name.animate()
        self.lbl_driver_name2.animate()
        self.lbl_timing.animate()
        self.info_position.animate()
        self.info_position_lead.animate()        
        self.lbl_split.animate()
        self.lbl_fastest_split.animate()
        self.lbl_border.animate()
     
    def resetVisibility(self):  
        self.lbl_driver_name.hide()
        self.lbl_driver_name2.hideText()
        self.lbl_border.hide()
        self.lbl_driver_name_visible_fin.setValue(0)
        self.lbl_timing.hide()
        self.lbl_timing_visible.setValue(0)
        self.lbl_fastest_split.hideText()
        self.lbl_split.hideText()
        self.info_position_lead.hide()
        self.info_position.hide()  
        self.visible_end = 0   
        
    def visibilityQualif(self):
        self.lbl_fastest_split.hideText()
        if self.lbl_driver_name_visible.value == 1 and self.lbl_driver_name.isVisible.value==0:
            self.lbl_driver_name_visible.changed=True
        if self.lbl_timing_visible.value == 1 and self.lbl_timing.isVisible.value==0:
            self.lbl_timing_visible.changed=True
            
        self.lbl_driver_name_visible_fin.setValue(self.lbl_driver_name_visible.value)
        self.nameOffsetValue.setValue(self.nameOffset)
        if self.lbl_driver_name_visible_fin.hasChanged():         
            if self.lbl_driver_name_visible_fin.value == 0:
                self.lbl_driver_name.hide()
                self.lbl_driver_name2.hideText()
                self.lbl_border.hide()
            else:
                self.lbl_driver_name.show()
                self.lbl_driver_name2.showText()
                self.lbl_border.show()
                
        if self.lbl_timing_visible.hasChanged():         
            if self.lbl_timing_visible.value == 0:
                self.lbl_timing.hide()
            else:
                self.lbl_timing.show()
                
        if self.lbl_driver_name_text.hasChanged():
            self.lbl_driver_name2.setText(self.lbl_driver_name_text.value.lstrip())
        if self.nameOffsetValue.hasChanged(): 
            self.lbl_driver_name2.setX(self.nameOffsetValue.value,True)
        if self.lbl_timing_text.hasChanged():
            self.lbl_timing.setText(self.lbl_timing_text.value)
    
    def visibilityRace(self):
        self.nameOffsetValue.setValue(self.nameOffset)
        if self.lbl_driver_name_visible.hasChanged():         
            if self.lbl_driver_name_visible.value == 0:
                self.lbl_driver_name.hide()
                self.lbl_driver_name2.hideText()
                self.lbl_border.hide()
            else:
                self.lbl_driver_name.show()
                self.lbl_driver_name2.showText()
                self.lbl_border.show()
            
        if self.lbl_timing_visible.hasChanged():         
            if self.lbl_timing_visible.value == 0:
                self.lbl_timing.hide()
            else:
                self.lbl_timing.show()
                
        if self.lbl_driver_name_text.hasChanged():
            self.lbl_driver_name2.setText(self.lbl_driver_name_text.value) 
        if self.nameOffsetValue.hasChanged(): 
            self.lbl_driver_name2.setX(self.nameOffsetValue.value,True) 
        if self.lbl_timing_text.hasChanged():
            self.lbl_timing.setText(self.lbl_timing_text.value,hidden=bool(self.lbl_timing_height < 30)) 
            
    def getBestLap(self,lap=False):
        #old bestLap
        return self.fastestLap2.old
        '''
        if self.fastestLap.hasChanged():
            return self.fastestLap.old
        return self.fastestLap.value
        '''
    
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
            self.fastestLapSectors = [0,0,0,0,0,0]               
        if self.cursor.hasChanged() or sessionChanged:
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)  
            else:   
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False)
        
    def onUpdate(self, sim_info, fl):
        self.session.setValue(sim_info.graphics.session)
        self.manageWindow()
        self.animate()
        if self.carsCount==0:
            self.carsCount = ac.getCarsCount()
        sessionTimeLeft=sim_info.graphics.sessionTimeLeft
        sim_info_status=sim_info.graphics.status
        self.currentVehicule.setValue(ac.getFocusedCar())        
        backupLaptime=0
        backupLastLapInPits=0
        if len(self.lapTimesArray) < self.carsCount:
            for x in range(self.carsCount):
                c = ac.getCarState(x,acsys.CS.LapCount)
                self.driversLap.append(Value(c))
                self.lapTimesArray.append(lapTimeStart(c,sessionTimeLeft,0)) 
        else:
            for x in range(self.carsCount):
                c = ac.getCarState(x,acsys.CS.LapCount)
                self.driversLap[x].setValue(c)
                if self.driversLap[x].hasChanged():
                    self.lapTimesArray[x].lap=self.driversLap[x].value
                    self.lapTimesArray[x].time=sessionTimeLeft
                if bool(ac.isCarInPitline(x)) or bool(ac.isCarInPit(x)):
                    self.lapTimesArray[x].lastpit=c
                if x == self.currentVehicule.value:
                    backupLaptime=self.lapTimesArray[x].time-sessionTimeLeft
                    self.lastLapStart = self.lapTimesArray[x].time
                    backupLastLapInPits = self.lapTimesArray[x].lastpit
        
                            
        currentVehiculeChanged=self.currentVehicule.hasChanged()
        if self.colorsByClass.hasChanged() and not self.fastestLapBorderActive:
            car = ac.getCarName(self.currentVehicule.value)        
            self.lbl_border.setBgColor(Colors.colorFromCar(car,self.colorsByClass.value)) 
                    
        if currentVehiculeChanged or (self.fastestLapBorderActive and sessionTimeLeft < self.visible_end-2000):
            self.fastestLapBorderActive = False
            car = ac.getCarName(self.currentVehicule.value)        
            self.lbl_border.setBgColor(Colors.colorFromCar(car,self.colorsByClass.value))           
            
        if sim_info_status == 2:
            #LIVE
            strOffset = "  "
            #self.nameOffset=14
            if self.session.value != 2 :
                #NOT RACE
                #qtime 
                self.fastestLap.setValue(fl)         
                bestlap = ac.getCarState(self.currentVehicule.value,acsys.CS.BestLap)
                isInPit = (bool(ac.isCarInPitline(self.currentVehicule.value)) or bool(ac.isCarInPit(self.currentVehicule.value)))
                LapCount = ac.getCarState(self.currentVehicule.value,acsys.CS.LapCount)
                if self.lastLap != LapCount:
                    self.lastLap = LapCount
                    self.firstLapStarted=False
                    if self.currentVehicule.value==0:
                        self.lastLapStart = sessionTimeLeft
                curLapTime = ac.getCarState(self.currentVehicule.value, acsys.CS.LapTime)
                if curLapTime == 0 and backupLaptime > 0 and self.minLapCount > 0:
                    curLapTime = backupLaptime
                if curLapTime > 0:
                    self.firstLapStarted=True
                #if self.minLapCount == 0 and self.firstLapStarted and ((self.lastLapTime > curLapTime and curLapTime < 1000) or self.lastLapStart==10000):
                #    self.lastLapStart = sessionTimeLeft                  
                self.lastLapTime = curLapTime
                                  
                if isInPit :
                    self.lastLapInPit = LapCount
                    self.lastTimeInPit = sessionTimeLeft
                if self.currentVehicule.value==0 and sim_info.physics.numberOfTyresOut >= 4 and self.lapCanBeInvalidated:
                    self.lastLapInvalidated = LapCount
                if isInPit and self.minLapCount == 0:
                    self.lastLapInvalidated = -1
                if self.sectorCount < 0:
                    self.sectorCount = sim_info.static.sectorCount    
                
                if self.fastestLap.value > 0:
                    for x in range(self.carsCount): 
                        c = ac.getCarState(x,acsys.CS.BestLap)
                        if self.fastestLap2.value == 0 or (c > 0 and c < self.fastestLap2.value):               
                            self.fastestLap2.setValue(c)
                            self.fastestLapSectors = ac.getLastSplits(x)
                else:
                    self.fastestLapSectors = [0,0,0,0,0,0]
                            
                #lapInvalidated = bool(ac.getCarState(0, acsys.CS.LapInvalidated))
                lapInvalidated = bool(self.lastLapInvalidated==LapCount)
                if currentVehiculeChanged or self.lbl_driver_name_text.value=="":
                    self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicule.value)))
                #sector_delay = 5000
                # live or info      
                #ac.console("("+str(self.lastLapInPit)+" < "+str(LapCount)+" or "+str(self.minLapCount)+"==0) and not "+str(lapInvalidated)+" and ("+str(self.lastTimeInPit)+"==0 or "+str(self.lastTimeInPit)+" > "+str(self.lastLapStart)+")")            
                if ((self.lastLapStart < 0 and self.minLapCount > 0) or (self.minLapCount == 0 and lapInvalidated)) and self.session.value != 0:                    
                    self.lbl_driver_name_visible.setValue(0)
                    self.lbl_timing_visible.setValue(0)  
                    self.lbl_split.hideText()  
                    self.info_position.hide()
                    self.info_position_lead.hide()          
                elif (self.lastLapInPit < LapCount or self.minLapCount==0) and not lapInvalidated and (self.lastTimeInPit==0 or self.lastTimeInPit > self.lastLapStart or self.minLapCount==0) :
                    
                    if self.currentVehicule.value == 0:
                        sector = sim_info.graphics.currentSectorIndex
                    else:
                        sector = self.getSector()
                    
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_timing_visible.setValue(1)  
                    
                    #lapTime = ac.getCarState(self.currentVehicule.value, acsys.CS.LapTime)
                    if self.currentVehicule.value == 0:
                        lastLap = sim_info.graphics.iLastTime
                    else: 
                        lastLap=0                       
                        lastSplits = ac.getLastSplits(self.currentVehicule.value)
                        for c in lastSplits:
                            lastLap+=c
                        if lastLap==0:
                            lastLap=ac.getCarState(self.currentVehicule.value, acsys.CS.LastLap)
                            
                    
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
                    if i < self.sectorCount:
                        fastestSplit_fin+=self.fastestLapSectors[i]
                         
                    #Situation
                    for s in range(0,self.sectorCount):                    
                        if self.fastestLap.value > 0 and curLapTime > fastestSplit_fin - self.sector_delay:
                            #LAST_SECONDS_OF_SECTOR_X, sector == s and
                            self.info_position.hide() 
                            self.nameOffset=self.rowHeight*14/36 #14
                            if self.sectorCount-1 == sector:
                                #LAST_SECONDS_OF_SECTOR_LAP,
                                self.lbl_split.setText(self.time_splitting(self.fastestLap.value,"yes")).setColor(Colors.white()).showText()
                                self.info_position_lead.show() 
                                
                                showSplit=True
                            elif fastestSplit_fin > 0:
                                self.lbl_split.setText(self.time_splitting(fastestSplit_fin,"yes")).setColor(Colors.white()).showText()
                                self.info_position_lead.show() 
                                showSplit=True
                            break
                        if sector == s + 1 and s + 1 <= self.sectorCount and curLapTime - timeSplit <= self.sector_delay and fastestSplit > 0 :
                            #SECTOR_X_FINISHED_BEGIN_SECTOR_Y    
                            self.nameOffset=self.rowHeight*14/36 #14            
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(timeSplit,"yes")) 
                            if fastestSplit < timeSplit:
                                self.lbl_split.setText("+"+self.time_splitting(timeSplit-fastestSplit,"yes")).setColor(Colors.yellow()).showText()
                            else:
                                self.lbl_split.setText("-"+self.time_splitting(fastestSplit-timeSplit,"yes")).setColor(Colors.green()).showText()
                            self.info_position_lead.show() 
                            self.info_position.hide()
                            traite=True
                            break
                    
                    if not traite:
                        if self.sectorCount-1 == sector and self.fastestLap.value > 0 and curLapTime > self.fastestLap.value - self.sector_delay:
                            #LAST_SECONDS_OF_SECTOR_LAP,
                            self.nameOffset=self.rowHeight*14/36 #14
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(curLapTime)) 
                            self.info_position.hide()
                            #self.lbl_split.setText(self.time_splitting(self.fastestLap,"yes") + strOffset).setVisible(1)
                        elif self.lastLapInvalidated!=LapCount-1 and ((self.lastLapInPit!=LapCount-1 and sector == 0) or (self.minLapCount==0)) and curLapTime <= self.sector_delay and lastLap > 0:
                            #LAP_FINISHED_BEGIN_NEW_LAP,                       
                            pos = ac.getCarLeaderboardPosition(self.currentVehicule.value)
                            if pos == -1:
                                pos = self.getStandingsPosition(self.currentVehicule.value)                                
                
                            if pos > 1:
                                self.info_position.setColor(Colors.white()).setBgColor(Colors.grey(bg = True)).setBgOpacity(0.8)
                            else:
                                self.info_position.setColor(Colors.white()).setBgColor(Colors.red(bg = True)).setBgOpacity(0.8)
                            self.info_position.setText(str(pos))
                            self.info_position.show()
                            
                            self.nameOffset=self.rowHeight*49/36 #49
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(lastLap,"yes")) 
                            if self.fastestLap.value < lastLap:
                                self.lbl_split.setText("+"+self.time_splitting(lastLap-self.fastestLap.value,"yes")).setColor(Colors.yellow()).showText()
                            else:                            
                                self.lbl_split.setText("-"+self.time_splitting(self.getBestLap()-lastLap,"yes")).setColor(Colors.green()).showText()
                            self.info_position_lead.show() 
                            
                        else:
                            #OTHER
                            self.nameOffset=self.rowHeight*14/36 #14
                            self.lbl_timing_text.setValue(strOffset + self.time_splitting(curLapTime))  
                            self.info_position.hide()
                            if not showSplit:
                                self.lbl_split.hideText()
                                self.info_position_lead.hide()
                    self.fastestLap.changed=False
                else :                    
                    self.info_position_lead.hide()                     
                    normalizedSplinePosition = ac.getCarState(self.currentVehicule.value,acsys.CS.NormalizedSplinePosition)
                    if normalizedSplinePosition <= 0.001:
                        normalizedSplinePosition=1
                    if sessionTimeLeft > 0 and self.minLapCount==1 and normalizedSplinePosition > 0.95 and not isInPit :          
                        self.lbl_driver_name_visible.setValue(1)
                        self.nameOffset=self.rowHeight*14/36 #14
                        self.lbl_timing_visible.setValue(1)  
                        self.lbl_split.hideText()  
                        self.info_position.hide()
                        self.lbl_timing_text.setValue(strOffset + "0.0") 
                        
                    elif lapInvalidated and self.lastLapInPit < LapCount and self.minLapCount > 0 :
                        self.lbl_driver_name_visible.setValue(0)
                        self.lbl_timing_visible.setValue(0)  
                        self.lbl_split.hideText()  
                        self.info_position.hide()  
                    elif bestlap > 0 :             
                        self.lbl_driver_name_visible.setValue(1)
                        self.lbl_timing_visible.setValue(1)  
                         
                        if self.fastestLap.value < bestlap:
                            self.lbl_split.setText("+"+self.time_splitting(bestlap-self.fastestLap.value,"yes")).setColor(Colors.yellow()).showText()                           
                        else:                            
                            self.lbl_split.hideText()
                        
                        self.lbl_timing_text.setValue(strOffset + self.time_splitting(bestlap,"yes")) 
                                            
                        self.nameOffset=self.rowHeight*49/36 #49
                        #pos = sim_info.graphics.position
                        pos = ac.getCarLeaderboardPosition(self.currentVehicule.value)
                        if pos == -1:
                            pos = self.getStandingsPosition(self.currentVehicule.value) 
                        if pos > 1:
                            self.info_position.setColor(Colors.white()).setBgColor(Colors.grey(bg = True)).setBgOpacity(1)
                        else:
                            self.info_position.setColor(Colors.white()).setBgColor(Colors.red(bg = True)).setBgOpacity(1)
                        self.info_position.setText(str(pos)).show()   
                        self.lbl_position_text.setValue(str(pos))                
                            
                    elif isInPit :     
                        self.lbl_driver_name_visible.setValue(0)
                        self.lbl_timing_visible.setValue(0)  
                        self.lbl_split.hideText()  
                        self.info_position.hide()
                    else :
                        self.nameOffset=self.rowHeight*14/36 #14
                        self.lbl_driver_name_visible.setValue(1)
                        self.lbl_timing_visible.setValue(1)
                        if self.currentVehicule.value==0:
                            self.lbl_timing_text.setValue(strOffset + self.format_tire(sim_info.graphics.tyreCompound))
                        else:
                            self.lbl_timing_text.setValue(strOffset + "Out Lap")
                        self.lbl_split.hideText()
                        self.info_position.hide() 
                     
                if curLapTime <= self.sector_delay and ac.getCarState(self.currentVehicule.value, acsys.CS.LastLap) > 0 and backupLastLapInPits + 1 < ac.getCarState(x,acsys.CS.LapCount) and sessionTimeLeft < 0:
                    self.nameOffset=self.rowHeight*49/36 #49
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_timing_visible.setValue(1)
                    self.lbl_split.showText()
                    self.info_position.show() 
                    #time vis
                self.visibilityQualif()
                    
            else:
                ################ Race ################
                self.info_position_lead.hide() 
                self.lbl_split.hideText()
                #fastest lap
                completed=0
                for x in range(self.carsCount): 
                    c = ac.getCarState(x,acsys.CS.LapCount)
                    if c > completed:
                        completed=c
                if completed <=1:
                    self.race_fastest_lap.setValue(0)
                else:
                    for i in range(self.carsCount): 
                        bl=ac.getCarState(i,acsys.CS.BestLap)
                        l = ac.getCarState(i,acsys.CS.LapCount)
                        if bl > 0 and l > self.minLapCount and (self.race_fastest_lap.value == 0 or bl < self.race_fastest_lap.value):
                            self.race_fastest_lap.setValue(bl)
                            self.race_fastest_lap_driver.setValue(i)
                        
                if self.race_fastest_lap.hasChanged() and self.race_fastest_lap.value > 0:
                    self.fastestLapBorderActive = True
                    car = ac.getCarName(self.race_fastest_lap_driver.value)        
                    self.lbl_border.setBgColor(Colors.colorFromCar(car,self.colorsByClass.value))            
                    self.visible_end = sessionTimeLeft - 8000
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.race_fastest_lap_driver.value)))
                    self.nameOffset=self.rowHeight*14/36 #14
                    self.lbl_timing_text.setValue(strOffset + "Fastest Lap")
                    self.lbl_timing_visible.setValue(1)
                    self.info_position.hide() 
                    self.lbl_fastest_split.setText(self.time_splitting(self.race_fastest_lap.value,"yes")).showText()
                    
                elif currentVehiculeChanged:  
                    #driver info                  
                    self.visible_end = sessionTimeLeft - 8000
                    self.lbl_driver_name_visible.setValue(1)
                    self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicule.value)))
                    self.nameOffset=self.rowHeight*49/36 #49
                    #pos = ac.getCarLeaderboardPosition(self.currentVehicule.value)
                    pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicule.value) + 1
                    if pos > 1:
                        self.info_position.setColor(Colors.white()).setBgColor(Colors.grey(bg = True)).setBgOpacity(1)
                    else:
                        self.info_position.setColor(Colors.white()).setBgColor(Colors.red(bg = True)).setBgOpacity(1)
                    self.info_position.setText(str(pos)).show() 
                    self.lbl_timing_visible.setValue(0)
                    self.lbl_fastest_split.hideText()
                elif self.visible_end == 0 or sessionTimeLeft < self.visible_end or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                    self.lbl_driver_name_visible.setValue(0)
                    self.info_position.hide()
                    self.lbl_timing_visible.setValue(0)
                    self.lbl_fastest_split.hideText()
                    
                self.visibilityRace()
                    
        elif sim_info_status == 1 and self.session.value != 2:
            #Replay Qualif
            strOffset = "  "
            showSplit=False
            LapCount = ac.getCarState(self.currentVehicule.value,acsys.CS.LapCount)
            curLapTime = ac.getCarState(self.currentVehicule.value, acsys.CS.LapTime)
            isInPit = (bool(ac.isCarInPitline(self.currentVehicule.value)) or bool(ac.isCarInPit(self.currentVehicule.value)))
            if currentVehiculeChanged or self.lbl_driver_name_text.value=="":
                self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicule.value)))
            if isInPit:
                self.lbl_driver_name_visible.setValue(0)
                self.lbl_timing_visible.setValue(0)  
                self.lbl_split.hideText()  
                self.info_position.hide()
            elif curLapTime <= self.sector_delay and LapCount > 1:
                #show last lap
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_timing_visible.setValue(1)
                if self.currentVehicule.value == 0:
                    lastLap = sim_info.graphics.iLastTime
                else: 
                    lastLap=0                       
                    lastSplits = ac.getLastSplits(self.currentVehicule.value)
                    for c in lastSplits:
                        lastLap+=c
                    if lastLap==0:
                        lastLap=ac.getCarState(self.currentVehicule.value, acsys.CS.LastLap)
                pos = ac.getCarLeaderboardPosition(self.currentVehicule.value)
                if pos == -1:
                    pos = self.getStandingsPosition(self.currentVehicule.value)                                
    
                if pos > 1:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.grey(bg = True)).setBgOpacity(0.8)
                else:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.red(bg = True)).setBgOpacity(0.8)
                self.info_position.setText(str(pos))
                self.info_position.show()
                self.nameOffset=self.rowHeight*49/36 #49
                self.lbl_timing_text.setValue(strOffset + self.time_splitting(lastLap,"yes")) 
                if self.fastestLap.value < lastLap:
                    self.lbl_split.setText("+"+self.time_splitting(lastLap-self.fastestLap.value,"yes")).setColor(Colors.yellow()).showText()
                else:                            
                    self.lbl_split.setText("-"+self.time_splitting(self.fastestLap.old-lastLap,"yes")).setColor(Colors.green()).showText()
                self.info_position_lead.show()
                self.fastestLap.changed=False
            elif LapCount > self.minLapCount:
                #showTiming
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_timing_visible.setValue(1)
                self.info_position_lead.hide() 
                self.nameOffset=self.rowHeight*14/36 #14
                self.lbl_timing_text.setValue(strOffset + self.time_splitting(curLapTime))  
                self.info_position.hide()
                if not showSplit:
                    self.lbl_split.hideText()
                    self.info_position_lead.hide()
            else:
                #showTireInfo
                self.info_position_lead.hide() 
                self.nameOffset=self.rowHeight*14/36 #14
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_timing_visible.setValue(1)
                if self.currentVehicule.value==0:
                    self.lbl_timing_text.setValue(strOffset + self.format_tire(sim_info.graphics.tyreCompound))
                else:
                    self.lbl_timing_text.setValue(strOffset + "Out Lap")
                self.lbl_split.hideText()
                self.info_position.hide()            
            
            self.visibilityQualif()
                
                
            
        elif sim_info_status == 1 and self.session.value == 2:
            #Replay Race
            todo=1
            '''
            if currentVehiculeChanged:
                self.visible_end = sessionTimeLeft - 8000
                self.lbl_driver_name_visible.setValue(1)
                self.lbl_driver_name_text.setValue(self.format_name(ac.getDriverName(self.currentVehicule.value)))
                self.nameOffset=self.rowHeight*49/36 #49
                pos = ac.getCarRealTimeLeaderboardPosition(self.currentVehicule.value) + 1
                if pos > 1:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.grey(bg = True)).setBgOpacity(1)
                else:
                    self.info_position.setColor(Colors.white()).setBgColor(Colors.red(bg = True)).setBgOpacity(1)
                self.info_position.setText(str(pos)).show() 
                self.lbl_timing_visible.setValue(0)
                self.lbl_fastest_split.hideText()
                
                if self.lbl_driver_name_visible.hasChanged():         
                    if self.lbl_driver_name_visible.value == 0:
                        self.lbl_driver_name.hide()
                        self.lbl_border.hide()
                    else:
                        self.lbl_driver_name.show()
                        self.lbl_border.show()
                    
                if self.lbl_timing_visible.hasChanged():         
                    if self.lbl_timing_visible.value == 0:
                        self.lbl_timing.hide()
                    else:
                        self.lbl_timing.show()
                        
                if self.lbl_driver_name_text.hasChanged():
                    self.lbl_driver_name.setText(self.lbl_driver_name_text.value)  
                if self.lbl_timing_text.hasChanged():
                    self.lbl_timing.setText(self.lbl_timing_text.value,hidden=bool(self.lbl_timing_height < 30)) 
            '''
        else:
            #REPLAY
            self.resetVisibility()
        
    
    