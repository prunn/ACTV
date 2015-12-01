import sys, traceback
import ac
import math
import configparser
import ctypes
from apps.util.func import rgb


class Window:
	
	# INITIALIZATION
	
	def __init__(self, name="defaultAppWindow", title="", icon=True, width=100, height=100, scale=1, texture=""):
		# local variables
		self.name        = name
		self.title       = title
		self.width       = width
		self.height      = height
		self.scale       = scale
		self.x           = 0
		self.y           = 0
		self.last_x      = 0
		self.last_y      = 0
		self.is_attached = False
		self.attached_l  = -1
		self.attached_r  = -1
		
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
		ac.setSize(self.app, math.floor(self.width*scale), math.floor(self.height*scale))
		
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
	

#-#####################################################################################################################################-#
class Value:
	def __init__(self, value = 0):
		self.value = value
		self.old = value
		self.changed=False
		
	def setValue(self, value):
		if self.value != value:
			self.old=self.value
			self.value=value
			self.changed=True
	def hasChanged(self):
		if self.changed:
			self.changed=False
			return True
		return False


class POINT(ctypes.Structure):
	_fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]  

class Colors:
	@staticmethod
	def bmw():
		return rgb([62, 121, 218], bg = True)
	@staticmethod
	def mercedes():
		return rgb([191, 191, 191], bg = True)
	@staticmethod
	def corvette():
		return rgb([240, 171, 1], bg = True)
	@staticmethod
	def lamborghini():
		return rgb([150, 191, 13], bg = True)
	@staticmethod
	def default():
		return rgb([191, 0, 0], bg = True)
	
	@staticmethod
	def colorFromCar(car):
		if car.find("bmw")>=0 or car.find("ford")>=0:
			return Colors.bmw()
		if car.find("merc")>=0 or car.find("alfa")>=0:
			return Colors.mercedes()
		if car.find("ruf")>=0 or car.find("corvette")>=0 or car.find("lotus")>=0 or car.find("porsche")>=0:
			return Colors.corvette()
		if car.find("lamborghini")>=0 or car.find("pagani")>=0:
			return Colors.lamborghini()
		return Colors.default()	
	
class Label:

	# INITIALIZATION
	
	def __init__(self, window, text = ""):
		self.text      = text
		self.label     = ac.addLabel(window, self.text)
		self.size      = { "w" : 0, "h" : 0 }
		self.pos       = { "x" : 0, "y" : 0 }
		self.color     = (1, 1, 1, 1)
		self.bgColor   = (0, 0, 0, 1)
		self.fontSize  = 12
		self.align     = "left"
		self.bgTexture = ""
		self.opacity   = 1
		self.visible=0
		
	# PUBLIC METHODS
	
	def setText(self, text, hidden=False):
		self.text = text
		if hidden :
			ac.setText(self.label, "")
		else:
			ac.setText(self.label, self.text)
		return self
	
	def hideText(self):
		ac.setText(self.label, "")
		return self
	
	def showText(self):
		ac.setText(self.label, self.text)
		return self
	
	def setSize(self, w, h):
		self.size["w"] = w
		self.size["h"] = h
		ac.setSize(self.label, self.size["w"], self.size["h"])
		return self
	
	def setPos(self, x, y):
		self.pos["x"] = x
		self.pos["y"] = y
		ac.setPosition(self.label, self.pos["x"], self.pos["y"])
		return self
		
	def setColor(self, color):
		self.color = color
		ac.setFontColor(self.label, *self.color)
		return self
	
	def setFontSize(self, fontSize):
		self.fontSize = fontSize
		ac.setFontSize(self.label, self.fontSize)
		return self
	
	def setAlign(self, align = "left"):
		self.align = align
		ac.setFontAlignment(self.label, self.align)
		return self
	
	def setBgTexture(self, texture):
		self.bgTexture = texture
		ac.setBackgroundTexture(self.label, self.bgTexture)
		return self
	
	def setBgColor(self, color):
		ac.setBackgroundColor(self.label, *color)
		return self
	
	def setBgOpacity(self, opacity):
		ac.setBackgroundOpacity(self.label, opacity)
		return self
	
	def setVisible(self, value):
		self.visible=value
		ac.setVisible(self.label, value)
		return self

		
#-#####################################################################################################################################-#

	
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
	
	def setPos(self, x, y):
		self.x = x
		self.y = y
		ac.setPosition(self.button, self.x, self.y)
		return self
	
	def setBgTexture(self, texture):
		ac.setBackgroundTexture(self.button, texture)
		return self
		

#-#####################################################################################################################################-#

class Log:
	@staticmethod
	def w(message):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		ac.console(message + ":")		
		for line in lines:               
			ac.log(line)
		for line in lines:
			if line.find("Traceback")>=0:
				continue
			s = line.replace("\n"," -> ")
			s = s.replace("  ","")
			if s[-4:] == " -> ":
				s=s[:-4]			
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
					self.parser.set(section, option, value)
					self._write()
		# if sections is not specified
		else:
			ac.console("Prunn: Config.set -- section must be specified.")
		
	
	def get(self, section, option, type = ""):
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

