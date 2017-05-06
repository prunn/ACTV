import sys, traceback
import ac
import math
import configparser
import ctypes
import os.path
import json
from apps.util.func import rgb


class Window:
    # INITIALIZATION

    def __init__(self, name="defaultAppWindow", title="", icon=True, width=100, height=100, scale=1, texture=""):
        # local variables
        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.scale = scale
        self.x = 0
        self.y = 0
        self.last_x = 0
        self.last_y = 0
        self.is_attached = False
        self.attached_l = -1
        self.attached_r = -1

        # creating the app window
        self.app = ac.newApp(self.name)

        # default settings
        ac.drawBorder(self.app, 0)
        ac.setBackgroundOpacity(self.app, 0)
        if icon is False:
            ac.setIconPosition(self.app, 0, -10000)

        # applying settings
        ac.setTitle(self.app, "")
        ac.setBackgroundTexture(self.app, texture)
        ac.setSize(self.app, math.floor(self.width * scale), math.floor(self.height * scale))

    # PUBLIC METHODS

    def onRenderCallback(self, func):
        ac.addRenderCallback(self.app, func)
        return self

    def setBgOpacity(self, alpha):
        ac.setBackgroundOpacity(self.app, alpha)
        return self

    def showTitle(self, show):
        if show:
            ac.setTitle(self.app, self.name)
        else:
            ac.setTitle(self.app, "")
        return self

    def border(self, value):
        ac.drawBorder(self.app, value)
        return self

    def setBgTexture(self, texture):
        ac.setBackgroundTexture(self.app, texture)
        return self

    def setPos(self, x, y):
        self.x = x
        self.y = y
        ac.setPosition(self.app, self.x, self.y)
        return self

    def setLastPos(self):
        self.x = self.last_x
        self.y = self.last_y
        ac.setPosition(self.app, self.last_x, self.last_y)
        return self

    def getPos(self):
        self.x, self.y = ac.getPosition(self.app)
        return self


# -#####################################################################################################################################-#
class Value:
    def __init__(self, value=0):
        self.value = value
        self.old = value
        self.changed = False

    def setValue(self, value):
        if self.value != value:
            self.old = self.value
            self.value = value
            self.changed = True

    def hasChanged(self):
        if self.changed:
            self.changed = False
            return True
        return False


class raceGaps:
    def __init__(self, sector, time):
        self.sector = sector
        self.time = time


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]


