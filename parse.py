def parse(string):
	arr = str2arr(string)
	lst = hex2dec(arr)
	dic = create_dict(lst)
	return dic

def str2arr(s):
	s = s.replace("  ", " ")
	return s.split(" ")
	
def hex2dec(h):
	lst = []
	for num in h:
		lst.append(int(num, 16))
	return lst

def create_dict(lst):
	d = lst[4:-1]
	dic = {"Battery": d[33-1]/4.0,
		"RPM": (256.0*d[34-1]+d[35-1])/8.0,
		"Pump RPM": (256.0*d[34-1]+d[35-1])/16.0,
		"Desired idle": d[39-1]*12.5,
		"Speed": d[40-1],
		"Coolant temp": d[44-1]*0.75-42.5,
		"Air temp": d[46-1]*0.75-42.5,
		"Atmosf temp": d[47-1]*0.75-42.5,
		"MAF": (256.0*d[49-1]+d[50-1])*0.0281,
		"Boost pressure": d[52-1],
		"Target boost pressure": d[53-1],
		"Boost control valve": d[54-1]*100.0/255.0,
		"Pedal position": d[58-1]*100.0/255.0,
		"EGR": d[61-1]*100.0/255.0,
		"Fuel temp": d[66-1]*0.75-42.5,
		"Injection Q": d[67-1] if (d[67]<250) else 0,
		"Injection start": d[68-1],
		"Atmosf pressure": d[70-1]}
	return dic

