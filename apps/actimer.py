import ac
import acsys
import os.path
import json
import ctypes
from apps.util.func import rgb,getFontSize
from apps.util.classes import Window, Label, Value, POINT, Colors, Config

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
		self.ui_row_height = Value(-1)
		self.numberOfLaps=0
		self.rowHeight=36
		self.window = Window(name="ACTV Timer", icon=False, width=228, height=42, texture="")
		
		self.lbl_session_info=Label(self.window.app,"Loading").setSize(154, self.rowHeight).setPos(self.rowHeight, 0).setFontSize(26).setAlign("center").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64)
		self.lbl_session_title=Label(self.window.app,"P").setSize(self.rowHeight, self.rowHeight).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(Colors.red(bg = True)).setBgOpacity(0.64)
		
		self.lbl_session_single=Label(self.window.app,"Loading").setSize(190, self.rowHeight).setPos(0, 0).setFontSize(26).setAlign("center").setBgColor(rgb([55, 55, 55], bg = True)).setBgOpacity(0.64).setColor(Colors.white()).setVisible(0)
		self.lbl_session_border=Label(self.window.app,"").setSize(154+self.rowHeight, 1).setPos(0, self.rowHeight+1).setBgColor(Colors.red(bg = True)).setBgOpacity(0.7).setVisible(1)
		
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
				if self.trackName[12] == " " or self.trackName[12] == "-":
					self.trackName = self.trackName[:12]
				else:
					self.trackName = self.trackName[:12]
					#cut multiword
					space = self.trackName.rfind(" ")
					dash = self.trackName.rfind("-")
					if space > 0:
						self.trackName = self.trackName[:space]
					elif dash > 0:
						self.trackName = self.trackName[:dash]
			
		else:
			self.trackName = ac.getTrackName(0)
		if len(self.trackName) > 12:
			self.trackName = self.trackName[:12]
			
		self.loadCFG()
			
		
	# PUBLIC METHODS
	#---------------------------------------------------------------------------------------------------------------------------------------------    
	def loadCFG(self):        
		cfg = Config("apps/python/prunn/", "config.ini")		
		self.ui_row_height.setValue(cfg.get("SETTINGS", "ui_row_height", "int")) 
		if self.ui_row_height.hasChanged():
			self.reDrawSize()

	def reDrawSize(self):
		self.rowHeight=self.ui_row_height.value
		fontSize=getFontSize(self.rowHeight)
		width=self.rowHeight*5
		self.lbl_session_info.setSize(self.rowHeight*4, self.rowHeight).setPos(self.rowHeight, 0).setFontSize(fontSize)		
		self.lbl_session_title.setSize(self.rowHeight, self.rowHeight).setFontSize(fontSize)		
		self.lbl_session_single.setSize(width, self.rowHeight).setFontSize(fontSize)		
		self.lbl_session_border.setSize(width, 1).setPos(0, self.rowHeight+1)	
		if len(self.finish_labels) > 0:
			i=0
			j=0
			height=self.rowHeight/3
			for label in self.finish_labels:
				label.setSize(height, height)
				if i % 2 == 1 and j < 7:		
					label.setPos(height + j*height*2, i*height)
				elif i % 2 == 0:
					label.setPos(j*height*2, i*height)
				j+=1
				if (i % 2 == 0 and j >= 8) or (i % 2 == 1 and j >= 7):
					i+=1
					j=0	

	def setFont(self,fontName):
		self.lbl_session_info.setFont(fontName,0,0)
		self.lbl_session_title.setFont(fontName,0,0) 
		self.lbl_session_single.setFont(fontName,0,0) 

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
			height=self.rowHeight/3
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
			else:   
				#pin outside
				self.window.setBgOpacity(0).border(0) 
		
	def onUpdate(self, sim_info):		
		self.session_draw.setValue(sim_info.graphics.session)
		self.manageWindow()
		sim_info_status=sim_info.graphics.status
		if sim_info_status == 2: #LIVE
			if self.replay_initialised:
				self.lbl_session_single.setColor(rgb([255,255,255]))
			self.session.setValue(self.session_draw.value)
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
						self.lbl_session_title.setSize(self.rowHeight, self.rowHeight)
						self.lbl_session_info.setSize(self.rowHeight*4, self.rowHeight).setPos(self.rowHeight, 0)						
						if self.session.value == 1 :
							self.lbl_session_title.setText("Q")
						else:
							self.lbl_session_title.setText("P")  
					self.lbl_session_info.setText(self.time_splitting(sessionTimeLeft))
					if not self.finish_initialised:
						if sim_info.graphics.flag == 2:
							self.lbl_session_info.setBgColor(Colors.yellow(True))
							self.lbl_session_info.setColor(Colors.black(),True)
							self.lbl_session_border.setBgColor(Colors.black(bg = True),True)
							self.lbl_session_title.setBgColor(Colors.black(bg = True),True)
						else:
							self.lbl_session_info.setBgColor(rgb([55, 55, 55], bg = True))
							self.lbl_session_info.setColor(Colors.white(),True)	
							self.lbl_session_border.setBgColor(Colors.red(bg = True),True)	
							self.lbl_session_title.setBgColor(Colors.red(bg = True),True)
					self.lbl_session_border.animate()		
					self.lbl_session_info.animate()
					self.lbl_session_title.animate()
			elif self.session.value == 2 :
				completed=0
				for x in range(ac.getCarsCount()): 
					c = ac.getCarState(x,acsys.CS.LapCount)
					if c > completed:
						completed=c     
				completed+=1    
				if self.numberOfLaps==0:
					self.numberOfLaps=sim_info.graphics.numberOfLaps
				if sessionTimeLeft > 1800000 or (sim_info.graphics.iCurrentTime == 0 and sim_info.graphics.completedLaps == 0):
					if self.finish_initialised:
						self.destoy_finish()
					self.lbl_session_info.setVisible(0)
					self.lbl_session_title.setVisible(0)
					self.lbl_session_single.setVisible(1)
					self.lbl_session_border.setVisible(1)
					self.lbl_session_single.setText(self.trackName)
				elif completed > self.numberOfLaps:
					if not self.finish_initialised:
						self.init_finish()
				elif completed == self.numberOfLaps:
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
						self.lbl_session_info.setSize(self.rowHeight*4,  self.rowHeight).setPos(self.rowHeight, 0)
						self.lbl_session_title.setSize(self.rowHeight, self.rowHeight)
						self.lbl_session_title.setText("Lap")
					self.lbl_session_single.setText("{0} / {1}".format(completed,self.numberOfLaps))
				if not self.finish_initialised:
					if sim_info.graphics.flag == 2:
						self.lbl_session_single.setBgColor(Colors.yellow(True),True)
						self.lbl_session_single.setColor(Colors.black(),True)
						self.lbl_session_border.setBgColor(Colors.black(bg = True),True)
					else:
						self.lbl_session_single.setBgColor(rgb([55, 55, 55], bg = True),True)
						self.lbl_session_single.setColor(Colors.white(),True)
						self.lbl_session_border.setBgColor(Colors.red(bg = True),True)
				self.lbl_session_border.animate()		
				self.lbl_session_single.animate()
			else:
				self.lbl_session_info.setVisible(0)
				self.lbl_session_title.setVisible(0)
				self.lbl_session_single.setVisible(0)
				self.lbl_session_border.setVisible(0)
			
					
		elif sim_info_status == 1:
			replayTimeMultiplier=sim_info.graphics.replayTimeMultiplier
			if self.finish_initialised:
				self.destoy_finish()
			self.lbl_session_info.setVisible(0)
			self.lbl_session_title.setVisible(0)
			self.lbl_session_border.setVisible(1)
			self.lbl_session_single.setVisible(1)
			self.replay_initialised=True
			self.lbl_session_single.setColor(rgb([self.replay_rgb,self.replay_rgb,self.replay_rgb]))
			if self.replay_asc and replayTimeMultiplier > 0:
				self.replay_rgb += 2
			elif replayTimeMultiplier > 0:
				self.replay_rgb -= 2
			if self.replay_rgb < 100:
				self.replay_asc=True
			elif self.replay_rgb >= 246:
				self.replay_rgb=246
				self.replay_asc=False
			self.lbl_session_single.setText("REPLAY")
		
	
	