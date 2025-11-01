import paho.mqtt.client as mqtt
import numpy as np
import sys

bins_level = [0, 0, 0, 0, 0]

# actions = {
# 	0 : lambda: print("wait!"),
# 	1 : lambda: client_1.publish("central/empty1", payload, 0, False),
# 	2 : lambda: client_1.publish("central/empty2", payload, 0, False),
# 	3 : lambda: client_1.publish("central/empty3", payload, 0, False),
# 	4 : lambda: client_1.publish("central/empty4", payload, 0, False),
# 	5 : lambda: client_1.publish("central/empty5", payload, 0, False)
# }


cur_itr = 0

#policy will store the actions to be done while being in a specified state , default actions is 0 = "wait"
policy = np.zeros( (11, 11, 11, 11, 11) , dtype=int)


def onMessage(client, userdata, msg):
	payload = "anymsg"
	global bins_level
	# global actions
	global policy

	#actions are {wait, collect trash from i bin} , collect trash cost = 1 , wait cost = 0 , if bin is full 95% reward = -5 & 0 otherwise

	if msg.topic == "bin_1/waste_level" :
		bins_level[0] = int ( msg.payload.decode() )
		print("bin1_level = ",bins_level[0])
		
	if msg.topic == "bin_2/waste_level" :
		bins_level[1] = int ( msg.payload.decode() )
		print("bin2_level = ",bins_level[1])
		
	if msg.topic == "bin_3/waste_level" :
		bins_level[2] = int ( msg.payload.decode() )
		print("bin3_level = ",bins_level[2])
		
	if msg.topic == "bin_4/waste_level" :
		bins_level[3] = int ( msg.payload.decode() )
		print("bin4_level = ",bins_level[3])
		
	if msg.topic == "bin_5/waste_level" :
		bins_level[4] = int ( msg.payload.decode() )
		print("bin5_level = ",bins_level[4])
		
		# TRY ----- TRY ----- TRY ----- TRY
		# if bin5_level == 100 :
		# 	# print("TEST")
		# 	client_1.publish("central/empty5", payload, 0, False)

	#We need to call the policy for the state where we are
	# actions[ policy[ bins_level[0], bins_level[1], bins_level[2], bins_level[3], bins_level[4] ] ]()
	# the past syntax keep crashing the program

	action = policy[ bins_level[0], bins_level[1], bins_level[2], bins_level[3], bins_level[4] ]
	match action:
		case 0: print("wait!")
		case 1:
			print("empty1!")
			client_1.publish("central/empty1", payload, 0, False)
		case 2:
			print("empty2!")
			client_1.publish("central/empty2", payload, 0, False)
		case 3:
			print("empty3!")
			client_1.publish("central/empty3", payload, 0, False)
		case 4:
			print("empty4!")
			client_1.publish("central/empty4", payload, 0, False)
		case 5:
			print("empty5!")
			client_1.publish("central/empty5", payload, 0, False)



# ------------------- Value iteration -------------------
def value_iteration():
	# global actions
	global policy
	global cur_itr

	#then we have at each bin, state level 0 && 10% -> 100% which is 11 state for each bin, index from 0 to 10 
	v_state = np.zeros( (11, 11, 11, 11, 11) )
	#we have here v_state[0, 0, 0, 0, 0] = state where level is 0 at all bins && v_state[7, 7, 7, 7, 7] = [70% all bins]

	gamma = 0.9
	delta_0 = 0.001
	n_actions = 6
	# -------------------------- idea, needs enhancement --------------------------
	# #to make the state space smaller, we limit the state space to be from >= 70, we have MAX_M = 5 && if 95 there's minus reward
	# #so when any state reaches 65 level, we should run the algorithm to find the best policy in various state cases
	# #becasue we need to take best decision when reaching 90 and we have 5 bins, so 5 * MAX_M = 25 .. I mean at each time step if one bin 
	# #reached 75 and we empty it, next bin2 reached 80/we empty, bin3 reached 85/we empty, bin4 90/empty, bin5 95/empty so we have penality 
	# #so we need to start take actions other than wait from state 70

	delta_iteration = 10000
	
	while delta_iteration > delta_0 :
		
		cur_itr += 1
		delta_iteration = 0
		for i in range(10, -1, -1):
			for j in range(10, -1, -1):
				for k in range(10, -1, -1):
					for m in range(10, -1, -1):
						for n in range(10, -1, -1):
							temp = v_state[i, j, k, m, n]
							# print("old v_state =", temp)

							# R1 = -5 if i+throw_S_dash >= 95 else 0
							# R2 = -5 if j+throw_S_dash >= 95 else 0
							# R3..... bla bla bla ------------> this is wrong, we need to estimate expected value (using probability)
							# which means to see -5 with probability 1/6 and 0 with probability 5/6 and so on

							# i want to go through the various actions and estimate the MAX action that has higher REWARD
							# we will consider the action to be "wait" when the if condition happens .. based on the previous idea
							# if bins_level[0]<70 and bins_level[1]<70 and bins_level[2]<70 and bins_level[3]<70 and bins_level[4]<70:
							# -----> this equal to 
							if (i<7)   and   (j<7)   and   (k<7)   and   (m<7)   and   (n<7):
								#we will compute the state value but the policy won't be updated, it will be the default 0 = "wait"
								#if action = "wait", we have 32 next state possible 2 to power 5 as each bin either remain with same level or increase by 10%
								#if action = "empty", we have 16 next state possible 
								#probability to sustain level for each bin or to increase by 10% is depending on the fill level before rounding to 10% step
								#so, we settle for just equal probability 

								a = 0
								q = 0
								for prob, reward, v_state_s_dash in fun_next_stat(i, j, k, m, n, a):
									# print(prob)
									# print(reward)
									# print(v_state[v_state_s_dash])
									q += ( prob *(reward + (gamma * v_state[v_state_s_dash])) )
									v_state[i, j, k, m, n] = q
								# print(f"if below 7, new v_state ({i}, {j}, {k}, {m}, {n}) =", v_state[i, j, k, m, n])
								# print("--------------------------------------")
																
							else:
								#here we can't expect the best action so will estimate it
								q_values = []
								for a in range(n_actions):
									q = 0
									for prob, reward, v_state_s_dash in fun_next_stat(i, j, k, m, n, a):
										# print(prob)
										# print(reward)
										# print(v_state[v_state_s_dash])
										q += ( prob *(reward + (gamma * v_state[v_state_s_dash])) )
									q_values.append(q)
									# print("action end with q =", q)

								v_state[i, j, k, m, n] = max(q_values)
								# print(f"if above 7, new v_state ({i}, {j}, {k}, {m}, {n}) =", v_state[i, j, k, m, n])
								# print("--------------------------------------")

								#we start from a = 0, so the q_values has [ (q when a = 0), (q when a = 1), (q when a = 2), ....]
								#i mean the highest value of q has index equal to the action so we can use argmax to get the index of the highest value-->
								policy[i, j, k, m, n] = np.argmax(q_values)

							#we now going for every state value and compute it, then will check the delta_iteration to be within accepted tolerance
							delta_iteration = max(delta_iteration, abs(v_state[i, j, k, m, n] - temp))

		print(f"delta_iteration = {delta_iteration}")
		print(f"cur_itr = {cur_itr}")
		if cur_itr >= 10000:
			print("Value iteration doesn't converge")
			sys.exit(-1)

	#ending the value iteration function
	print(f"Value iteration converged after {cur_itr}")
	return policy



