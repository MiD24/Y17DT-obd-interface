#import serial
import time
import re
import bluetooth

port = 1
class obd_serial:
	def __init__(self):
		self.logging = True
		self.ELM_socket = None
		
	
	def connect(self, MAC_address):
		try:
			self.ELM_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
			self.log('New socket created')
			self.ELM_socket.connect((MAC_address, port))
			self.log('ELM socket created')
		except:
			self.error('Unable to connect to ELM327')
			self.ELM_socket = None
			return False
				
			
	def elm(self, cmd, testing=False):
		if testing:
			time.sleep(0.3)
			#return('NO DATA')
			return("80 F1 11 46 61 01 00 00 00 00 00 00 00 00 30 00 42 00 00 A2 EF 00 A7 2F 00 00 EF 81 00 09 00 00 00 0  78 00 36 1A 28 1A 36 44 44 1A 78 90 32 AD AD 54 50 74 07 5D 7B 69 64 0D 32 19 40 00 3B 46 00 00 00 00 00 62 06 10 F5 65 A2")
		r = self.send_and_listen(cmd)	
#		if r:
#			print('<<< ' + r[-1])
		return r[-1]
	
	def send_and_listen(self, cmd):
		if not self.ELM_socket:
			self.error('Unable to send, not connected')
			return None
		self.write(cmd)
		r = self.__read()
		return r
	
	def write(self, cmd=None):
		if cmd:
			#cmd = cmd.encode('UTF-8') + b'\r\n'
			cmd = cmd + '\r\n'
		try:
			self.log("Writing " + cmd)
			self.ELM_socket.send(cmd)
		except:
			self.error('Unable to write to serial')
			
	def __read(self):
		"""
		"low-level" read function
		
		accumulates characters until the prompt character is seen
		returns a list of [/r/n] delimited strings
		"""
		if not self.ELM_socket:
			self.log("cannot perform __read() when unconnected")
			return []
		
		buffer = bytearray()
		
		while True:
			# retrieve as much data as possible
			data = self.ELM_socket.recv(1024)
		
			# if nothing was recieved
			if not data:
				self.log("Failed to read port")
				break
		
			buffer.extend(data)
		
			# end on chevron (ELM prompt character)
			if b'>' in buffer:
				break
		
		# log, and remove the "bytearray(   ...   )" part
		self.log("read: " + repr(buffer)[10:-1])
		
		# clean out any null characters
		buffer = re.sub(b"\x00", b"", buffer)
		
		# remove the prompt character
		if buffer.endswith(b'>'):
			buffer = buffer[:-1]
		
		# convert bytes into a standard string
		string = buffer.decode()
		
		# splits into lines while removing empty lines and trailing spaces
		lines = [ s.strip() for s in re.split("[\r\n]", string) if bool(s) ]
		
		return lines
	
	def log(self, msg):
		if self.logging:
			print('LOG: ' + msg)
	
	def error(self, msg):
		print('ERROR: ' + msg)
	
	def init_ELM(self):
		self.send_and_listen('ATZ') #reset
		time.sleep(1)
		self.send_and_listen('ATE0') #echo off
		self.send_and_listen('ATAL') #allow long messages
		self.send_and_listen('ATSP5') #Set protocol ISO 14230-4 (KWP FAST)
		self.send_and_listen('ATH1') #headers on
		self.send_and_listen('ATSH8111F1') #header 8111F1
		self.log('Voltage = ' + self.send_and_listen('ATRV')[-1])
	
	def close(self):
		if self.ELM_socket:
			self.ELM_socket.close()
	
	def set_logging(self, status):
		self.logging = status
