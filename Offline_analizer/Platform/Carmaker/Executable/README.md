# CarMaker Release [forked from VR_HIL]

Subversion: 2.15.1 [Architecture].[Major release].[Minor release]
TDP
	N/A

Deliverables
	VV_Tools_HILs (Carmaker executable project) tag ADAS_HIL_Platform_2.15.1 https://sourcecode01.de.bosch.com/projects/NRCSGEN2/repos/vv_tools_hils/browse/VR-HIL/Projects/FORD
	

Released for the Tool Software
	- Carmaker 12.0.2 Office Pro

Taken quality measures and status of the measures:
	N/A

Changelog:
2.15 major release
- ADASXIL-1596 - DIL status flag - section [1.5.]
- SOSFORDDAT-130243 - additional USS fault injection options
- SOSFORDDAT-161205 - hotfixes for USS sensor control
2.15.1 minor release
- SOSFORDDAT-147611 - hotfix of USS firing state at power reset


## Content

### 1. Robert Bosch (RB) quantities
#### 1.1. Car parameters
##### 1.1.1. Sensor mounting
###### 1.1.1.1. Carmera (FVideo)
 - position (x, y, z)
 - orientaiton (yaw)
###### 1.1.1.2. Radar (FC, FL, FR, RL, RR)
 - position (x, y, z)
 - orientaiton (yaw)
##### 1.1.2. Ego parameters
 - Dimensions (wheelBase, trackWidth, overhangFront, overhangRear, mass)
 - Gear (gearbox kind, nbr of gear posiitons)
 - Motion (max velocity, driven distance)
 - Wheel dimensions (nbr of wheels, wheel parameters)
#### 1.2 Ground truth sensor
##### 1.2.1. Line (points)
 - line data (nbr of points, type, width)
 - position (x, y, z)
#### 1.3. Object sensors
##### 1.3.1. Radars (FC, FL, FR, RL, RR)
 - relative orientation (yaw)
 - relative acceleration (x, y)
 - relative velocity (x, y)
 - relative distance/coordinates (x, y, z)
 - classification
 - dimensions (size)
 - line of sight
 - radar signal attributes (RCS, SNR, strength)
##### 1.3.2. Video (FV)
 - relative orientation (yaw)
 - relative acceleration (x, y)
 - relative velocity (x, y)
 - relative distance/coordinates (x, y, z)
 - classification
 - dimensions (size)
##### 1.3.3. Traffic Sign (TS1)
 - nbr of signs
 - object ID
 - relative distance/coordinates (x, y, z)
 - main sign ID
 - time stamp
#### 1.4. Ultra sonic sensors
 - Multitesters (front/rear sensor cluster fault) [writable]
 - position (x, y)
 - firing state [writable]
 - sensor fault [writable]
#### 1.5. Traffic Object control
 - nbr of objects
 - object ID
 - relative orientation (z/yaw) [writable]
 - relative distance/coordinates (x, y, z) [writable]
 - acceleration (longitudinal)
 - velocity (longitudinal) [writable]
 - lateral distance (relative to assigned path) [writable]
 - lalongitudinal distance (relative to assigned path) [writable]
 - steering wheel angle [writable]
 - indicator light [writable]
 - DIL status [writable]
#### 1.6. Ego motion
 - steepness of road under Ego (measured pitch and roll angles)
 - measured suspension delta position to Normal Ride Height for all wheels
