'''###########################################################################
#
# Project ACTV
# Version Beta 0.9.5
#
******************************************************************************
*** .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..-  ***
***                                                               ***
*** ooooooooo.   ooooooooo.   ooooo     ooo ooooo      ooo ooooo      ooo  ***
*** `888   `Y88. `888   `Y88. `888'     `8' `888b.     `8' `888b.     `8'  ***
***  888   .d88'  888   .d88'  888       8   8 `88b.    8   8 `88b.    8   ***
***  888ooo88P'   888ooo88P'   888       8   8   `88b.  8   8   `88b.  8   ***
***  888          888`88b.     888       8   8     `88b.8   8     `88b.8   ***
***  888          888  `88b.   `88.    .8'   8       `888   8       `888   ***
*** o888o        o888o  o888o    `YbodP'    o8o        `8  o8o        `8   ***
***                                       ***            
*** .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..-  ***
******************************************************************************
***************************************************************************'''
import ac
import sys,traceback
import os
import platform

try:      
    if platform.architecture()[0] == "64bit":
        sysdir = "prunn_dll_x64"
    else:
        sysdir = "prunn_dll_x86"
        
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), sysdir))
    os.environ['PATH'] = os.environ['PATH'] + ";." 
    
    from apps.util.sim_info import SimInfo
    from apps.actimer import ACTimer
    from apps.acinfo import ACInfo
    from apps.actower import ACTower
    from apps.speedtrap import ACSpeedTrap
    from apps.configuration import Configuration
    from apps.util.classes import Log
    sim_info = SimInfo()
except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    for line in lines:               
        ac.log(line)
        
timer=0
info=0
tower=0
speed=0
config=0

timerInit=False
infoInit=False
towerInit=False
speedInit=False
configInit=False

def acMain(ac_version):
    global timer,info,tower,speed,timerInit,infoInit,towerInit,speedInit,config,configInit
    try:
        config=Configuration()
        configInit=True
    except:
        Log.w("Error init config") 
    try:
        timer=ACTimer()
        timerInit=True
    except:
        Log.w("Error init timer")
    try:
        info=ACInfo()
        infoInit=True
    except:
        Log.w("Error init info")
    try:
        tower=ACTower()
        towerInit=True
    except:
        Log.w("Error init tower") 
    try:
        speed=ACSpeedTrap()
        speedInit=True
    except:
        Log.w("Error init speedtrap")  
                   
    return "Prunn"


def acUpdate(deltaT):
    global timer,info,tower,speed,timerInit,infoInit,towerInit,speedInit,config,configInit
    configChanged=False
    if configInit:     
        try:
            configChanged = config.onUpdate(deltaT,sim_info)
            if configChanged:
                if timerInit:
                    timer.loadCFG()
                if infoInit:
                    info.loadCFG()
                if towerInit:
                    tower.loadCFG()
                if speedInit:    
                    speed.loadCFG()
        except:
            Log.w("Error config")
    if timerInit:
        try:
            timer.onUpdate(deltaT,sim_info)
        except:
            Log.w("Error timer")
    if infoInit:
        try:
            info.onUpdate(deltaT,sim_info)
        except:
            Log.w("Error info")
    if towerInit:
        try:
            tower.onUpdate(deltaT,sim_info)
        except:
            Log.w("Error tower")  
    if speedInit:     
        try:
            speed.onUpdate(deltaT,sim_info)
        except:
            Log.w("Error speedtrap")
    
def acShutdown():    
    ac.console("shutting down actv")

    