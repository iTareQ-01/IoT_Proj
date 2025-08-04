import paho.mqtt.client as mqtt
import sys

payload = "anymsg"

def onMessage(client, userdata, msg):
	global payload
	if msg.topic == "bin_1/waste_level" :
		bin1_level = int( msg.payload.decode() )
		print("bin1_level = ",bin1_level, type(bin1_level))
		
		if bin1_level == 100 :
			# print("TEST")
			client_1.publish("central/empty1", payload, 0, False)

	if msg.topic == "bin_2/waste_level" :
		bin2_level = int ( msg.payload.decode() )
		print("bin2_level = ",bin2_level, type(bin2_level))
		
		if bin2_level == 100 :
			# print("TEST")
			client_1.publish("central/empty2", payload, 0, False)


#first, central station is subscriber to the waste_level .... 
#next it will publish to EMPTY topic to send msg to the smart_bin which will be reset

######### mqttBroker = "demo.thingsboard.io" -> changed the solution arch 
mqttBroker = "localhost"

#create mqtt client named as central_station --> we used here the paho.mqtt.client lib 
client_1 = mqtt.Client("central_station")
if client_1.connect(mqttBroker, 1883, 60) == 0:
	print("Listening ...")		
	print("Press CTRL+C to exit ...")
else:
	print("Couldn't connect to MQTT Broker")
	sys.exit(-2)
#we can replace the previous if condition with <<<< on_connect >>>> function

client_1.subscribe("bin_1/waste_level")
client_1.subscribe("bin_2/waste_level")

#some code to be done when it recieves msg from the broker
client_1.on_message = onMessage

try:
	client_1.loop_forever()
except:
	print("\nDisconnecting from Broker")

client_1.disconnect()
