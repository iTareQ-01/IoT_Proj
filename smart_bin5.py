import paho.mqtt.client as mqtt
from random import randint, uniform
import time
import sys
import threading

#first, smart_bin1 is publisher its waste_level .... 
#next it will subscribe to EMPTY topic to get msg from central station

MAX_M = 5
waste_level5 = 0
lock = threading.Lock()  #to prevent race-condition that may happen as loop_start() fun runs onMessage fun in another thread

def onConnect(client_5, userdata, flags, rc):
	if rc == 0:
		print("Connected to Broker Successfully!")

	else:
		print("Couldn't connect to MQTT Broker!")
		sys.exit(-1)

def onMessage(client_5, userdata, msg):
	global waste_level5
	with lock:
		waste_level5 = 0
	print("bin_5 got empty")

######### mqttBroker = "demo.thingsboard.io" -> changed the solution arch 
mqttBroker = "localhost"

#create mqtt client named as waste_level5 --> we used here the paho.mqtt.client lib 
client_5 = mqtt.Client("waste_level5")
client_5.connect(mqttBroker, 1883, 60)
client_5.on_connect = onConnect

#------------------------------------------------- HERE WE will Start the subscribe to central station -----------------#
client_5.subscribe("central/empty5")
#some code to be done when it recieves msg from the broker
client_5.on_message = onMessage

#starting another thread to make MQTT loop on on_message & on_connect
try:
	client_5.loop_start()
except:
	print("\nDisconnecting from Broker")
	client_5.disconnect()
	sys.exit(-1)

#main task of the smart bin
while True:
	throw = round( uniform (0, MAX_M) )
	#WAS FOR INSPECT ------------- print("Rubbish Thrown:", throw)
	with lock:
		waste_level5 = min( (waste_level5 + throw), 100 )	

	#to make the value published increase with only 10, I mean if it was increased by 1, the level still = 0
	waste_level_pub = round(waste_level5 / 10) * 10

	client_5.publish("bin_5/waste_level", waste_level_pub, 2, False)	
	#at the previous step we put the retain to false & qos=0 to make no congestion in the network
	#i changed qos=2 to be more precise in reaching the central station when multi bins publish data 
	
	print("Just published " + str(waste_level_pub) + "% to TOPIC bin_5/waste_level")
	time.sleep(5)
	#i assumed that every 5 seconds, there're people will throw something in the bin
	#this is to simulate the sensors and rasperrybi 


#just in case, we got out of the endless loop
client_5.loop_stop()
client_5.disconnect()


