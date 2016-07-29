import ac
import acsys
import apps.util.win32con, ctypes, ctypes.wintypes
import threading
from apps.util.classes import Window, Label, Value, Config, Log

class Configuration:
    configChanged=False
    race_mode=0
    qual_mode=0
    lapCanBeInvalidated=1
    max_num_cars=18 
    max_num_laps_stint=8
    ui_row_height=36
    # INITIALIZATION
    def __init__(self):
        self.session=Value(-1)
        self.listen_active = True
        self.window = Window(name="ACTV Config", icon=True, width=251, height=480, texture="").setBgOpacity(0.6)    
               
        y=60
        self.spin_race_mode = ac.addSpinner(self.window.app, "Race tower mode :")
        ac.setRange(self.spin_race_mode, 0,2)
        ac.setPosition(self.spin_race_mode,20,y)
        ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        ac.addOnValueChangeListener(self.spin_race_mode, self.onSpinRaceModeChanged) 
        self.lbl_race_mode = Label(self.window.app,"Auto").setSize(120, 26).setPos(186, y-28).setFontSize(12).setAlign("left").setVisible(1) 
        
        y+=80
        self.spin_qual_mode = ac.addSpinner(self.window.app, "Qual tower mode :")
        ac.setRange(self.spin_qual_mode, 0,1)
        ac.setPosition(self.spin_qual_mode,20,y)
        ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        ac.addOnValueChangeListener(self.spin_qual_mode, self.onSpinQualModeChanged) 
        self.lbl_qual_mode = Label(self.window.app,"Gaps").setSize(120, 26).setPos(186, y-28).setFontSize(12).setAlign("left").setVisible(1)       
          
        y+=80  
        self.spin_num_cars = ac.addSpinner(self.window.app, "Number cars tower")
        ac.setRange(self.spin_num_cars, 2,28)
        ac.setPosition(self.spin_num_cars,20,y)
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.addOnValueChangeListener(self.spin_num_cars, self.onSpinNumCarsChanged)          
        
        y+=80
        self.spin_num_laps = ac.addSpinner(self.window.app, "Number laps stint mode")
        ac.setRange(self.spin_num_laps, 2,28)
        ac.setPosition(self.spin_num_laps,20,y)
        ac.setValue(self.spin_num_laps, self.__class__.max_num_laps_stint)
        ac.addOnValueChangeListener(self.spin_num_laps, self.onSpinNumLapsChanged)   
        
        y+=80 
        self.spin_row_height = ac.addSpinner(self.window.app, "Row height")
        ac.setRange(self.spin_row_height, 20,48)
        ac.setPosition(self.spin_row_height,20,y)
        ac.setValue(self.spin_row_height, self.__class__.ui_row_height)
        ac.addOnValueChangeListener(self.spin_row_height, self.onSpinRowHeightChanged)       
        
        y+=60
        self.chk_invalidated = ac.addCheckBox(self.window.app, "")
        ac.setPosition(self.chk_invalidated,20,y)
        ac.addOnCheckBoxChanged(self.chk_invalidated, self.onCheckInvalidatedChanged)
        self.lbl_title_invalidated = Label(self.window.app,"Lap can be invalidated").setSize(200, 26).setPos(65, y+1).setFontSize(16).setAlign("left").setVisible(1)
        
        self.cfg_loaded = False
        self.cfg = Config("apps/python/prunn/", "config.ini")
        self.loadCFG()
        
        #thread
        self.key_listener = threading.Thread(target=self.listen_key)  
        self.key_listener.daemon = True      
        self.key_listener.start()        
    
    def __del__(self):
        self.listen_active = False
            
    def loadCFG(self):
        self.__class__.lapCanBeInvalidated = self.cfg.get("SETTINGS", "lap_can_be_invalidated", "int") 
        if self.__class__.lapCanBeInvalidated == -1:
            self.__class__.lapCanBeInvalidated=1
        self.__class__.max_num_cars = self.cfg.get("SETTINGS", "num_cars_tower", "int") 
        if self.__class__.max_num_cars == -1:
            self.__class__.max_num_cars=18
        self.__class__.max_num_laps_stint = self.cfg.get("SETTINGS", "num_laps_stint", "int")  
        if self.__class__.max_num_laps_stint == -1:
            self.__class__.max_num_laps_stint=8
        self.__class__.ui_row_height = self.cfg.get("SETTINGS", "ui_row_height", "int")  
        if self.__class__.ui_row_height == -1:
            self.__class__.ui_row_height=36
        self.__class__.race_mode = self.cfg.get("SETTINGS", "race_mode", "int") 
        if self.__class__.race_mode == -1:
            self.__class__.race_mode=0
        self.__class__.qual_mode = self.cfg.get("SETTINGS", "qual_mode", "int")
        if self.__class__.qual_mode == -1:
            self.__class__.qual_mode=0            
            
        ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)        
        ac.setValue(self.spin_num_cars, self.__class__.max_num_cars)
        ac.setValue(self.spin_num_laps, self.__class__.max_num_laps_stint)
        ac.setValue(self.spin_row_height, self.__class__.ui_row_height)
        ac.setValue(self.chk_invalidated,self.__class__.lapCanBeInvalidated)
        self.setLabelQual()
        self.setLabelRace()
        self.cfg_loaded = True
        
    def saveCFG(self):
        self.setLabelRace()   
        self.setLabelQual()
        self.cfg.set("SETTINGS", "race_mode", self.__class__.race_mode)   
        self.cfg.set("SETTINGS", "qual_mode", self.__class__.qual_mode) 
        self.cfg.set("SETTINGS", "lap_can_be_invalidated", self.__class__.lapCanBeInvalidated)
        self.cfg.set("SETTINGS", "num_cars_tower", self.__class__.max_num_cars)    
        self.cfg.set("SETTINGS", "num_laps_stint", self.__class__.max_num_laps_stint) 
        self.cfg.set("SETTINGS", "ui_row_height", self.__class__.ui_row_height) 
    
    def setLabelQual(self):
        if self.__class__.qual_mode == 0:
            self.lbl_qual_mode.setText("Gaps")
        else:
            self.lbl_qual_mode.setText("Times")
            
    def setLabelRace(self):
        if self.__class__.race_mode == 0:
            self.lbl_race_mode.setText("Auto")
        elif self.__class__.race_mode == 1:
            self.lbl_race_mode.setText("Full-Gaps")
        else:
            self.lbl_race_mode.setText("Full")
                        
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
    
    def listen_key(self):
        try:        
            #ctypes.windll.user32.RegisterHotKey(None, 1, 0, apps.util.win32con.VK_F7)
            ctypes.windll.user32.RegisterHotKey(None, 1, apps.util.win32con.MOD_CONTROL, 0x44)#CTRL+D
            msg = ctypes.wintypes.MSG()
            while self.listen_active :
                if ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0: 
                    #ac.console("loopmess."+ str(msg.message))              
                    if msg.message == apps.util.win32con.WM_HOTKEY:
                        self.hotkey_pressed()
                    ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                    ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))           
        except:
            Log.w("Error")
        finally:
            ctypes.windll.user32.UnregisterHotKey(None, 1)
          
    def hotkey_pressed(self):
        if self.session.value == 2:
            if self.__class__.race_mode >= 2:
                self.__class__.race_mode = 0
            else:
                self.__class__.race_mode += 1
            ac.setValue(self.spin_race_mode, self.__class__.race_mode)
        else: 
            if self.__class__.qual_mode >= 1:
                self.__class__.qual_mode = 0
            else:
                self.__class__.qual_mode += 1
            ac.setValue(self.spin_qual_mode, self.__class__.qual_mode)
        self.__class__.configChanged=True        
     
    @staticmethod
    def onCheckInvalidatedChanged(name, state): 
        Configuration.lapCanBeInvalidated = state
        Configuration.configChanged=True
        
    @staticmethod
    def onSpinNumCarsChanged(value):
        Configuration.max_num_cars = value
        Configuration.configChanged=True
        
    @staticmethod
    def onSpinNumLapsChanged(value): 
        Configuration.max_num_laps_stint = value
        Configuration.configChanged=True  
        
    @staticmethod
    def onSpinRowHeightChanged(value): 
        Configuration.ui_row_height = value
        Configuration.configChanged=True       
    
    @staticmethod
    def onSpinRaceModeChanged(value):
        Configuration.race_mode = value
        Configuration.configChanged=True      
        
    @staticmethod
    def onSpinQualModeChanged(value):
        Configuration.qual_mode = value
        Configuration.configChanged=True
       
    
    