class Colors:
    theme_red = -1
    theme_green = -1
    theme_blue = -1
    theme_highlight = -1
    dataCarsClasses = []
    carsClassesLoaded = False

    @staticmethod
    def theme(bg=False, reload=False):
        # get theme color
        if reload or Colors.theme_red < 0 or Colors.theme_green < 0 or Colors.theme_blue < 0:
            cfg = Config("apps/python/prunn/", "config.ini")
            Colors.theme_red = cfg.get("SETTINGS", "red", "int")
            if Colors.theme_red < 0 or Colors.theme_red > 255:
                Colors.theme_red = 191
            Colors.theme_green = cfg.get("SETTINGS", "green", "int")
            if Colors.theme_green < 0 or Colors.theme_green > 255:
                Colors.theme_green = 0
            Colors.theme_blue = cfg.get("SETTINGS", "blue", "int")
            if Colors.theme_blue < 0 or Colors.theme_blue > 255:
                Colors.theme_blue = 0
        # return rgb([40, 152, 211], bg = bg)
        return rgb([Colors.theme_red, Colors.theme_green, Colors.theme_blue], bg=bg)

    @staticmethod
    def highlight(bg=False, reload=False):
        # get theme color
        if reload or Colors.theme_highlight < 0:
            cfg = Config("apps/python/prunn/", "config.ini")
            Colors.theme_highlight = cfg.get("SETTINGS", "tower_highlight", "int")
            if Colors.theme_highlight != 1:
                Colors.theme_highlight = 0
        if Colors.theme_highlight == 1:
            return Colors.green(bg=bg)
        return Colors.red(bg=bg)

    @staticmethod
    def loadCarClasses():
        Colors.dataCarsClasses = []
        loadedCars = []
        for i in range(ac.getCarsCount()):
            carName = ac.getCarName(i)
            if not carName in loadedCars:
                loadedCars.append(carName)
                filePath = "content/cars/" + carName + "/ui/ui_car.json"
                if os.path.exists(filePath):
                    with open(filePath) as data_file:
                        d = data_file.read().replace('\r', '').replace('\n', '').replace('\t', '')
                        data = json.loads(d)
                        for t in data["tags"]:
                            if t[0] == "#":
                                Colors.dataCarsClasses.append({"c": carName, "t": t[1:].lower()})
        Colors.carsClassesLoaded = True

    @staticmethod
    def getClassForCar(car):
        for c in Colors.dataCarsClasses:
            if c["c"] == car:
                return c["t"]
        return False

    @staticmethod
    def background():
        return rgb([55, 55, 55], bg=True)

    @staticmethod
    def background_dark():
        return rgb([20, 20, 20], bg=True)

    @staticmethod
    def background_tower():
        return rgb([32, 32, 32], bg=True)

    @staticmethod
    def background_first():
        return rgb([192, 0, 0], bg=True)

    @staticmethod
    def background_tower_position_odd():
        return rgb([12, 12, 12], bg=True)

    @staticmethod
    def background_tower_position_even():
        return rgb([0, 0, 0], bg=True)

    @staticmethod
    def background_tower_position_highlight():
        return rgb([255, 255, 255], bg=True)

    @staticmethod
    def background_info_position():
        return rgb([112, 112, 112], bg=True)

    @staticmethod
    def background_speedtrap():
        return rgb([12, 12, 12], bg=True)

    @staticmethod
    def background_opacity():
        return 0.64

    @staticmethod
    def border_opacity():
        return 0.7

    @staticmethod
    def bmw():
        # return rgb([42, 101, 198], bg = True)
        return rgb([40, 152, 211], bg=True)

    @staticmethod
    def ford():
        # return rgb([0, 165, 255], bg = True)
        return rgb([62, 121, 218], bg=True)

    # return rgb([2, 58, 117], bg = True)
    @staticmethod
    def mercedes():
        return rgb([191, 191, 191], bg=True)

    @staticmethod
    def corvette():
        return rgb([240, 171, 1], bg=True)

    @staticmethod
    def lamborghini():
        return rgb([150, 191, 13], bg=True)

    @staticmethod
    def ktm():
        return rgb([250, 88, 0], bg=True)

    @staticmethod
    def nissan():
        return rgb([175, 71, 169], bg=True)

    @staticmethod
    def ferrari():
        return rgb([191, 0, 0], bg=True)

    @staticmethod
    def alfa():
        # return rgb([0, 154, 100], bg = True)
        return rgb([54, 172, 68], bg=True)

    @staticmethod
    def white(bg=False):
        return rgb([255, 255, 255], bg=bg)

    @staticmethod
    def black(bg=False):
        if bg:
            return rgb([0, 0, 0], bg=bg)
        return rgb([12, 12, 12], bg=bg)

    @staticmethod
    def red(bg=False):
        return rgb([191, 0, 0], bg=bg)

    @staticmethod
    def dnf(bg=False):
        return rgb([168, 48, 48], bg=bg)

    @staticmethod
    def green(bg=False):
        return rgb([32, 192, 31], bg=bg)

    @staticmethod
    def yellow(bg=False):
        return rgb([240, 171, 1], bg=bg)

    @staticmethod
    def grey(bg=False):
        return rgb([112, 112, 112], bg=bg)

    @staticmethod
    def purple(bg=False):
        return rgb([135, 31, 144], bg=bg)

    @staticmethod
    def pitColor(bg=False):
        return rgb([225, 225, 225], bg=bg)

    @staticmethod
    def orange(bg=False):
        return rgb([250, 88, 0], bg=bg)

    @staticmethod
    def lmp1():
        return rgb([205, 0, 0], bg=True)

    @staticmethod
    def gte():
        return rgb([0, 150, 54], bg=True)

    @staticmethod
    def colorFromCar(car, byclass=False):
        if byclass:
            if not Colors.carsClassesLoaded:
                Colors.loadCarClasses()
            cl = Colors.getClassForCar(car)
            if cl != False:
                if cl == 'lmp1':
                    return Colors.lmp1()
                if cl == 'lmp3':
                    return Colors.nissan()
                if cl == 'proto c':
                    return rgb([0, 86, 198], bg=True)  # blue
                if cl == 'gte-gt3':
                    return Colors.gte()
                if cl == 'gt4':
                    return Colors.ktm()
                if cl == 'suv':
                    return rgb([10, 10, 10], bg=True)
                if cl == 'hypercars':
                    return rgb([240, 212, 0], bg=True)
                if cl == 'hypercars r':
                    return Colors.lamborghini()
                if cl == 'supercars':
                    return rgb([97, 168, 219], bg=True)
                if cl == 'sportscars':
                    return Colors.mercedes()
                if cl == 'vintage supercars':
                    return rgb([214, 112, 157], bg=True)
                if cl == 'vintage gt':
                    return rgb([98, 203, 236], bg=True)
                if cl == 'vintage touring':
                    return Colors.alfa()
                if cl == 'small sports':
                    return Colors.nissan()
                if cl == '90s touring':
                    return Colors.gte()

        if car.find("ferrari") >= 0:
            return Colors.ferrari()
        if car.find("bmw") >= 0:
            return Colors.bmw()
        if car.find("ford") >= 0 or car.find("shelby") >= 0:
            return Colors.ford()
        if car.find("merc") >= 0 or car.find("mazda") >= 0:
            return Colors.mercedes()
        if car.find("ruf") >= 0 or car.find("corvette") >= 0 or car.find("lotus") >= 0 or car.find("porsche") >= 0:
            return Colors.corvette()
        if car.find("lamborghini") >= 0 or car.find("pagani") >= 0:
            return Colors.lamborghini()
        if car.find("ktm") >= 0 or car.find("mclaren") >= 0:
            return Colors.ktm()
        if car.find("nissan") >= 0:
            return Colors.nissan()
        if car.find("alfa") >= 0:
            return Colors.alfa()
        if car.find("honda") >= 0:
            return rgb([214, 112, 157], bg=True)
        # if car.find("glickenhaus")>=0 or car.find("p4-5_2011")>=0:
        #	return rgb([0, 0, 0], bg = True)
        return Colors.theme(bg=True)


