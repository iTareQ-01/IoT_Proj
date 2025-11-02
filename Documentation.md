# Smart Bins — IoT Waste Management System				
				
## Introduction				
The Smart Bins system is an Internet of Things (IoT)-based solution designed to automate the monitoring and collection of waste across multiple locations.				
Each bin is equipped with sensors (such as ultrasonic and weight sensors) to detect its fill level, which is periodically transmitted to a **central station** using the MQTT protocol.	We simulated the work of the sensors with a simple code block in each smart_bin.py 			
				
The central station collects this data, analyzes bin statuses, and determines optimal emptying schedules using a reinforcement learning-inspired decision mechanism.				
This improves waste collection efficiency, reduces operational costs, and prevents overflow situations.				
				
---				
				
## System Overview / Objective				
The main goal of this system is to **enable real-time monitoring** and **intelligent decision-making** in waste collection.				
The architecture is composed of:				
- **Smart Bins (Edge Devices):** sends measurements for fill percentage.				
- **MQTT Broker (e.g., Mosquitto):** Handles communication between bins and the central station.				
- **Central Station:** A Python-based service that receives MQTT messages, processes data, and applies decision logic (value iteration).				
- **Dashboard (optional):** Displays real-time bin status and collection events (e.g., ThingsBoard or custom MQTT dashboard). For that project, I just used my pc to work as the MQTT Broker.				
				
Objectives:				
1. Collect live bin fill-level data using sensors.				
2. Communicate efficiently via MQTT publish/subscribe.				
3. Compute collection actions dynamically.				
4. Provide a scalable and low-maintenance smart waste management platform.				
				
---				
				
## 🧱 Code Structure				
central_station.py	


├── `on_connect()` # MQTT callback to subscribe to bin topics when connected.			

├── `on_message()` # Callback triggered when bin sends data, sends the optimized action to the bin.	

├── `value_iteration()` # Reinforcement learning-based optimization, decides the best action.	

├── `fun_next_stat()` # Computes transitions given current state and action.

├── `connect_MQTT()` # Connects to broker.

├── `main()` # Starts MQTT client and message loop				
				
			
smart_bin.py

├── `on_connect()` # MQTT callback to print if the connection is done or not.			

├── `on_message()` # Callback triggered when central_station sends emptying command, empty the bin.	

├── `connect_MQTT()` # Connects to broker.

├── `main()` # Sends bin fill percentage every 5 seconds to mimic the sensor work.						
				
---				
				
## Algorithm Description				
The central station can apply either a **rule-based policy** or a **value iteration policy**:				
- **Rule-based policy:** If a bin’s fill percentage > 80%, mark it for emptying.				
- **Value Iteration policy:** Learns the optimal action based on rewards (e.g., +1 for empty bins, -1 for overfilled).				
Each bin’s fill level represents a **state**, and the emptying decision represents an **action**.				
Rewards encourage maintaining low congestion and avoiding overflow.	


Our Algorithm is following **Value Iteration policy** approach.	

At each iteration, the value of every state \( s \) is updated using:

$$
V(s) \leftarrow \max_a \sum_{s'} P(s' \mid s, a)
\left[ R(s, a, s') + \gamma V(s') \right]
$$

where:

- \( V(s) \): value of being in state \( s \)
- \( a \): action (which light is green)
- \( gamma \): discount factor (0.9 used here)
- \( P(s' \mid s, a) \): probability of transitioning to next state \( s' \) given action \( a \)
- \( R(s, a, s') \): immediate reward from the resulting traffic condition

The algorithm repeats these updates until the change in value between iterations, Delta falls below a small threshold \( theta = 0.001 \) denoted: 

$$ 
Delta = |V_{\text{new}}(s) - V_{\text{old}}(s)| 
$$

Once the values converge, the **optimal policy**  \( pi^*(s) \) is derived as:

$$
pi^*(s) = \arg\max_a Q(s, a)
$$

where

$$
Q(s, a) = \sum_{s'} P(s' \mid s, a)
\left[ R(s, a, s') + \gamma V(s') \right]
$$		

				
---				
				
## 📊 Input / Output Description				
**Inputs**				
- **Smart Bins (Edge Devices)** sends measurements for fill percentage %.				
- They sends to MQTT topics (e.g., `bin_1/waste_level`).				
				
**Outputs**				
- **Central Station** receives fill precentage, processes data, and applies decision logic (value iteration) then sends commands back to bins under MQTT topics (e.g., `central/empty1`).

  

https://github.com/user-attachments/assets/33a9368b-a733-494c-8863-1b68546d3a5b


				
				
**MQTT Flow:**				
Bin → MQTT Broker → Central Station → Decision → Command → MQTT Broker → Bin				
				
			
---				
				
## Summary				
The Smart Bins system combines IoT sensing, MQTT communication, and decision-making algorithms to enable real-time waste management automation.				
It’s efficient, scalable, and demonstrates how IoT devices can collaborate intelligently in smart cities.				
