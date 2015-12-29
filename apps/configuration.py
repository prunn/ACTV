import ac
import acsys

from apps.util.classes import Window, Label, Value, Config

class Configuration:
    configChanged=False
    pinHack=1
    lapCanBeInvalidated=1
    max_num_cars = 18 
    max_num_laps_stint = 8
    # INITIALIZATION
    def __init__(self):
        self.session=Value(-1)
        #self.session.setValue(-1)
        self.window = Window(name="ACTV Config", icon=True, width=260, height=380, texture="").setBgOpacity(0.6)    
               
        self.spin_num_cars = ac.addSpinner(self.window.app, "Number cars tower")
        ac.setRange(self.spin_num_cars, 2,28)
        ac.setPosition(self.spin_num_cars,30,60)
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.addOnValueChangeListener(self.spin_num_cars, self.onSpinNumCarsChanged)       
        
        
        self.spin_num_laps = ac.addSpinner(self.window.app, "Number laps stint mode")
        ac.setRange(self.spin_num_laps, 2,28)
        ac.setPosition(self.spin_num_laps,30,140)
        ac.setValue(self.spin_num_laps, self.__class__.max_num_laps_stint)
        ac.addOnValueChangeListener(self.spin_num_laps, self.onSpinNumLapsChanged)        
        
        
        self.chk_pins = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_pins,30,200)  
        ac.addOnCheckBoxChanged(self.chk_pins, self.onCheckPinChanged)
        self.lbl_title_pins = Label(self.window.app,"Hide pins").setSize(200, 26).setPos(70, 202).setFontSize(16).setAlign("left").setVisible(1)        
        
        
        self.chk_invalidated = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_invalidated,30,250)
        ac.addOnCheckBoxChanged(self.chk_invalidated, self.onCheckInvalidatedChanged)
        self.lbl_title_invalidated = Label(self.window.app,"Lap can be invalidated").setSize(200, 26).setPos(70, 252).setFontSize(16).setAlign("left").setVisible(1)
        
        self.cfg = Config("apps/python/prunn/cfg/", "config.ini")
        self.cfg_loaded = False
        self.loadCFG()
        
    def loadCFG(self):  
        #if no cfg create cfg
        self.pinHack = self.cfg.get("SETTINGS", "hide_pins", "int") 
        self.lapCanBeInvalidated = self.cfg.get("SETTINGS", "lap_can_be_invalidated", "int") 
        self.max_num_cars = self.cfg.get("SETTINGS", "num_cars_tower", "int") 
        self.max_num_laps_stint = self.cfg.get("SETTINGS", "num_laps_stint", "int") 
            
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.setValue(self.spin_num_laps, self.__class__.max_num_laps_stint)
        ac.setValue(self.chk_pins,self.__class__.pinHack)
        ac.setValue(self.chk_invalidated,self.__class__.lapCanBeInvalidated)
        self.cfg_loaded = True
        
    def saveCFG(self):      
        self.cfg.set("SETTINGS", "hide_pins", self.__class__.pinHack)   
        self.cfg.set("SETTINGS", "lap_can_be_invalidated", self.__class__.lapCanBeInvalidated)   
        self.cfg.set("SETTINGS", "num_cars_tower", self.__class__.max_num_cars)    
        self.cfg.set("SETTINGS", "num_laps_stint", self.__class__.max_num_laps_stint) 
                    
    def onUpdate(self, deltaT, sim_info):
        self.window.setBgOpacity(0.6).border(0)
        self.session.setValue(sim_info.graphics.session)
        if self.__class__.configChanged and self.cfg_loaded:
            self.saveCFG()
            self.__class__.configChanged = False
            return True
        elif self.__class__.configChanged and not self.cfg_loaded:
            self.__class__.configChanged = False
        return False
        
    @staticmethod
    def onCheckPinChanged(name, state):  
        #ac.console("chk changed " + str(name) + " " + str(state))
        Configuration.pinHack = state
        Configuration.configChanged=True
        
    @staticmethod
    def onCheckInvalidatedChanged(name, state):
        #ac.console("chk changed " + str(name) + " " + str(state)) 
        Configuration.lapCanBeInvalidated = state
        Configuration.configChanged=True
        
    @staticmethod
    def onSpinNumCarsChanged(value):
        #ac.console("onSpinChanged " + str(value)) 
        Configuration.max_num_cars = value
        Configuration.configChanged=True
        
    @staticmethod
    def onSpinNumLapsChanged(value):
        #ac.console("onSpinChanged " + str(value))  
        Configuration.max_num_laps_stint = value
        Configuration.configChanged=True
        
        
       
    
    