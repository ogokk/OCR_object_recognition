import os 
import time
import RPi.GPIO as GPIO

while True:
	GPIO.setmode(GPIO.BOARD)

	TRIG = 10
	ECHO = 18 

	GPIO.setup(TRIG,GPIO.OUT)
	GPIO.output(TRIG,0)

	GPIO.setup(ECHO, GPIO.IN)
	time.sleep(0.1)


	trigger_data = []
	realtime_data = []
	condition = True

	while condition:
		print("*****Start Measurement*******")
		GPIO.output(TRIG, 1)
		time.sleep(0.00001)
		GPIO.output(TRIG, 0)
		while GPIO.input(ECHO) == 0:
			start = time.time()
		while GPIO.input(ECHO) == 1:
			stop = time.time()
		measure = (stop - start)*17000
		print("measure distance : " measure)
		GPIO.cleanup()
		#measure = object(distance, container) % returns distance value
		realtime_data.append(measure)
		if measure >= 2 and measure <= 3.5 # if measured data is between 2 and 3.5 m 	
			trigger_data.append(measure)
			if len(trigger_data) == 3:
				condition = False
			else:
				condition = True
			time.sleep(1)
		else:
			pass

	if trigger_data[0] == trigger_data[1] and trigger_data[1] == trigger_data[2] and trigger_data[0] == trigger_data[2]: # check for the first three data whether they are the same or not
		set_mode(GPIO12, IN) # returns 1 (True) to trigger 
	else:
		set_mode(GPIO12, OUT) # returns 0 (False) to no-trigger

	check_same_measured_values = all(i for i in range(len(realtime_data)) if realtime_data[i] == trigger_data[i+2])
	if check_same_measured_values == True:
		time.sleep(3)
	else:
		pass
	
	# data = []
	# while next measurement is the same with the above first three measurement, then set_mode(GPIO12, OUT)
	# or
	# time.sleep(2)
	

	