class Label:
    # INITIALIZATION

    def __init__(self, window, text=""):
        self.text = text
        self.label = ac.addLabel(window, self.text)
        self.params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(1), "bg": Value(1),
                       "bb": Value(1), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(1)}
        self.f_params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(1), "bg": Value(1),
                         "bb": Value(1), "o": Value(0), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(1)}
        self.o_params = {"x": Value(0), "y": Value(0), "w": Value(0), "h": Value(0), "br": Value(1), "bg": Value(1),
                         "bb": Value(1), "o": Value(1), "r": Value(1), "g": Value(1), "b": Value(1), "a": Value(1)}
        self.multiplier = {"x": Value(3), "y": Value(3), "w": Value(1), "h": Value(1), "br": Value(0.06),
                           "bg": Value(0.06), "bb": Value(0.06), "o": Value(0.02), "r": Value(0.06), "g": Value(0.06),
                           "b": Value(0.06), "a": Value(0.02)}
        self.multiplier_mode = {"x": "", "y": "", "w": "", "h": "", "br": "", "bg": "", "bb": "", "o": "", "r": "",
                                "g": "", "b": "", "a": ""}
        self.fontSize = 12
        self.spring_multiplier = 36
        self.align = "left"
        self.bgTexture = ""
        self.fontName = ""
        # self.opacity   = 1
        self.visible = 0
        self.isVisible = Value(False)
        self.isTextVisible = Value(False)

    # PUBLIC METHODS
    def set(self, text=None, align=None, color=None, font_size=None, font=None, w=None, h=None, x=None, y=None, texture=None, background=None, opacity=None, visible=None, animated=False, text_hidden=False):
        # Text
        if text is not None:
            self.setText(text, text_hidden)
        # Text alignment
        if align is not None:
            self.setAlign(align)
        # Size
        if w is not None and h is not None:
            self.setSize(w, h, animated)
        elif w is not None:
            self.setSize(w, self.params["h"].value, animated)
        elif h is not None:
            self.setSize(self.params["w"].value, h, animated)
        # Position
        if x is not None and y is not None:
            self.setPos(x, y, animated)
        elif x is not None:
            self.setX(x, animated)
        elif y is not None:
            self.setY(y, animated)
        # Font color
        if color is not None:
            self.setColor(color, animated)
        # Font
        if font is not None:
            self.setFont(font, 0, 0)
        # Font size
        if font_size is not None:
            self.setFontSize(font_size)
        # Background texture
        if texture is not None:
            self.setBgTexture(texture)
        # Background color
        if background is not None:
            self.setBgColor(background, animated)
        # Background opacity
        if opacity is not None:
            self.setBgOpacity(opacity, animated)
        # Visibility
        if visible is not None:
            self.setVisible(visible)
        return self

    def setText(self, text, hidden=False):
        self.text = text
        if hidden:
            ac.setText(self.label, "")
            self.isTextVisible.setValue(False)
        else:
            ac.setText(self.label, self.text)
            self.isTextVisible.setValue(True)
        return self

    def setSize(self, w, h, animated=False):
        self.f_params["w"].setValue(w)
        self.f_params["h"].setValue(h)
        if not animated:
            self.o_params["w"].setValue(w)
            self.o_params["h"].setValue(h)
            self.params["w"].setValue(w)
            self.params["h"].setValue(h)
            if self.params["w"].hasChanged() or self.params["h"].hasChanged():
                ac.setSize(self.label, self.params["w"].value, self.params["h"].value)
        return self

    def setPos(self, x, y, animated=False):
        self.f_params["x"].setValue(x)
        self.f_params["y"].setValue(y)
        if not animated:
            self.o_params["x"].setValue(x)
            self.o_params["y"].setValue(y)
            self.params["x"].setValue(x)
            self.params["y"].setValue(y)
            if self.params["x"].hasChanged() or self.params["y"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setY(self, y, animated=False):
        self.f_params["y"].setValue(y)
        if not animated:
            self.o_params["y"].setValue(y)
            self.params["y"].setValue(y)
            if self.params["y"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setX(self, x, animated=False):
        self.f_params["x"].setValue(x)
        if not animated:
            self.o_params["x"].setValue(x)
            self.params["x"].setValue(x)
            if self.params["x"].hasChanged():
                ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        return self

    def setColor(self, color, animated=False):
        self.f_params["r"].setValue(color[0])
        self.f_params["g"].setValue(color[1])
        self.f_params["b"].setValue(color[2])
        self.f_params["a"].setValue(color[3])
        if not animated:
            self.o_params["r"].setValue(color[0])
            self.o_params["g"].setValue(color[1])
            self.o_params["b"].setValue(color[2])
            self.o_params["a"].setValue(color[3])
            self.params["r"].setValue(color[0])
            self.params["g"].setValue(color[1])
            self.params["b"].setValue(color[2])
            self.params["a"].setValue(color[3])
            ac.setFontColor(self.label, *color)
        return self

    def setFont(self, fontName, italic, bold):
        self.fontName = fontName
        ac.setCustomFont(self.label, self.fontName, italic, bold)
        #if fontName == "Khula":
        #    self.fontSize += 1
        #    ac.setFontSize(self.label, self.fontSize)
        return self

    def update_font(self):
        self.setFont(Font.get_font(), 0, 0)
        return self

    def setFontSize(self, fontSize):
        self.fontSize = fontSize
        ac.setFontSize(self.label, self.fontSize)
        return self

    def setAlign(self, align="left"):
        self.align = align
        ac.setFontAlignment(self.label, self.align)
        return self

    def setBgTexture(self, texture):
        self.bgTexture = texture
        ac.setBackgroundTexture(self.label, self.bgTexture)
        return self

    def setBgColor(self, color, animated=False):
        self.f_params["br"].setValue(color[0])
        self.f_params["bg"].setValue(color[1])
        self.f_params["bb"].setValue(color[2])
        if not animated:
            self.o_params["br"].setValue(color[0])
            self.o_params["bg"].setValue(color[1])
            self.o_params["bb"].setValue(color[2])
            self.params["br"].setValue(color[0])
            self.params["bg"].setValue(color[1])
            self.params["bb"].setValue(color[2])
            ac.setBackgroundColor(self.label, *color)
            if self.f_params["o"].value > 0:
                ac.setBackgroundOpacity(self.label, self.params["o"].value)
        return self

    def setBgOpacity(self, opacity, animated=False):
        self.f_params["o"].setValue(opacity)
        if not animated:
            self.o_params["o"].setValue(opacity)
            # self.opacity=opacity
            self.params["o"].setValue(opacity)
            ac.setBackgroundOpacity(self.label, self.params["o"].value)
        return self

    ############################## Animations ##############################
    def setVisible(self, value):
        self.visible = value
        self.isVisible.setValue(bool(value))
        ac.setVisible(self.label, value)
        # self.params = self.o_params
        # self.f_params = self.o_params
        return self

    def setAnimationSpeed(self, param, value):
        for p in param:
            self.multiplier[p].setValue(value)
        return self

    def setAnimationMode(self, param, value):
        for p in param:
            self.multiplier_mode[p] = value
        return self

    def hide(self):
        self.setBgOpacity(0, True)
        return self

    def slideUp(self):
        self.f_params["h"].setValue(0)
        return self

    def show(self):
        self.f_params["o"].setValue(self.o_params["o"].value)
        return self

    def slideDown(self):
        self.f_params["h"].setValue(self.o_params["h"].value)
        return self

    def showText(self):
        # if self.params["a"].value == self.opacity:
        #	self.params["a"].setValue(0)
        self.f_params["a"].setValue(self.o_params["a"].value)
        return self

    def hideText(self):
        self.f_params["a"].setValue(0)
        return self

    def adjustParam(self, p):
        if self.params[p].value != self.f_params[p].value:
            if self.multiplier_mode[p] == "spring":
                multiplier = self.multiplier[p].value
                spring_multi = self.spring_multiplier
                if p == "y":
                    spring_multi = self.f_params["h"].value - 1
                    if not spring_multi > 0:
                        spring_multi = 36
                if abs(self.f_params[p].value - self.params[p].value) > spring_multi * self.multiplier[p].value:
                    multiplier = round(abs(self.f_params[p].value - self.params[p].value) / spring_multi)
            else:
                multiplier = self.multiplier[p].value
            if abs(self.f_params[p].value - self.params[p].value) < multiplier:
                multiplier = abs(self.f_params[p].value - self.params[p].value)
            if self.params[p].value < self.f_params[p].value:
                self.params[p].setValue(self.params[p].value + multiplier)
            else:
                self.params[p].setValue(self.params[p].value - multiplier)
        return self

    def animate(self):
        # adjust size +1
        self.adjustParam("w").adjustParam("h")
        # adjust position +3
        self.adjustParam("x").adjustParam("y")
        # adjust background
        self.adjustParam("br").adjustParam("bg").adjustParam("bb").adjustParam("o")
        # adjust colors + 0.02
        self.adjustParam("r").adjustParam("g").adjustParam("b").adjustParam("a")

        # commit changes
        if self.params["x"].hasChanged() or self.params["y"].hasChanged():
            ac.setPosition(self.label, self.params["x"].value, self.params["y"].value)
        if self.params["w"].hasChanged() or self.params["h"].hasChanged():
            ac.setSize(self.label, self.params["w"].value, self.params["h"].value)
            if self.params["h"].value == 0:
                self.isVisible.setValue(False)
            else:
                self.isVisible.setValue(True)
        if self.params["br"].hasChanged() or self.params["bg"].hasChanged() or self.params["bb"].hasChanged():
            ac.setBackgroundColor(self.label, self.params["br"].value, self.params["bg"].value, self.params["bb"].value)
            if self.f_params["o"].value > 0:
                ac.setBackgroundOpacity(self.label, self.params["o"].value)
        if self.params["o"].hasChanged():
            if self.params["o"].value == 0:
                self.isVisible.setValue(False)
            else:
                self.isVisible.setValue(True)
            changed = self.isVisible.hasChanged()
            if changed and self.params["o"].value > 0:
                self.setVisible(1)
            elif changed:
                self.setVisible(0)
            # fg opacity
            ac.setBackgroundOpacity(self.label, self.params["o"].value)
            if self.params["o"].value >= 0.4:
                self.isTextVisible.setValue(True)
            else:
                self.isTextVisible.setValue(False)
            if self.isTextVisible.hasChanged():
                if self.isTextVisible.value:
                    ac.setText(self.label, self.text)
                else:
                    ac.setText(self.label, "")

        if self.params["r"].hasChanged() or self.params["g"].hasChanged() or self.params["b"].hasChanged() or \
                self.params["a"].hasChanged():
            ac.setFontColor(self.label, self.params["r"].value, self.params["g"].value, self.params["b"].value,
                            self.params["a"].value)
            if self.params["a"].value == 0:
                self.isVisible.setValue(False)
            else:
                self.isVisible.setValue(True)
            changed = self.isVisible.hasChanged()
            if changed and self.params["a"].value > 0:
                self.setVisible(1)
            elif changed:
                self.setVisible(0)


# -#####################################################################################################################################-#


class Button:
    # INITIALIZATION

    def __init__(self, window, clickFunc, width=60, height=20, x=0, y=0, text="", texture=""):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.button = ac.addButton(window, text)

        # adding default settings
        self.setSize(width, height)
        self.setPos(x, y)
        if texture != "":
            self.setBgTexture(texture)

        # default settings
        ac.drawBorder(self.button, 0)
        ac.setBackgroundOpacity(self.button, 0)

        # adding a click event
        ac.addOnClickedListener(self.button, clickFunc)

    # PUBLIC METHODS

    def setSize(self, width, height):
        self.width = width
        self.height = height
        ac.setSize(self.button, self.width, self.height)
        return self

    def setFontSize(self, fontSize):
        self.fontSize = fontSize
        ac.setFontSize(self.button, self.fontSize)
        return self

    def setPos(self, x, y):
        self.x = x
        self.y = y
        ac.setPosition(self.button, self.x, self.y)
        return self

    def setBgTexture(self, texture):
        ac.setBackgroundTexture(self.button, texture)
        return self

    def setText(self, text, hidden=False):
        ac.setText(self.button, text)
        return self

    def setAlign(self, align="left"):
        ac.setFontAlignment(self.button, align)
        return self

    def setBgColor(self, color, animated=False):
        ac.setBackgroundColor(self.button, *color)
        # ac.setBackgroundOpacity(self.label, self.params["o"].value)
        return self

    def setBgOpacity(self, opacity, animated=False):
        ac.setBackgroundOpacity(self.button, opacity)
        return self

    def setVisible(self, value):
        ac.setVisible(self.button, value)
        return self


# -#####################################################################################################################################-#

class Log:
    @staticmethod
    def w(message):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        ac.console(message + ":")
        for line in lines:
            ac.log(line)
        for line in lines:
            if line.find("Traceback") >= 0:
                continue
            s = line.replace("\n", " -> ")
            s = s.replace("  ", "")
            if s[-4:] == " -> ":
                s = s[:-4]
            ac.console(s)


class Config:
    # INITIALIZATION

    def __init__(self, path, filename):
        self.file = path + filename
        self.parser = 0

        try:
            self.parser = configparser.RawConfigParser()
        except:
            ac.console("Prunn: Config -- Failed to initialize ConfigParser.")

        # read the file
        self._read()

    # LOCAL METHODS

    def _read(self):
        self.parser.read(self.file)

    def _write(self):
        with open(self.file, "w") as cfgFile:
            self.parser.write(cfgFile)

    # PUBLIC METHODS

    def has(self, section=None, option=None):
        if section is not None:
            # if option is not specified, search only for the section
            if option is None:
                return self.parser.has_section(section)
            # else, search for the option within the specified section
            else:
                return self.parser.has_option(section, option)
        # if section is not specified
        else:
            ac.console("Prunn: Config.has -- section must be specified.")

    def set(self, section=None, option=None, value=None):
        if section is not None:
            # if option is not specified, add the specified section
            if option is None:
                self.parser.add_section(section)
                self._write()
            # else, add the option within the specified section
            else:
                if not self.has(section, option) and value is None:
                    ac.console("Prunn: Config.set -- a value must be passed.")
                else:
                    if not self.has(section):
                        self.parser.add_section(section)
                    self.parser.set(section, option, value)
                    self._write()
        # if sections is not specified
        else:
            ac.console("Prunn: Config.set -- section must be specified.")

    def get(self, section, option, type=""):
        if self.has(section) and self.has(section, option):
            # if option request is an integer
            if type == "int":
                return self.parser.getint(section, option)
            # if option request is a float
            elif type == "float":
                return self.parser.getfloat(section, option)
            # if option request is boolean
            elif type == "bool":
                return self.parser.getboolean(section, option)
            # it must be a string then!
            else:
                return self.parser.get(section, option)
        else:
            return -1

    def remSection(self, section):
        if self.has(section):
            self.parser.remove_section(section)
            self._write()
        else:
            ac.console("Prunn: Config.remSection -- section not found.")

    def remOption(self, section, option):
        if self.has(section) and self.has(section, option):
            self.parser.remove_option(section, option)
            self._write()
        else:
            ac.console("Prunn: Config.remOption -- option not found.")


class Font:
    fonts = ["Segoe UI", "Khula", "PT Sans", "Lato", "Aller", "Noto Sans"]
    offsets = [0, 4, 2, 2, 2, 0]
    support = [True, True, True, True, True, True]
    init = [False, False, False, False, False, False]
    current = 0

    @staticmethod
    def set_font(font):
        Font.current = font
        if not Font.init[Font.current]:
            if ac.initFont(0, Font.fonts[Font.current], 0, 0) > 0:
                Font.init[Font.current] = True

    @staticmethod
    def get_font():
        return Font.fonts[Font.current]

    @staticmethod
    def get_font_offset():
        return Font.offsets[Font.current]

    @staticmethod
    def get_font_size(row_height):
        if row_height == 50 or row_height == 49:
            return 34
        if row_height == 48 or row_height == 47:
            return 33
        if row_height == 46 or row_height == 45:
            return 32
        if row_height == 44 or row_height == 43:
            return 31
        if row_height == 42:
            return 30
        if row_height == 41:
            return 29
        if row_height == 40:
            return 28
        if row_height == 39:
            return 27
        if row_height == 38 or row_height == 37:
            return 26
        if row_height == 36 or row_height == 35:
            return 25
        if row_height == 34:
            return 24
        if row_height == 33:
            return 23
        if row_height == 32 or row_height == 31:
            return 22
        if row_height == 30 or row_height == 29:
            return 21
        if row_height == 28:
            return 19
        if row_height == 27:
            return 19
        if row_height == 26:
            return 19
        if row_height == 25:
            return 18
        if row_height == 24 or row_height == 23:
            return 17
        if row_height == 22:
            return 16
        if row_height == 21:
            return 15
        if row_height == 20:
            return 14
        if row_height < 30:
            return row_height - 6
        return 26
