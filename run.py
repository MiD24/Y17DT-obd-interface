#!/usr/bin/env python3
print('Start script')
import obd_serial
import time

filename = time.strftime("%Y%m%d_%H-%M-%S", time.localtime())		#filename YYYYMMDD_HH-MM-SS
try:
	file = open(filename + '.obd', 'a')					#open file in append mode
except IOError:
	print('Cannot open file')
T = 0.5											#logging period
obd = None
try:
	obd = obd_serial.obd_serial()						#open bluetooth connection
except:	print("Unable to connect")
try:
	if obd:
		obd.init_ELM()								#initialize ELM327
		obd.set_logging(False)							#disable log messages
		try:
			print("Starting measurements")
			while True:								#infinite loop
				t0 = time.time()
				resp = obd.elm('2101')					#write '2101' to ELM327 and return response
				file.write(resp + '\n')				#write response to file
				dt = time.time() - t0
				time.sleep(T - max(T-dt, 0))
		except KeyboardInterrupt:						#break from loop on ctrl+c
			file.write("end" + "\n\n")
			print("Stopped measurements")
except:
	print('Unknown error caught')
	pass
file.close()
if obd:
	obd.close()
print('Stop script')

