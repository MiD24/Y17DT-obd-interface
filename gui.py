# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 16:43:35 2016

@author: Michiel
"""

import pyglet
import time
import obd_serial
import parse

class Gui:
	def __init__(self, testing, ELM_MAC_Address, filename, timestep=1):
		self.dt = timestep
		self.index = 0
		self.testing = testing
		self.ELM_MAC_Address = ELM_MAC_Address
		self.filename = filename
		
		self.window = pyglet.window.Window()
		self.label = pyglet.text.Label(str(0),
                          font_name='Times New Roman',
                          font_size=36,
                          x=self.window.width//2, y=self.window.height//2,
                          anchor_x='center', anchor_y='center')
		
		@self.window.event
		def on_draw():
		    self.window.clear()
		    self.label.draw()
		def update(dt):
			self.update(dt)
		pyglet.clock.schedule_interval(update, self.dt)
					
	def update(self, dt):
		#print("Time step: " + str(dt))
		r = self.retreive()
		self.label = pyglet.text.Label("Speed = " + str(parse.parse(r)['Speed']),
                          font_name='Times New Roman',
                          font_size=36,
                          x=self.window.width//2, y=self.window.height//2,
                          anchor_x='center', anchor_y='center')
	
	def run(self):
		try:
			print("Starting measurements")
			pyglet.app.run()
		except KeyboardInterrupt:									#break from loop on ctrl+c
			pass
		except IOError:
			print("I/O error")
		except:
			print("Unexpected error")
			print("Stopped measurements")
			self.terminate()
			raise
		print("Stopped measurements")
		self.terminate()
		
	def open_file(self):
		try:
			self.output = open(self.filename + '.obd', 'a')								#open file in append mode
		except IOError: print('Cannot open file')

	def open_connection(self):
		try:
			self.obd = obd_serial.obd_serial()
			if not self.testing: self.obd.connect(self.ELM_MAC_Address)
			if not self.testing: self.obd.init_ELM()								#initialize ELM327
			self.obd.set_logging(False)						#open bluetooth connection
		except: 
			print("Unable to connect")
			return False
		return True		
	
	def retreive(self):
		if self.obd:									#disable log messages
			t0 = time.time()
			self.resp = self.obd.elm('2101', self.testing)						#write '2101' to ELM327 and return response
			self.output.write(self.resp + '\n')								#write response to file
			diff = time.time() - t0
			print("Time needed to retreive: " + str(diff))
			return self.resp
		return None
			
	def terminate(self):
		self.output.close()
		if self.obd:
			self.obd.close()

	
				
if __name__ == "__main__":
	T = 0.5
	testing = False
	ELM_MAC_Address = "00:0D:18:00:00:01"
	filename = time.strftime("%Y%m%d_%H-%M-%S", time.localtime())		#filename YYYYMMDD_HH-MM-SS
	
	g = Gui(testing, ELM_MAC_Address, filename,timestep=T)
	g.open_file()
	if g.open_connection(): 
		g.run()
	