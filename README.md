This project is a simulation of a lunar lander tasked with landing safely in a designated area while
avoiding asteroids. The simulation leverages the Deep Deterministic Policy Gradient (DDPG)
algorithm for controlling the lander. The lander is equipped with three engines, each of which can be
controlled in terms of thrust and thrust angle.

**Key Features:**

**DDPG Algorithm:** Implemented for continuous control of the lander's engines.

**Sensors:** The lander is equipped with sensors to detect nearby asteroids, helping it navigate and avoid collisions.

**Neural Network Inputs:** The neural network receives the following inputs:
  * Sensor readings (asteroid proximity)
  * Lander velocity in both the x and y axes
  * Lander position in both the x and y axes
  * 
**Neural Network Outputs:**
  * Thrust force for each of the three engines
  * Thrust angle for each of the three engines

This simulation demonstrates reinforcement learning in a dynamic and challenging environment, providing insights into autonomous navigation and obstacle avoidance.