def fun_next_stat(i, j, k, m, n, a):
	global cur_itr
	result = []
	cost = 0
	prob = (1/32) if a == 0 else (1/16)

	# if action was to empty one of the bins, then the bin level (next stat) would be zero
	if a == 1:  i, y1, cost = 0, 1, 1 
	else: 		i, y1 = i, 2
	
	if a == 2:  j, y2, cost = 0, 1, 1
	else: 		j, y2 = j, 2
	
	if a == 3:  k, y3, cost = 0, 1, 1  
	else: 		k, y3 = k, 2
	
	if a == 4:  m, y4, cost = 0, 1, 1 
	else: 		m, y4 = m, 2
	
	if a == 5:  n, y5, cost = 0, 1, 1 
	else: 		n, y5 = n, 2

	# print(f"a = {a}, y1 = {y1}, y2 = {y2}, y3 = {y3}, y4 = {y4}, y5 = {y5}")
	# for_loop = 0
	for x1 in range(y1):
		for x2 in range(y2):
			for x3 in range(y3):
				for x4 in range(y4):
					for x5 in range(y5):
						reward = 0
						# for_loop += 1	
						# print(f"for_loop = {for_loop} & reward = {reward}")
						if (i+x1) > 10: x1=0	
						if (j+x2) > 10: x2=0	
						if (k+x3) > 10: x3=0	
						if (m+x4) > 10: x4=0	
						if (n+x5) > 10: x5=0	

						v_state_s_dash = (i+x1, j+x2, k+x3, m+x4, n+x5)
						reward = -5 * sum( var > 9 for var in v_state_s_dash)
						# checks if there's value > 9 in the v_state_s_dash
						reward = reward - cost
						# print(f"for_loop = {for_loop} & reward = {reward}")
						result.append( (prob, reward, v_state_s_dash) )


	#ending the fun_next_stat 
	# if cur_itr > 3:
	# 	print(result)
	return result

def onConnect(client_1, userdata, flags, rc):
	if rc == 0:
		print("Listening ...")		
		print("Press CTRL+C to exit ...")
		client_1.subscribe("bin_1/waste_level")
		client_1.subscribe("bin_2/waste_level")
		client_1.subscribe("bin_3/waste_level")
		client_1.subscribe("bin_4/waste_level")
		client_1.subscribe("bin_5/waste_level")
	else:
		print("Couldn't connect to MQTT Broker. Error code:", rc)
		sys.exit(-2)



#we want to run the value iteration in another thread 
#i will settle for running the function in the same main thread as we can't proceed further until having the policy
policy = value_iteration()


#first, central station is subscriber to the waste_level .... 
#next when level = 100, it will publish to EMPTY topic to send msg to the smart_bin which will be reset

######### mqttBroker = "demo.thingsboard.io" -> changed the solution arch 
mqttBroker = "localhost"
                                                                                
#create mqtt client named as central_station --> we used here the paho.mqtt.client lib 
client_1 = mqtt.Client("central_station")
client_1.on_connect = onConnect

client_1.connect(mqttBroker, 1883, 60)	

#some code to be done when it recieves msg from the broker
client_1.on_message = onMessage



try:
	client_1.loop_forever()
except:
	print("\nDisconnecting from Broker")

client_1.disconnect()
