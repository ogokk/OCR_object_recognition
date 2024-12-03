import os 
import time
import RPi.GPIO as GPIO
import datetime

GPIO.setmode(GPIO.BOARD)

TRIG = 10
ECHO = 18
RELAY_PIN = 7
RELAY_PIN_2 = 11

start = 0.0
stop  = 0.0

def measurement():
		global start
		global stop		
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.output(TRIG, False)
        #GPIO.output(TRIG, LOW)
        #GPIO.output(TRIG, 0)

        GPIO.setup(ECHO, GPIO.IN)
        time.sleep(0.1)

        GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.output(RELAY_PIN, 1)

        GPIO.setup(RELAY_PIN_2, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.output(RELAY_PIN_2, 1)

        print("**************Start Measurement***************")

        GPIO.output(TRIG, 1)
        time.sleep(0.00001)
        GPIO.output(TRIG, 0)

        while GPIO.input(ECHO) == 0:
                start = time.time()

        while GPIO.input(ECHO) == 1:
                stop = time.time()

        measure = (stop - start) * 17150
        #measure = round(measure, 1)
        measure = int(measure)

        print("Container distance : %d cm" % measure)

        return measure

##def check_same_data(items):
##        return all(x == items[0] for x in items)

count = 0 

while True:
        while True:
                data = []
                measure = measurement()
                if measure > 20 and measure < 130:
                        for item in range(0,3):
                                data.append(measurement())
                                time.sleep(3)
##                        if check_same_data(data):
                        
                        tolerance = 10
                        if abs(data[0]- data[1]) < tolerance and abs(data[0]- data[2]) < tolerance:
                                print(data[0], data[1], data[2])
                                print("testing the range")
##                              first trigger                                
                                GPIO.output(RELAY_PIN, 0)
                                GPIO.output(RELAY_PIN_2, 0)
                                time.sleep(0.5) # relay time during on mode
                                GPIO.output(RELAY_PIN, 1)
                                GPIO.output(RELAY_PIN_2, 1)
                                time.sleep(0.5)
##                              second trigger
                                GPIO.output(RELAY_PIN, 0)
                                GPIO.output(RELAY_PIN_2, 0)
                                time.sleep(0.5) # relay time during on mode
                                GPIO.output(RELAY_PIN, 1)
                                GPIO.output(RELAY_PIN_2, 1)
                                time.sleep(0.5)
##                              Third trigger
                                GPIO.output(RELAY_PIN, 0)
                                GPIO.output(RELAY_PIN_2, 0)
                                time.sleep(0.5) # relay time during on mode
                                GPIO.output(RELAY_PIN, 1)
                                GPIO.output(RELAY_PIN_2, 1)
                                count = count + 1
                                path = "/home/pi/"
                                os.chdir(path)
                                with open("Trigger Log.txt", "a") as nemport:
                                        nemport.write("%s\nContainer distance measured values : %s %s %s\nTrigger time : %s\n" % (count, data[0], data[1], data[2], datetime.datetime.now()))
                                        nemport.write("-----------------------------*************------------------------\n")
                                print("trigger time : %s" % datetime.datetime.now())
                                waiting_time = 0
                                while True:
                                        new_measurement = measurement()
                                        if data[len(data)-1] == new_measurement or data[len(data)-1] == new_measurement-1\
                                        or data[len(data)-1] == new_measurement+1\
                                        or data[len(data)-1] == new_measurement - 2 or data[len(data)-1] == new_measurement +2:
                                                time.sleep(10)
                                                waiting_time  = waiting_time + 1
                                                print("waiting time : %d sn" % (10 * waiting_time))
                                        else:
                                                break
                                
                
                time.sleep(5)
 
        GPIO.cleanup()
        
