import ac
import acsys
import os.path
import json
import ctypes
import math
from apps.util.func import rgb
from apps.util.classes import Window, Label, Value, POINT

class ACTimer:

	# INITIALIZATION

	def __init__(self):
		self.finish_labels = []
		self.finish_initialised = False
		self.replay_initialised = False
		self.replay_asc = False
		self.replay_rgb=255
		self.session=Value()
		self.cursor=Value()
		self.cursor.setValue(False)
		self.session_draw=Value()
		self.session_draw.setValue(-1)
		self.window = Window(name="ACTV Timer", icon=False, width=228, height=42, texture="")
		
		self.lbl_session_info=Label(self.window.app,"Loading").setSize(154, 38).setPos(38, 0).setFontSize(26).setAlign("center").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64)
		self.lbl_session_title=Label(self.window.app,"P").setSize(38, 38).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(rgb([192, 0, 0], bg = True)).setBgOpacity(0.64)
		
		self.lbl_session_single=Label(self.window.app,"Loading").setSize(190, 38).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64).setVisible(0)
		self.lbl_session_border=Label(self.window.app,"").setSize(190, 1).setPos(0, 39).setBgColor(rgb([191, 0, 0], bg = True)).setBgOpacity(0.7).setVisible(1)
		
		trackFilePath = "content/tracks/"+ ac.getTrackName(0) + "/ui/"
		if ac.getTrackConfiguration(0) != "":
			trackFilePath += ac.getTrackConfiguration(0) + "/ui_track.json"
		else:			
			trackFilePath += "ui_track.json"
		if os.path.exists(trackFilePath):
			with open(trackFilePath) as data_file:    
				data = json.load(data_file)			
			self.trackName = data["name"]
			if len(self.trackName) > 12:
				#cut multiword
				space = self.trackName.find(" ")
				dash = self.trackName.find("-")
				if space > 0:
					self.trackName = self.trackName[:space]
				elif dash > 0:
					self.trackName = self.trackName[:dash]
		else:
			self.trackName = ac.getTrackName(0)
		if len(self.trackName) > 12:
			self.trackName = self.trackName[:12]
			
		self.screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
			
		
	# PUBLIC METHODS
	
	
	#---------------------------------------------------------------------------------------------------------------------------------------------                                        
	def time_splitting(self, ms):
		s=ms/1000 
		m,s=divmod(s,60) 
		h,m=divmod(m,60) 
		#d,h=divmod(h,24) 
		if h > 0:
			return "{0}:{1}:{2}".format(int(h), str(int(m)).zfill(2), str(int(s)).zfill(2)) 
		else:  
			return "{0}:{1}".format(int(m), str(int(s)).zfill(2))  
		
	def init_finish(self):
		self.lbl_session_info.setVisible(0)
		self.lbl_session_title.setVisible(0)
		self.lbl_session_border.setVisible(0)
		self.lbl_session_single.setVisible(1)
		self.lbl_session_single.setText("").setBgColor(rgb([255, 255, 255], bg = True)).setBgOpacity(0.76).setVisible(1)
		if len(self.finish_labels) > 0:
			for label in self.finish_labels:		
				label.setVisible(1)
		else:
			height=38/3
			for i in range(0,3):			
				for j in range(0,8):
					if i % 2 == 1 and j < 7:
						self.finish_labels.append(Label(self.window.app).setSize(height, height).setPos(height + j*height*2, i*height).setBgColor(rgb([0, 0, 0], bg = True)).setBgOpacity(0.8).setVisible(1))
					elif i % 2 == 0:
						self.finish_labels.append(Label(self.window.app).setSize(height, height).setPos(j*height*2, i*height).setBgColor(rgb([0, 0, 0], bg = True)).setBgOpacity(0.8).setVisible(1))
			
		self.finish_initialised = True
	
	def destoy_finish(self):
		#Destroy
		self.lbl_session_single.setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64).setVisible(0)
		for label in self.finish_labels:		
			label.setVisible(0)
		self.finish_initialised = False
	
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
		
		if self.cursor.hasChanged() or self.session_draw.hasChanged():
			if self.cursor.value:
				self.window.setBgOpacity(0.4).border(0)
				ac.setSize(self.window.app, math.floor(self.window.width*self.window.scale), math.floor(self.window.height*self.window.scale))   
			else:   
				#pin outside
				self.window.setBgOpacity(0).border(0)
				ac.setSize(self.window.app, self.screenWidth*2, 0) 
		
	def onUpdate(self, deltaT, sim_info):		
		self.session_draw.setValue(sim_info.graphics.session)
		self.manageWindow()
		if sim_info.graphics.status == 2:
			if self.replay_initialised:
				self.lbl_session_single.setColor(rgb([255,255,255]))
			self.session.setValue(sim_info.graphics.session)
			sessionTimeLeft = sim_info.graphics.sessionTimeLeft
			if self.session.value < 2  :				
				#0 to -5000 show finish
				if sessionTimeLeft < 0 and sessionTimeLeft > -5000:
					if not self.finish_initialised:
						self.init_finish()
				else:
					if sessionTimeLeft < 0:
						sessionTimeLeft = 0	
					if self.finish_initialised:
						self.destoy_finish()
					self.lbl_session_info.setVisible(1)
					self.lbl_session_title.setVisible(1)
					self.lbl_session_single.setVisible(0)
					self.lbl_session_border.setVisible(1)
					if self.session.hasChanged():
						self.lbl_session_title.setSize(38, 38)
						self.lbl_session_info.setSize(154, 38).setPos(38, 0)						
						if self.session.value == 1 :
							self.lbl_session_title.setText("Q")
						else:
							self.lbl_session_title.setText("P")  
					self.lbl_session_info.setText(self.time_splitting(sessionTimeLeft))
			elif self.session.value == 2 :
				completed=0
				for x in range(ac.getCarsCount()): 
					c = ac.getCarState(x,acsys.CS.LapCount)
					if c > completed:
						completed=c     
				completed+=1    
				total=sim_info.graphics.numberOfLaps
				if sessionTimeLeft > 1800000:
					if self.finish_initialised:
						self.destoy_finish()
					self.lbl_session_info.setVisible(0)
					self.lbl_session_title.setVisible(0)
					self.lbl_session_single.setVisible(1)
					self.lbl_session_border.setVisible(1)
					self.lbl_session_single.setText(self.trackName)
				elif completed > total:
					if not self.finish_initialised:
						self.init_finish()
				elif completed == total:
					if self.finish_initialised:
						self.destoy_finish()
					self.lbl_session_info.setVisible(0)
					self.lbl_session_title.setVisible(0)
					self.lbl_session_single.setVisible(1)
					self.lbl_session_border.setVisible(1)
					self.lbl_session_single.setText("Final lap")
				else:
					if self.finish_initialised:
						self.destoy_finish()
					self.lbl_session_info.setVisible(0)
					self.lbl_session_title.setVisible(0)
					self.lbl_session_single.setVisible(1)
					self.lbl_session_border.setVisible(1)
					if self.session.hasChanged():
						self.lbl_session_info.setSize(134,  38).setPos(58, 0)
						self.lbl_session_title.setSize(58, 38)
						self.lbl_session_title.setText("Lap")
					self.lbl_session_single.setText("{0} / {1}".format(completed,total))
			else:
				self.lbl_session_info.setVisible(0)
				self.lbl_session_title.setVisible(0)
				self.lbl_session_single.setVisible(0)
				self.lbl_session_border.setVisible(0)
					
		elif sim_info.graphics.status == 1:
			if self.finish_initialised:
				self.destoy_finish()
			self.lbl_session_info.setVisible(0)
			self.lbl_session_title.setVisible(0)
			self.lbl_session_border.setVisible(1)
			self.lbl_session_single.setVisible(1)
			self.replay_initialised=True
			self.lbl_session_single.setColor(rgb([self.replay_rgb,self.replay_rgb,self.replay_rgb]))
			if self.replay_asc and sim_info.graphics.replayTimeMultiplier > 0:
				self.replay_rgb += 2
			elif sim_info.graphics.replayTimeMultiplier > 0:
				self.replay_rgb -= 2
			if self.replay_rgb < 100:
				self.replay_asc=True
			elif self.replay_rgb >= 246:
				self.replay_rgb=246
				self.replay_asc=False
			self.lbl_session_single.setText("REPLAY")
		
	
	