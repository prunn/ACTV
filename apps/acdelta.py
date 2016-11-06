import ac
import acsys
import ctypes
import os,threading,json,math
import gzip
import time
from apps.util.func import rgb, getFontSize
from apps.util.classes import Window, Label, Value, POINT, Colors, Config, Log, Button, raceGaps

        
class ACDelta:
    resetPressed=False
    # INITIALIZATION
    def __init__(self): 
        self.window = Window(name="ACTV Delta", icon=False, width=268, height=114, texture="")
        self.cursor=Value(False)
        self.session=Value(-1)
        self.performance=Value(0)
        self.spline=Value(0)
        self.laptime=Value(0)
        self.TimeLeftUpdate=Value(0)
        self.referenceLap=[]
        self.referenceLapTime=Value(0)
        self.lastLapTime=Value(0)
        self.lapCount=0
        self.lastLapIsValid=True
        self.currentLap=[]
        self.lastLap=[]
        self.deltaLoaded=False
        self.thread_save=False
        self.highlight_end = 0
        #self.lbl_delta = Label(self.window.app,"+0.000").setSize(128, 36).setPos(0, 0).setFontSize(24).setAlign("right").setBgColor(rgb([12, 12, 12], bg = True)).setBgOpacity(0.8).setVisible(1)
        #self.lbl_lap = Label(self.window.app,"0.000").setSize(128, 32).setPos(0, 36).setFontSize(18).setAlign("center").setBgColor(rgb([12, 12, 12], bg = True)).setBgOpacity(0.8).setVisible(1)
        self.lbl_delta = Label(self.window.app,"+0.000").setSize(114, 36).setPos(0, 0).setFontSize(26).setAlign("right").setVisible(1)
        self.lbl_lap = Label(self.window.app,"0.000").setSize(114, 32).setPos(0, 36).setFontSize(18).setAlign("center").setVisible(1)
        self.btn_reset = Button(self.window.app,self.onResetPress).setPos(32, 68).setSize(60, 20).setText("Reset").setAlign("center").setBgColor(rgb([255, 12, 12], bg = True)).setVisible(0)
        fontName="Segoe UI"
        if ac.initFont(0,fontName,0,0) > 0:
            self.lbl_delta.setFont(fontName,0,1)
            
    
    @staticmethod
    def onResetPress(a,b):
        ACDelta.resetPressed=True
                
    # PUBLIC METHODS
    def getDeltaFilePath(self):        
        trackFilePath = os.path.join(os.path.expanduser("~"), "Documents","Assetto Corsa","plugins","actv_deltas","default")
        if not os.path.exists(trackFilePath):
            os.makedirs(trackFilePath)
        trackFilePath += "/" + ac.getTrackName(0)       
        if ac.getTrackConfiguration(0) != "":
            trackFilePath += "_" + ac.getTrackConfiguration(0)
        trackFilePath += "_" + ac.getCarName(0) + ".delta" 
        
        return trackFilePath
    
    def saveDelta(self):  
        #ac.log(str(time.time())+" saveDelta start:")  
        referenceLap=list(self.referenceLap)
        #referenceLap=self.referenceLap 
        referenceLapTime=self.referenceLapTime.value
        if len(referenceLap) > 0:
            try:
                times=[]
                for l in referenceLap:
                    times.append((l.sector,l.time))         
                data_file = {
                            'lap': referenceLapTime, 
                            'times': times, 
                            'track': ac.getTrackName(0), 
                            'config': ac.getTrackConfiguration(0), 
                            'car': ac.getCarName(0), 
                            'user': ac.getDriverName(0)
                            }                  
                file = self.getDeltaFilePath()
                with gzip.open(file, 'wt') as outfile:
                    json.dump(data_file, outfile)
            except:
                Log.w("Error tower")  
        
            #ac.console("lap saved:" + str(referenceLapTime) + ","+str(len(referenceLap)))
            #ac.log(str(time.time())+" lap saved:" + str(referenceLapTime) + ","+str(len(referenceLap)))
        
    def loadDelta(self):
        self.deltaLoaded=True
        file = self.getDeltaFilePath()
        if os.path.exists(file):
            try:
                with gzip.open(file, 'rt') as data_file:   
                    data = json.load(data_file)
                    self.referenceLapTime.setValue(data["lap"])                    
                    times=data["times"]
                    self.referenceLap=[]
                    for t in times:
                        self.referenceLap.append(raceGaps(t[0],t[1]))                    
                    ac.console("AC Delta: File loaded")
            except:
                Log.w("Error tower")  
     
    def getPerformanceGap(self,sector,time):
        if len(self.referenceLap) < 10:
            return round(ac.getCarState(0,acsys.CS.PerformanceMeter)*1000)
        #if self.referenceLap[sector*100] 
        if sector > 0.5:
            referenceLap=reversed(self.referenceLap) 
        else:
            referenceLap=self.referenceLap 
        for l in referenceLap:
            if l.sector == sector:
                return time - l.time
        #do not update
        return False     
    
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
            self.resetData()
        if self.cursor.hasChanged() or sessionChanged:
            if self.cursor.value:
                self.window.setBgOpacity(0.4).border(0)
                self.window.showTitle(True)
                self.btn_reset.setVisible(1)
            else:
                self.window.setBgOpacity(0).border(0)
                self.window.showTitle(False) 
                self.btn_reset.setVisible(0)
                
    def resetData(self):
        self.currentLap=[]
        self.lastLapIsValid=True
        self.lapCount=0  
        self.highlight_end = 0
                    
    def onUpdate(self, sim_info):
        if not self.deltaLoaded:
            thread_load = threading.Thread(target=self.loadDelta)  
            thread_load.daemon = True      
            thread_load.start() 
        if self.__class__.resetPressed:
            self.referenceLapTime.setValue(0)
            self.referenceLap=[]
            self.__class__.resetPressed=False
        self.session.setValue(sim_info.graphics.session)
        self.manageWindow()
        self.lbl_delta.animate()
        self.lbl_lap.animate()       
        sim_info_status=sim_info.graphics.status
        if sim_info_status == 2: #LIVE
            sessionTimeLeft=sim_info.graphics.sessionTimeLeft
            if math.isinf(sessionTimeLeft) :# or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
                self.resetData() 
            elif self.session.value == 2 and sessionTimeLeft > 1800000:
                self.resetData()
            elif bool(ac.isCarInPitline(0)) or bool(ac.isCarInPit(0)):
                self.resetData() 
            self.spline.setValue(round(ac.getCarState(0,acsys.CS.NormalizedSplinePosition),3))
            
            if self.lastLapIsValid and sim_info.physics.numberOfTyresOut >= 4:
                self.lastLapIsValid=False
            
            if self.spline.hasChanged():
                self.laptime.setValue(round(ac.getCarState(0, acsys.CS.LapTime),3))
                self.lastLapTime.setValue(ac.getCarState(0, acsys.CS.LastLap))
                gap=self.getPerformanceGap(self.spline.value,self.laptime.value)
                if gap != False:
                    self.performance.setValue(gap)
                #new lap
                if self.lastLapTime.hasChanged():                        
                    #ac.console("newlap----")(self.laptime.old > self.laptime.value) or  
                    #ac.console("lastLap=currentLap---waiting " + str(self.laptime.old) + ":" + str(self.laptime.value))
                    #ac.log(str(time.time()) +" lastLap=currentLap---waiting " + str(self.laptime.old) + ":" + str(self.laptime.value))
                    self.lastLap=list(self.currentLap)
                    #self.lastLap=self.currentLap 
                    self.currentLap=[]
                    if (self.referenceLapTime.value == 0 or self.lastLapTime.value < self.referenceLapTime.value) and self.lastLapIsValid and self.lastLapTime.value > 0 and self.lapCount < ac.getCarState(0, acsys.CS.LapCount):  
                        self.referenceLapTime.setValue(self.lastLapTime.value)
                        self.referenceLap=list(self.lastLap)
                        #self.referenceLap=self.lastLap
                        #ac.log(str(time.time()) +" referenceLap=lastlap --- lets save")
                        #ac.console("referenceLap=lastlap --- lets save")
                        thread_save = threading.Thread(target=self.saveDelta)  
                        thread_save.daemon = True
                        thread_save.start()
                        #make it green for 5 sec
                        self.highlight_end = sim_info.graphics.sessionTimeLeft - 6000
                        self.lbl_lap.setColor(Colors.green(),True)
                    #else:
                    #    ac.log(str(time.time()) +" dismissed")
                    self.lapCount=ac.getCarState(0, acsys.CS.LapCount)
                    self.lastLapIsValid=True
                    
                self.currentLap.append(raceGaps(self.spline.value, self.laptime.value))
                #ac.console("--currentLap : " + str(len(self.currentLap)) + " --lastLap : " + str(len(self.lastLap)) + " --referenceLap : " + str(len(self.referenceLap)))
            
            #update graphics  
            if not math.isinf(sessionTimeLeft):
                self.TimeLeftUpdate.setValue(int(sessionTimeLeft/500))
            if self.TimeLeftUpdate.hasChanged():    
                if self.performance.hasChanged():
                    time_prefix = ""
                    color = Colors.white()
                    if self.performance.value > 0:
                        time_prefix = "+"
                        if self.lastLapIsValid:
                            color = Colors.yellow()
                        else:
                            color = Colors.red()
                    elif self.performance.value < 0:
                        time_prefix = "-"
                        if self.lastLapIsValid:
                            color = Colors.green()
                        else:
                            color = Colors.orange()
                    else:
                        if not self.lastLapIsValid:
                            color = Colors.red()
                    self.lbl_delta.setText(time_prefix + self.time_splitting(abs(self.performance.value),"yes")).setColor(color,True)
                        
            if self.referenceLapTime.hasChanged():
                self.lbl_lap.setText(self.time_splitting(self.referenceLapTime.value,"yes"))
            if self.highlight_end == 0 or sessionTimeLeft < self.highlight_end:
                self.lbl_lap.setColor(Colors.white(),True)
    
    