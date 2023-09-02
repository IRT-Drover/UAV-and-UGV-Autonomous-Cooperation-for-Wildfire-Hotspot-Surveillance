# Drover-UAV-and-UGV-Autonomous-Cooperation-for-Wildfire-Hotspot-Surveillance

This repository is the code for the paper [_UAV and UGV Autonomous Cooperation for Wildfire Hotspot Surveillance_](https://ieeexplore.ieee.org/document/10002208/) published in IEEE and presented at the MIT Undergraduate Research and Technology Conference. 



## Abstract
As wildfires burn millions of acres each year around the globe and have become more severe due to climate change, wildfire prevention is more important now than ever. Existing wildfire surveying techniques such as hotspotting and cold trailing require human interventions that can lead to dangerous situations or satellite imagery which does not provide real-time data on hotspots. To address this problem, we propose a low-cost and effective integrated system of robots composed of an unmanned aerial vehicle (UAV, or drone) and unmanned ground vehicle (UGV, or rover) that autonomously cooperate and pathfind to detect and investigate hotspots. The UAV monitors a post-forest fire area from the air and uses aerial footage to create long-term direction for the UGV to inspect specific suspected hotspots. The UGV then follows the path to investigate each hotspot with centimeter-level accuracy. Testing of the pathfinding system with satellite imagery yielded highly accurate and consistent results necessary for high-precision autonomous navigation when investigating hotspots in dynamic environments.

![image](https://github.com/IRT-Drover/UAV-and-UGV-Autonomous-Cooperation-for-Wildfire-Hotspot-Surveillance/assets/74738050/c3c52e14-d321-4884-bf1d-6824f154db81)

*Picture of the Drone*

![image](https://github.com/IRT-Drover/UAV-and-UGV-Autonomous-Cooperation-for-Wildfire-Hotspot-Surveillance/assets/74738050/5579a661-48cd-47b0-886c-6625530fd0f0)

*Picutre of the Rover*

## System Design
The system consists of three main components: a drone, a rover, and a ground station (The Drone and Rover are seen in images below). All devices are connected through a server powered by [Apache Kafka](https://kafka.apache.org/) to which data and commands are sent. The order of operations for the system is:

   1. The drone lifts off, travels to its designated waypoint, and takes a photo of the area in which the rover will be moving.

   2. The image is then sent to the ground station which creates a path using a modified pixel weighting A* pathfinding algorithm. The path includes points of interest detected by the drone (suspected hotspots). Each pixel in the path is converted to GPS coordinates.

   3.The GPS coordinates are then sent to the rover. The rover follows the path and adjusts to any obstacles overlooked by A* with an obstacle-avoidance algorithm.

![image](https://github.com/IRT-Drover/UAV-and-UGV-Autonomous-Cooperation-for-Wildfire-Hotspot-Surveillance/assets/74738050/72b39f77-eef9-4f0d-8e65-1530d33ab0e0)

*Figure of the System Design*


## How this respository is structured
The Drone folder contains autonomous programs for the drone, including takeoff scripts, the apache kafka consumer and producers, and the autonomous gyroscopic camera functions. 

The Ground Station folder contains python scripts for the A* pathfinding algorithm, pixels to coordinate algorithms, and communications software for the system.

The Rover folder contains movement python scripts and the short term obstacle avoidance algorithm. 

The Camera Calibration folder contains intrinsic parameters for camera undistortion. 

The parts list is also included in the repository.

![image](https://github.com/IRT-Drover/UAV-and-UGV-Autonomous-Cooperation-for-Wildfire-Hotspot-Surveillance/assets/74738050/e6e88831-7b5c-49aa-b36a-5d0e377425f4)

*Picture of the Softwares Used*

## Support

For support, please email dpasini@seas.upenn.edu or cjiang@nd.edu.

