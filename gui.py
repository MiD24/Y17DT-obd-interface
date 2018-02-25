# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 16:43:35 2016

@author: Michiel
"""

import pyglet
import time
import obd_serial
import parse

class Gui(pyglet.window.Window):
	def __init__(self, testing, ELM_MAC_Address, filename, timestep=1):
		super().__init__(resizable=True)
#		self.set_size(1000, 600)
		self.maximize()
		self.dt = timestep
		self.index = 0
		self.testing = testing
		self.ELM_MAC_Address = ELM_MAC_Address
		self.filename = filename
		
		grid_x = [100, 550, 1000, 1450]
		grid_y = [100, 250, 400, 550, 700, 850, 1000]
		
		self.speed_bar = 		bar(grid_x[0], grid_y[0], 250, 50, 0, 150, 0, 'km/h', 'Speed', [30, 255, 0])
		self.pedal_bar = 		bar(grid_x[0], grid_y[1], 250, 50, 0, 100, 0, '%', 'Pedal', [30, 255, 0])
		self.rpm_bar = 		bar(grid_x[0], grid_y[2], 250, 50, 0, 5000, 0, 'rpm', 'Engine speed', [30, 255, 0])
		self.boost_bar = 		bar(grid_x[0], grid_y[3], 250, 50, 100, 200, 100, 'kPa', 'Boost pressure', [30, 255, 0])
		self.t_boost_bar = 	bar(grid_x[1], grid_y[3], 250, 50, 100, 200, 100, 'kPa', 'Target boost pressure', [30, 255, 0])
		self.boost_ctl_bar = 	bar(grid_x[1], grid_y[2], 250, 50, 0, 100, 0, '%', 'Boost ctrl valve', [30, 255, 0])
		self.inj_bar = 		bar(grid_x[1], grid_y[0], 250, 50, 0, 50, 0, 'mg/stroke', 'Injected quantity', [30, 255, 0])
		pyglet.clock.schedule_interval(self.update, self.dt)
		
	def on_draw(self):
		self.clear()
		self.speed_bar.draw()
		self.pedal_bar.draw()
		self.rpm_bar.draw()
		self.boost_bar.draw()
		self.t_boost_bar.draw()
		self.boost_ctl_bar.draw()
		self.inj_bar.draw()
						
	def update(self, dt):
		#print("Time step: " + str(dt))
		r = self.retreive()
		if 'NO DATA' in r or 'ERROR' in r:
			self.terminate()
			pyglet.app.exit()
			return
		self.speed_bar.update(dt, parse.parse(r)['Speed'])
		self.pedal_bar.update(dt, parse.parse(r)['Pedal position'])
		self.rpm_bar.update(dt, parse.parse(r)['RPM'])
		self.boost_bar.update(dt, parse.parse(r)['Boost pressure'])
		self.t_boost_bar.update(dt, parse.parse(r)['Target boost pressure'])
		self.boost_ctl_bar.update(dt, parse.parse(r)['Boost control valve'])
		self.inj_bar.update(dt, parse.parse(r)['Injection Q'])
	
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
			#print("Time needed to retreive: " + str(diff))
			return self.resp
		return None
			
	def terminate(self):
		self.output.close()
		if self.obd:
			self.obd.close()

	
class bar:
	def __init__(self, x, y, width, height, low, high, value, unit, name, rgb):
		self.label = pyglet.text.Label('1',
	                          font_name='Times New Roman',
	                          font_size=36,
	                          x=100, y=100,
	                          anchor_x='center', anchor_y='center')
		self.x = x
		self.y = y
		self.bar_width = width
		self.bar_height = height
		self.low = low
		self.high = high
		self.value = value
		self.name = name
		self.unit = unit
		self.color = []
		for i in range(0,4): 
			self.color.extend(rgb)
		self.font = 'Times New Roman'
		self.vertices_box = (self.x, self.y, self.x+self.bar_width, self.y,  self.x+self.bar_width, self.y+self.bar_height, self.x, self.y+self.bar_height)
		self.vertices_bar = (self.x, self.y, self.x+int((self.value-self.low)/(self.high-self.low)*self.bar_width), self.y,  self.x+int((self.value-self.low)/self.high*self.bar_width), self.y+self.bar_height, self.x, self.y+self.bar_height)
		self.box_vertex_list = pyglet.graphics.vertex_list_indexed(4,
			[0, 1, 2, 3],
			('v2i', self.vertices_box),
			)
		self.bar_vertex_list = pyglet.graphics.vertex_list_indexed(4,  [0, 1, 3, 1, 2, 3],
			('v2i', self.vertices_bar),
			('c3B', self.color)
			)
		self.label_val = pyglet.text.Label(str(self.value)+' '+self.unit,
	                          font_name=self.font,
	                          font_size=20,
	                          x=self.vertices_box[2]+10, y=self.y+self.bar_height/2,
	                          anchor_x='left', anchor_y='center')
		self.label_name = pyglet.text.Label(self.name,
	                          font_name=self.font,
	                          font_size=20,
	                          x=self.x, y=self.y+self.bar_height+5,
	                          anchor_x='left', anchor_y='bottom')
		self.label_low = pyglet.text.Label(str(self.low),
	                          font_name=self.font,
	                          font_size=10,
	                          x=self.x, y=self.y-5,
	                          anchor_x='left', anchor_y='top')
		self.label_high = pyglet.text.Label(str(self.high),
	                          font_name=self.font,
	                          font_size=10,
	                          x=self.x+self.bar_width, y=self.y-5,
	                          anchor_x='right', anchor_y='top')
		self.label_mid = pyglet.text.Label(str((self.high+self.low)//2),
	                          font_name=self.font,
	                          font_size=10,
	                          x=self.x+self.bar_width//2, y=self.y-5,
	                          anchor_x='center', anchor_y='top')
	
	def draw(self):
		self.bar_vertex_list.draw(pyglet.gl.GL_TRIANGLES)
		self.box_vertex_list.draw(pyglet.gl.GL_LINE_LOOP)	
		self.label_val.draw()
		self.label_name.draw()
		self.label_low.draw()
		self.label_high.draw()
		self.label_mid.draw()
		
	def update(self, dt, value):
		self.value = value
		self.vertices_bar = (self.x, self.y, self.x+int((self.value-self.low)/self.high*self.bar_width), self.y,  self.x+int((self.value-self.low)/self.high*self.bar_width), self.y+self.bar_height, self.x, self.y+self.bar_height)
		self.bar_vertex_list.vertices = self.vertices_bar
		if isinstance(self.value, int):
			self.label_val.text = str(value)+' '+self.unit
		else:
			self.label_val.text = "{0:.2f}".format(self.value)+' '+self.unit
				
if __name__ == "__main__":
	T = 0.5
	testing = False
	ELM_MAC_Address = "00:0D:18:00:00:01"
	filename = time.strftime("%Y%m%d_%H-%M-%S", time.localtime())		#filename YYYYMMDD_HH-MM-SS
	
	g = Gui(testing, ELM_MAC_Address, filename,timestep=T)
	g.open_file()
	if g.open_connection(): 
		g.run()
	g.terminate()
	